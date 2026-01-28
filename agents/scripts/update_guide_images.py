#!/usr/bin/env python3
"""
Update guide featured images in Supabase.

Generated as part of Round 13 — guide page design overhaul.
These images were generated using Replicate Flux Schnell.

Usage:
    cd agents && python scripts/update_guide_images.py
    cd agents && python scripts/update_guide_images.py --dry-run
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client


# Guide slug -> featured image URL mapping
# Generated with Replicate Flux Schnell (Round 13, 2026-01-28)
GUIDE_IMAGES = {
    "ski-like-an-olympian-resorts": "https://replicate.delivery/czjl/0LQQdlf6U4UcbKM8p8DVqyqZJQFH3tnZejy747mOQ8kBuBCWA/out-0.webp",
    "cortina-skiing-2026-olympics": "https://replicate.delivery/czjl/jvAmGZpubWpAKtATf22AXskSyAf7kfgyXY1S6yFFByp3cDEsA/out-0.webp",
    "family-ski-trip-checklist": "https://replicate.delivery/czjl/pJWmgUQkffj5JUWaJeqprdfpZN9jzNw00z1r3fOY3AYz1NQwC/out-0.webp",
    "dolomites-family-resorts-olympics": "https://replicate.delivery/czjl/n79dwscG2XYuChLt6QDPJQGgHPeF7kjEBHkzVrOlkRKg3ABLA/out-0.webp",
    "best-resorts-for-toddlers": "https://replicate.delivery/czjl/XoAfnZe1tvism0e8Mx8bDzu0FhQZr60lpfCdp2l57rMP9GIYB/out-0.webp",
    "milan-cortina-2026-family-guide": "https://replicate.delivery/czjl/oQwQf9U0GDV4BK564qnDo8TiSU5KWuohRD7R1JMe49UmvBCWA/out-0.webp",
    "olympics-italy-family-itinerary": "https://replicate.delivery/czjl/nee1HaFYZJjhWkmzfy7r56qGxsU96xIIjpTqmuoyCqj0fGIYB/out-0.webp",
    "milan-to-cortina-with-kids": "https://replicate.delivery/czjl/FiGWspi1hLZ1C1lJ6TPc1Jfuj8RNnPuYUh493Rw0AF4G4ABLA/out-0.webp",
    "first-family-ski-trip": "https://replicate.delivery/czjl/XZk4agipvJ7iCNods6E1uTFt5W88OaoTC3oeXGe7f3oBhDEsA/out-0.webp",
    "epic-vs-ikon-families": "https://replicate.delivery/czjl/1zkEtdfMi2VEJSQWasR7Aj1CGFCmZEG0uQ95AAnL8Hwa4ABLA/out-0.webp",
    "cortina-family-budget-guide": "https://replicate.delivery/czjl/LgA6zMdIk6YnJpb42FSuHZiQatiHn16OmrHJHIufFlSk4ABLA/out-0.webp",
}


def main():
    parser = argparse.ArgumentParser(description="Update guide featured images")
    parser.add_argument("--dry-run", action="store_true", help="Print what would be updated without doing it")
    args = parser.parse_args()

    client = get_supabase_client()

    for slug, image_url in GUIDE_IMAGES.items():
        if args.dry_run:
            print(f"[DRY RUN] Would update {slug} -> {image_url[:80]}...")
            continue

        result = (
            client.table("guides")
            .update({"featured_image_url": image_url})
            .eq("slug", slug)
            .execute()
        )

        if result.data:
            print(f"[OK] Updated {slug}")
        else:
            print(f"[SKIP] {slug} — not found or no update needed")

    print(f"\nDone! Updated {len(GUIDE_IMAGES)} guides.")


if __name__ == "__main__":
    main()
