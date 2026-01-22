#!/usr/bin/env python
"""Quick verification of Railway environment configuration.

Run this script to verify all required environment variables are set
and that connections to external services work.

Usage:
    python railway_check.py          # Full check with connection tests
    python railway_check.py --quick  # Just check env vars, no connections

This is useful for:
- Debugging Railway deployment issues
- Verifying environment before running pipeline
- Quick health checks
"""

import os
import sys
import argparse


def check_env_vars() -> list[str]:
    """Check required environment variables are set.

    Returns:
        List of missing variable names
    """
    required = [
        ("SUPABASE_URL", "Database connection"),
        ("SUPABASE_SERVICE_KEY", "Database authentication"),
        ("ANTHROPIC_API_KEY", "Claude AI access"),
    ]

    optional = [
        ("EXA_API_KEY", "Semantic search"),
        ("BRAVE_API_KEY", "Web search"),
        ("TAVILY_API_KEY", "Web research"),
    ]

    missing_required = []

    print("=" * 60)
    print("ENVIRONMENT VARIABLE CHECK")
    print("=" * 60)

    print("\nRequired variables:")
    for var, purpose in required:
        value = os.getenv(var)
        if value:
            # Mask the value for security
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"  ✓ {var}: {masked} ({purpose})")
        else:
            print(f"  ✗ {var}: NOT SET ({purpose})")
            missing_required.append(var)

    print("\nOptional variables:")
    for var, purpose in optional:
        value = os.getenv(var)
        if value:
            masked = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
            print(f"  ✓ {var}: {masked} ({purpose})")
        else:
            print(f"  ⚠ {var}: NOT SET ({purpose}) - some features may not work")

    return missing_required


def test_supabase_connection() -> bool:
    """Test Supabase database connection.

    Returns:
        True if connection works
    """
    print("\n" + "=" * 60)
    print("SUPABASE CONNECTION TEST")
    print("=" * 60)

    try:
        from shared.supabase_client import get_supabase_client

        print("\nConnecting to Supabase...")
        client = get_supabase_client()

        # Test query
        print("Running test query (SELECT id FROM resorts LIMIT 1)...")
        result = client.table("resorts").select("id").limit(1).execute()

        print("  ✓ Connection successful")
        print(f"  ✓ Test query returned {len(result.data)} row(s)")

        # Get resort count
        count_result = client.table("resorts").select("id", count="exact").execute()
        print(f"  ✓ Total resorts in database: {count_result.count}")

        return True

    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        print("    Make sure you're running from the agents/ directory")
        return False
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        return False


def test_anthropic_connection() -> bool:
    """Test Anthropic API connection.

    Returns:
        True if connection works
    """
    print("\n" + "=" * 60)
    print("ANTHROPIC API TEST")
    print("=" * 60)

    try:
        from anthropic import Anthropic
        from shared.config import settings

        print("\nInitializing Anthropic client...")
        client = Anthropic(api_key=settings.anthropic_api_key)

        print("Sending test message (simple ping)...")
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=10,
            messages=[{"role": "user", "content": "Say 'OK' and nothing else."}]
        )

        reply = response.content[0].text if response.content else ""
        print(f"  ✓ API responding: '{reply.strip()}'")
        print(f"  ✓ Usage: {response.usage.input_tokens} in, {response.usage.output_tokens} out")

        return True

    except ImportError as e:
        print(f"  ✗ Import error: {e}")
        return False
    except Exception as e:
        print(f"  ✗ API call failed: {e}")
        return False


def test_research_apis() -> dict[str, bool]:
    """Test research API connections (optional).

    Returns:
        Dict mapping API name to success boolean
    """
    print("\n" + "=" * 60)
    print("RESEARCH APIS TEST (Optional)")
    print("=" * 60)

    results = {}

    # Exa
    exa_key = os.getenv("EXA_API_KEY")
    if exa_key:
        try:
            import httpx
            print("\nTesting Exa API...")
            response = httpx.post(
                "https://api.exa.ai/search",
                headers={"x-api-key": exa_key},
                json={"query": "test", "numResults": 1},
                timeout=10.0,
            )
            if response.status_code == 200:
                print("  ✓ Exa API working")
                results["exa"] = True
            else:
                print(f"  ✗ Exa API returned {response.status_code}")
                results["exa"] = False
        except Exception as e:
            print(f"  ✗ Exa API error: {e}")
            results["exa"] = False
    else:
        print("\n  ⚠ Exa API: Skipped (no key)")
        results["exa"] = None

    # Brave
    brave_key = os.getenv("BRAVE_API_KEY")
    if brave_key:
        try:
            import httpx
            print("\nTesting Brave API...")
            response = httpx.get(
                "https://api.search.brave.com/res/v1/web/search",
                headers={"X-Subscription-Token": brave_key},
                params={"q": "test"},
                timeout=10.0,
            )
            if response.status_code == 200:
                print("  ✓ Brave API working")
                results["brave"] = True
            else:
                print(f"  ✗ Brave API returned {response.status_code}")
                results["brave"] = False
        except Exception as e:
            print(f"  ✗ Brave API error: {e}")
            results["brave"] = False
    else:
        print("\n  ⚠ Brave API: Skipped (no key)")
        results["brave"] = None

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Verify Railway environment configuration"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode: only check env vars, skip connection tests"
    )
    parser.add_argument(
        "--skip-anthropic",
        action="store_true",
        help="Skip Anthropic API test (to avoid API costs)"
    )
    args = parser.parse_args()

    print("\n" + "=" * 60)
    print("RAILWAY ENVIRONMENT VERIFICATION")
    print("=" * 60)
    print(f"Mode: {'Quick (env vars only)' if args.quick else 'Full (with connection tests)'}")

    # Step 1: Check environment variables
    missing = check_env_vars()

    if missing:
        print("\n" + "=" * 60)
        print("❌ REQUIRED VARIABLES MISSING")
        print("=" * 60)
        for var in missing:
            print(f"  - {var}")
        print("\nSet these variables in Railway dashboard or .env file.")
        sys.exit(1)

    if args.quick:
        print("\n" + "=" * 60)
        print("✓ QUICK CHECK PASSED")
        print("=" * 60)
        print("All required environment variables are set.")
        print("Run without --quick to test actual connections.")
        sys.exit(0)

    # Step 2: Test Supabase connection
    supabase_ok = test_supabase_connection()

    # Step 3: Test Anthropic connection (optional)
    if args.skip_anthropic:
        print("\n⚠ Skipping Anthropic API test (--skip-anthropic)")
        anthropic_ok = True
    else:
        anthropic_ok = test_anthropic_connection()

    # Step 4: Test research APIs
    research_results = test_research_apis()

    # Summary
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    all_critical_ok = supabase_ok and anthropic_ok

    print("\nCritical services:")
    print(f"  Supabase:   {'✓ OK' if supabase_ok else '✗ FAILED'}")
    print(f"  Anthropic:  {'✓ OK' if anthropic_ok else '✗ FAILED'}")

    print("\nResearch APIs (optional):")
    for api, status in research_results.items():
        if status is None:
            print(f"  {api.capitalize()}:  ⚠ Not configured")
        elif status:
            print(f"  {api.capitalize()}:  ✓ OK")
        else:
            print(f"  {api.capitalize()}:  ✗ FAILED")

    if all_critical_ok:
        print("\n" + "=" * 60)
        print("✓ ALL CRITICAL CHECKS PASSED")
        print("=" * 60)
        print("The pipeline should be able to run.")
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("❌ CRITICAL CHECKS FAILED")
        print("=" * 60)
        print("Fix the issues above before running the pipeline.")
        sys.exit(1)


if __name__ == "__main__":
    main()
