#!/usr/bin/env python3
"""
Load email templates into Supabase production database.

This script:
1. Seeds the email_templates, email_sequences, and email_sequence_steps tables
2. Updates body_html with the actual HTML content from template files

Usage:
    cd agents && python scripts/load_email_templates.py
    cd agents && python scripts/load_email_templates.py --dry-run
"""

import argparse
import os
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client


# Template file mappings: template_name -> file_path
TEMPLATE_FILES = {
    "welcome_checklist": "templates/welcome_checklist.html",
    "welcome_day2": "templates/welcome_day2.html",
    "welcome_day4": "templates/welcome_day4.html",
    "welcome_day7": "templates/welcome_day7.html",
    "welcome_day14": "templates/welcome_day14.html",
}

# Template metadata for seeding
TEMPLATES = [
    {
        "name": "welcome_checklist",
        "subject": "Your Family Ski Trip Checklist",
        "preview_text": "Everything you need for your first family ski trip",
        "body_text": "Welcome to Snowthere! Here is your family ski trip checklist...",
        "category": "sequence",
        "variables": ["name", "email"],
    },
    {
        "name": "welcome_day2",
        "subject": "Wait... the Alps can be CHEAPER than Colorado?",
        "preview_text": "I know it sounds backwards",
        "body_text": "I know it sounds backwards. Fly across the ocean to SAVE money? But stick with me here...",
        "category": "sequence",
        "variables": ["name", "email"],
    },
    {
        "name": "welcome_day4",
        "subject": "Your kids' ages change EVERYTHING",
        "preview_text": "I see parents make this mistake all the time",
        "body_text": "I see parents make this mistake all the time...",
        "category": "sequence",
        "variables": ["name", "email"],
    },
    {
        "name": "welcome_day7",
        "subject": "Epic vs Ikon: Let's end the confusion",
        "preview_text": "Should we get the Epic Pass or Ikon Pass?",
        "body_text": "Should we get the Epic Pass or Ikon Pass? Here is the honest answer...",
        "category": "sequence",
        "variables": ["name", "email"],
    },
    {
        "name": "welcome_day14",
        "subject": "Ready to pick your resort?",
        "preview_text": "Two weeks ago, you signed up for the checklist",
        "body_text": "Two weeks ago, you signed up for the checklist. Now let us put it all together...",
        "category": "sequence",
        "variables": ["name", "email"],
    },
]

# Sequence steps: (step_number, template_name, delay_days)
SEQUENCE_STEPS = [
    (1, "welcome_checklist", 0),  # Day 0: Immediate
    (2, "welcome_day2", 2),       # Day 2: +2 days
    (3, "welcome_day4", 2),       # Day 4: +2 days
    (4, "welcome_day7", 3),       # Day 7: +3 days
    (5, "welcome_day14", 7),      # Day 14: +7 days
]


def load_html_template(template_name: str) -> str | None:
    """Load HTML content from template file."""
    agents_dir = Path(__file__).parent.parent
    file_path = agents_dir / TEMPLATE_FILES.get(template_name, "")

    if not file_path.exists():
        print(f"  WARNING: Template file not found: {file_path}")
        return None

    return file_path.read_text(encoding="utf-8")


def seed_templates(client, dry_run: bool = False) -> dict[str, str]:
    """Seed email templates and return mapping of name -> id."""
    print("\n1. Seeding email templates...")
    template_ids = {}

    for template in TEMPLATES:
        # Load HTML content from file
        html_content = load_html_template(template["name"])
        if html_content is None:
            html_content = f"<p>Template content for {template['name']} not found.</p>"

        data = {
            "name": template["name"],
            "subject": template["subject"],
            "preview_text": template["preview_text"],
            "body_html": html_content,
            "body_text": template["body_text"],
            "category": template["category"],
            "variables": template["variables"],
        }

        if dry_run:
            print(f"  [DRY-RUN] Would upsert template: {template['name']}")
            print(f"            Subject: {template['subject']}")
            print(f"            HTML length: {len(html_content)} chars")
            template_ids[template["name"]] = "dry-run-id"
        else:
            # Upsert template
            result = client.table("email_templates").upsert(
                data,
                on_conflict="name"
            ).execute()

            if result.data:
                template_ids[template["name"]] = result.data[0]["id"]
                print(f"  OK: {template['name']} (HTML: {len(html_content)} chars)")
            else:
                print(f"  ERROR: Failed to upsert {template['name']}")

    return template_ids


def seed_sequence(client, dry_run: bool = False) -> str | None:
    """Seed the welcome email sequence and return its ID."""
    print("\n2. Seeding welcome sequence...")

    data = {
        "name": "welcome",
        "trigger_event": "on_subscribe",
        "trigger_conditions": {},
        "status": "active",
    }

    if dry_run:
        print("  [DRY-RUN] Would upsert sequence: welcome")
        return "dry-run-sequence-id"

    result = client.table("email_sequences").upsert(
        data,
        on_conflict="name"
    ).execute()

    if result.data:
        sequence_id = result.data[0]["id"]
        print(f"  OK: welcome sequence (id: {sequence_id[:8]}...)")
        return sequence_id
    else:
        print("  ERROR: Failed to upsert sequence")
        return None


def seed_sequence_steps(client, sequence_id: str, template_ids: dict[str, str], dry_run: bool = False):
    """Seed the sequence steps linking sequence to templates."""
    print("\n3. Seeding sequence steps...")

    for step_number, template_name, delay_days in SEQUENCE_STEPS:
        template_id = template_ids.get(template_name)
        if not template_id:
            print(f"  SKIP: Step {step_number} - template '{template_name}' not found")
            continue

        data = {
            "sequence_id": sequence_id,
            "step_number": step_number,
            "template_id": template_id,
            "delay_days": delay_days,
        }

        if dry_run:
            print(f"  [DRY-RUN] Step {step_number}: {template_name} (delay: {delay_days} days)")
        else:
            # Delete existing step first to avoid conflict issues
            client.table("email_sequence_steps").delete().eq(
                "sequence_id", sequence_id
            ).eq("step_number", step_number).execute()

            # Insert new step
            result = client.table("email_sequence_steps").insert(data).execute()

            if result.data:
                print(f"  OK: Step {step_number}: {template_name} (delay: {delay_days} days)")
            else:
                print(f"  ERROR: Failed to insert step {step_number}")


def verify_setup(client, dry_run: bool = False):
    """Verify the email system is properly configured."""
    print("\n4. Verification...")

    if dry_run:
        print("  [DRY-RUN] Skipping verification")
        return

    # Check templates
    templates = client.table("email_templates").select("name, subject").like("name", "welcome%").execute()
    print(f"  Templates: {len(templates.data)} welcome templates found")

    # Check sequence
    sequences = client.table("email_sequences").select("name, status").eq("name", "welcome").execute()
    if sequences.data:
        print(f"  Sequence: {sequences.data[0]['name']} ({sequences.data[0]['status']})")

    # Check steps
    steps = client.table("email_sequence_steps").select(
        "step_number, delay_days, template_id"
    ).order("step_number").execute()
    print(f"  Steps: {len(steps.data)} steps configured")

    # Verify HTML content is real (not placeholder)
    sample = client.table("email_templates").select("name, body_html").eq("name", "welcome_checklist").execute()
    if sample.data:
        html = sample.data[0].get("body_html", "")
        if "<!DOCTYPE html>" in html or len(html) > 500:
            print("  HTML: Real template content loaded!")
        else:
            print(f"  WARNING: HTML appears to be placeholder ({len(html)} chars)")


def main():
    parser = argparse.ArgumentParser(description="Load email templates into Supabase")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done without making changes")
    args = parser.parse_args()

    print("=" * 60)
    print("Email Template Loader")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***\n")

    # Get Supabase client
    print("Connecting to Supabase...")
    client = get_supabase_client()

    # Check connection
    try:
        test = client.table("email_templates").select("count").limit(1).execute()
        print("  Connected to Supabase")
    except Exception as e:
        print(f"  ERROR: Failed to connect to Supabase: {e}")
        sys.exit(1)

    # Seed everything
    template_ids = seed_templates(client, args.dry_run)
    sequence_id = seed_sequence(client, args.dry_run)

    if sequence_id and template_ids:
        seed_sequence_steps(client, sequence_id, template_ids, args.dry_run)

    # Verify
    verify_setup(client, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply changes")
    else:
        print("DONE - Email templates loaded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
