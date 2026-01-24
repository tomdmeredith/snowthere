#!/usr/bin/env python3
"""Main entry point for API comparison testing.

Orchestrates the full comparison pipeline:
1. Collect raw results from all APIs
2. Evaluate results using Claude
3. Analyze metrics and overlap
4. Generate markdown report

Usage:
    # Full run
    python -m scripts.api_comparison.run_comparison

    # Dry run (see what would happen)
    python -m scripts.api_comparison.run_comparison --dry-run

    # Quick test (2 resorts, 3 queries)
    python -m scripts.api_comparison.run_comparison --quick

    # Skip collection (use existing raw results)
    python -m scripts.api_comparison.run_comparison --skip-collect --raw-file path/to/raw.json

    # Skip evaluation (use existing evaluated results)
    python -m scripts.api_comparison.run_comparison --skip-eval --eval-file path/to/eval.json
"""

import argparse
import asyncio
import sys
from datetime import datetime
from pathlib import Path

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from scripts.api_comparison.collector import collect_all
from scripts.api_comparison.evaluator import evaluate_all
from scripts.api_comparison.analyzer import analyze
from scripts.api_comparison.reporter import generate


async def run_full_comparison(
    output_dir: Path,
    dry_run: bool = False,
    quick: bool = False,
    skip_collect: bool = False,
    skip_eval: bool = False,
    raw_file: Path | None = None,
    eval_file: Path | None = None,
    max_resorts: int | None = None,
    max_queries: int | None = None,
    max_results_per_api: int = 5,
) -> dict:
    """Run the full comparison pipeline.

    Args:
        output_dir: Directory for all output files
        dry_run: If True, show what would happen without executing
        quick: If True, use small test set (2 resorts, 3 queries)
        skip_collect: Skip collection, use existing raw file
        skip_eval: Skip evaluation, use existing eval file
        raw_file: Path to existing raw results
        eval_file: Path to existing evaluated results
        max_resorts: Override max resorts
        max_queries: Override max queries
        max_results_per_api: Results to evaluate per API (default 5)

    Returns:
        Dictionary with paths to all generated files
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Quick mode settings
    if quick:
        max_resorts = max_resorts or 2
        max_queries = max_queries or 3
        max_results_per_api = 3

    results = {
        "output_dir": str(output_dir),
        "raw_file": None,
        "eval_file": None,
        "analysis_file": None,
        "report_file": None,
    }

    print("\n" + "="*70)
    print("  SEARCH API COMPARISON TESTING SUITE")
    print("="*70)
    print(f"  Output directory: {output_dir}")
    print(f"  Mode: {'DRY RUN' if dry_run else 'FULL RUN'}")
    if quick:
        print(f"  Quick mode: {max_resorts} resorts, {max_queries} queries")
    print("="*70)

    # =========================================================================
    # STEP 1: Collection
    # =========================================================================
    print("\n" + "-"*70)
    print("  STEP 1: Data Collection")
    print("-"*70)

    if skip_collect:
        if not raw_file or not raw_file.exists():
            print("ERROR: --skip-collect requires --raw-file with valid path")
            sys.exit(1)
        print(f"  Skipping collection, using: {raw_file}")
        results["raw_file"] = str(raw_file)
    else:
        raw_results = await collect_all(
            output_dir=output_dir,
            dry_run=dry_run,
            max_resorts=max_resorts,
            max_queries=max_queries,
        )

        if dry_run:
            print("  [DRY RUN] Would collect data here")
        else:
            # Find the generated file
            raw_files = sorted(output_dir.glob("raw_results_*.json"))
            if raw_files:
                results["raw_file"] = str(raw_files[-1])
                raw_file = raw_files[-1]

    if dry_run:
        print("\n" + "="*70)
        print("  DRY RUN COMPLETE")
        print("="*70)
        return results

    # =========================================================================
    # STEP 2: Evaluation
    # =========================================================================
    print("\n" + "-"*70)
    print("  STEP 2: LLM Evaluation")
    print("-"*70)

    if skip_eval:
        if not eval_file or not eval_file.exists():
            print("ERROR: --skip-eval requires --eval-file with valid path")
            sys.exit(1)
        print(f"  Skipping evaluation, using: {eval_file}")
        results["eval_file"] = str(eval_file)
    else:
        if not raw_file:
            print("ERROR: No raw file available for evaluation")
            sys.exit(1)

        await evaluate_all(
            raw_results_file=raw_file,
            output_dir=output_dir,
            max_results_per_api=max_results_per_api,
            max_queries=max_queries,
        )

        # Find the generated file
        eval_files = sorted(output_dir.glob("evaluated_results_*.json"))
        if eval_files:
            results["eval_file"] = str(eval_files[-1])
            eval_file = eval_files[-1]

    # =========================================================================
    # STEP 3: Analysis
    # =========================================================================
    print("\n" + "-"*70)
    print("  STEP 3: Analysis")
    print("-"*70)

    if not eval_file:
        print("ERROR: No evaluated file available for analysis")
        sys.exit(1)

    analyze(
        evaluated_file=eval_file,
        raw_file=raw_file,
        output_dir=output_dir,
    )

    # Find the generated file
    analysis_files = sorted(output_dir.glob("analysis_*.json"))
    if analysis_files:
        results["analysis_file"] = str(analysis_files[-1])
        analysis_file = analysis_files[-1]

    # =========================================================================
    # STEP 4: Report Generation
    # =========================================================================
    print("\n" + "-"*70)
    print("  STEP 4: Report Generation")
    print("-"*70)

    if not analysis_file:
        print("ERROR: No analysis file available for report")
        sys.exit(1)

    generate(
        analysis_file=analysis_file,
        output_dir=output_dir,
    )

    # Find the generated file
    report_files = sorted(output_dir.glob("report_*.md"))
    if report_files:
        results["report_file"] = str(report_files[-1])

    # =========================================================================
    # Summary
    # =========================================================================
    print("\n" + "="*70)
    print("  COMPARISON COMPLETE")
    print("="*70)
    print(f"\n  Generated files:")
    print(f"    Raw results:  {results['raw_file']}")
    print(f"    Evaluated:    {results['eval_file']}")
    print(f"    Analysis:     {results['analysis_file']}")
    print(f"    Report:       {results['report_file']}")
    print("\n  Review the report for recommendations!")
    print("="*70 + "\n")

    return results


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run API comparison testing suite",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Full comparison (all 10 resorts, all 7 query types)
  python -m scripts.api_comparison.run_comparison

  # Quick test (2 resorts, 3 queries)
  python -m scripts.api_comparison.run_comparison --quick

  # Dry run (see estimated costs)
  python -m scripts.api_comparison.run_comparison --dry-run

  # Resume from existing raw data
  python -m scripts.api_comparison.run_comparison --skip-collect --raw-file comparison_results/raw_results_*.json
        """,
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without executing",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick test mode (2 resorts, 3 queries, 3 results each)",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path(__file__).parent.parent.parent / "comparison_results",
        help="Output directory (default: comparison_results/)",
    )
    parser.add_argument(
        "--skip-collect",
        action="store_true",
        help="Skip collection step, use existing raw file",
    )
    parser.add_argument(
        "--skip-eval",
        action="store_true",
        help="Skip evaluation step, use existing eval file",
    )
    parser.add_argument(
        "--raw-file",
        type=Path,
        help="Path to existing raw_results_*.json",
    )
    parser.add_argument(
        "--eval-file",
        type=Path,
        help="Path to existing evaluated_results_*.json",
    )
    parser.add_argument(
        "--max-resorts",
        type=int,
        help="Limit number of resorts to test",
    )
    parser.add_argument(
        "--max-queries",
        type=int,
        help="Limit total number of queries",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=5,
        help="Results per API to evaluate (default: 5)",
    )

    args = parser.parse_args()

    asyncio.run(
        run_full_comparison(
            output_dir=args.output_dir,
            dry_run=args.dry_run,
            quick=args.quick,
            skip_collect=args.skip_collect,
            skip_eval=args.skip_eval,
            raw_file=args.raw_file,
            eval_file=args.eval_file,
            max_resorts=args.max_resorts,
            max_queries=args.max_queries,
            max_results_per_api=args.max_results,
        )
    )


if __name__ == "__main__":
    main()
