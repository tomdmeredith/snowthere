"""Markdown report generation for API comparison.

Generates a human-readable report from analysis results.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


# Estimated costs per 1000 queries
API_COSTS_PER_1000 = {
    "exa": 11.0,      # $0.001/search + $0.001/result (10 results)
    "brave": 5.0,     # $5/1000 after free tier
    "tavily": 5.0,    # $5/1000 (advanced)
}


def generate_report(analysis: dict[str, Any]) -> str:
    """Generate markdown report from analysis data."""

    overall = analysis["overall"]
    by_query = analysis["by_query_type"]
    overlap = analysis["overlap"]
    by_resort = analysis["by_resort"]
    winners = analysis["query_type_winners"]

    # Determine overall winner
    overall_scores = {api: data["composite_score"] for api, data in overall.items()}
    overall_winner = max(overall_scores, key=overall_scores.get)

    # Count query type wins
    win_counts = {"exa": 0, "brave": 0, "tavily": 0}
    for winner in winners.values():
        win_counts[winner] += 1

    report = f"""# Search API Comparison Report
## Family Ski Directory Research

**Generated:** {analysis["generated_at"]}
**Total Queries Analyzed:** {analysis["total_queries"]}

---

## Executive Summary

**Overall Winner: {overall_winner.title()}** (composite score: {overall_scores[overall_winner]})

| Metric | Exa | Brave | Tavily |
|--------|-----|-------|--------|
| Composite Score | {overall["exa"]["composite_score"]} | {overall["brave"]["composite_score"]} | {overall["tavily"]["composite_score"]} |
| Avg Relevance | {overall["exa"]["avg_relevance"]} | {overall["brave"]["avg_relevance"]} | {overall["tavily"]["avg_relevance"]} |
| Avg Family Relevance | {overall["exa"]["avg_family_relevance"]} | {overall["brave"]["avg_family_relevance"]} | {overall["tavily"]["avg_family_relevance"]} |
| Avg Freshness | {overall["exa"]["avg_freshness"]} | {overall["brave"]["avg_freshness"]} | {overall["tavily"]["avg_freshness"]} |
| Has Current Prices | {overall["exa"]["current_season_pct"]}% | {overall["brave"]["current_season_pct"]}% | {overall["tavily"]["current_season_pct"]}% |
| Avg Latency (ms) | {overall["exa"]["avg_latency_ms"]} | {overall["brave"]["avg_latency_ms"]} | {overall["tavily"]["avg_latency_ms"]} |

**Query Type Wins:** Exa: {win_counts["exa"]} | Brave: {win_counts["brave"]} | Tavily: {win_counts["tavily"]}

---

## Best API by Query Type

| Query Type | Winner | Exa Score | Brave Score | Tavily Score |
|------------|--------|-----------|-------------|--------------|
"""

    for qt, data in by_query.items():
        winner = data["winner"]
        exa_score = data["exa"]["composite_score"]
        brave_score = data["brave"]["composite_score"]
        tavily_score = data["tavily"]["composite_score"]

        # Bold the winner
        exa_fmt = f"**{exa_score}**" if winner == "exa" else str(exa_score)
        brave_fmt = f"**{brave_score}**" if winner == "brave" else str(brave_score)
        tavily_fmt = f"**{tavily_score}**" if winner == "tavily" else str(tavily_score)

        report += f"| {qt} | {winner.title()} | {exa_fmt} | {brave_fmt} | {tavily_fmt} |\n"

    report += f"""
### Query Type Insights

"""

    # Add insights for each query type
    for qt, data in by_query.items():
        winner = data["winner"]
        report += f"- **{qt}**: {winner.title()} wins"
        if qt == "family_reviews":
            report += " (semantic search strength)"
        elif qt == "official_info":
            report += " (web search finds official sites)"
        elif qt in ["lift_prices", "lodging_rates"]:
            report += " (pricing-specific queries)"
        report += "\n"

    report += f"""
---

## URL Overlap Analysis

| Category | Count | % of Total |
|----------|-------|------------|
| Total Unique URLs | {overlap["total_unique_urls"]} | 100% |
| Found by All 3 APIs | {overlap["in_all_three"]} | {round(overlap["in_all_three"]/overlap["total_unique_urls"]*100, 1) if overlap["total_unique_urls"] else 0}% |
| Found by 2 APIs | {overlap["exa_brave_only"] + overlap["exa_tavily_only"] + overlap["brave_tavily_only"]} | {round((overlap["exa_brave_only"] + overlap["exa_tavily_only"] + overlap["brave_tavily_only"])/overlap["total_unique_urls"]*100, 1) if overlap["total_unique_urls"] else 0}% |
| Unique to Exa | {overlap["only_exa"]} | {round(overlap["only_exa"]/overlap["total_unique_urls"]*100, 1) if overlap["total_unique_urls"] else 0}% |
| Unique to Brave | {overlap["only_brave"]} | {round(overlap["only_brave"]/overlap["total_unique_urls"]*100, 1) if overlap["total_unique_urls"] else 0}% |
| Unique to Tavily | {overlap["only_tavily"]} | {round(overlap["only_tavily"]/overlap["total_unique_urls"]*100, 1) if overlap["total_unique_urls"] else 0}% |

**Overlap Rate: {overlap["overlap_pct"]}%** (URLs found by multiple APIs)

### Overlap Interpretation

"""

    if overlap["overlap_pct"] > 50:
        report += """- **High Overlap**: More than half of URLs are found by multiple APIs
- Consider consolidating to fewer APIs
- Savings potential is significant
"""
    elif overlap["overlap_pct"] > 25:
        report += """- **Moderate Overlap**: Some redundancy but each API adds unique value
- Consider smart routing by query type
- Keep APIs but optimize usage
"""
    else:
        report += """- **Low Overlap**: Each API finds mostly unique content
- All three APIs provide distinct value
- Keep all APIs for comprehensive coverage
"""

    report += f"""
---

## Cost Analysis

Estimated monthly cost at different volumes:

| Daily Queries | Exa | Brave | Tavily | Total |
|---------------|-----|-------|--------|-------|
"""

    for daily in [10, 50, 100, 500]:
        monthly = daily * 30
        exa_cost = (monthly / 1000) * API_COSTS_PER_1000["exa"]
        brave_cost = (monthly / 1000) * API_COSTS_PER_1000["brave"]
        tavily_cost = (monthly / 1000) * API_COSTS_PER_1000["tavily"]
        total = exa_cost + brave_cost + tavily_cost
        report += f"| {daily} | ${exa_cost:.2f} | ${brave_cost:.2f} | ${tavily_cost:.2f} | ${total:.2f} |\n"

    # Cost per quality point
    total_evaluations = sum(data["total_evaluations"] for data in overall.values())
    if total_evaluations > 0:
        exa_cpp = API_COSTS_PER_1000["exa"] / 1000 / overall["exa"]["composite_score"] if overall["exa"]["composite_score"] else 0
        brave_cpp = API_COSTS_PER_1000["brave"] / 1000 / overall["brave"]["composite_score"] if overall["brave"]["composite_score"] else 0
        tavily_cpp = API_COSTS_PER_1000["tavily"] / 1000 / overall["tavily"]["composite_score"] if overall["tavily"]["composite_score"] else 0

        report += f"""
### Cost per Quality Point

| API | Cost/Query | Composite Score | Cost per Score Point |
|-----|------------|-----------------|----------------------|
| Exa | ${API_COSTS_PER_1000["exa"]/1000:.4f} | {overall["exa"]["composite_score"]} | ${exa_cpp:.5f} |
| Brave | ${API_COSTS_PER_1000["brave"]/1000:.4f} | {overall["brave"]["composite_score"]} | ${brave_cpp:.5f} |
| Tavily | ${API_COSTS_PER_1000["tavily"]/1000:.4f} | {overall["tavily"]["composite_score"]} | ${tavily_cpp:.5f} |

"""

    report += f"""
---

## Performance by Resort

| Resort | Best API | Exa | Brave | Tavily |
|--------|----------|-----|-------|--------|
"""

    for resort, apis in by_resort.items():
        scores = {api: data["composite_score"] for api, data in apis.items()}
        winner = max(scores, key=scores.get)

        exa_fmt = f"**{scores['exa']}**" if winner == "exa" else str(scores["exa"])
        brave_fmt = f"**{scores['brave']}**" if winner == "brave" else str(scores["brave"])
        tavily_fmt = f"**{scores['tavily']}**" if winner == "tavily" else str(scores["tavily"])

        report += f"| {resort} | {winner.title()} | {exa_fmt} | {brave_fmt} | {tavily_fmt} |\n"

    report += f"""
---

## Recommendations

"""

    # Generate recommendations based on data
    if overall_winner == "exa":
        report += """### Primary Recommendation: Prioritize Exa

Exa's semantic search performs best overall for family ski research.

"""
    elif overall_winner == "brave":
        report += """### Primary Recommendation: Prioritize Brave

Brave's traditional web search finds the most relevant results.

"""
    else:
        report += """### Primary Recommendation: Prioritize Tavily

Tavily's AI synthesis provides the most useful results.

"""

    # Query routing recommendation
    report += """### Query Routing Strategy

Based on per-query-type performance:

"""

    for qt, winner in winners.items():
        report += f"- **{qt}** → Use {winner.title()}\n"

    report += f"""
### Consolidation Options

"""

    if overlap["overlap_pct"] > 40:
        report += """1. **Drop lowest performer**: Could save ~33% on API costs
2. **Keep winner + one specialist**: Best balance of coverage and cost
"""
    else:
        report += """1. **Keep all three**: Low overlap means each adds unique value
2. **Smart routing**: Use best API per query type to maximize quality
"""

    report += """
---

## Methodology

- **Resorts tested**: 10 (mix of famous/obscure, US/Europe/Asia)
- **Query types**: 7 (matching production search_resort_info())
- **Results evaluated**: Top 5 per API per query
- **Evaluation**: Claude Sonnet rated each result on 5 criteria (1-5 scale)
- **Composite score**: Weighted average (relevance 30%, family 25%, freshness 20%, density 15%, quality 10%)

---

*Report generated by API Comparison Testing Suite*
"""

    return report


def generate(
    analysis_file: Path,
    output_dir: Path | None = None,
) -> str:
    """Generate report from analysis file.

    Args:
        analysis_file: Path to analysis_*.json
        output_dir: Directory to save report

    Returns:
        Report markdown string
    """
    with open(analysis_file) as f:
        analysis = json.load(f)

    if output_dir is None:
        output_dir = analysis_file.parent

    report = generate_report(analysis)

    # Save report
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"report_{timestamp}.md"
    with open(output_file, "w") as f:
        f.write(report)

    print(f"\n{'='*60}")
    print("Report generated!")
    print(f"{'='*60}")
    print(f"  Saved to: {output_file}")

    return report


def main():
    """Run reporter from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Generate markdown report from analysis")
    parser.add_argument("analysis_file", type=Path, help="Path to analysis_*.json")
    parser.add_argument("--output-dir", type=Path, help="Output directory")

    args = parser.parse_args()

    if not args.analysis_file.exists():
        print(f"Error: File not found: {args.analysis_file}")
        sys.exit(1)

    report = generate(
        analysis_file=args.analysis_file,
        output_dir=args.output_dir,
    )

    # Print summary
    print("\n" + "="*60)
    print("REPORT PREVIEW (first 50 lines)")
    print("="*60)
    for line in report.split("\n")[:50]:
        print(line)


if __name__ == "__main__":
    main()
