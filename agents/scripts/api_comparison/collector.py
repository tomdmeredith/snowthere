"""Data collection for API comparison.

Runs the same queries against Exa, Brave, and Tavily, saving raw results.
"""

import asyncio
import json
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Any

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.primitives.research import (
    exa_search,
    brave_search,
    tavily_search,
    SearchResult,
)
from shared.config import settings


# Test matrix: 10 resorts across different regions and fame levels
RESORTS = [
    ("Park City", "USA"),           # Famous, North America
    ("Vail", "USA"),                # Famous, North America
    ("Taos Ski Valley", "USA"),     # Obscure, North America
    ("Zermatt", "Switzerland"),     # Famous, Europe
    ("St. Anton", "Austria"),       # Famous, Europe (German)
    ("Serfaus-Fiss-Ladis", "Austria"),  # Family-focused, Europe
    ("Kronplatz", "Italy"),         # Moderate, Europe (Italian/German)
    ("Niseko", "Japan"),            # Famous, Asia
    ("Myrkdalen", "Norway"),        # Obscure, Europe
    ("Valle Nevado", "Chile"),      # Moderate, South America
]

# Query templates matching search_resort_info()
QUERY_TEMPLATES = {
    "family_reviews": "{resort} {country} family ski trip review kids",
    "official_info": "{resort} ski resort official site lift tickets",
    "ski_school": "{resort} ski school children lessons childcare",
    "lodging": "{resort} family lodging ski-in ski-out hotels",
    "lift_prices": "{resort} lift ticket prices 2025 2026",
    "lodging_rates": "{resort} hotel prices per night winter ski season",
    "ski_school_cost": "{resort} ski school lesson prices children cost",
}

NUM_RESULTS = 10  # Results per API per query


def serialize_search_result(result: SearchResult) -> dict[str, Any]:
    """Convert SearchResult to JSON-serializable dict."""
    return {
        "title": result.title,
        "url": result.url,
        "snippet": result.snippet,
        "source": result.source,
        "score": result.score,
        "published_date": result.published_date,
    }


async def collect_single_query(
    resort: str,
    country: str,
    query_type: str,
    query_template: str,
) -> dict[str, Any]:
    """Collect results from all three APIs for a single query."""

    query = query_template.format(resort=resort, country=country)

    results: dict[str, Any] = {
        "resort": resort,
        "country": country,
        "query_type": query_type,
        "query_text": query,
        "timestamp": datetime.utcnow().isoformat(),
        "exa": {"results": [], "latency_ms": 0, "error": None},
        "brave": {"results": [], "latency_ms": 0, "error": None},
        "tavily": {"results": [], "answer": None, "latency_ms": 0, "error": None},
    }

    # Exa
    try:
        start = time.perf_counter()
        exa_results = await exa_search(query, num_results=NUM_RESULTS)
        results["exa"]["latency_ms"] = int((time.perf_counter() - start) * 1000)
        results["exa"]["results"] = [serialize_search_result(r) for r in exa_results]
    except Exception as e:
        results["exa"]["error"] = str(e)

    # Brave
    try:
        start = time.perf_counter()
        brave_results = await brave_search(query, num_results=NUM_RESULTS)
        results["brave"]["latency_ms"] = int((time.perf_counter() - start) * 1000)
        results["brave"]["results"] = [serialize_search_result(r) for r in brave_results]
    except Exception as e:
        results["brave"]["error"] = str(e)

    # Tavily
    try:
        start = time.perf_counter()
        tavily_response = await tavily_search(query, max_results=NUM_RESULTS)
        results["tavily"]["latency_ms"] = int((time.perf_counter() - start) * 1000)
        results["tavily"]["answer"] = tavily_response.get("answer")
        results["tavily"]["results"] = [
            serialize_search_result(r) for r in tavily_response.get("results", [])
        ]
    except Exception as e:
        results["tavily"]["error"] = str(e)

    return results


async def collect_all(
    output_dir: Path | None = None,
    dry_run: bool = False,
    max_resorts: int | None = None,
    max_queries: int | None = None,
) -> list[dict[str, Any]]:
    """Collect all queries for the test matrix.

    Args:
        output_dir: Directory to save results (default: comparison_results/)
        dry_run: If True, only show what would be collected
        max_resorts: Limit number of resorts (for testing)
        max_queries: Limit total queries (for testing)

    Returns:
        List of all collected query results
    """
    if output_dir is None:
        output_dir = Path(__file__).parent.parent.parent / "comparison_results"
    output_dir.mkdir(exist_ok=True)

    resorts = RESORTS[:max_resorts] if max_resorts else RESORTS

    if dry_run:
        total_queries = len(resorts) * len(QUERY_TEMPLATES)
        print(f"\n{'='*60}")
        print("DRY RUN - Would collect:")
        print(f"{'='*60}")
        print(f"  Resorts: {len(resorts)}")
        print(f"  Query types: {len(QUERY_TEMPLATES)}")
        print(f"  Total queries: {total_queries} per API = {total_queries * 3} total")
        print(f"\nResorts:")
        for resort, country in resorts:
            print(f"  - {resort}, {country}")
        print(f"\nQuery types:")
        for qt in QUERY_TEMPLATES:
            print(f"  - {qt}")
        print(f"\nEstimated cost: ~${total_queries * 0.02:.2f}")
        return []

    all_results: list[dict[str, Any]] = []
    query_count = 0

    for resort, country in resorts:
        print(f"\n{'='*60}")
        print(f"Collecting: {resort}, {country}")
        print(f"{'='*60}")

        for query_type, template in QUERY_TEMPLATES.items():
            if max_queries and query_count >= max_queries:
                print(f"\nMax queries ({max_queries}) reached, stopping.")
                break

            print(f"  {query_type}...", end=" ", flush=True)

            result = await collect_single_query(resort, country, query_type, template)
            all_results.append(result)
            query_count += 1

            # Show quick stats
            e = len(result["exa"]["results"])
            b = len(result["brave"]["results"])
            t = len(result["tavily"]["results"])
            e_err = " (ERR)" if result["exa"]["error"] else ""
            b_err = " (ERR)" if result["brave"]["error"] else ""
            t_err = " (ERR)" if result["tavily"]["error"] else ""
            print(f"Exa:{e}{e_err} Brave:{b}{b_err} Tavily:{t}{t_err}")

            # Rate limit protection - stagger requests
            await asyncio.sleep(1.5)

        if max_queries and query_count >= max_queries:
            break

    # Save raw results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"raw_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Collection complete!")
    print(f"{'='*60}")
    print(f"  Total queries: {len(all_results)}")
    print(f"  Results saved to: {output_file}")

    # Quick summary
    exa_total = sum(len(r["exa"]["results"]) for r in all_results)
    brave_total = sum(len(r["brave"]["results"]) for r in all_results)
    tavily_total = sum(len(r["tavily"]["results"]) for r in all_results)
    print(f"\n  Total results:")
    print(f"    Exa: {exa_total}")
    print(f"    Brave: {brave_total}")
    print(f"    Tavily: {tavily_total}")

    return all_results


async def main():
    """Run collector from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Collect search API comparison data")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be collected")
    parser.add_argument("--max-resorts", type=int, help="Limit number of resorts")
    parser.add_argument("--max-queries", type=int, help="Limit total queries")
    parser.add_argument("--output-dir", type=Path, help="Output directory")

    args = parser.parse_args()

    await collect_all(
        output_dir=args.output_dir,
        dry_run=args.dry_run,
        max_resorts=args.max_resorts,
        max_queries=args.max_queries,
    )


if __name__ == "__main__":
    asyncio.run(main())
