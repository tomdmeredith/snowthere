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
import asyncio
import json
import sys
from datetime import datetime

from pipeline import run_daily_pipeline, run_single_resort
from pipeline.guide_orchestrator import run_guide_generation


async def run_email_sequences() -> dict:
    """Run email sequence advancement for all due subscribers.

    Returns a dict with results suitable for logging.
    """
    from shared.primitives.email import advance_sequences

    print("Advancing email sequences...")
    try:
        result = await advance_sequences()
        if result.success:
            print(f"✓ Email sequences: {result.message}")
        else:
            print(f"⚠️  Email sequences: {result.message}")
            if result.errors:
                for error in result.errors[:5]:  # Show first 5 errors
                    print(f"    - {error}")
        return {
            "success": result.success,
            "emails_sent": result.emails_sent,
            "errors": result.errors,
        }
    except Exception as e:
        print(f"❌ Email sequences failed: {e}")
        return {
            "success": False,
            "emails_sent": 0,
            "errors": [str(e)],
        }


async def run_weekly_newsletter() -> dict:
    """Run weekly newsletter generation and sending if due.

    Runs on Thursdays at 6am PT. Generates content from:
    - New resort guides published this week
    - Trending discovery candidates
    - Parent hack of the week
    - Community photo
    - Referral CTA

    Returns a dict with results suitable for logging.
    """
    from shared.primitives.newsletter import (
        check_newsletter_due,
        generate_newsletter,
        send_newsletter,
    )

    print("Checking if newsletter is due...")

    try:
        if not check_newsletter_due():
            print("  Newsletter not due today")
            return {
                "success": True,
                "status": "not_due",
                "message": "Newsletter not due today",
            }

        print("  Newsletter is due! Generating...")

        # Generate newsletter content
        gen_result = await generate_newsletter()

        if not gen_result.success:
            print(f"❌ Newsletter generation failed: {gen_result.error}")
            return {
                "success": False,
                "status": "generation_failed",
                "error": gen_result.error,
            }

        print(f"✓ Newsletter #{gen_result.issue_number} generated")
        print(f"  Subject: {gen_result.content.subject if gen_result.content else 'N/A'}")

        # Send the newsletter
        print("  Sending to subscribers...")
        send_result = await send_newsletter(gen_result.issue_id)

        if send_result.success:
            print(f"✓ Newsletter sent: {send_result.emails_sent}/{send_result.recipients_count} emails")
        else:
            print(f"⚠️  Newsletter send had issues: {send_result.message}")
            if send_result.errors:
                for error in send_result.errors[:5]:
                    print(f"    - {error}")

        return {
            "success": send_result.success,
            "status": "sent" if send_result.success else "send_failed",
            "issue_number": gen_result.issue_number,
            "issue_id": gen_result.issue_id,
            "emails_sent": send_result.emails_sent,
            "recipients_count": send_result.recipients_count,
            "errors": send_result.errors,
        }

    except Exception as e:
        print(f"❌ Newsletter failed: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
        }


def validate_environment():
    """Validate all required environment variables and connections.

    This runs BEFORE any pipeline work to fail fast on configuration issues.
    Previously, the pipeline would run (incurring API costs) then fail silently
    when trying to save to Supabase.
    """
    from shared.config import settings
    from shared.supabase_client import get_supabase_client
    from shared.primitives.alerts import alert_startup_failure

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
        # Send Slack alert before exiting
        alert_startup_failure(errors)
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
        alert_startup_failure([f"Configuration error: {e}"])
        sys.exit(1)
    except ConnectionError as e:
        print(f"❌ Supabase connection failed: {e}")
        alert_startup_failure([f"Supabase connection failed: {e}"])
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error connecting to Supabase: {e}")
        alert_startup_failure([f"Unexpected Supabase error: {e}"])
        sys.exit(1)

    print("✓ Environment validation passed\n")


def main():
    # Validate environment FIRST - fail fast before incurring API costs
    validate_environment()

    # Run email sequences (independent of content pipeline)
    # This advances subscribers through welcome sequences, sends due emails
    email_result = asyncio.run(run_email_sequences())

    # Run weekly newsletter (Thursdays at 6am PT)
    # Generates and sends Morning Brew-style digest to all subscribers
    newsletter_result = asyncio.run(run_weekly_newsletter())

    # Run guide generation (Monday and Thursday)
    # Produces 2 guides/week through autonomous discovery and 3-agent approval
    guide_result = asyncio.run(run_guide_generation())

    parser = argparse.ArgumentParser(
        description="Snowthere autonomous content generation pipeline"
    )

    parser.add_argument(
        "--max-resorts",
        type=int,
        default=8,
        help="Maximum resorts to process (default: 8)",
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

        result = asyncio.run(run_single_resort(
            resort_name=args.resort,
            country=args.country,
            auto_publish=not args.no_publish,
        ))

    else:
        # Daily pipeline mode
        selection_mode = "mixed" if args.use_mixed_selection else "claude"
        discovery_mode = "enabled" if args.run_discovery else "disabled"

        print(f"\n{'='*60}")
        print(f"DAILY PIPELINE - {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')}")
        print(f"Max resorts: {args.max_resorts} | Dry run: {args.dry_run}")
        print(f"Selection: {selection_mode} | Discovery: {discovery_mode}")
        print(f"{'='*60}\n")

        result = asyncio.run(run_daily_pipeline(
            max_resorts=args.max_resorts,
            dry_run=args.dry_run,
            use_mixed_selection=args.use_mixed_selection,
            run_discovery=args.run_discovery,
            force_discovery=args.force_discovery,
        ))

    # Add email, newsletter, and guide results to output
    result["email_sequences"] = email_result
    result["weekly_newsletter"] = newsletter_result
    result["guide_generation"] = guide_result

    # Output results
    if args.json:
        print(json.dumps(result, indent=2, default=str))
    else:
        print_human_readable(result, single_resort=bool(args.resort), email_result=email_result)

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


def print_human_readable(result: dict, single_resort: bool = False, email_result: dict | None = None):
    """Print results in a human-readable format."""
    print(f"\n{'='*60}")
    print("RESULTS")
    print(f"{'='*60}\n")

    # Email sequences
    if email_result:
        emails_sent = email_result.get("emails_sent", 0)
        if emails_sent > 0:
            print(f"Email Sequences: {emails_sent} email(s) sent")
        else:
            print("Email Sequences: No emails due")
        if email_result.get("errors"):
            print(f"  Errors: {len(email_result['errors'])}")
        print()

    # Weekly newsletter
    newsletter_result = result.get("weekly_newsletter")
    if newsletter_result:
        status = newsletter_result.get("status", "unknown")
        if status == "sent":
            issue_num = newsletter_result.get("issue_number", "?")
            emails = newsletter_result.get("emails_sent", 0)
            print(f"Weekly Newsletter: #{issue_num} sent to {emails} subscribers")
        elif status == "not_due":
            print("Weekly Newsletter: Not due today")
        else:
            print(f"Weekly Newsletter: {status}")
        print()

    # Guide generation
    guide_result = result.get("guide_generation")
    if guide_result:
        status = guide_result.get("status", "unknown")
        if status == "completed":
            published = guide_result.get("published", 0)
            drafts = guide_result.get("drafts", 0)
            failed = guide_result.get("failed", 0)
            print(f"Guide Generation: {published} published, {drafts} drafts, {failed} failed")
            guides = guide_result.get("guides", [])
            for g in guides:
                status_emoji = {"published": "✓", "draft": "○", "failed": "✗"}.get(g.get("status"), "?")
                conf = g.get("confidence", 0)
                conf_str = f" ({conf:.2f})" if conf else ""
                print(f"  {status_emoji} {g.get('title', 'Unknown')}{conf_str}")
        elif status == "not_scheduled":
            print(f"Guide Generation: {guide_result.get('message', 'Not scheduled')}")
        else:
            print(f"Guide Generation: {status}")
        print()

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
