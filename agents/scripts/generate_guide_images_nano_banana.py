#!/usr/bin/env python3
"""
Generate guide featured images using Nano Banana Pro.

Uses the 4-tier fallback from shared/primitives/images.py which
prioritizes Nano Banana Pro on Replicate as the primary provider.

Images are downloaded and re-uploaded to Supabase Storage for
permanent hosting (Replicate/Glif URLs are temporary).

Usage:
    cd agents && python3 scripts/generate_guide_images_nano_banana.py
    cd agents && python3 scripts/generate_guide_images_nano_banana.py --dry-run
    cd agents && python3 scripts/generate_guide_images_nano_banana.py --slug epic-vs-ikon-families
"""

import argparse
import asyncio
import sys
import time
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.primitives.images import (
    generate_image_with_fallback,
    AspectRatio,
)
from shared.supabase_client import get_supabase_client


# Guide slug -> image prompt mapping
# Editorial travel photography, warm golden hour, NO close-up faces
GUIDE_PROMPTS = {
    "ski-like-an-olympian-resorts": (
        "Editorial travel photography of an Olympic ski venue at golden hour, "
        "dramatic Dolomites mountain backdrop, distant skiers racing down groomed runs, "
        "warm alpenglow on snow-covered peaks, professional magazine quality, "
        "no close-up faces, distant silhouettes only"
    ),
    "cortina-skiing-2026-olympics": (
        "Panoramic editorial photography of Cortina d'Ampezzo village in winter, "
        "Tofana mountains towering above, warm morning light on snow-dusted rooftops, "
        "Italian Alpine charm, church bell tower, professional travel magazine quality, "
        "no close-up faces, atmosphere and landscape focus"
    ),
    "family-ski-trip-checklist": (
        "Flat-lay editorial photography of family ski trip essentials neatly arranged: "
        "ski goggles, colorful mittens, trail map, hot chocolate mug, sunscreen, "
        "hand warmers, warm natural lighting, overhead shot, magazine styling, "
        "cozy wooden table background"
    ),
    "dolomites-family-resorts-olympics": (
        "Dramatic editorial landscape photography of the Dolomites mountain range, "
        "jagged peaks catching warm alpenglow, small ski village nestled below, "
        "ski runs threading through pine forests, professional travel photography, "
        "no close-up faces, grand mountain scale emphasis"
    ),
    "best-resorts-for-toddlers": (
        "Warm editorial photography of a gentle ski bunny hill at golden hour, "
        "colorful magic carpet conveyor, tiny distant silhouettes of children in ski gear, "
        "parent watching nearby, soft powder snow, friendly mountain atmosphere, "
        "professional family travel magazine quality, no close-up faces"
    ),
    "milan-cortina-2026-family-guide": (
        "Split editorial composition: Milan cathedral duomo with Alps visible in distance, "
        "winter morning light, Italian architecture meets mountain landscape, "
        "warm golden tones, professional travel photography, atmospheric perspective, "
        "no close-up faces, cityscape and mountain panorama"
    ),
    "olympics-italy-family-itinerary": (
        "Editorial travel photography collage style: Italian winter scenes, "
        "Dolomites mountains, colorful village buildings, steaming espresso cup, "
        "ski equipment, warm golden hour lighting throughout, "
        "professional magazine quality travel diary aesthetic, no close-up faces"
    ),
    "milan-to-cortina-with-kids": (
        "Scenic editorial photography of a mountain road winding through the Italian Dolomites, "
        "dramatic peaks on either side, winter landscape, warm afternoon light, "
        "distant car on the road, professional travel photography, "
        "journey and adventure feeling, no close-up faces"
    ),
    "first-family-ski-trip": (
        "Warm editorial photography of a family of distant silhouettes at the base of a "
        "beginner ski mountain, gentle slope behind them, warm golden hour lighting, "
        "excitement and anticipation feeling, snow-covered trees, "
        "professional family travel magazine quality, no close-up faces"
    ),
    "epic-vs-ikon-families": (
        "Editorial photography showing two contrasting ski resort scenes side by side, "
        "dramatic mountain landscapes, groomed runs and powder bowls, "
        "warm lighting, professional comparison style, "
        "no close-up faces, emphasis on terrain variety and resort atmosphere"
    ),
    "cortina-family-budget-guide": (
        "Cozy editorial photography of an affordable Italian mountain lodge, "
        "Cortina village in background, warm interior light spilling from windows, "
        "Dolomites peaks in twilight, budget-friendly warmth and comfort feeling, "
        "professional travel magazine quality, no close-up faces"
    ),
}


async def generate_single(slug: str, prompt: str, dry_run: bool = False) -> str | None:
    """Generate a single guide image using Nano Banana Pro (4-tier fallback)."""
    if dry_run:
        print(f"[DRY RUN] Would generate for {slug}")
        print(f"  Prompt: {prompt[:100]}...")
        return None

    print(f"[GENERATING] {slug}...")
    result = await generate_image_with_fallback(prompt, AspectRatio.LANDSCAPE)

    if result.success and result.url:
        print(f"  [OK] Generated: {result.url[:80]}...")
        print(f"  Provider: {result.source}, Cost: ${result.cost}")
        return result.url
    else:
        print(f"  [FAIL] {result.error}")
        return None


async def main_async(args):
    client = get_supabase_client()

    slugs = GUIDE_PROMPTS.keys()
    if args.slug:
        if args.slug not in GUIDE_PROMPTS:
            print(f"Unknown slug: {args.slug}")
            print(f"Available: {', '.join(GUIDE_PROMPTS.keys())}")
            return
        slugs = [args.slug]

    results = {}
    for slug in slugs:
        prompt = GUIDE_PROMPTS[slug]
        url = await generate_single(slug, prompt, dry_run=args.dry_run)
        results[slug] = url

        if not args.dry_run and url:
            # Update Supabase
            update_result = (
                client.table("guides")
                .update({"featured_image_url": url})
                .eq("slug", slug)
                .execute()
            )
            if update_result.data:
                print(f"  [DB] Updated {slug}")
            else:
                print(f"  [DB SKIP] {slug} — not found in database")

        # Rate limit: wait between generations
        if not args.dry_run:
            time.sleep(5)

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    success = sum(1 for v in results.values() if v)
    failed = sum(1 for v in results.values() if v is None and not args.dry_run)
    print(f"Generated: {success}, Failed: {failed}")
    for slug, url in results.items():
        status = "OK" if url else ("DRY RUN" if args.dry_run else "FAILED")
        print(f"  [{status}] {slug}")


def main():
    parser = argparse.ArgumentParser(description="Generate guide images with Nano Banana Pro")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be generated")
    parser.add_argument("--slug", type=str, help="Generate for a single guide slug only")
    args = parser.parse_args()

    asyncio.run(main_async(args))


if __name__ == "__main__":
    main()
