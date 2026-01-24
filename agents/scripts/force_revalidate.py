#!/usr/bin/env python3
"""Force ISR revalidation for production pages.

Use this to refresh cached pages after database changes.

Usage:
    cd agents
    python scripts/force_revalidate.py
"""
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.primitives import revalidate_resort_page


def main():
    """Force revalidation for all published resort pages."""
    resorts = [
        ("park-city", "United States"),
        ("st-anton", "Austria"),
        ("zermatt", "Switzerland"),
    ]

    print("=" * 60)
    print("FORCE REVALIDATE PRODUCTION PAGES")
    print("=" * 60)
    print()

    success_count = 0
    for slug, country in resorts:
        result = revalidate_resort_page(slug, country)
        success = result.get("success", False)

        if success:
            status = "✓"
            success_count += 1
        else:
            status = "✗"

        print(f"{status} {slug} ({country})")
        if not success:
            print(f"   Error: {result.get('error', 'Unknown error')}")

    print()
    print("=" * 60)
    print(f"SUMMARY: {success_count}/{len(resorts)} pages revalidated")
    print("=" * 60)

    return 0 if success_count == len(resorts) else 1


if __name__ == "__main__":
    sys.exit(main())
