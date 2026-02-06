#!/usr/bin/env python3
"""Backfill hybrid scores for all published resorts.

Runs the three-layer scoring system (structural + content + review)
and stores composite scores, dimensions, and confidence levels.

Usage:
    python scripts/backfill_hybrid_scores.py                    # Full backfill
    python scripts/backfill_hybrid_scores.py --dry-run           # Preview only
    python scripts/backfill_hybrid_scores.py --limit 3           # Process 3 resorts
    python scripts/backfill_hybrid_scores.py --resort "Zermatt"  # Single resort
"""

import argparse
import asyncio
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client
from shared.primitives.scoring import (
    calculate_structural_score,
    calculate_composite_family_score,
)
from shared.primitives.intelligence import (
    assess_family_friendliness,
    assess_review_sentiment,
)


async def backfill_hybrid_scores(
    dry_run: bool = False,
    limit: int | None = None,
    resort_filter: str | None = None,
):
    """Score all resorts with the three-layer hybrid system."""
    client = get_supabase_client()

    # Get published resorts
    query = (
        client.table("resorts")
        .select("id, name, country, slug")
        .eq("status", "published")
    )
    if resort_filter:
        query = query.ilike("name", f"%{resort_filter}%")

    resorts_resp = query.execute()
    resorts = resorts_resp.data or []

    if limit:
        resorts = resorts[:limit]

    print(f"Processing {len(resorts)} resorts")

    results = []

    for resort in resorts:
        print(f"\n{'='*60}")
        print(f"Resort: {resort['name']} ({resort['country']})")

        # Get family metrics
        metrics_resp = (
            client.table("resort_family_metrics")
            .select("*")
            .eq("resort_id", resort["id"])
            .execute()
        )
        metrics = metrics_resp.data[0] if metrics_resp.data else {}

        # Get content sections
        content_resp = (
            client.table("resort_content")
            .select("*")
            .eq("resort_id", resort["id"])
            .execute()
        )
        content = content_resp.data[0] if content_resp.data else {}

        # Layer 1: Structural score
        structural = calculate_structural_score(metrics)
        print(f"  Structural: {structural:.1f}")

        # Layer 2: Content assessment
        content_score = None
        content_dimensions = {}
        content_reasoning = ""
        try:
            assessment = await assess_family_friendliness(
                resort_name=resort["name"],
                country=resort["country"],
                content_sections=content,
            )
            if assessment:
                content_score = assessment.overall_score
                content_dimensions = assessment.dimensions
                content_reasoning = assessment.reasoning
                print(f"  Content: {content_score:.1f}")
                for dim, val in content_dimensions.items():
                    print(f"    {dim}: {val:.1f}")
        except Exception as e:
            print(f"  Content assessment failed: {e}")

        # Layer 3: Review sentiment
        review_score = None
        reviews_html = content.get("parent_reviews_summary", "")
        if reviews_html and len(reviews_html) > 50:
            try:
                review_score = await assess_review_sentiment(
                    resort_name=resort["name"],
                    parent_reviews_content=reviews_html,
                )
                if review_score is not None:
                    print(f"  Review: {review_score:.1f}")
            except Exception as e:
                print(f"  Review assessment failed: {e}")

        # Composite
        composite = calculate_composite_family_score(
            structural=structural,
            content=content_score,
            review=review_score,
            content_dimensions=content_dimensions,
            content_reasoning=content_reasoning,
        )

        print(f"  Composite: {composite.family_score:.1f} (confidence: {composite.confidence})")

        results.append({
            "resort": resort["name"],
            "old_score": metrics.get("family_overall_score"),
            "new_score": composite.family_score,
            "confidence": composite.confidence,
        })

        if not dry_run:
            # Update family metrics with all scoring components
            update_data = {
                "family_overall_score": composite.family_score,
                "structural_score": structural,
                "score_confidence": composite.confidence,
                "score_reasoning": composite.reasoning,
                "score_dimensions": json.dumps(content_dimensions),
                "scored_at": datetime.now(timezone.utc).isoformat(),
            }
            if content_score is not None:
                update_data["content_score"] = content_score
            if review_score is not None:
                update_data["review_score"] = review_score

            client.table("resort_family_metrics").update(
                update_data
            ).eq("resort_id", resort["id"]).execute()
            print(f"  Saved to database")
        else:
            print(f"  [DRY RUN] Would save")

    # Summary
    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(results)} resorts scored")
    for r in results:
        old = f"{r['old_score']:.1f}" if r['old_score'] else "N/A"
        print(f"  {r['resort']}: {old} -> {r['new_score']:.1f} ({r['confidence']})")


def main():
    parser = argparse.ArgumentParser(description="Backfill hybrid scores")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--limit", type=int, help="Max resorts to process")
    parser.add_argument("--resort", type=str, help="Filter by resort name")
    args = parser.parse_args()

    asyncio.run(backfill_hybrid_scores(
        dry_run=args.dry_run,
        limit=args.limit,
        resort_filter=args.resort,
    ))


if __name__ == "__main__":
    main()
