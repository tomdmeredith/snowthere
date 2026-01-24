"""LLM-based evaluation of search results.

Uses Claude Sonnet to rate each search result on multiple criteria.
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

import anthropic

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from shared.config import settings


EVALUATION_PROMPT = """You are evaluating a search result for a family ski directory research task.

## Context
- Resort: {resort}, {country}
- Query Type: {query_type}
- Query: {query_text}

## Search Result
- Title: {title}
- URL: {url}
- Snippet: {snippet}

## Evaluation Criteria

Rate each criterion from 1-5:

### 1. RELEVANCE (Does this answer what we're looking for?)
- 5: Exactly what we need - direct answer to the query
- 4: Very relevant - contains most of what we need
- 3: Somewhat relevant - partial answer or tangential
- 2: Marginally relevant - mentions topic but doesn't help
- 1: Irrelevant - wrong resort, wrong topic, or spam

### 2. FRESHNESS (Is the data current?)
- 5: Current season (2025-2026) prices/info
- 4: Last season (2024-2025) data
- 3: 2-3 years old
- 2: 4-5 years old
- 1: Very outdated (>5 years) or undated

### 3. SOURCE QUALITY
- 5: Official resort website
- 4: Reputable aggregator (OnTheSnow, SkiResort.info) or major booking site
- 3: Quality travel blog or review site (TripAdvisor, specialized ski site)
- 2: Generic travel site or forum
- 1: SEO spam, content farm, or unreliable source

### 4. INFORMATION DENSITY
- 5: Rich with specific details (prices, names, ages, dates)
- 4: Good amount of useful detail
- 3: Some useful information
- 2: Mostly generic or vague
- 1: No useful specific information

### 5. FAMILY RELEVANCE (For a family ski directory)
- 5: Explicitly about families with kids
- 4: Contains significant family-relevant info (childcare, ski school, kids)
- 3: Some mention of family considerations
- 2: General info that could apply to families
- 1: Not family-relevant (adult-focused, extreme skiing, etc.)

## Additional Flags
Set these to true or false based on the content:
- contains_prices: Does it mention specific dollar/euro amounts?
- contains_family_info: Does it mention childcare, kids programs, family lodging?
- contains_specific_names: Does it name specific hotels, restaurants, instructors?
- mentions_kids: Does it mention children, kids, or young learners?
- mentions_childcare: Does it mention childcare, daycare, or babysitting?
- mentions_ski_school: Does it mention ski school or lessons?
- data_age_months: Your best estimate of how old the core data is (null if unclear)
- has_current_season_prices: Does it have 2025-2026 season prices?

## Output Format
Respond with ONLY a JSON object (no markdown, no explanation):
{{
    "relevance_score": <1-5>,
    "relevance_reasoning": "<brief explanation, max 50 words>",
    "freshness_score": <1-5>,
    "data_age_months": <number or null>,
    "has_current_season_prices": <true or false>,
    "source_quality_score": <1-5>,
    "source_type": "<official|aggregator|trip_report|news|seo_spam|booking|review_site|unknown>",
    "information_density_score": <1-5>,
    "family_relevance_score": <1-5>,
    "contains_prices": <true or false>,
    "contains_family_info": <true or false>,
    "contains_specific_names": <true or false>,
    "mentions_kids": <true or false>,
    "mentions_childcare": <true or false>,
    "mentions_ski_school": <true or false>
}}"""


async def evaluate_single_result(
    client: anthropic.Anthropic,
    result: dict[str, Any],
    resort: str,
    country: str,
    query_type: str,
    query_text: str,
) -> dict[str, Any]:
    """Evaluate a single search result using Claude."""

    prompt = EVALUATION_PROMPT.format(
        resort=resort,
        country=country,
        query_type=query_type,
        query_text=query_text,
        title=result.get("title", ""),
        url=result.get("url", ""),
        snippet=result.get("snippet", "")[:1500],  # Limit snippet length
    )

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  # Fast, cost-effective for bulk evaluation
            max_tokens=500,
            messages=[{"role": "user", "content": prompt}],
        )

        text = response.content[0].text.strip()

        # Handle potential markdown code blocks
        if text.startswith("```"):
            # Remove ```json and ``` markers
            lines = text.split("\n")
            text = "\n".join(
                line for line in lines
                if not line.startswith("```")
            )

        evaluation = json.loads(text)

        # Add original result info
        evaluation["url"] = result.get("url", "")
        evaluation["title"] = result.get("title", "")

        return evaluation

    except json.JSONDecodeError as e:
        return {
            "error": f"JSON parse error: {e}",
            "raw_response": text if "text" in dir() else None,
            "url": result.get("url", ""),
            "title": result.get("title", ""),
        }
    except Exception as e:
        return {
            "error": str(e),
            "url": result.get("url", ""),
            "title": result.get("title", ""),
        }


async def evaluate_query_results(
    client: anthropic.Anthropic,
    query_data: dict[str, Any],
    max_results_per_api: int = 5,
) -> dict[str, Any]:
    """Evaluate results from all APIs for a single query."""

    resort = query_data["resort"]
    country = query_data["country"]
    query_type = query_data["query_type"]
    query_text = query_data["query_text"]

    evaluated: dict[str, Any] = {
        "resort": resort,
        "country": country,
        "query_type": query_type,
        "query_text": query_text,
        "exa": [],
        "brave": [],
        "tavily": [],
        "tavily_answer": query_data.get("tavily", {}).get("answer"),
    }

    for api in ["exa", "brave", "tavily"]:
        results = query_data.get(api, {}).get("results", [])[:max_results_per_api]

        for i, result in enumerate(results):
            print(f"      {api}[{i+1}]...", end=" ", flush=True)

            eval_result = await evaluate_single_result(
                client, result, resort, country, query_type, query_text
            )
            eval_result["rank"] = i + 1

            if "error" in eval_result:
                print(f"ERR: {eval_result['error'][:30]}")
            else:
                print(f"rel={eval_result.get('relevance_score', '?')}")

            evaluated[api].append(eval_result)

            # Small delay to avoid rate limits
            await asyncio.sleep(0.3)

    return evaluated


async def evaluate_all(
    raw_results_file: Path,
    output_dir: Path | None = None,
    max_results_per_api: int = 5,
    max_queries: int | None = None,
    dry_run: bool = False,
) -> list[dict[str, Any]]:
    """Evaluate all collected results.

    Args:
        raw_results_file: Path to raw_results_*.json from collector
        output_dir: Directory to save evaluated results
        max_results_per_api: How many results per API to evaluate (default 5)
        max_queries: Limit queries to evaluate (for testing)
        dry_run: If True, show what would be evaluated

    Returns:
        List of evaluated query results
    """
    with open(raw_results_file) as f:
        raw_data = json.load(f)

    if output_dir is None:
        output_dir = raw_results_file.parent
    output_dir.mkdir(exist_ok=True)

    if max_queries:
        raw_data = raw_data[:max_queries]

    total_evaluations = len(raw_data) * 3 * max_results_per_api
    estimated_cost = total_evaluations * 0.003  # ~$0.003 per Sonnet call

    if dry_run:
        print(f"\n{'='*60}")
        print("DRY RUN - Would evaluate:")
        print(f"{'='*60}")
        print(f"  Queries: {len(raw_data)}")
        print(f"  Results per API: {max_results_per_api}")
        print(f"  Total evaluations: {total_evaluations}")
        print(f"  Estimated cost: ~${estimated_cost:.2f}")
        return []

    print(f"\n{'='*60}")
    print(f"Starting evaluation")
    print(f"{'='*60}")
    print(f"  Queries: {len(raw_data)}")
    print(f"  Results per API: {max_results_per_api}")
    print(f"  Total evaluations: {total_evaluations}")
    print(f"  Estimated cost: ~${estimated_cost:.2f}")

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    evaluated: list[dict[str, Any]] = []

    for i, query_data in enumerate(raw_data):
        resort = query_data["resort"]
        query_type = query_data["query_type"]

        print(f"\n[{i+1}/{len(raw_data)}] {resort} - {query_type}")

        query_eval = await evaluate_query_results(
            client, query_data, max_results_per_api
        )
        evaluated.append(query_eval)

    # Save evaluated results
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"evaluated_results_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(evaluated, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Evaluation complete!")
    print(f"{'='*60}")
    print(f"  Queries evaluated: {len(evaluated)}")
    print(f"  Results saved to: {output_file}")

    return evaluated


async def main():
    """Run evaluator from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Evaluate search API results with Claude")
    parser.add_argument("raw_results_file", type=Path, help="Path to raw_results_*.json")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be evaluated")
    parser.add_argument("--max-results", type=int, default=5, help="Results per API to evaluate")
    parser.add_argument("--max-queries", type=int, help="Limit queries to evaluate")
    parser.add_argument("--output-dir", type=Path, help="Output directory")

    args = parser.parse_args()

    if not args.raw_results_file.exists():
        print(f"Error: File not found: {args.raw_results_file}")
        sys.exit(1)

    await evaluate_all(
        raw_results_file=args.raw_results_file,
        output_dir=args.output_dir,
        max_results_per_api=args.max_results,
        max_queries=args.max_queries,
        dry_run=args.dry_run,
    )


if __name__ == "__main__":
    asyncio.run(main())
