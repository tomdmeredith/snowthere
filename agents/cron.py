#!/usr/bin/env python
"""Railway cron entry point for daily content generation.

This is the file Railway calls on schedule.

Usage:
    # Full daily pipeline (default: up to 4 resorts, Claude-based selection)
    python cron.py

    # Custom max resorts
    python cron.py --max-resorts 2

    # Dry run (see what would happen without doing it)
    python cron.py --dry-run

    # Single resort (manual trigger)
    python cron.py --resort "Zermatt" --country "Switzerland"

    # Use mixed selection (discovery + stale + queue) instead of Claude
    python cron.py --use-mixed-selection

    # Run discovery before selection (finds new resort opportunities)
    python cron.py --run-discovery

    # Force discovery even if ran recently
    python cron.py --run-discovery --force-discovery

    # Full autonomous mode: discovery + mixed selection
    python cron.py --run-discovery --use-mixed-selection

Railway Configuration:
    In railway.toml or dashboard:
    - Command: python cron.py --run-discovery --use-mixed-selection
    - Schedule: 0 8 * * * (8am UTC daily)

Environment Variables Required:
    SUPABASE_URL
    SUPABASE_SERVICE_KEY
    ANTHROPIC_API_KEY
    EXA_API_KEY
    SERPAPI_API_KEY
    TAVILY_API_KEY
"""

import argparse
import json
import sys
from datetime import datetime

from pipeline import run_daily_pipeline, run_single_resort


def validate_environment():
    """Validate all required environment variables and connections.

    This runs BEFORE any pipeline work to fail fast on configuration issues.
    Previously, the pipeline would run (incurring API costs) then fail silently
    when trying to save to Supabase.
    """
    from shared.config import settings
    from shared.supabase_client import get_supabase_client

    print("Validating environment...")
    errors = []

    # Check required env vars
    required_vars = [
        ("SUPABASE_URL", settings.supabase_url),
        ("SUPABASE_SERVICE_KEY", settings.supabase_service_key),
        ("ANTHROPIC_API_KEY", settings.anthropic_api_key),
    ]

    # Check optional but important vars
    optional_vars = [
        ("EXA_API_KEY", settings.exa_api_key),
        ("BRAVE_API_KEY", getattr(settings, "brave_api_key", None)),
        ("TAVILY_API_KEY", settings.tavily_api_key),
    ]

    for name, value in required_vars:
        if not value:
            errors.append(f"Missing required env var: {name}")

    if errors:
        print("❌ STARTUP VALIDATION FAILED:")
        for e in errors:
            print(f"  - {e}")
        sys.exit(1)

    # Warn about missing optional vars
    for name, value in optional_vars:
        if not value:
            print(f"⚠️  Warning: {name} not set (some research features may be limited)")

    # Test Supabase connection
    try:
        client = get_supabase_client()
        # Connection test is built into get_supabase_client now
        print("✓ Supabase connection verified")
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    except ConnectionError as e:
        print(f"❌ Supabase connection failed: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error connecting to Supabase: {e}")
        sys.exit(1)

    print("✓ Environment validation passed\n")


def main():
    # Validate environment FIRST - fail fast before incurring API costs
    validate_environment()

    parser = argparse.ArgumentParser(
        description="Snowthere autonomous content generation pipeline"
    )

    parser.add_argument(
        "--max-resorts",
        type=int,
        default=4,
        help="Maximum resorts to process (default: 4)",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Log what would happen without executing",
    )

    parser.add_argument(
        "--resort",
        type=str,
        help="Process a single specific resort",
    )

    parser.add_argument(
        "--country",
        type=str,
        help="Country for single resort (required with --resort)",
    )

    parser.add_argument(
        "--no-publish",
        action="store_true",
        help="Skip auto-publishing (save as drafts)",
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )

    parser.add_argument(
        "--use-mixed-selection",
        action="store_true",
        help="Use balanced selection from multiple sources (discovery, stale, queue) instead of Claude-based selection",
    )

    parser.add_argument(
        "--run-discovery",
        action="store_true",
        help="Run discovery agent before selection to find new resort opportunities",
    )

    parser.add_argument(
        "--force-discovery",
        action="store_true",
        help="Force discovery run even if it ran recently (requires --run-discovery)",
    )

    args = parser.parse_args()

    # Validate args
    if args.resort and not args.country:
        parser.error("--country is required when using --resort")

    # Run appropriate mode
    if args.resort:
        # Single resort mode
        print(f"\n{'='*60}")
        print(f"SINGLE RESORT MODE: {args.resort}, {args.country}")
        print(f"{'='*60}\n")

        result = run_single_resort(
            resort_name=args.resort,
            country=args.country,
            auto_publish=not args.no_publish,
        )

    else:
        # Daily pipeline mode
        selection_mode = "mixed" if args.use_mixed_selection else "claude"
        discovery_mode = "enabled" if args.run_discovery else "disabled"

        print(f"\n{'='*60}")
        print(f"DAILY PIPELINE - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Max resorts: {args.max_resorts} | Dry run: {args.dry_run}")
        print(f"Selection: {selection_mode} | Discovery: {discovery_mode}")
        print(f"{'='*60}\n")

        result = run_daily_pipeline(
            max_resorts=args.max_resorts,
            dry_run=args.dry_run,
            use_mixed_selection=args.use_mixed_selection,
            run_discovery=args.run_discovery,
            force_discovery=args.force_discovery,
        )

    # Output results
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_human_readable(result, single_resort=bool(args.resort))

    # Exit with appropriate code
    status = result.get("status", "unknown")
    success_statuses = ("completed", "published", "draft", "dry_run_complete")
    partial_statuses = ("partial_failure",)  # Some succeeded
    failure_statuses = ("all_failed", "failed", "error", "no_content")

    if status in success_statuses:
        sys.exit(0)
    elif status in partial_statuses:
        # Some succeeded, some failed - exit 0 but log warning
        print("⚠️  Pipeline completed with some failures")
        sys.exit(0)
    else:
        # All failed or unknown status
        print(f"❌ Pipeline failed with status: {status}")
        sys.exit(1)


def print_human_readable(result: dict, single_resort: bool = False):
    """Print results in a human-readable format."""
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}\n")

    print(f"Status: {result.get('status', 'unknown').upper()}")

    if single_resort:
        # Single resort output
        print(f"Confidence: {result.get('confidence', 'N/A')}")
        print(f"Resort ID: {result.get('resort_id', 'N/A')}")

        if result.get("stages"):
            print("\nStages:")
            for stage, info in result["stages"].items():
                status = info if isinstance(info, str) else info.get("status", "unknown")
                print(f"  - {stage}: {status}")

        if result.get("error"):
            print(f"\nError: {result['error']}")

    else:
        # Daily pipeline output
        summary = result.get("summary", {})

        print(f"Duration: {summary.get('duration', 'N/A')}")
        print(f"Daily Spend: {summary.get('daily_spend', 'N/A')}")
        print(f"Selection Method: {summary.get('selection_method', 'N/A')}")

        # Show discovery result if available
        discovery_result = result.get("discovery_result")
        if discovery_result:
            if discovery_result.get("skipped"):
                print(f"Discovery: Skipped - {discovery_result.get('reason', 'N/A')}")
            elif discovery_result.get("error"):
                print(f"Discovery: Error - {discovery_result.get('reason', 'N/A')}")
            else:
                print(f"Discovery: Found {discovery_result.get('candidates_saved', 0)} new candidates")

        print(f"\nSelection Reasoning: {summary.get('selection_reasoning', 'N/A')}")

        # Show source breakdown if available
        source_breakdown = summary.get("source_breakdown", {})
        if source_breakdown:
            print("\nSource Breakdown:")
            for source, count in source_breakdown.items():
                print(f"  - {source}: {count}")

        print(f"\nResults:")
        print(f"  Published: {summary.get('published', 0)}")
        print(f"  Drafts: {summary.get('drafts', 0)}")
        print(f"  Failed: {summary.get('failed', 0)}")

        if result.get("resorts_processed"):
            print("\nResorts Processed:")
            for resort in result["resorts_processed"]:
                status_emoji = {
                    "published": "✓",
                    "draft": "○",
                    "failed": "✗",
                    "error": "✗",
                }.get(resort.get("status"), "?")

                confidence = resort.get("confidence")
                conf_str = f" ({confidence:.2f})" if confidence else ""

                source = resort.get("source", "")
                source_str = f" [{source}]" if source else ""

                print(f"  {status_emoji} {resort['resort']}, {resort['country']}{conf_str}{source_str}")

    print(f"\n{'='*60}\n")


if __name__ == "__main__":
    main()
