"""Fix Jan 28 pipeline failures.

1. Re-queue 5 failed discovery candidates from Jan 28 run
2. Check Cerro Catedral draft status
3. Trigger ISR revalidation of /resorts listing page

Run from agents/ directory:
    python scripts/fix_jan28_failures.py
"""

import sys
import os

# Add parent to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from shared.supabase_client import get_supabase_client
from shared.primitives.publishing import revalidate_page, publish_resort


def main():
    client = get_supabase_client()

    # =========================================================================
    # 1. Re-queue 5 failed discovery candidates
    # =========================================================================
    print("=" * 60)
    print("STEP 1: Re-queue failed discovery candidates from Jan 28")
    print("=" * 60)

    failed_resorts = [
        ("Grindelwald", "Switzerland"),
        ("Alta Badia", "Italy"),
        ("Nozawa Onsen", "Japan"),
        ("Queenstown", "New Zealand"),
        ("Davos-Klosters", "Switzerland"),
    ]

    for name, country in failed_resorts:
        # Find the candidate
        result = (
            client.table("discovery_candidates")
            .select("id, resort_name, country, status, opportunity_score")
            .eq("resort_name", name)
            .eq("country", country)
            .execute()
        )

        if result.data:
            candidate = result.data[0]
            print(f"\n  {name}, {country}:")
            print(f"    Current status: {candidate['status']}")
            print(f"    Opportunity score: {candidate.get('opportunity_score', 'N/A')}")

            if candidate["status"] in ("rejected", "queued", "failed"):
                # Reset to pending
                client.table("discovery_candidates").update({
                    "status": "pending",
                    "queued_at": None,
                    "processed_at": None,
                }).eq("id", candidate["id"]).execute()
                print(f"    -> Reset to 'pending' ✓")
            elif candidate["status"] == "pending":
                print(f"    -> Already pending, no action needed")
            else:
                print(f"    -> Status is '{candidate['status']}', skipping")
        else:
            print(f"\n  {name}, {country}: NOT FOUND in discovery_candidates")

    # =========================================================================
    # 2. Check Cerro Catedral draft
    # =========================================================================
    print("\n" + "=" * 60)
    print("STEP 2: Check Cerro Catedral draft")
    print("=" * 60)

    cerro = (
        client.table("resorts")
        .select("id, name, country, status, slug, updated_at")
        .eq("name", "Cerro Catedral")
        .execute()
    )

    if cerro.data:
        resort = cerro.data[0]
        print(f"\n  Name: {resort['name']}")
        print(f"  Country: {resort['country']}")
        print(f"  Status: {resort['status']}")
        print(f"  Slug: {resort['slug']}")
        # Family score is in resort_family_metrics table
        print(f"  Updated: {resort['updated_at']}")

        # Check if it has content
        content = (
            client.table("resort_content")
            .select("quick_take, getting_there, where_to_stay, lift_tickets")
            .eq("resort_id", resort["id"])
            .execute()
        )

        if content.data:
            c = content.data[0]
            has_qt = bool(c.get("quick_take"))
            has_gt = bool(c.get("getting_there"))
            has_ws = bool(c.get("where_to_stay"))
            has_lt = bool(c.get("lift_tickets"))
            print(f"  Content: QT={'✓' if has_qt else '✗'} GT={'✓' if has_gt else '✗'} WS={'✓' if has_ws else '✗'} LT={'✓' if has_lt else '✗'}")

            if resort["status"] == "draft" and has_qt and has_gt:
                print(f"\n  -> Publishing Cerro Catedral...")
                published = publish_resort(resort["id"])
                if published:
                    print(f"  -> Published ✓")
                else:
                    print(f"  -> Publish failed ✗")
            elif resort["status"] == "published":
                print(f"  -> Already published")
        else:
            print(f"  Content: NO CONTENT FOUND")
    else:
        print(f"\n  Cerro Catedral: NOT FOUND in resorts table")

    # =========================================================================
    # 3. Trigger ISR revalidation of /resorts listing page
    # =========================================================================
    print("\n" + "=" * 60)
    print("STEP 3: Trigger ISR revalidation")
    print("=" * 60)

    pages_to_revalidate = ["/resorts", "/"]
    for page in pages_to_revalidate:
        result = revalidate_page(page)
        if result and result.get("success"):
            print(f"  Revalidated {page} ✓")
        else:
            print(f"  Revalidation of {page}: {result}")

    # =========================================================================
    # 4. Show current resort count
    # =========================================================================
    print("\n" + "=" * 60)
    print("STEP 4: Current resort stats")
    print("=" * 60)

    published = (
        client.table("resorts")
        .select("id", count="exact")
        .eq("status", "published")
        .execute()
    )
    drafts = (
        client.table("resorts")
        .select("id", count="exact")
        .eq("status", "draft")
        .execute()
    )

    print(f"\n  Published resorts: {published.count}")
    print(f"  Draft resorts: {drafts.count}")

    # Show most recently updated resorts
    recent = (
        client.table("resorts")
        .select("name, country, status, updated_at")
        .order("updated_at", desc=True)
        .limit(10)
        .execute()
    )

    print(f"\n  Most recently updated:")
    for r in recent.data:
        print(f"    {r['name']}, {r['country']} — {r['status']} (updated: {r['updated_at'][:16]})")


if __name__ == "__main__":
    main()
