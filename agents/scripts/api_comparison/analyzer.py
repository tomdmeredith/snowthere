"""Analysis and metrics calculation for API comparison.

Calculates overlap, per-API scores, and cost-effectiveness.
"""

import json
import sys
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


@dataclass
class APIMetrics:
    """Aggregated metrics for a single API."""

    name: str
    total_results: int = 0
    total_evaluations: int = 0

    # Score averages (across all evaluated results)
    relevance_scores: list[int] = field(default_factory=list)
    freshness_scores: list[int] = field(default_factory=list)
    source_quality_scores: list[int] = field(default_factory=list)
    information_density_scores: list[int] = field(default_factory=list)
    family_relevance_scores: list[int] = field(default_factory=list)

    # Boolean flag counts
    contains_prices_count: int = 0
    contains_family_info_count: int = 0
    mentions_kids_count: int = 0
    mentions_ski_school_count: int = 0
    has_current_season_count: int = 0

    # Latency
    latencies_ms: list[int] = field(default_factory=list)

    # URLs for overlap analysis
    all_urls: set[str] = field(default_factory=set)

    def avg(self, scores: list[int]) -> float:
        """Calculate average of scores."""
        return sum(scores) / len(scores) if scores else 0.0

    @property
    def avg_relevance(self) -> float:
        return self.avg(self.relevance_scores)

    @property
    def avg_freshness(self) -> float:
        return self.avg(self.freshness_scores)

    @property
    def avg_source_quality(self) -> float:
        return self.avg(self.source_quality_scores)

    @property
    def avg_information_density(self) -> float:
        return self.avg(self.information_density_scores)

    @property
    def avg_family_relevance(self) -> float:
        return self.avg(self.family_relevance_scores)

    @property
    def avg_latency_ms(self) -> float:
        return self.avg(self.latencies_ms)

    @property
    def composite_score(self) -> float:
        """Weighted composite score (family directory priorities)."""
        # Weights: relevance most important, then family relevance, then freshness
        return (
            self.avg_relevance * 0.3
            + self.avg_family_relevance * 0.25
            + self.avg_freshness * 0.2
            + self.avg_information_density * 0.15
            + self.avg_source_quality * 0.1
        )


@dataclass
class QueryTypeMetrics:
    """Metrics broken down by query type."""

    query_type: str
    exa: APIMetrics = field(default_factory=lambda: APIMetrics("exa"))
    brave: APIMetrics = field(default_factory=lambda: APIMetrics("brave"))
    tavily: APIMetrics = field(default_factory=lambda: APIMetrics("tavily"))

    @property
    def winner(self) -> str:
        """API with highest composite score for this query type."""
        scores = {
            "exa": self.exa.composite_score,
            "brave": self.brave.composite_score,
            "tavily": self.tavily.composite_score,
        }
        return max(scores, key=scores.get)


@dataclass
class OverlapAnalysis:
    """URL overlap analysis across APIs."""

    total_unique_urls: int = 0
    urls_all_three: list[str] = field(default_factory=list)
    urls_exa_brave: list[str] = field(default_factory=list)
    urls_exa_tavily: list[str] = field(default_factory=list)
    urls_brave_tavily: list[str] = field(default_factory=list)
    urls_only_exa: list[str] = field(default_factory=list)
    urls_only_brave: list[str] = field(default_factory=list)
    urls_only_tavily: list[str] = field(default_factory=list)

    @property
    def overlap_pct(self) -> float:
        """Percentage of URLs found by multiple APIs."""
        if self.total_unique_urls == 0:
            return 0.0
        multi_api = (
            len(self.urls_all_three)
            + len(self.urls_exa_brave)
            + len(self.urls_exa_tavily)
            + len(self.urls_brave_tavily)
        )
        return (multi_api / self.total_unique_urls) * 100


def normalize_url(url: str) -> str:
    """Normalize URL for comparison (remove trailing slashes, www, etc)."""
    parsed = urlparse(url.lower())
    netloc = parsed.netloc.replace("www.", "")
    path = parsed.path.rstrip("/")
    return f"{netloc}{path}"


def analyze_url_overlap(
    exa_urls: set[str],
    brave_urls: set[str],
    tavily_urls: set[str],
) -> OverlapAnalysis:
    """Analyze URL overlap between the three APIs."""

    # Normalize all URLs
    exa_norm = {normalize_url(u) for u in exa_urls}
    brave_norm = {normalize_url(u) for u in brave_urls}
    tavily_norm = {normalize_url(u) for u in tavily_urls}

    all_urls = exa_norm | brave_norm | tavily_norm

    return OverlapAnalysis(
        total_unique_urls=len(all_urls),
        urls_all_three=list(exa_norm & brave_norm & tavily_norm),
        urls_exa_brave=list((exa_norm & brave_norm) - tavily_norm),
        urls_exa_tavily=list((exa_norm & tavily_norm) - brave_norm),
        urls_brave_tavily=list((brave_norm & tavily_norm) - exa_norm),
        urls_only_exa=list(exa_norm - brave_norm - tavily_norm),
        urls_only_brave=list(brave_norm - exa_norm - tavily_norm),
        urls_only_tavily=list(tavily_norm - exa_norm - brave_norm),
    )


def process_result(metrics: APIMetrics, result: dict[str, Any]) -> None:
    """Add a single result's data to API metrics."""

    metrics.total_evaluations += 1

    # Skip results with errors
    if "error" in result:
        return

    # Scores
    if "relevance_score" in result:
        metrics.relevance_scores.append(result["relevance_score"])
    if "freshness_score" in result:
        metrics.freshness_scores.append(result["freshness_score"])
    if "source_quality_score" in result:
        metrics.source_quality_scores.append(result["source_quality_score"])
    if "information_density_score" in result:
        metrics.information_density_scores.append(result["information_density_score"])
    if "family_relevance_score" in result:
        metrics.family_relevance_scores.append(result["family_relevance_score"])

    # Boolean flags
    if result.get("contains_prices"):
        metrics.contains_prices_count += 1
    if result.get("contains_family_info"):
        metrics.contains_family_info_count += 1
    if result.get("mentions_kids"):
        metrics.mentions_kids_count += 1
    if result.get("mentions_ski_school"):
        metrics.mentions_ski_school_count += 1
    if result.get("has_current_season_prices"):
        metrics.has_current_season_count += 1

    # URL
    if result.get("url"):
        metrics.all_urls.add(result["url"])


def analyze_evaluated_results(
    evaluated_data: list[dict[str, Any]],
    raw_data: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Analyze evaluated results and calculate all metrics.

    Args:
        evaluated_data: List of evaluated query results from evaluator
        raw_data: Optional raw data for latency info

    Returns:
        Dictionary with all analysis results
    """

    # Overall API metrics
    overall = {
        "exa": APIMetrics("exa"),
        "brave": APIMetrics("brave"),
        "tavily": APIMetrics("tavily"),
    }

    # Per-query-type metrics
    by_query_type: dict[str, QueryTypeMetrics] = {}

    # Per-resort metrics
    by_resort: dict[str, dict[str, APIMetrics]] = {}

    # Process each query's results
    for query_eval in evaluated_data:
        query_type = query_eval["query_type"]
        resort = query_eval["resort"]

        # Initialize query type if needed
        if query_type not in by_query_type:
            by_query_type[query_type] = QueryTypeMetrics(query_type)

        # Initialize resort if needed
        if resort not in by_resort:
            by_resort[resort] = {
                "exa": APIMetrics("exa"),
                "brave": APIMetrics("brave"),
                "tavily": APIMetrics("tavily"),
            }

        # Process each API's results
        for api in ["exa", "brave", "tavily"]:
            results = query_eval.get(api, [])
            overall[api].total_results += len(results)

            for result in results:
                process_result(overall[api], result)
                process_result(getattr(by_query_type[query_type], api), result)
                process_result(by_resort[resort][api], result)

    # Add latency from raw data if available
    if raw_data:
        for query_raw in raw_data:
            for api in ["exa", "brave", "tavily"]:
                latency = query_raw.get(api, {}).get("latency_ms", 0)
                if latency:
                    overall[api].latencies_ms.append(latency)

    # Calculate overall overlap
    overlap = analyze_url_overlap(
        overall["exa"].all_urls,
        overall["brave"].all_urls,
        overall["tavily"].all_urls,
    )

    # Determine winners by query type
    query_type_winners = {
        qt: metrics.winner for qt, metrics in by_query_type.items()
    }

    # Build final analysis
    analysis = {
        "generated_at": datetime.utcnow().isoformat(),
        "total_queries": len(evaluated_data),
        "overall": {
            api: {
                "total_results": m.total_results,
                "total_evaluations": m.total_evaluations,
                "avg_relevance": round(m.avg_relevance, 2),
                "avg_freshness": round(m.avg_freshness, 2),
                "avg_source_quality": round(m.avg_source_quality, 2),
                "avg_information_density": round(m.avg_information_density, 2),
                "avg_family_relevance": round(m.avg_family_relevance, 2),
                "composite_score": round(m.composite_score, 2),
                "avg_latency_ms": round(m.avg_latency_ms, 0),
                "contains_prices_pct": round(
                    m.contains_prices_count / m.total_evaluations * 100, 1
                ) if m.total_evaluations else 0,
                "current_season_pct": round(
                    m.has_current_season_count / m.total_evaluations * 100, 1
                ) if m.total_evaluations else 0,
                "unique_urls": len(m.all_urls),
            }
            for api, m in overall.items()
        },
        "by_query_type": {
            qt: {
                "winner": metrics.winner,
                "exa": {
                    "avg_relevance": round(metrics.exa.avg_relevance, 2),
                    "composite_score": round(metrics.exa.composite_score, 2),
                },
                "brave": {
                    "avg_relevance": round(metrics.brave.avg_relevance, 2),
                    "composite_score": round(metrics.brave.composite_score, 2),
                },
                "tavily": {
                    "avg_relevance": round(metrics.tavily.avg_relevance, 2),
                    "composite_score": round(metrics.tavily.composite_score, 2),
                },
            }
            for qt, metrics in by_query_type.items()
        },
        "query_type_winners": query_type_winners,
        "overlap": {
            "total_unique_urls": overlap.total_unique_urls,
            "overlap_pct": round(overlap.overlap_pct, 1),
            "in_all_three": len(overlap.urls_all_three),
            "exa_brave_only": len(overlap.urls_exa_brave),
            "exa_tavily_only": len(overlap.urls_exa_tavily),
            "brave_tavily_only": len(overlap.urls_brave_tavily),
            "only_exa": len(overlap.urls_only_exa),
            "only_brave": len(overlap.urls_only_brave),
            "only_tavily": len(overlap.urls_only_tavily),
        },
        "by_resort": {
            resort: {
                api: {
                    "avg_relevance": round(m.avg_relevance, 2),
                    "composite_score": round(m.composite_score, 2),
                }
                for api, m in apis.items()
            }
            for resort, apis in by_resort.items()
        },
    }

    return analysis


def analyze(
    evaluated_file: Path,
    raw_file: Path | None = None,
    output_dir: Path | None = None,
) -> dict[str, Any]:
    """Run analysis on evaluated results.

    Args:
        evaluated_file: Path to evaluated_results_*.json
        raw_file: Optional path to raw_results_*.json for latency
        output_dir: Directory to save analysis

    Returns:
        Analysis dictionary
    """
    with open(evaluated_file) as f:
        evaluated_data = json.load(f)

    raw_data = None
    if raw_file and raw_file.exists():
        with open(raw_file) as f:
            raw_data = json.load(f)

    if output_dir is None:
        output_dir = evaluated_file.parent

    analysis = analyze_evaluated_results(evaluated_data, raw_data)

    # Save analysis
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    output_file = output_dir / f"analysis_{timestamp}.json"
    with open(output_file, "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n{'='*60}")
    print("Analysis complete!")
    print(f"{'='*60}")
    print(f"  Results saved to: {output_file}")

    # Quick summary
    print(f"\nOverall Composite Scores:")
    for api, data in analysis["overall"].items():
        print(f"  {api.title()}: {data['composite_score']}")

    print(f"\nURL Overlap: {analysis['overlap']['overlap_pct']}%")
    print(f"  Unique to Exa: {analysis['overlap']['only_exa']}")
    print(f"  Unique to Brave: {analysis['overlap']['only_brave']}")
    print(f"  Unique to Tavily: {analysis['overlap']['only_tavily']}")

    return analysis


def main():
    """Run analyzer from command line."""
    import argparse

    parser = argparse.ArgumentParser(description="Analyze evaluated API results")
    parser.add_argument("evaluated_file", type=Path, help="Path to evaluated_results_*.json")
    parser.add_argument("--raw-file", type=Path, help="Path to raw_results_*.json for latency")
    parser.add_argument("--output-dir", type=Path, help="Output directory")

    args = parser.parse_args()

    if not args.evaluated_file.exists():
        print(f"Error: File not found: {args.evaluated_file}")
        sys.exit(1)

    analyze(
        evaluated_file=args.evaluated_file,
        raw_file=args.raw_file,
        output_dir=args.output_dir,
    )


if __name__ == "__main__":
    main()
