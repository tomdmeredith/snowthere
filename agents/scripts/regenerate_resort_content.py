#!/usr/bin/env python3
"""Regenerate content sections for resorts using stored data.

Uses existing Supabase data as input (no new research API calls), then runs
the full content-generation pipeline with current voice prompts. Useful for
validating voice/prompt changes end-to-end.

Single resort:
    python scripts/regenerate_resort_content.py --resort "Garmisch-Partenkirchen"
    python scripts/regenerate_resort_content.py --resort "Garmisch-Partenkirchen" --write
    python scripts/regenerate_resort_content.py --resort "Serfaus-Fiss-Ladis" --sections quick_take,getting_there

Batch mode (all published resorts, oldest first):
    python scripts/regenerate_resort_content.py --batch --batch-limit 5
    python scripts/regenerate_resort_content.py --batch --batch-limit 10 --write
    python scripts/regenerate_resort_content.py --batch --batch-limit 10 --batch-offset 10 --write

Cost: ~$0.50-$1.00 per resort (Opus for content, Sonnet for extraction, Haiku for atoms).
"""

import argparse
import asyncio
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.content import write_section, generate_faq, generate_seo_meta
from shared.primitives.quick_take import QuickTakeContext, generate_quick_take
from shared.primitives.intelligence import (
    extract_quick_take_context,
    extract_tagline_atoms,
    generate_diverse_tagline,
    evaluate_tagline_quality,
)
from shared.primitives.database import (
    update_resort_content,
    update_resort_family_metrics,
    get_recent_portfolio_taglines,
)
from shared.primitives.system import get_daily_spend
from shared.primitives.style import apply_deterministic_style
from shared.config import settings


CONTENT_SECTIONS = [
    "getting_there",
    "where_to_stay",
    "lift_tickets",
    "on_mountain",
    "off_mountain",
    "parent_reviews_summary",
]

SCRATCHPAD = Path(
    os.environ.get(
        "SCRATCHPAD_DIR",
        Path(__file__).parent.parent.parent / "scratchpad",
    )
)


def fetch_resort_data(resort_name: str) -> dict:
    """Fetch all stored data for a resort from Supabase."""
    client = get_supabase_client()

    # Find the resort
    resort_resp = (
        client.table("resorts")
        .select("*")
        .ilike("name", resort_name)
        .limit(1)
        .execute()
    )
    if not resort_resp.data:
        print(f"Resort not found: {resort_name}")
        sys.exit(1)

    resort = resort_resp.data[0]
    resort_id = resort["id"]
    print(f"Found resort: {resort['name']} ({resort['country']}) [{resort_id}]")

    # Fetch content
    content_resp = (
        client.table("resort_content")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )

    # Fetch family metrics
    metrics_resp = (
        client.table("resort_family_metrics")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )

    # Fetch costs
    costs_resp = (
        client.table("resort_costs")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )

    # Fetch calendar
    calendar_resp = (
        client.table("ski_quality_calendar")
        .select("*")
        .eq("resort_id", resort_id)
        .order("month")
        .execute()
    )

    return {
        "resort": resort,
        "content": content_resp.data or {},
        "family_metrics": metrics_resp.data or {},
        "costs": costs_resp.data or {},
        "calendar": calendar_resp.data or [],
    }


def build_research_data(stored: dict) -> dict:
    """Build a synthetic research_data dict from stored Supabase data.

    The existing content sections serve as "research sources" since they
    contain all the specific names, prices, and details originally extracted.
    """
    content = stored["content"]
    return {
        "family_metrics": stored["family_metrics"],
        "costs": stored["costs"],
        "quick_take": content.get("quick_take", ""),
        "calendar": stored["calendar"],
        "getting_there": content.get("getting_there", ""),
        "where_to_stay": content.get("where_to_stay", ""),
        "on_mountain": content.get("on_mountain", ""),
        "off_mountain": content.get("off_mountain", ""),
        "lift_tickets": content.get("lift_tickets", ""),
        "parent_reviews_summary": content.get("parent_reviews_summary", ""),
    }


def build_content_context(stored: dict) -> dict:
    """Build the context dict that write_section() expects for template formatting."""
    resort = stored["resort"]
    fm = stored["family_metrics"]
    costs = stored["costs"]
    content = stored["content"]

    return {
        "resort_name": resort["name"],
        "country": resort["country"],
        "region": resort.get("region", ""),
        "family_score": fm.get("family_overall_score") or fm.get("family_score", "N/A"),
        "best_age_min": fm.get("best_age_min"),
        "best_age_max": fm.get("best_age_max"),
        "has_childcare": fm.get("has_childcare", False),
        "has_ski_school": fm.get("has_ski_school", True),
        "ski_school_min_age": fm.get("ski_school_min_age"),
        "kids_ski_free_age": fm.get("kids_ski_free_age"),
        "terrain_pct_beginner": fm.get("beginner_terrain_pct") or fm.get("kid_friendly_terrain_pct"),
        # Cost context
        "lift_adult_daily": costs.get("lift_adult_daily"),
        "lift_child_daily": costs.get("lift_child_daily"),
        "estimated_family_daily": costs.get("estimated_family_daily"),
        "price_level": costs.get("price_level"),
        # Existing content as research context
        "existing_getting_there": content.get("getting_there", ""),
        "existing_where_to_stay": content.get("where_to_stay", ""),
        "existing_on_mountain": content.get("on_mountain", ""),
        "existing_off_mountain": content.get("off_mountain", ""),
        "existing_lift_tickets": content.get("lift_tickets", ""),
        "existing_reviews": content.get("parent_reviews_summary", ""),
    }


def save_json(data: dict, filepath: Path):
    """Save data as formatted JSON."""
    filepath.parent.mkdir(parents=True, exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2, default=str)
    print(f"Saved: {filepath}")


def word_count(html: str) -> int:
    """Count words in HTML content."""
    if not html:
        return 0
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain).strip()
    return len(plain.split())


def preview(html: str, chars: int = 200) -> str:
    """Return first N chars of plain text from HTML."""
    if not html:
        return "(empty)"
    plain = re.sub(r"<[^>]+>", " ", html)
    plain = re.sub(r"\s+", " ", plain).strip()
    if len(plain) > chars:
        return plain[:chars] + "..."
    return plain


async def regenerate(
    resort_name: str,
    write: bool = False,
    sections_filter: list[str] | None = None,
):
    """Main regeneration flow."""

    print(f"\n{'='*70}")
    print(f"CONTENT REGENERATION - Voice Validation")
    print(f"{'='*70}")
    print(f"Resort: {resort_name}")
    print(f"Mode: {'WRITE (will update DB)' if write else 'DRY RUN (compare only)'}")
    if sections_filter:
        print(f"Sections: {', '.join(sections_filter)}")
    print(f"{'='*70}\n")

    # 1. Fetch stored data
    print("[1/11] Fetching stored data from Supabase...")
    stored = fetch_resort_data(resort_name)
    resort = stored["resort"]
    resort_id = resort["id"]
    slug = resort["slug"]
    country = resort["country"]

    # 2. Save "before" snapshot
    print("[2/11] Saving 'before' snapshot...")
    before_path = SCRATCHPAD / f"before_{slug}.json"
    save_json(stored["content"], before_path)

    # 3. Build synthetic research data
    print("[3/11] Building synthetic research data...")
    research_data = build_research_data(stored)
    content_context = build_content_context(stored)

    # Track new content
    new_content = {}

    # 4. Extract Quick Take editorial context
    should_do = lambda s: sections_filter is None or s in (sections_filter or [])

    if should_do("quick_take"):
        print("\n[4/11] Extracting Quick Take editorial context...")
        qt_context_result = await extract_quick_take_context(
            resort_name=resort["name"],
            country=country,
            research_data=research_data,
        )
        print(f"  Confidence: {qt_context_result.extraction_confidence:.2f}")
        print(f"  Unique angle: {qt_context_result.unique_angle}")
        print(f"  Primary weakness: {qt_context_result.primary_weakness}")

        # 5. Generate Quick Take
        print("\n[5/11] Generating Quick Take...")
        fm = stored["family_metrics"]
        qt_ctx = QuickTakeContext(
            resort_name=resort["name"],
            country=country,
            region=resort.get("region"),
            family_score=fm.get("family_overall_score") or fm.get("family_score"),
            best_age_min=fm.get("best_age_min"),
            best_age_max=fm.get("best_age_max"),
            unique_angle=qt_context_result.unique_angle,
            signature_experience=qt_context_result.signature_experience,
            primary_strength=qt_context_result.primary_strength,
            primary_weakness=qt_context_result.primary_weakness,
            who_should_skip=qt_context_result.who_should_skip,
            memorable_detail=qt_context_result.memorable_detail,
            price_context=qt_context_result.price_context,
            terrain_pct_beginner=fm.get("beginner_terrain_pct") or fm.get("kid_friendly_terrain_pct"),
            has_ski_school=fm.get("has_ski_school", True),
            ski_school_min_age=fm.get("ski_school_min_age"),
            has_childcare=fm.get("has_childcare", False),
            kids_ski_free_age=fm.get("kids_ski_free_age"),
        )

        qt_result = await generate_quick_take(qt_ctx, voice_profile="snowthere_guide")
        print(f"  Valid: {qt_result.is_valid}")
        print(f"  Words: {qt_result.word_count}")
        print(f"  Specificity: {qt_result.specificity_score:.2f}")
        if qt_result.validation_errors:
            print(f"  Errors: {qt_result.validation_errors}")
        if qt_result.forbidden_phrases_found:
            print(f"  Forbidden: {qt_result.forbidden_phrases_found}")

        new_content["quick_take"] = qt_result.quick_take_html
        new_content["_perfect_if"] = qt_result.perfect_if
        new_content["_skip_if"] = qt_result.skip_if
    else:
        print("\n[4/11] Skipping Quick Take (not in sections filter)")
        print("[5/11] Skipping Quick Take generation")

    # 6. Generate content sections
    print("\n[6/11] Generating content sections...")
    sections_to_generate = [s for s in CONTENT_SECTIONS if should_do(s)]

    for section in sections_to_generate:
        print(f"  Writing: {section}...")
        section_html = await write_section(
            section_name=section,
            context=content_context,
            voice_profile="snowthere_guide",
        )
        new_content[section] = section_html
        print(f"    {word_count(section_html)} words")

    skipped_sections = [s for s in CONTENT_SECTIONS if not should_do(s)]
    if skipped_sections:
        print(f"  Skipped: {', '.join(skipped_sections)}")

    # 7. Generate FAQs
    if should_do("faqs"):
        print("\n[7/11] Generating FAQs...")
        faqs = await generate_faq(
            resort_name=resort["name"],
            country=country,
            context=content_context,
            voice_profile="snowthere_guide",
        )
        new_content["faqs"] = json.dumps(faqs)
        print(f"  Generated {len(faqs)} FAQ pairs")
    else:
        print("\n[7/11] Skipping FAQs")

    # 8. Generate SEO meta
    if should_do("seo_meta"):
        print("\n[8/11] Generating SEO metadata...")
        qt_text = new_content.get("quick_take") or stored["content"].get("quick_take", "")
        seo = await generate_seo_meta(
            resort_name=resort["name"],
            country=country,
            quick_take=qt_text,
        )
        new_content["seo_meta"] = json.dumps(seo)
        print(f"  Title: {seo.get('title', 'N/A')}")
        print(f"  Description: {seo.get('description', 'N/A')[:80]}...")
    else:
        print("\n[8/11] Skipping SEO metadata")

    # 9. Generate tagline
    if should_do("tagline"):
        print("\n[9/11] Generating tagline...")
        atoms = await extract_tagline_atoms(
            resort_name=resort["name"],
            country=country,
            research_data=research_data,
        )
        print(f"  Atoms: {len(atoms.numbers)} numbers, landmark={atoms.landmark_or_icon is not None}")

        recent_taglines = get_recent_portfolio_taglines(limit=10, exclude_country=country)

        best_tagline = None
        best_quality = None

        for attempt in range(3):
            temperature = 0.7 + (attempt * 0.15)
            candidate = await generate_diverse_tagline(
                resort_name=resort["name"],
                country=country,
                atoms=atoms,
                recent_taglines=recent_taglines,
                temperature=temperature,
            )
            quality = await evaluate_tagline_quality(
                tagline=candidate,
                atoms=atoms,
                resort_name=resort["name"],
                recent_taglines=recent_taglines,
            )
            if best_quality is None or quality.overall_score > best_quality.overall_score:
                best_tagline = candidate
                best_quality = quality

            if quality.passes_threshold and quality.structure_novelty >= 0.6:
                print(f"  Accepted on attempt {attempt + 1}: \"{candidate}\"")
                break
            else:
                print(f"  Attempt {attempt + 1}: \"{candidate}\" (score={quality.overall_score:.2f}, novelty={quality.structure_novelty:.2f})")

        new_content["tagline"] = best_tagline or f"Your family adventure starts in {resort['name']}"
        print(f"  Final tagline: \"{new_content['tagline']}\"")
        if best_quality:
            print(f"  Quality: score={best_quality.overall_score:.2f}, novelty={best_quality.structure_novelty:.2f}")
    else:
        print("\n[9/11] Skipping tagline")

    # 10. Save "after" snapshot
    print("\n[10/11] Saving 'after' snapshot...")
    after_path = SCRATCHPAD / f"after_{slug}.json"
    save_json(new_content, after_path)

    # 11. Print comparison
    print(f"\n[11/11] Comparison: {resort['name']}")
    print(f"{'='*70}")
    print(f"{'Section':<25} {'Before (words)':<16} {'After (words)':<16} {'Delta':<10}")
    print(f"{'-'*70}")

    old = stored["content"]
    all_sections = ["quick_take"] + CONTENT_SECTIONS + ["faqs", "tagline"]

    for section in all_sections:
        if section not in new_content:
            continue

        old_val = old.get(section, "")
        new_val = new_content[section]

        # For JSON fields, convert to string for word counting
        if section in ("faqs", "seo_meta"):
            old_wc = word_count(str(old_val))
            new_wc = word_count(str(new_val))
        else:
            old_wc = word_count(str(old_val))
            new_wc = word_count(str(new_val))

        delta = new_wc - old_wc
        delta_str = f"+{delta}" if delta > 0 else str(delta)
        print(f"{section:<25} {old_wc:<16} {new_wc:<16} {delta_str:<10}")

    # Print previews of key sections
    print(f"\n{'='*70}")
    print("BEFORE/AFTER PREVIEWS")
    print(f"{'='*70}")

    for section in ["quick_take"] + CONTENT_SECTIONS:
        if section not in new_content:
            continue
        print(f"\n--- {section} ---")
        print(f"BEFORE: {preview(str(old.get(section, '')))}")
        print(f"AFTER:  {preview(str(new_content[section]))}")

    if "tagline" in new_content:
        print(f"\n--- tagline ---")
        print(f"BEFORE: {old.get('tagline', '(none)')}")
        print(f"AFTER:  {new_content['tagline']}")

    # Write to DB if requested
    if write:
        print(f"\n{'='*70}")
        print("WRITING TO DATABASE...")
        print(f"{'='*70}")

        # Build content update (filter out internal keys)
        content_update = {
            k: v for k, v in new_content.items()
            if not k.startswith("_")
        }

        # Apply deterministic style fixes before writing
        content_update = apply_deterministic_style(content_update)

        update_resort_content(resort_id, content_update)
        print(f"  Updated resort_content for {resort['name']}")

        # Update perfect_if / skip_if in family_metrics
        if "_perfect_if" in new_content or "_skip_if" in new_content:
            metrics_update = {}
            if "_perfect_if" in new_content:
                metrics_update["perfect_if"] = new_content["_perfect_if"]
            if "_skip_if" in new_content:
                metrics_update["skip_if"] = new_content["_skip_if"]
            update_resort_family_metrics(resort_id, metrics_update)
            print(f"  Updated perfect_if/skip_if in family_metrics")

        print("  Done.")
    else:
        print(f"\n[DRY RUN] No changes written. Use --write to save to database.")
        print(f"  Before: {before_path}")
        print(f"  After:  {after_path}")


async def batch_regenerate(
    limit: int = 10,
    offset: int = 0,
    write: bool = False,
    sections_filter: list[str] | None = None,
):
    """Regenerate content for multiple published resorts, oldest first."""
    client = get_supabase_client()

    resorts = (
        client.table("resorts")
        .select("name, slug, updated_at")
        .eq("status", "published")
        .order("updated_at", desc=False)
        .range(offset, offset + limit - 1)
        .execute()
    )

    if not resorts.data:
        print("No published resorts found.")
        return

    total = len(resorts.data)
    print(f"\n{'='*70}")
    print(f"BATCH CONTENT REGENERATION")
    print(f"{'='*70}")
    print(f"Resorts: {total} (offset={offset}, limit={limit})")
    print(f"Mode: {'WRITE' if write else 'DRY RUN'}")
    if sections_filter:
        print(f"Sections: {', '.join(sections_filter)}")
    print(f"{'='*70}\n")

    succeeded, failed, skipped = 0, 0, 0

    for i, resort in enumerate(resorts.data):
        # Budget guard: ~$1.50 per resort, leave $2 buffer
        try:
            spend = get_daily_spend()
            budget = getattr(settings, "daily_budget_limit", 50.0)
            if spend + 1.5 > budget:
                print(f"\nBudget limit reached (${spend:.2f}/${budget:.2f}).")
                print(f"Resume with: --batch-offset {offset + i}")
                break
        except Exception:
            pass  # Budget check is best-effort

        print(f"\n[{i + 1}/{total}] {resort['name']} (updated: {resort.get('updated_at', 'N/A')[:10]})")

        try:
            await regenerate(
                resort["name"],
                write=write,
                sections_filter=sections_filter,
            )
            succeeded += 1
        except Exception as e:
            print(f"FAILED: {resort['name']}: {e}")
            failed += 1

        # Rate limit courtesy between resorts
        if i < total - 1:
            print("  Waiting 5s...")
            await asyncio.sleep(5)

    print(f"\n{'='*70}")
    print(f"BATCH COMPLETE")
    print(f"{'='*70}")
    print(f"Succeeded: {succeeded}")
    print(f"Failed: {failed}")
    if offset + limit < 200:  # rough upper bound
        print(f"Next run: --batch-offset {offset + succeeded + failed}")


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate content for resorts using current voice prompts"
    )
    parser.add_argument(
        "--resort", help='Resort name (e.g., "Garmisch-Partenkirchen")'
    )
    parser.add_argument(
        "--write", action="store_true", help="Write results back to Supabase (default: dry run)"
    )
    parser.add_argument(
        "--sections",
        help="Comma-separated list of sections to regenerate (default: all). "
             "Options: quick_take,getting_there,where_to_stay,lift_tickets,"
             "on_mountain,off_mountain,parent_reviews_summary,faqs,seo_meta,tagline",
    )
    parser.add_argument(
        "--batch", action="store_true",
        help="Batch mode: regenerate all published resorts (oldest first)",
    )
    parser.add_argument(
        "--batch-limit", type=int, default=10,
        help="Max resorts per batch run (default: 10)",
    )
    parser.add_argument(
        "--batch-offset", type=int, default=0,
        help="Skip first N resorts (for resuming batch runs)",
    )

    args = parser.parse_args()

    if not args.resort and not args.batch:
        parser.error("Either --resort or --batch is required")

    sections_filter = None
    if args.sections:
        sections_filter = [s.strip() for s in args.sections.split(",")]

    if args.batch:
        asyncio.run(batch_regenerate(
            limit=args.batch_limit,
            offset=args.batch_offset,
            write=args.write,
            sections_filter=sections_filter,
        ))
    else:
        asyncio.run(regenerate(args.resort, write=args.write, sections_filter=sections_filter))


if __name__ == "__main__":
    main()
