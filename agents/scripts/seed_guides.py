#!/usr/bin/env python3
"""
Seed initial guides into Supabase production database.

This script creates starter guides with comprehensive content for the /guides section.

Usage:
    cd agents && python scripts/seed_guides.py
    cd agents && python scripts/seed_guides.py --dry-run
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime, timezone

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from shared.supabase_client import get_supabase_client


# =============================================================================
# GUIDE CONTENT
# =============================================================================

GUIDES = [
    {
        "slug": "family-ski-trip-checklist",
        "title": "The Ultimate Family Ski Trip Checklist",
        "guide_type": "how-to",
        "category": "packing",
        "excerpt": "Everything you need to pack for a stress-free family ski vacation, organized by timeline and age group.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>Planning a family ski trip can feel overwhelming, especially if it's your first time hitting the slopes with kids. The key to a stress-free vacation? <strong>Starting early and staying organized.</strong></p><p>This checklist covers everything from booking essentials to last-minute packing, broken down by timeline so nothing falls through the cracks.</p>"
                },
                {
                    "type": "checklist",
                    "title": "2-4 Weeks Before",
                    "items": [
                        {"text": "Book ski lessons for kids (they fill up fast!)"},
                        {"text": "Reserve childcare if needed"},
                        {"text": "Check passport expiration dates (6+ months validity)"},
                        {"text": "Book airport transfers or rental car"},
                        {"text": "Purchase travel insurance"},
                        {"text": "Start breaking in new ski boots"},
                        {"text": "Check lift ticket pricing and multi-day discounts"},
                        {"text": "Research kids-ski-free policies"}
                    ]
                },
                {
                    "type": "checklist",
                    "title": "1 Week Before",
                    "items": [
                        {"text": "Check weather forecast and pack accordingly"},
                        {"text": "Download resort trail maps"},
                        {"text": "Confirm all reservations (hotels, lessons, rentals)"},
                        {"text": "Charge all devices and download entertainment for kids"},
                        {"text": "Print boarding passes and hotel confirmations"},
                        {"text": "Prepare snacks for travel day"},
                        {"text": "Do a helmet fit check for kids"}
                    ]
                },
                {
                    "type": "checklist",
                    "title": "Packing Essentials - Adults",
                    "items": [
                        {"text": "Ski jacket (waterproof, breathable)"},
                        {"text": "Ski pants or bibs"},
                        {"text": "Base layers (moisture-wicking)"},
                        {"text": "Mid layers (fleece or down)"},
                        {"text": "Ski socks (bring extras!)"},
                        {"text": "Gloves + backup pair"},
                        {"text": "Helmet"},
                        {"text": "Goggles"},
                        {"text": "Neck gaiter or balaclava"},
                        {"text": "Sunscreen (SPF 50+)"},
                        {"text": "Lip balm with SPF"},
                        {"text": "Hand and toe warmers"}
                    ]
                },
                {
                    "type": "checklist",
                    "title": "Packing Essentials - Kids",
                    "items": [
                        {"text": "Ski jacket (slightly oversized for layering)"},
                        {"text": "Ski pants or snow bibs"},
                        {"text": "Multiple base layers"},
                        {"text": "Warm mid layers"},
                        {"text": "Ski socks (pack 3+ pairs)"},
                        {"text": "Mittens (warmer than gloves for little ones)"},
                        {"text": "Spare mittens (trust us)"},
                        {"text": "Helmet (properly fitted)"},
                        {"text": "Goggles (kid-sized)"},
                        {"text": "Neck warmer"},
                        {"text": "Favorite snacks for chairlift"},
                        {"text": "Small backpack for carrying their gear"},
                        {"text": "Hand warmers"}
                    ]
                },
                {
                    "type": "text",
                    "title": "Pro Tips",
                    "content": "<ul><li><strong>Label everything</strong> - Kids lose gear constantly. Put names on helmets, gloves, and jackets.</li><li><strong>Rent locally</strong> - Kids' equipment changes every year. Renting at the resort saves luggage fees and hassle.</li><li><strong>Pack a \"survival bag\"</strong> - Keep snacks, hand warmers, tissues, and sunscreen in a small bag you carry on the mountain.</li><li><strong>Arrive a day early</strong> - Give everyone time to adjust to altitude and time zones before hitting the slopes.</li></ul>"
                },
                {
                    "type": "faq",
                    "title": "Common Questions",
                    "items": [
                        {
                            "question": "Should I buy or rent ski equipment for kids?",
                            "answer": "Rent for kids under 10 unless you ski 10+ days per season. They outgrow equipment quickly, and rental shops have the latest safety gear."
                        },
                        {
                            "question": "How early should I book ski lessons?",
                            "answer": "Book 2-4 weeks ahead for regular lessons, 6-8 weeks for holiday periods. Popular instructors and time slots fill up fast."
                        },
                        {
                            "question": "What if my kid doesn't like skiing?",
                            "answer": "Most resorts offer snowshoeing, tubing, and indoor activities. Don't force it - some kids need a few trips before they love it."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "Family Ski Trip Checklist - What to Pack | Snowthere",
            "description": "Complete family ski trip packing checklist with timelines, gear lists for adults and kids, and pro tips for a stress-free vacation."
        }
    },
    {
        "slug": "best-resorts-for-toddlers",
        "title": "Best Ski Resorts for Toddlers (Ages 2-5)",
        "guide_type": "comparison",
        "category": "toddlers",
        "excerpt": "Finding the right resort for your littlest skiers makes all the difference. These resorts excel at childcare, beginner terrain, and keeping toddlers happy.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>Skiing with toddlers is a different game entirely. You need excellent childcare, gentle terrain, short lift lines, and activities for when (not if) they hit their limit.</p><p>We've evaluated resorts based on <strong>childcare quality, beginner terrain, family amenities, and overall convenience</strong> for families with kids under 5.</p>"
                },
                {
                    "type": "text",
                    "title": "What Toddlers Need in a Ski Resort",
                    "content": "<p>Before looking at specific resorts, here's what matters most for families with toddlers:</p><ul><li><strong>Quality childcare</strong> that accepts ages 2-3 (many only take 4+)</li><li><strong>Magic carpets</strong> instead of chairlifts for beginners</li><li><strong>Ski school</strong> that starts at age 3 (some start at 2.5!)</li><li><strong>Short distances</strong> between lodging, lifts, and childcare</li><li><strong>Indoor backup activities</strong> for bad weather or meltdowns</li></ul>"
                },
                {
                    "type": "list",
                    "title": "Top 5 Resorts for Toddlers",
                    "items": [
                        {
                            "name": "Deer Valley, Utah",
                            "description": "Gold-standard childcare accepting infants from 2 months. Dedicated beginner area with magic carpet. Ski school from age 3. No snowboarders means calmer slopes.",
                            "resort_slug": "united-states/deer-valley"
                        },
                        {
                            "name": "Keystone, Colorado",
                            "description": "Excellent ski school (Kidtopia) from age 3. Kids ski free with adult lift ticket. Gondola access to beginner terrain. Snow fort and activities village.",
                            "resort_slug": "united-states/keystone"
                        },
                        {
                            "name": "Smugglers' Notch, Vermont",
                            "description": "Consistently rated #1 for families. Childcare from 6 weeks. Ski school from 2.5 years. Dedicated kids-only terrain. Slope-side lodging.",
                            "resort_slug": "united-states/smugglers-notch"
                        },
                        {
                            "name": "Serfaus-Fiss-Ladis, Austria",
                            "description": "Purpose-built for families. Car-free village with underground train. Bertas Kinderland has magic carpets, mascots, and heated rest areas.",
                            "resort_slug": "austria/serfaus-fiss-ladis"
                        },
                        {
                            "name": "Les Gets, France",
                            "description": "Charming Alpine village at lower altitude (better for little lungs). Village Igloo childcare from 6 months. Gentle slopes and beginner areas throughout.",
                            "resort_slug": "france/les-gets"
                        }
                    ]
                },
                {
                    "type": "comparison_table",
                    "title": "Quick Comparison",
                    "columns": ["Resort", "Min Childcare Age", "Min Ski School Age", "Kids Ski Free?", "Magic Carpet"],
                    "rows": [
                        ["Deer Valley", "2 months", "3 years", "No", "Yes"],
                        ["Keystone", "2 months", "3 years", "Yes (12 & under)", "Yes"],
                        ["Smugglers' Notch", "6 weeks", "2.5 years", "No", "Yes"],
                        ["Serfaus-Fiss-Ladis", "3 months", "3 years", "Under 6", "Yes"],
                        ["Les Gets", "6 months", "3 years", "Under 5", "Yes"]
                    ]
                },
                {
                    "type": "text",
                    "title": "Budget Tip",
                    "content": "<p>European resorts often offer better value for families. Serfaus-Fiss-Ladis and Les Gets both cost significantly less than US counterparts when you factor in lodging, lessons, and lift tickets.</p>"
                },
                {
                    "type": "faq",
                    "title": "Toddler Skiing FAQ",
                    "items": [
                        {
                            "question": "What age can toddlers start skiing?",
                            "answer": "Most kids can start lessons at 3, though some programs accept 2.5-year-olds. At home, you can practice in the backyard from 2 if you have snow and a flat area."
                        },
                        {
                            "question": "How long can toddlers ski?",
                            "answer": "Plan for 1-2 hours max. Toddler ski lessons are typically 1.5-2 hours including lots of breaks and games."
                        },
                        {
                            "question": "Should we do half-day or full-day childcare?",
                            "answer": "Start with half-day if it's your child's first time. You can always extend, but overtired toddlers can't be un-tired."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "Best Ski Resorts for Toddlers 2026 | Family Ski Guide",
            "description": "Top ski resorts for families with toddlers ages 2-5. Compare childcare, ski school ages, beginner terrain, and family amenities."
        }
    },
    {
        "slug": "epic-vs-ikon-families",
        "title": "Epic vs Ikon Pass: Which Is Better for Families?",
        "guide_type": "pass",
        "category": "ski passes",
        "excerpt": "Breaking down the two major ski passes to help you pick the right one for your family's ski style and budget.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>The Epic vs Ikon debate rages every fall as families try to pick their pass. The truth? <strong>Neither pass is universally better</strong> - it depends on where you live, where you want to ski, and how many days you'll actually use it.</p><p>Let's break down what matters most for families.</p>"
                },
                {
                    "type": "comparison_table",
                    "title": "At a Glance",
                    "columns": ["Feature", "Epic Pass", "Ikon Pass"],
                    "rows": [
                        ["Total Resorts", "40+", "50+"],
                        ["US Resorts", "~20", "~25"],
                        ["International", "~20", "~25"],
                        ["Kids Pass (5-12)", "Yes (discounted)", "Yes (discounted)"],
                        ["Under 5", "Free at most", "Free at most"],
                        ["Blackout Dates", "None (full)", "Some (base)"],
                        ["Price (Adult)", "$929-$979", "$949-$1,169"],
                        ["Buddy Tickets", "Yes", "Yes"]
                    ]
                },
                {
                    "type": "text",
                    "title": "Epic Pass - Best For",
                    "content": "<ul><li>Families who ski <strong>Vail, Beaver Creek, Park City, or Whistler</strong></li><li>Colorado-based families (most Epic resorts are here)</li><li>Those who want <strong>no blackout dates</strong></li><li>European ski trips (extensive Swiss, French, Austrian access)</li><li>Summit County Colorado lovers (Keystone, Breckenridge, Vail)</li></ul><p><strong>Family highlight:</strong> Keystone offers free skiing for kids 12 and under with an adult Epic Pass holder - a huge savings for families!</p>"
                },
                {
                    "type": "text",
                    "title": "Ikon Pass - Best For",
                    "content": "<ul><li>Families who ski <strong>Jackson Hole, Big Sky, Aspen, or Mammoth</strong></li><li>Those who prioritize <strong>terrain variety</strong> over unlimited days</li><li>Families who ski 7-14 days per season (Ikon Base is good value)</li><li>Pacific Northwest (Crystal, Mt. Bachelor) and California access</li><li>Taos, Steamboat, or Winter Park loyalists</li></ul><p><strong>Family highlight:</strong> Many Ikon resorts have strong ski school programs and family-friendly cultures.</p>"
                },
                {
                    "type": "text",
                    "title": "The Real Question: Where Do You Want to Ski?",
                    "content": "<p>Forget the marketing. Make a list of 3-5 resorts you actually want to visit this season. Then see which pass covers more of them.</p><p>If your list is split or you're not sure, consider:</p><ul><li><strong>Day tickets</strong> for one-off visits</li><li><strong>Regional passes</strong> (Mountain Collective, Indy Pass)</li><li><strong>One parent on each pass</strong> (yes, families do this!)</li></ul>"
                },
                {
                    "type": "faq",
                    "title": "Common Questions",
                    "items": [
                        {
                            "question": "Can I get a refund if my kid doesn't like skiing?",
                            "answer": "Epic has Epic Coverage for $99 that allows refunds for any reason. Ikon has similar Adventure Assurance. Both must be purchased with your pass."
                        },
                        {
                            "question": "What age do kids need their own pass?",
                            "answer": "Kids 4 and under ski free at most Epic and Ikon resorts. Ages 5-12 need a kids' pass (significantly discounted)."
                        },
                        {
                            "question": "Do passes include lessons?",
                            "answer": "No. Both passes are for lift access only. Lessons, rentals, and childcare are separate costs."
                        },
                        {
                            "question": "When should I buy?",
                            "answer": "Best prices are in spring (April-May) for the following season. Next best is fall before December."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "Epic vs Ikon Pass for Families 2025-26 | Comparison Guide",
            "description": "Compare Epic Pass vs Ikon Pass for family skiing. Pricing, resorts, blackout dates, and which pass is best for families with kids."
        }
    },
    {
        "slug": "first-family-ski-trip",
        "title": "Your First Family Ski Trip: A Complete Guide",
        "guide_type": "how-to",
        "category": "beginners",
        "excerpt": "Never been skiing with kids? This guide covers everything from choosing a resort to surviving the first day on snow.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>Taking kids skiing for the first time is equal parts exciting and terrifying. Will they love it? Will someone cry? (Spoiler: probably yes to both.)</p><p>This guide walks you through planning your first family ski trip, from picking the right resort to making it through Day One without losing your mind.</p>"
                },
                {
                    "type": "text",
                    "title": "Step 1: Set Realistic Expectations",
                    "content": "<p>Your first family ski trip will NOT be like your pre-kid ski trips. Accept this now and you'll be much happier.</p><p><strong>Expect:</strong></p><ul><li>Half the ski time you're used to</li><li>Triple the time getting ready</li><li>At least one meltdown (possibly yours)</li><li>Magical moments that make it all worth it</li></ul>"
                },
                {
                    "type": "text",
                    "title": "Step 2: Choose the Right Resort",
                    "content": "<p>For your first trip, prioritize:</p><ul><li><strong>Convenience over cool:</strong> Skip the famous resorts and find one with ski-in/ski-out or short shuttle rides</li><li><strong>Great ski school:</strong> This is the most important factor - research reviews of kids' programs</li><li><strong>Beginner terrain:</strong> Look for magic carpets and gentle slopes</li><li><strong>Non-ski activities:</strong> Have backup plans for tired or reluctant kids</li></ul>"
                },
                {
                    "type": "text",
                    "title": "Step 3: Book Lessons (Yes, For Everyone)",
                    "content": "<p>Here's the secret experienced ski families know: <strong>everyone takes lessons on the first day</strong>.</p><ul><li>Kids learn better from instructors than parents (no power struggles)</li><li>Parents can re-learn proper technique after years away</li><li>Family lessons after individual instruction = way more fun</li></ul><p>Book lessons for the morning. Afternoons are for free skiing or calling it quits.</p>"
                },
                {
                    "type": "text",
                    "title": "Step 4: Plan Your First Day",
                    "content": "<p>Day One is about having fun, not logging miles. Here's a realistic schedule:</p><ul><li><strong>8:00 AM:</strong> Wake up, big breakfast</li><li><strong>9:30 AM:</strong> Arrive at ski school (buffer time for gear chaos)</li><li><strong>10:00 AM - 12:00 PM:</strong> Kids in lessons, parents ski</li><li><strong>12:00 PM:</strong> Lunch together (plan 90 minutes, not 30)</li><li><strong>1:30 PM:</strong> Family skiing or more lessons</li><li><strong>3:00 PM:</strong> Call it a day. Hot chocolate time.</li></ul><p>Three hours of skiing on Day One is a massive success. Don't push it.</p>"
                },
                {
                    "type": "text",
                    "title": "Step 5: Embrace the Chaos",
                    "content": "<p>Things will go wrong. Goggles will fog. Gloves will get wet. Someone will need to pee the moment you get on the chairlift.</p><p>The families who become ski families are the ones who laugh through the chaos. Pack extra everything, take lots of breaks, and celebrate every small victory.</p><p><strong>Your only goals for Trip One:</strong></p><ol><li>Nobody gets hurt</li><li>Everyone wants to come back</li></ol><p>Everything else is bonus points.</p>"
                },
                {
                    "type": "faq",
                    "title": "First-Timer FAQs",
                    "items": [
                        {
                            "question": "How many days should our first trip be?",
                            "answer": "3-4 ski days is ideal. Shorter trips feel rushed, longer ones risk burnout. Add a travel day on each end."
                        },
                        {
                            "question": "Should we rent or buy gear?",
                            "answer": "Rent for your first trip. If everyone loves it, buy during end-of-season sales for next year."
                        },
                        {
                            "question": "What if my kid hates it?",
                            "answer": "This happens! Some kids need 2-3 trips before they click. Don't force it - have non-ski activities ready as backup."
                        },
                        {
                            "question": "Is it cheaper to ski in Europe?",
                            "answer": "Often, yes! When you factor in lodging, meals, and lift tickets, places like Austria can be 30-40% cheaper than Colorado."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "First Family Ski Trip Guide - Everything You Need to Know",
            "description": "Complete guide to planning your first family ski trip. From choosing a resort to surviving Day One, tips for skiing with kids for the first time."
        }
    }
]


def seed_guides(client, dry_run: bool = False):
    """Seed guides into database."""
    print("\nSeeding guides...")

    for guide in GUIDES:
        data = {
            "slug": guide["slug"],
            "title": guide["title"],
            "guide_type": guide["guide_type"],
            "category": guide.get("category"),
            "excerpt": guide.get("excerpt"),
            "content": guide["content"],
            "featured_image_url": guide.get("featured_image_url"),
            "seo_meta": guide.get("seo_meta", {}),
            "author": guide.get("author", "Snowthere Team"),
            "status": "published",
            "published_at": datetime.now(timezone.utc).isoformat(),
        }

        if dry_run:
            print(f"  [DRY-RUN] Would upsert: {guide['title']}")
            print(f"            Type: {guide['guide_type']}, Sections: {len(guide['content']['sections'])}")
        else:
            result = client.table("guides").upsert(
                data,
                on_conflict="slug"
            ).execute()

            if result.data:
                print(f"  OK: {guide['title']}")
            else:
                print(f"  ERROR: Failed to upsert {guide['slug']}")


def verify_guides(client, dry_run: bool = False):
    """Verify guides were created."""
    print("\nVerification...")

    if dry_run:
        print("  [DRY-RUN] Skipping verification")
        return

    result = client.table("guides").select("slug, title, guide_type, status").eq("status", "published").execute()

    print(f"  Published guides: {len(result.data)}")
    for guide in result.data:
        print(f"    - {guide['title']} ({guide['guide_type']})")


def main():
    parser = argparse.ArgumentParser(description="Seed initial guides")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    print("=" * 60)
    print("Guide Seeder")
    print("=" * 60)

    if args.dry_run:
        print("\n*** DRY RUN MODE - No changes will be made ***")

    print("\nConnecting to Supabase...")
    client = get_supabase_client()

    try:
        test = client.table("guides").select("count").limit(1).execute()
        print("  Connected to Supabase")
    except Exception as e:
        print(f"  ERROR: Failed to connect: {e}")
        sys.exit(1)

    seed_guides(client, args.dry_run)
    verify_guides(client, args.dry_run)

    print("\n" + "=" * 60)
    if args.dry_run:
        print("DRY RUN COMPLETE - Run without --dry-run to apply")
    else:
        print("DONE - Guides seeded successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
