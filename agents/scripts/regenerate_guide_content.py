#!/usr/bin/env python3
"""Regenerate guide content with current MEO voice prompts.

Handles both draft guides (stuck in approval) and published guides (stale voice).

Draft guides (--drafts):
    1. Load guide from DB
    2. Re-plan structure
    3. Regenerate all sections with current voice
    4. Run expert approval loop (3 iterations max)
    5. If approved: update content + publish + revalidate ISR
    6. If rejected: update content, keep as draft

Published guides (--published):
    1. Load guide from DB
    2. Regenerate sections with current voice
    3. Update content in-place (skip approval)
    4. Revalidate ISR page

Usage:
    python scripts/regenerate_guide_content.py --drafts
    python scripts/regenerate_guide_content.py --published --write
    python scripts/regenerate_guide_content.py --guide-id <uuid> --write

Cost: ~$0.30-0.60 per guide.
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.guides import (
    GuideCandidate,
    GuideOutline,
    list_guides,
    get_guide,
    update_guide,
    publish_guide,
    plan_guide_structure,
    generate_guide_content,
)
from shared.primitives.expert_panel import expert_approval_loop
from shared.primitives.publishing import revalidate_page

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


def _section_word_count(sections: list[dict]) -> int:
    """Count total words across all guide sections."""
    import re
    total = 0
    for section in sections:
        for value in section.values():
            if isinstance(value, str):
                plain = re.sub(r"<[^>]+>", " ", value)
                total += len(plain.split())
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        for v in item.values():
                            if isinstance(v, str):
                                plain = re.sub(r"<[^>]+>", " ", v)
                                total += len(plain.split())
                    elif isinstance(item, str):
                        total += len(item.split())
    return total


async def regenerate_guide(
    guide_id: str,
    write: bool = False,
    run_approval: bool = False,
):
    """Regenerate content for a single guide."""
    guide = get_guide(guide_id)
    if not guide:
        print(f"Guide not found: {guide_id}")
        return False

    title = guide["title"]
    slug = guide["slug"]
    status = guide["status"]
    guide_type = guide.get("guide_type", "how-to")
    content = guide.get("content", {})
    old_sections = content.get("sections", []) if isinstance(content, dict) else []

    print(f"\n{'='*70}")
    print(f"GUIDE REGENERATION: {title}")
    print(f"{'='*70}")
    print(f"Status: {status} | Type: {guide_type} | Slug: {slug}")
    print(f"Old sections: {len(old_sections)} ({_section_word_count(old_sections)} words)")
    print(f"Mode: {'WRITE' if write else 'DRY RUN'} | Approval: {'YES' if run_approval else 'SKIP'}")
    print(f"{'='*70}\n")

    # Step 1: Re-plan structure from the existing title/type
    print("[1/4] Planning guide structure...")
    topic = GuideCandidate(
        title=title,
        guide_type=guide_type,
        category=guide.get("category"),
        source="regeneration",
    )
    outline = await plan_guide_structure(topic)
    print(f"  Planned {len(outline.sections)} sections")

    # Step 2: Generate content with current voice
    print("[2/4] Generating content with current MEO voice...")
    new_content = await generate_guide_content(outline)
    new_sections = new_content.get("sections", [])
    print(f"  Generated {len(new_sections)} sections ({_section_word_count(new_sections)} words)")

    # Step 3: Expert approval (for drafts only)
    approved = True
    if run_approval:
        print("[3/4] Running expert approval panel...")
        approval = await expert_approval_loop(
            content=new_content,
            content_type="guide",
            voice_profile="snowthere_guide",
            context=f"Guide: {title} ({guide_type})",
            max_iterations=3,
        )
        approved = approval.approved
        print(f"  Result: {'APPROVED' if approved else 'NOT APPROVED'} "
              f"after {approval.iterations} iteration(s)")
        if approval.final_issues:
            for issue in approval.final_issues[:5]:
                print(f"    - {issue}")

        # Use improved content if available
        if approval.final_content is not None:
            new_content = approval.final_content
            if isinstance(new_content, dict):
                new_sections = new_content.get("sections", new_sections)
    else:
        print("[3/4] Skipping approval (published guide refresh)")

    # Step 4: Write to DB
    if write:
        print("[4/4] Writing to database...")
        update_guide(guide_id, content=new_content)
        print(f"  Updated content for '{title}'")

        if run_approval and approved and status == "draft":
            publish_guide(guide_id)
            print(f"  Published guide!")

        # Revalidate ISR pages
        try:
            revalidate_page("/guides")
            revalidate_page(f"/guides/{slug}")
            print(f"  Revalidated /guides and /guides/{slug}")
        except Exception as e:
            print(f"  Revalidation failed (non-fatal): {e}")

        return approved
    else:
        print("[4/4] DRY RUN - no changes written")

        # Print section comparison
        print(f"\n{'Section Type':<20} {'Old':<6} {'New':<6}")
        print(f"{'-'*32}")

        old_types = {s.get("type", "?"): s for s in old_sections}
        for section in new_sections:
            stype = section.get("type", "?")
            old_s = old_types.get(stype, {})
            print(f"{stype:<20} {'yes':<6} {'yes':<6}")

        return approved


async def run_batch(
    mode: str,
    write: bool = False,
    guide_id: str | None = None,
):
    """Run guide regeneration in batch."""
    if guide_id:
        guides = [get_guide(guide_id)]
        if not guides[0]:
            print(f"Guide not found: {guide_id}")
            return
        run_approval = guides[0]["status"] == "draft"
    elif mode == "drafts":
        guides = list_guides(status="draft")
        run_approval = True
    elif mode == "published":
        guides = list_guides(status="published")
        run_approval = False
    else:
        print(f"Unknown mode: {mode}")
        return

    if not guides:
        print(f"No {mode} guides found.")
        return

    print(f"\nFound {len(guides)} {mode or 'matching'} guide(s)")

    succeeded, failed, published = 0, 0, 0

    for i, guide in enumerate(guides):
        try:
            approved = await regenerate_guide(
                guide["id"],
                write=write,
                run_approval=run_approval,
            )
            succeeded += 1
            if approved and run_approval and write:
                published += 1
        except Exception as e:
            logger.error(f"FAILED: {guide.get('title', '?')}: {e}")
            failed += 1

        # Rate limit between guides
        if i < len(guides) - 1:
            await asyncio.sleep(3)

    print(f"\n{'='*70}")
    print(f"BATCH COMPLETE: {succeeded} succeeded, {failed} failed")
    if run_approval and write:
        print(f"Published: {published}/{succeeded}")
    print(f"{'='*70}")


def main():
    parser = argparse.ArgumentParser(
        description="Regenerate guide content with current MEO voice prompts"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--drafts", action="store_true",
        help="Regenerate all draft guides (runs approval, publishes if approved)",
    )
    group.add_argument(
        "--published", action="store_true",
        help="Refresh all published guides (skips approval)",
    )
    group.add_argument(
        "--guide-id",
        help="Regenerate a single guide by UUID",
    )
    parser.add_argument(
        "--write", action="store_true",
        help="Write results to database (default: dry run)",
    )

    args = parser.parse_args()

    if args.drafts:
        mode = "drafts"
    elif args.published:
        mode = "published"
    else:
        mode = "single"

    asyncio.run(run_batch(
        mode=mode,
        write=args.write,
        guide_id=args.guide_id,
    ))


if __name__ == "__main__":
    main()
