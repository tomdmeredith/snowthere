#!/usr/bin/env python
"""Quick check of Railway environment configuration.

Run this script to verify all required environment variables are set
and the Supabase connection works BEFORE running the full pipeline.

Usage:
    python railway_check.py

Exit codes:
    0 - All checks passed
    1 - One or more checks failed
"""

import os
import sys

# Load .env file if present (for local development)
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed, rely on system environment


def check_environment():
    """Check all required environment variables and connections."""
    print("=" * 60)
    print("RAILWAY ENVIRONMENT CHECK")
    print("=" * 60)
    print()

    errors = []
    warnings = []

    # Required environment variables
    required_vars = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_KEY",
        "ANTHROPIC_API_KEY",
    ]

    # Optional but important
    optional_vars = [
        "EXA_API_KEY",
        "BRAVE_API_KEY",
        "TAVILY_API_KEY",
    ]

    # Check required vars
    print("Checking required environment variables...")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Show partial value for verification (first 8 chars)
            masked = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ✗ {var}: NOT SET")
            errors.append(f"Missing required: {var}")
    print()

    # Check optional vars
    print("Checking optional environment variables...")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else value
            print(f"  ✓ {var}: {masked}")
        else:
            print(f"  ⚠ {var}: NOT SET (some features may be limited)")
            warnings.append(f"Missing optional: {var}")
    print()

    # If required vars are missing, stop here
    if errors:
        print("=" * 60)
        print("ENVIRONMENT CHECK FAILED")
        print("=" * 60)
        print()
        for error in errors:
            print(f"  ✗ {error}")
        print()
        print("Please set these environment variables in Railway dashboard:")
        print("  railway variables set VAR_NAME=value")
        return False

    # Test Supabase connection
    print("Testing Supabase connection...")
    try:
        # Import here so missing vars don't cause import errors
        from shared.supabase_client import get_supabase_client

        client = get_supabase_client()

        # Test read operation
        result = client.table("resorts").select("id, name, status").limit(5).execute()
        print(f"  ✓ Connection successful")
        print(f"  ✓ Found {len(result.data)} resorts in database")

        if result.data:
            print("    Sample resorts:")
            for resort in result.data[:3]:
                print(f"      - {resort.get('name', 'Unknown')} ({resort.get('status', 'unknown')})")

    except ValueError as e:
        print(f"  ✗ Configuration error: {e}")
        errors.append(f"Supabase config error: {e}")
    except ConnectionError as e:
        print(f"  ✗ Connection failed: {e}")
        errors.append(f"Supabase connection error: {e}")
    except Exception as e:
        print(f"  ✗ Unexpected error: {e}")
        errors.append(f"Supabase error: {e}")
    print()

    # Test Anthropic connection (optional - just check key format)
    print("Checking Anthropic API key format...")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if anthropic_key.startswith("sk-ant-"):
        print("  ✓ Anthropic API key format looks valid")
    else:
        print("  ⚠ Anthropic API key doesn't start with 'sk-ant-'")
        warnings.append("Anthropic key format unusual")
    print()

    # Check budget settings
    print("Checking budget configuration...")
    try:
        from shared.config import settings
        print(f"  ✓ Daily budget limit: ${settings.daily_budget_limit:.2f}")
    except Exception as e:
        print(f"  ⚠ Could not read settings: {e}")
        warnings.append(f"Settings error: {e}")
    print()

    # Summary
    print("=" * 60)
    if errors:
        print("CHECK FAILED")
        print("=" * 60)
        print()
        print("Errors:")
        for error in errors:
            print(f"  ✗ {error}")
        if warnings:
            print()
            print("Warnings:")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        return False
    else:
        print("ALL CHECKS PASSED")
        print("=" * 60)
        if warnings:
            print()
            print("Warnings (non-blocking):")
            for warning in warnings:
                print(f"  ⚠ {warning}")
        print()
        print("Environment is ready for pipeline execution.")
        print("Run: python cron.py --dry-run")
        return True


if __name__ == "__main__":
    # Need to be in agents directory for imports to work
    import pathlib
    script_dir = pathlib.Path(__file__).parent
    if script_dir.name == "agents":
        os.chdir(script_dir)

    success = check_environment()
    sys.exit(0 if success else 1)
