#!/usr/bin/env python3
"""Backfill external links for all published resorts.

Re-curates sidebar links (if sparse) and injects in-content entity links
(hotels, restaurants, ski schools -> Google Places / Maps / affiliate URLs).
Stores extracted entities as first-class atoms in resort_entities table.

Usage:
    python scripts/backfill_links.py                       # Full backfill
    python scripts/backfill_links.py --dry-run              # Preview only
    python scripts/backfill_links.py --limit 2              # Process 2 resorts
    python scripts/backfill_links.py --sidebar-only         # Only re-curate sidebar links
    python scripts/backfill_links.py --content-only         # Only inject in-content links
    python scripts/backfill_links.py --resort "Zermatt"     # Single resort
    python scripts/backfill_links.py --clear-cache          # Clear low-confidence cache before backfill
"""

import argparse
import asyncio
import re
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.external_links import (
    WELL_KNOWN_BRANDS,
    clear_low_confidence_cache,
    inject_links_in_content_sections,
    upsert_resort_entity,
)
from shared.primitives.intelligence import curate_resort_links
from shared.primitives.links import get_resort_links
from shared.primitives.system import log_cost


def _strip_existing_links(html_content: str) -> str:
    """Remove existing target="_blank" links from HTML content.

    This is necessary before re-injection because:
    1. Entity names inside <a> tags can't be matched by extraction regex
    2. Re-backfill needs to see clean entity names to re-extract and re-link

    Only strips external links (target="_blank"), preserves internal links.

    Args:
        html_content: HTML content with existing links

    Returns:
        HTML content with external links replaced by their text content
    """
    # Match <a> tags with target="_blank" and replace with their inner text
    pattern = r'<a\s+[^>]*target="_blank"[^>]*>(.*?)</a>'
    return re.sub(pattern, r'\1', html_content, flags=re.IGNORECASE | re.DOTALL)


async def backfill_sidebar_links(
    resort_id: str,
    resort_name: str,
    country: str,
    dry_run: bool = False,
    min_links: int = 5,
) -> dict:
    """Re-curate sidebar links if resort has fewer than min_links."""
    client = get_supabase_client()

    # Check existing link count
    existing_links = await get_resort_links(resort_id)
    if len(existing_links) >= min_links:
        return {"status": "skipped", "reason": f"Already has {len(existing_links)} links"}

    # Get research sources from audit log (most recent research for this resort)
    # Fall back to empty sources if none found -- Claude will use its knowledge
    sources_response = (
        client.table("agent_audit_log")
        .select("metadata")
        .eq("action", "research_complete")
        .like("reasoning", f"%{resort_name}%")
        .order("created_at", desc=True)
        .limit(1)
        .execute()
    )

    research_sources = []
    if sources_response.data:
        metadata = sources_response.data[0].get("metadata", {})
        research_sources = metadata.get("sources", [])

    # If no sources from audit log, try Exa search for fresh sources
    if not research_sources:
        try:
            from shared.primitives.research import exa_search
            exa_results = await exa_search(f"{resort_name} {country} ski resort family")
            research_sources = [
                {"url": r.url, "title": r.title, "snippet": r.text[:300]}
                for r in (exa_results or [])
            ]
        except Exception as e:
            print(f"    Exa search failed: {e}")

    if not research_sources:
        return {"status": "skipped", "reason": "No research sources available"}

    print(f"    Curating from {len(research_sources)} sources...")

    link_result = await curate_resort_links(
        resort_name=resort_name,
        country=country,
        research_sources=research_sources,
    )

    if not link_result.success or not link_result.links:
        return {"status": "failed", "error": link_result.error}

    if dry_run:
        for link in link_result.links:
            print(f"    [{link.category}] {link.title}: {link.url[:60]}...")
        return {"status": "dry_run", "links_count": len(link_result.links)}

    # Store curated links
    stored = 0
    for link in link_result.links:
        try:
            client.table("resort_links").upsert({
                "resort_id": resort_id,
                "title": link.title,
                "url": link.url,
                "category": link.category,
                "description": link.description,
            }, on_conflict="resort_id,url").execute()
            stored += 1
        except Exception as e:
            print(f"    Failed to store link {link.url}: {e}")

    log_cost("anthropic", 0.01, None, {"stage": "backfill_sidebar_links", "resort": resort_name})

    return {"status": "complete", "links_stored": stored, "has_official": link_result.has_official}


async def backfill_content_links(
    resort_id: str,
    resort_name: str,
    country: str,
    resort_slug: str,
    dry_run: bool = False,
    store_entities: bool = True,
) -> dict:
    """Inject in-content entity links for a resort.

    Steps:
    1. Strip existing external links from content
    2. Extract entities from clean content
    3. Resolve entities (brand registry -> Google Places -> Maps search)
    4. Inject links into content
    5. Store entities as atoms in resort_entities table
    """
    client = get_supabase_client()

    # Get existing content
    content_response = (
        client.table("resort_content")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )

    if not content_response.data:
        return {"status": "skipped", "reason": "No content found"}

    content_data = content_response.data

    # Build content dict from database columns
    content_sections = {}
    section_columns = [
        "quick_take", "getting_there", "where_to_stay", "lift_tickets",
        "on_mountain", "off_mountain", "parent_reviews_summary",
    ]
    for col in section_columns:
        if content_data.get(col):
            # Strip existing external links before re-injection
            content_sections[col] = _strip_existing_links(content_data[col])

    if not content_sections:
        return {"status": "skipped", "reason": "No content sections"}

    # Inject links
    modified_content, injected_links = await inject_links_in_content_sections(
        content=content_sections,
        resort_name=resort_name,
        country=country,
        resort_slug=resort_slug,
    )

    if not injected_links:
        return {"status": "no_entities", "reason": "No linkable entities found"}

    affiliate_count = sum(1 for link in injected_links if link.is_affiliate)
    maps_fallback_count = sum(1 for link in injected_links if link.is_maps_search_fallback)

    if dry_run:
        for link in injected_links:
            if link.is_affiliate:
                label = "[$]"
            elif link.is_maps_search_fallback:
                label = "[~]"
            else:
                label = "[>]"
            print(f"    {label} {link.entity_name} ({link.entity_type}) -> {link.url[:60]}...")
        return {
            "status": "dry_run",
            "links_count": len(injected_links),
            "affiliate_count": affiliate_count,
            "maps_fallback_count": maps_fallback_count,
        }

    # Save modified content back to database
    update_data = {}
    for section_name, html_content in modified_content.items():
        if section_name in section_columns:
            update_data[section_name] = html_content

    if update_data:
        client.table("resort_content").update(update_data).eq("resort_id", resort_id).execute()

    # Store entities as atoms in resort_entities table
    entities_stored = 0
    if store_entities:
        for link in injected_links:
            is_brand = link.entity_name.lower().strip() in WELL_KNOWN_BRANDS
            resolution_status = "brand" if is_brand else "resolved"
            if link.is_maps_search_fallback:
                resolution_status = "resolved"  # Maps search is a valid resolution

            stored = upsert_resort_entity(
                resort_id=resort_id,
                name=link.entity_name,
                entity_type=link.entity_type,
                source="extraction",
                resolution_status=resolution_status,
                resolved_url=link.url,
                confidence=1.0 if not link.is_maps_search_fallback else 0.5,
                maps_url=link.url if link.is_maps_search_fallback else None,
            )
            if stored:
                entities_stored += 1

    log_cost("anthropic", 0.01, None, {"stage": "backfill_content_links", "resort": resort_name})

    return {
        "status": "complete",
        "links_injected": len(injected_links),
        "affiliate_count": affiliate_count,
        "maps_fallback_count": maps_fallback_count,
        "entities_stored": entities_stored,
        "entities": [link.entity_name for link in injected_links],
    }


async def backfill_links(
    dry_run: bool = False,
    limit: int | None = None,
    sidebar_only: bool = False,
    content_only: bool = False,
    resort_name_filter: str | None = None,
    clear_cache: bool = False,
):
    """Run the link backfill across all published resorts."""
    client = get_supabase_client()

    # Clear low-confidence cache entries if requested
    if clear_cache:
        print("Clearing low-confidence cache entries...")
        cleared = clear_low_confidence_cache(min_confidence=0.65)
        print(f"Cleared {cleared} entries\n")

    # Get published resorts
    query = (
        client.table("resorts")
        .select("id, name, country, slug")
        .eq("status", "published")
        .order("name")
    )

    if resort_name_filter:
        query = query.ilike("name", f"%{resort_name_filter}%")

    if limit:
        query = query.limit(limit)

    resorts_response = query.execute()
    resorts = resorts_response.data or []

    do_sidebar = not content_only
    do_content = not sidebar_only

    print(f"\n{'='*60}")
    print(f"LINK BACKFILL")
    print(f"{'='*60}")
    print(f"Mode: {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"Resorts: {len(resorts)}")
    print(f"Sidebar links: {'YES' if do_sidebar else 'SKIP'}")
    print(f"Content links: {'YES' if do_content else 'SKIP'}")
    print(f"Clear cache: {'YES' if clear_cache else 'NO'}")
    print(f"{'='*60}\n")

    sidebar_updated = 0
    sidebar_skipped = 0
    content_updated = 0
    content_skipped = 0
    failed = 0
    total_entity_links = 0
    total_affiliate_links = 0
    total_maps_fallback = 0
    total_entities_stored = 0

    for i, resort in enumerate(resorts, 1):
        resort_id = resort["id"]
        name = resort["name"]
        country = resort["country"]
        slug = resort["slug"]

        print(f"\n[{i}/{len(resorts)}] {name}, {country}")
        print("-" * 40)

        try:
            # Sidebar links
            if do_sidebar:
                print("  Sidebar links:")
                sidebar_result = await backfill_sidebar_links(
                    resort_id=resort_id,
                    resort_name=name,
                    country=country,
                    dry_run=dry_run,
                )
                status = sidebar_result.get("status", "unknown")
                if status in ("complete", "dry_run"):
                    sidebar_updated += 1
                    count = sidebar_result.get("links_stored") or sidebar_result.get("links_count", 0)
                    print(f"    {count} links curated")
                else:
                    sidebar_skipped += 1
                    print(f"    Skipped: {sidebar_result.get('reason', sidebar_result.get('error', 'unknown'))}")

            # Content links
            if do_content:
                print("  Content links:")
                content_result = await backfill_content_links(
                    resort_id=resort_id,
                    resort_name=name,
                    country=country,
                    resort_slug=slug,
                    dry_run=dry_run,
                )
                status = content_result.get("status", "unknown")
                if status in ("complete", "dry_run"):
                    content_updated += 1
                    count = content_result.get("links_injected") or content_result.get("links_count", 0)
                    aff = content_result.get("affiliate_count", 0)
                    maps_fb = content_result.get("maps_fallback_count", 0)
                    ent_stored = content_result.get("entities_stored", 0)
                    total_entity_links += count
                    total_affiliate_links += aff
                    total_maps_fallback += maps_fb
                    total_entities_stored += ent_stored
                    print(f"    {count} entity links ({aff} affiliate, {maps_fb} maps fallback)")
                    if ent_stored:
                        print(f"    {ent_stored} entities stored as atoms")
                else:
                    content_skipped += 1
                    print(f"    Skipped: {content_result.get('reason', content_result.get('error', 'unknown'))}")

        except Exception as e:
            print(f"  ERROR: {e}")
            failed += 1

    # Summary
    print(f"\n{'='*60}")
    print(f"BACKFILL COMPLETE")
    print(f"{'='*60}")
    if do_sidebar:
        print(f"Sidebar: {sidebar_updated} updated, {sidebar_skipped} skipped")
    if do_content:
        print(f"Content: {content_updated} updated, {content_skipped} skipped")
        print(f"Entity links injected: {total_entity_links} ({total_affiliate_links} affiliate, {total_maps_fallback} maps fallback)")
        print(f"Entity atoms stored: {total_entities_stored}")
    print(f"Failed: {failed}")
    print(f"{'='*60}\n")


def main():
    parser = argparse.ArgumentParser(description="Backfill external links for published resorts")
    parser.add_argument("--dry-run", action="store_true", help="Preview only, don't save changes")
    parser.add_argument("--limit", type=int, help="Limit number of resorts to process")
    parser.add_argument("--sidebar-only", action="store_true", help="Only re-curate sidebar links")
    parser.add_argument("--content-only", action="store_true", help="Only inject in-content links")
    parser.add_argument("--resort", type=str, help="Process a single resort by name")
    parser.add_argument("--clear-cache", action="store_true", help="Clear low-confidence cache entries before backfill")
    args = parser.parse_args()

    if args.sidebar_only and args.content_only:
        print("Error: Cannot use --sidebar-only and --content-only together")
        sys.exit(1)

    asyncio.run(backfill_links(
        dry_run=args.dry_run,
        limit=args.limit,
        sidebar_only=args.sidebar_only,
        content_only=args.content_only,
        resort_name_filter=args.resort,
        clear_cache=args.clear_cache,
    ))


if __name__ == "__main__":
    main()
