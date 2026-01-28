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
    },
    # =========================================================================
    # 2026 MILAN-CORTINA WINTER OLYMPICS GUIDES
    # Olympics: February 6-22, 2026
    # =========================================================================
    {
        "slug": "cortina-skiing-2026-olympics",
        "title": "Can You Ski in Cortina During the 2026 Winter Olympics?",
        "guide_type": "regional",
        "category": "olympics",
        "excerpt": "The honest answer about skiing Cortina during the Olympics, plus nearby alternatives that will actually be skiable.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p><strong>Short answer: Yes, but it's complicated.</strong></p><p>The 2026 Milan-Cortina Winter Olympics run February 6-22, and families wondering if they can still ski Cortina are asking the right question. Here's the real situation: some terrain will be closed for events, accommodation prices are sky-high, and crowds will be significant. But skiing will still be possible on non-competition slopes.</p><p>If you're flexible on <em>where</em> you ski, you can have an incredible family trip. If you specifically need Cortina's famous runs, February 2026 is not your month.</p>"
                },
                {
                    "type": "comparison_table",
                    "title": "Cortina During Olympics: What's Open vs Closed",
                    "columns": ["Area", "Status During Olympics", "Notes"],
                    "rows": [
                        ["Tofana (Downhill Course)", "CLOSED", "Olympic women's downhill & super-G venue"],
                        ["Cinque Torri", "OPEN", "Family-friendly area, likely less crowded"],
                        ["Faloria", "PARTIALLY OPEN", "Some closures for training"],
                        ["Cortina Village", "VERY CROWDED", "Olympic fan zones, traffic controls"],
                        ["Ra Valles", "OPEN", "Good intermediate terrain"],
                        ["Lagazuoi", "OPEN", "Spectacular scenery, advanced terrain"]
                    ]
                },
                {
                    "type": "text",
                    "title": "The Real Talk on Accommodation",
                    "content": "<p>Hotels in Cortina during the Olympics are either <strong>sold out or 3-4x normal prices</strong>. A room that normally costs €200/night might be €800+ if you can find one at all.</p><p><strong>Family-smart alternatives:</strong></p><ul><li><strong>Stay in Alta Badia</strong> (30 min away) - Still connected via Dolomiti Superski, way cheaper</li><li><strong>Stay in San Cassiano</strong> - Charming village, excellent ski school, half the price</li><li><strong>Book an apartment in Cortina's outskirts</strong> - Locals rent out homes; search Airbnb now</li><li><strong>Day-trip from Arabba</strong> - Excellent skiing, shuttle access to Olympic events</li></ul>"
                },
                {
                    "type": "text",
                    "title": "Our Recommendation for Families",
                    "content": "<p>Unless watching Olympic events live is your primary goal, <strong>skip Cortina proper in February 2026</strong>. Instead:</p><ul><li>Base in Alta Badia or Val Gardena (same Dolomiti Superski pass)</li><li>Day-trip to Cortina for events if you want</li><li>Enjoy uncrowded slopes while everyone else is watching downhill</li></ul><p>Or consider coming <strong>March 2026</strong>. Post-Olympics Cortina will have that \"just hosted the world\" energy with normal prices and better snow conditions.</p>"
                },
                {
                    "type": "faq",
                    "title": "Common Questions",
                    "items": [
                        {
                            "question": "Will Cortina lift tickets cost more during the Olympics?",
                            "answer": "The Dolomiti Superski pass price stays the same, but day tickets at Cortina specifically may have limited availability. Buy your ski pass in advance."
                        },
                        {
                            "question": "Can kids ski during Olympic events?",
                            "answer": "Yes, on non-competition slopes. The beginner areas and most intermediate terrain will be open. Just avoid the marked Olympic venues."
                        },
                        {
                            "question": "Is it worth it to go during the Olympics?",
                            "answer": "For families who want the Olympics experience, yes, if you book NOW and accept higher costs. For families who just want great skiing, no. Visit Alta Badia or Val Gardena instead."
                        },
                        {
                            "question": "When do hotels release rooms for February 2026?",
                            "answer": "Most are already released and selling fast. Check booking.com with flexible dates or contact hotels directly. Many require 5-7 night minimums."
                        }
                    ]
                },
                {
                    "type": "cta",
                    "cta": {
                        "text": "Explore Cortina d'Ampezzo",
                        "href": "/resorts/italy/cortina-dampezzo",
                        "variant": "primary"
                    }
                }
            ]
        },
        "seo_meta": {
            "title": "Can You Ski Cortina During 2026 Olympics? | Family Guide",
            "description": "Can you ski Cortina during the 2026 Winter Olympics? What's open, what's closed, pricing reality, and better alternatives for families.",
            "keywords": ["Cortina 2026 Olympics", "ski during Olympics", "Milan-Cortina Winter Olympics", "Cortina family skiing"]
        }
    },
    {
        "slug": "milan-cortina-2026-family-guide",
        "title": "2026 Milan-Cortina Olympics: The Complete Family Guide",
        "guide_type": "regional",
        "category": "olympics",
        "excerpt": "Everything families need to know about the 2026 Winter Olympics. What to see, where to stay, and how to make it work with kids.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>The 2026 Winter Olympics come to Italy February 6-22, split between Milan and the Dolomites. For families, this is a once-in-a-generation opportunity to experience the Olympics while skiing some of Europe's most beautiful mountains.</p><p><strong>The key to making this work with kids:</strong> Pick ONE base location, plan for shorter days than you think, and book everything NOW. Here's how to do it right.</p>"
                },
                {
                    "type": "comparison_table",
                    "title": "2026 Olympics: What's Where",
                    "columns": ["Location", "Events", "Distance from Milan", "Best For"],
                    "rows": [
                        ["Milan", "Opening/Closing Ceremonies, Ice Hockey, Speed Skating", "0 (base city)", "City lovers, non-skiers"],
                        ["Cortina d'Ampezzo", "Downhill, Super-G, Combined, Curling", "160 km / 2h", "Alpine skiing fans"],
                        ["Bormio", "Men's Downhill & Super-G", "200 km / 2.5h", "Expert skiing families"],
                        ["Livigno", "Freestyle, Snowboarding", "230 km / 3h", "Teen-friendly, duty-free"],
                        ["Val di Fiemme", "Cross-Country, Ski Jumping", "180 km / 2h", "Nordic families"],
                        ["Anterselva", "Biathlon", "150 km / 1.5h", "Quieter, off-radar"]
                    ]
                },
                {
                    "type": "text",
                    "title": "Where Should Your Family Stay?",
                    "content": "<p>The biggest decision: <strong>City or Mountains?</strong></p><p><strong>Stay in Milan if:</strong></p><ul><li>You want to see Opening/Closing Ceremonies</li><li>Kids are more interested in atmosphere than skiing</li><li>You prefer train travel to driving</li><li>This is primarily a cultural trip with some snow days</li></ul><p><strong>Stay in the Dolomites if:</strong></p><ul><li>Skiing is the priority</li><li>You want to attend alpine events</li><li>Kids need daily ski time to stay happy</li><li>You're combining Olympics + family ski vacation</li></ul><p><strong>Our recommendation for most families:</strong> Base in Alta Badia or San Cassiano. Close enough to Cortina for events, excellent family skiing, and saner prices.</p>"
                },
                {
                    "type": "text",
                    "title": "Family-Friendly Events to Prioritize",
                    "content": "<p>Not all Olympic events are equal for kids. Here's what works best with shorter attention spans:</p><ul><li><strong>Best for kids:</strong> Freestyle skiing/snowboard (exciting, quick runs), curling (warm, indoor, relaxed pace)</li><li><strong>Good for kids:</strong> Downhill (dramatic, fast, loud cheering), ski jump (spectacular visuals)</li><li><strong>Harder with kids:</strong> Cross-country (long, slow), speed skating (indoor, hard to see), hockey (expensive, late nights)</li></ul><p>Best approach: Watch one event live, then follow others on the big screens in Olympic fan zones. Kids get the atmosphere without the logistics.</p>"
                },
                {
                    "type": "checklist",
                    "title": "Olympics Family Planning Checklist",
                    "items": [
                        {"text": "Book accommodation 6+ months ahead (NOW!)"},
                        {"text": "Register for Olympic ticket lottery or resale"},
                        {"text": "Reserve ski lessons (they'll fill up)"},
                        {"text": "Book airport transfers from Milan Malpensa"},
                        {"text": "Get Dolomiti Superski pass online"},
                        {"text": "Download offline maps of Cortina/Alta Badia"},
                        {"text": "Pack for COLD (-10°C to -20°C in February)"},
                        {"text": "Bring portable phone chargers"},
                        {"text": "Download Italian translation app"},
                        {"text": "Print hotel and ticket confirmations"}
                    ]
                },
                {
                    "type": "text",
                    "title": "Budget Reality Check",
                    "content": "<p>Let's be honest about costs. A family of 4 (2 adults, 2 kids) for one week:</p><p><strong>Budget Option (staying near Alta Badia):</strong> €4,000-6,000<br>Includes: apartment rental, ski passes, rentals, one Olympic event, meals mostly self-catered</p><p><strong>Mid-Range (Cortina outskirts, half-board):</strong> €8,000-12,000<br>Includes: hotel, ski passes, lessons, 2-3 Olympic events, mix of dining</p><p><strong>Premium (central Cortina hotel):</strong> €15,000-25,000+<br>Includes: premium hotel, full ski setup, multiple Olympic events, fine dining</p><p>Compare to a typical Cortina week outside Olympics: €5,000-8,000 for mid-range.</p>"
                },
                {
                    "type": "faq",
                    "title": "Olympics Family FAQ",
                    "items": [
                        {
                            "question": "How do we get Olympic tickets?",
                            "answer": "Official tickets will be sold via milano-cortina2026.org. There's typically a lottery for popular events. Sign up for the official newsletter now to be first in line."
                        },
                        {
                            "question": "Will there be traffic chaos?",
                            "answer": "Yes. The Cortina area will have traffic controls and parking restrictions. Use the official Olympic shuttle buses from park-and-ride lots, or base outside Cortina and ski in."
                        },
                        {
                            "question": "Can we ski AND attend events the same day?",
                            "answer": "Realistically, pick one per day. Ski in the morning or afternoon, attend an event the other half. Trying both will exhaust everyone."
                        },
                        {
                            "question": "Is the Olympics worth it with young kids?",
                            "answer": "Ages 7+ will remember it forever. Under 5, they won't remember and may find it overwhelming. Consider if the cost difference is worth it for your family stage."
                        },
                        {
                            "question": "Do we need travel insurance for Olympics skiing in Italy?",
                            "answer": "Yes, strongly recommended. European ski resorts often require proof of insurance for mountain rescue. Get a policy that covers ski-specific injuries, trip cancellation (Olympics logistics can be unpredictable), and medical evacuation. World Nomads and Allianz both offer ski-specific coverage."
                        }
                    ]
                },
                {
                    "type": "cta",
                    "cta": {
                        "text": "See Dolomites Resorts",
                        "href": "/resorts/italy",
                        "variant": "primary"
                    }
                }
            ]
        },
        "seo_meta": {
            "title": "2026 Milan-Cortina Olympics Family Guide | Complete Planning",
            "description": "Complete family guide to the 2026 Winter Olympics in Italy. Where to stay, which events to see, budget breakdown, and skiing with kids.",
            "keywords": ["2026 Winter Olympics family", "Milan-Cortina Olympics guide", "Olympics with kids", "Italy Winter Olympics planning"]
        }
    },
    {
        "slug": "dolomites-family-resorts-olympics",
        "title": "Best Dolomites Family Ski Resorts Near the 2026 Olympics",
        "guide_type": "comparison",
        "category": "olympics",
        "excerpt": "The top family-friendly Dolomites resorts for combining skiing with the 2026 Olympics, ranked by distance, value, and kid-friendliness.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>If you're planning a family ski trip around the 2026 Winter Olympics, the Dolomites offer world-class skiing within easy reach of the Cortina events. But which resort should you choose?</p><p>We've ranked the top family options by <strong>distance to Olympic venues, value for money, kid-friendliness, and skiing quality</strong>. All are connected via the Dolomiti Superski pass: 1,200 km of terrain on one ticket.</p>"
                },
                {
                    "type": "list",
                    "title": "Top 5 Family Resorts Near the 2026 Olympics",
                    "items": [
                        {
                            "name": "Alta Badia",
                            "description": "Our #1 pick for families during Olympics. Just 30 minutes to Cortina, excellent ski schools, gentle terrain for beginners, and authentic Italian mountain culture. The villages (La Villa, San Cassiano, Corvara) are charming without being overcrowded. Exceptional food scene. This is where chefs come to ski.",
                            "resort_slug": "italy/alta-badia"
                        },
                        {
                            "name": "Val Gardena",
                            "description": "Larger ski area with more terrain variety. Ortisei has great ski school and family infrastructure. About 45 minutes to Cortina. Better for families with confident skiers since some terrain is more challenging. Beautiful Sella Ronda circuit accessible.",
                            "resort_slug": "italy/selva-val-gardena"
                        },
                        {
                            "name": "Kronplatz (Plan de Corones)",
                            "description": "Best for families who prioritize wide, groomed runs. Excellent for beginners and intermediates. Modern lifts mean no queues. About 40 minutes to Cortina. The town of Brunico offers good non-ski activities.",
                            "resort_slug": "italy/kronplatz"
                        },
                        {
                            "name": "Arabba",
                            "description": "For families with advanced skiers. Spectacular Marmolada glacier access, Sella Ronda hub. Only 25 minutes to Cortina but smaller village with fewer amenities. Best value option if you prioritize skiing over nightlife.",
                            "resort_slug": "italy/arabba"
                        },
                        {
                            "name": "San Cassiano",
                            "description": "Quieter alternative to Alta Badia proper. Family-run hotels, lower prices, equally good skiing via connection to Alta Badia. Ski school picks kids up from hotel. About 35 minutes to Cortina. Our \"hidden gem\" pick.",
                            "resort_slug": "italy/san-cassiano"
                        }
                    ]
                },
                {
                    "type": "comparison_table",
                    "title": "Quick Comparison",
                    "columns": ["Resort", "To Cortina", "Family Rating", "Ski School From", "Budget/Night (Family 4)"],
                    "rows": [
                        ["Alta Badia", "30 min", "⭐⭐⭐⭐⭐", "3 years", "€400-800"],
                        ["Val Gardena", "45 min", "⭐⭐⭐⭐", "3 years", "€350-700"],
                        ["Kronplatz", "40 min", "⭐⭐⭐⭐⭐", "4 years", "€300-600"],
                        ["Arabba", "25 min", "⭐⭐⭐", "4 years", "€250-450"],
                        ["San Cassiano", "35 min", "⭐⭐⭐⭐⭐", "3 years", "€300-550"]
                    ]
                },
                {
                    "type": "text",
                    "title": "The Dolomiti Superski Advantage",
                    "content": "<p>Every resort on this list is covered by the <strong>Dolomiti Superski pass</strong>, one of the world's best ski pass deals.</p><ul><li>1,200 km of slopes across 12 valleys and 450 lifts</li><li>Kids under 8 ski free with paying adult</li><li>€324 for 6-day adult pass (2024/25 prices)</li><li>Ski a different valley every day without paying extra</li></ul><p>This means you can base in Alta Badia, ski Cortina one day, and never buy a separate ticket. Huge advantage over fragmented US ski areas.</p>"
                },
                {
                    "type": "text",
                    "title": "Our Verdict: Alta Badia or San Cassiano",
                    "content": "<p>For most families visiting during the 2026 Olympics, we recommend <strong>Alta Badia</strong> (specifically the villages of La Villa or Corvara) or <strong>San Cassiano</strong> for slightly better value.</p><p><strong>Why:</strong></p><ul><li>Short drive to Cortina Olympic events</li><li>World-class ski schools in multiple languages</li><li>Excellent family dining (including Michelin restaurants!)</li><li>Gentler terrain for beginners and intermediates</li><li>Prices 30-40% lower than Cortina proper</li><li>Authentic Italian atmosphere without tourist overwhelm</li></ul>"
                },
                {
                    "type": "faq",
                    "title": "Planning Questions",
                    "items": [
                        {
                            "question": "Can we ski from Alta Badia to Cortina?",
                            "answer": "Yes! The Lagazuoi connection links Alta Badia to Cortina via spectacular mountain scenery. It's a full-day excursion with advanced terrain, better suited for confident intermediates and above."
                        },
                        {
                            "question": "Which resort has the best ski school?",
                            "answer": "Alta Badia and Kronplatz both have excellent multilingual ski schools. San Cassiano's smaller schools offer more personal attention. Book early for Olympics weeks."
                        },
                        {
                            "question": "Should we rent a car?",
                            "answer": "Strongly recommended. Public transport exists but is infrequent. A car gives you flexibility for Olympic events and resort-hopping. Book early because rentals will be limited during Olympics."
                        },
                        {
                            "question": "What's the snow like in February?",
                            "answer": "February is peak season with excellent snow coverage. Expect cold temperatures (-5°C to -15°C), shorter days, and occasional snowfall. Best snow conditions of the season."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "Best Dolomites Family Ski Resorts for 2026 Olympics | Comparison",
            "description": "Best Dolomites family resorts near the 2026 Olympics. Alta Badia, Val Gardena, Kronplatz ranked by family-friendliness, value, and distance.",
            "keywords": ["Dolomites family ski resorts", "Olympics ski resorts", "Alta Badia Olympics", "Val Gardena family", "best ski resort near Cortina"]
        }
    },
    {
        "slug": "milan-to-cortina-with-kids",
        "title": "Milan to Cortina With Kids: Complete Transportation Guide",
        "guide_type": "how-to",
        "category": "olympics",
        "excerpt": "Every option for getting from Milan to Cortina with children. Trains, buses, rental cars, and private transfers compared.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>Getting from Milan to Cortina d'Ampezzo with kids requires planning, especially during the 2026 Olympics. The distance is about 420 km (260 miles), and there's no direct train. Here's every option broken down for families.</p><p><strong>Bottom line:</strong> Rent a car if you can drive in winter conditions. Otherwise, the train-to-bus combo is doable but long.</p>"
                },
                {
                    "type": "comparison_table",
                    "title": "Transportation Options Compared",
                    "columns": ["Option", "Duration", "Cost (Family 4)", "Kid-Friendly?", "Olympics Impact"],
                    "rows": [
                        ["Rental Car", "4-5 hours", "€200-400 total", "⭐⭐⭐⭐⭐", "Traffic controls near Cortina"],
                        ["Train + Bus", "5-6 hours", "€150-250 total", "⭐⭐⭐", "Crowded buses during events"],
                        ["Private Transfer", "4 hours", "€400-600 total", "⭐⭐⭐⭐⭐", "Pre-book essential"],
                        ["Flixbus (Direct)", "5.5 hours", "€80-150 total", "⭐⭐", "Very crowded"],
                        ["Fly to Venice + Drive", "3.5-4 hours", "Varies", "⭐⭐⭐⭐", "Less traffic from Venice"]
                    ]
                },
                {
                    "type": "text",
                    "title": "Option 1: Rental Car (Recommended)",
                    "content": "<p><strong>Best for:</strong> Families who want flexibility and can handle winter driving</p><p><strong>Route:</strong> Milan → A4 to Brescia → A22 to Brenner → Exit Bressanone → SS49/SS51 to Cortina</p><p><strong>What to know:</strong></p><ul><li>Winter tires mandatory (included with rental)</li><li>Tolls cost ~€35-45 one way</li><li>Last 2 hours are mountain roads, beautiful but slow</li><li>Olympic traffic controls start about 10km from Cortina</li><li>Pre-book parking in Cortina or use park-and-ride</li></ul><p><strong>The move:</strong> Rent from Venice instead of Milan. It's 2 hours closer to Cortina and avoids Milan traffic entirely.</p>"
                },
                {
                    "type": "text",
                    "title": "Option 2: Train + Bus",
                    "content": "<p><strong>Best for:</strong> Families who don't want to drive in mountains</p><p><strong>Route:</strong> Milan Centrale → Train to Calalzo di Cadore (3.5h) → Dolomiti Bus to Cortina (1h)</p><p><strong>What to know:</strong></p><ul><li>Trenitalia runs trains to Calalzo (~€25-50/person)</li><li>Dolomiti Bus connects to Cortina (€5/person)</li><li>Bus timing syncs with train arrivals, so check schedules</li><li>Kids under 4 free on trains, 4-12 half price</li><li>Bring snacks and entertainment for kids</li></ul><p><strong>Warning for Olympics:</strong> Buses will be crowded. Consider pre-booking private shuttle from Calalzo.</p>"
                },
                {
                    "type": "text",
                    "title": "Option 3: Private Transfer",
                    "content": "<p><strong>Best for:</strong> Families who want door-to-door comfort</p><p><strong>Companies:</strong> Alps2Alps, Cortina Transfer, Dolomitiwebtransfer</p><p><strong>What to know:</strong></p><ul><li>€400-600 for family of 4 (Milan airport to Cortina)</li><li>Child seats available on request</li><li>Driver handles traffic, parking, mountain roads</li><li>BOOK EARLY for Olympics weeks, limited availability</li><li>Some services include stop for lunch en route</li></ul><p>Split costs with another family. Transfer vans fit 6 to 8 people.</p>"
                },
                {
                    "type": "text",
                    "title": "Option 4: Alternative Starting Points",
                    "content": "<p>Consider flying into a closer airport:</p><ul><li><strong>Venice Marco Polo (VCE):</strong> 2.5 hours to Cortina by car. Easiest logistics.</li><li><strong>Treviso (TSF):</strong> Budget airlines, 2 hours to Cortina.</li><li><strong>Innsbruck (INN):</strong> 2.5 hours via Austria. Sometimes cheaper flights.</li><li><strong>Verona (VRN):</strong> 3 hours. Good flight connections.</li></ul><p>For 2026 Olympics, Venice will likely be less chaotic than Milan airports.</p>"
                },
                {
                    "type": "checklist",
                    "title": "Travel Day Checklist",
                    "items": [
                        {"text": "Download offline Google Maps of route"},
                        {"text": "Pack snacks for 5+ hours of travel"},
                        {"text": "Charge tablets and download shows"},
                        {"text": "Print train tickets and car rental confirmations"},
                        {"text": "Check chain/winter tire requirements"},
                        {"text": "Know parking location at destination"},
                        {"text": "Have Euros in cash for tolls and parking"},
                        {"text": "Save hotel address in phone GPS"},
                        {"text": "Pack motion sickness meds (mountain roads!)"},
                        {"text": "Bring layers, car and train temps vary"}
                    ]
                },
                {
                    "type": "faq",
                    "title": "Transportation FAQ",
                    "items": [
                        {
                            "question": "Do I need snow chains?",
                            "answer": "Winter tires are mandatory Nov-April on mountain roads. Chains must be carried in the car even with winter tires. Rentals include both. Confirm when booking."
                        },
                        {
                            "question": "Is the drive scary?",
                            "answer": "The A22 motorway is easy. The final stretch on SS51 has hairpin turns but is well-maintained. In snow, take it slow. Most families handle it fine."
                        },
                        {
                            "question": "Can we stop along the way?",
                            "answer": "Yes! Lake Garda (Sirmione) makes a nice lunch stop. The Dolomiti passes have stunning viewpoints. Build in 30-60 extra minutes for stops."
                        },
                        {
                            "question": "What about the Autostrada tolls?",
                            "answer": "Tolls are paid at exit booths. Credit cards accepted. Total Milan to Cortina is about €35 to 45. Don't use Telepass lanes without a Telepass device."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "Milan to Cortina With Kids - Transportation Guide 2026",
            "description": "How to get from Milan to Cortina with children. Rental car, train, bus, and private transfer options compared for families visiting the 2026 Winter Olympics.",
            "keywords": ["Milan to Cortina with kids", "Cortina transportation", "Milan Cortina train", "Dolomites with children", "Olympics transportation"]
        }
    },
    {
        "slug": "olympics-italy-family-itinerary",
        "title": "Olympics With Kids: A 5-Day Italy Itinerary That Actually Works",
        "guide_type": "how-to",
        "category": "olympics",
        "excerpt": "A realistic day-by-day plan for families visiting the 2026 Milan-Cortina Winter Olympics, with built-in flexibility for meltdowns.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>If you try to see everything at the Olympics with kids, you'll see nothing except tantrums. This itinerary is designed for <strong>real families who need naps, snacks, and bathroom breaks</strong>.</p><p>We're basing this around Alta Badia (our recommended family base), with day trips to Cortina for Olympics action. Adjust as needed, but resist the urge to add more. Less is more with kids.</p>"
                },
                {
                    "type": "text",
                    "title": "Day 1: Arrival & Settle In",
                    "content": "<p><strong>Morning:</strong> Arrive Milan Malpensa, pick up rental car</p><p><strong>Midday:</strong> Drive to Alta Badia (4-5 hours with stops)</p><p><strong>Stop suggestion:</strong> Lunch break in Verona or at Lake Garda. Stretch legs, see something beautiful</p><p><strong>Afternoon:</strong> Arrive Alta Badia, check into hotel/apartment</p><p><strong>Evening:</strong> Easy dinner at hotel or nearby pizzeria. Early bedtime. Everyone's tired.</p><p><strong>Key tasks:</strong></p><ul><li>Pick up ski rentals (many shops open until 7pm)</li><li>Confirm ski school for tomorrow</li><li>Buy groceries for snacks</li><li>Let kids explore the village</li></ul><p><strong>No skiing today.</strong> Arrival days are for recovery, not activity.</p>"
                },
                {
                    "type": "text",
                    "title": "Day 2: Ski Day (Full Family)",
                    "content": "<p><strong>Morning:</strong></p><ul><li>8:00 AM - Big breakfast at hotel</li><li>9:30 AM - Kids to ski school (drop-off takes time)</li><li>10:00 AM - Parents ski! You've earned it.</li></ul><p><strong>Midday:</strong></p><ul><li>12:00 PM - Pick up kids from ski school</li><li>12:30 PM - Lunch at mountain rifugio (book ahead for window seat)</li></ul><p><strong>Afternoon:</strong></p><ul><li>2:00 PM - Family skiing on easy slopes OR more ski school</li><li>3:30 PM - Hot chocolate break (non-negotiable)</li><li>4:00 PM - Last runs or call it quits</li></ul><p><strong>Evening:</strong></p><ul><li>Après-ski: Find a hotel with a pool/spa for tired muscles</li><li>Dinner: Try a traditional South Tyrolean restaurant</li></ul><p><strong>Don't overdo it.</strong> First ski day fatigue hits hard. 4 to 5 hours total is plenty.</p>"
                },
                {
                    "type": "text",
                    "title": "Day 3: Olympics Day in Cortina",
                    "content": "<p><strong>This is your big Olympics day. Go all in on the experience, skip skiing.</strong></p><p><strong>Morning:</strong></p><ul><li>7:30 AM - Early breakfast</li><li>8:30 AM - Drive to Cortina (30 min from Alta Badia)</li><li>9:00 AM - Park at official Olympic park-and-ride</li><li>9:30 AM - Shuttle to Olympic venue</li><li>10:00 AM - Your Olympic event (book morning session for kids)</li></ul><p><strong>Midday:</strong></p><ul><li>After event - Walk the Cortina Corso Italia (main street)</li><li>Lunch in Cortina village (pricey but festive)</li><li>Browse the Olympic fan zone, take photos with mascots</li></ul><p><strong>Afternoon:</strong></p><ul><li>2:00 PM - Free time in Cortina OR second event if you have tickets</li><li>4:00 PM - Drive back to Alta Badia before dark</li></ul><p><strong>Evening:</strong></p><ul><li>Early, easy dinner</li><li>Kids will be exhausted. Don't fight it</li></ul><p><strong>Tip:</strong> Bring snacks. Olympic venue food is expensive and lines are long.</p>"
                },
                {
                    "type": "text",
                    "title": "Day 4: Recovery Ski Day",
                    "content": "<p><strong>Chill day. No agenda, no pressure.</strong></p><p><strong>Morning:</strong></p><ul><li>Sleep in (you need it after Olympics day)</li><li>10:00 AM - Late start on the slopes</li><li>Ski at a relaxed pace, explore a new area</li></ul><p><strong>Option: Sella Ronda Circuit</strong><br>If you have confident intermediate skiers, try the famous Sella Ronda (4 valleys, one loop). Start by 10 AM to finish by 4 PM. Not recommended for beginners or kids under 8.</p><p><strong>Midday:</strong></p><ul><li>Long lunch at a mountain rifugio. This is what Italian skiing is about</li><li>Try the local specialties: canederli (bread dumplings), speck, apple strudel</li></ul><p><strong>Afternoon:</strong></p><ul><li>More skiing if kids have energy</li><li>Or quit early for swimming pool/spa time</li><li>Non-ski option: sledding at many resorts</li></ul><p><strong>Evening:</strong></p><ul><li>Pizza night. Kids love predictability after a long week</li></ul>"
                },
                {
                    "type": "text",
                    "title": "Day 5: Last Morning & Departure",
                    "content": "<p><strong>Resist the urge to squeeze in more skiing.</strong></p><p><strong>Morning:</strong></p><ul><li>Option A: One last ski (8:30 AM fresh corduroy is magical)</li><li>Option B: Sleep in, pack leisurely</li></ul><p><strong>10:00 AM:</strong> Check out (leave bags at hotel if skiing)</p><p><strong>11:00 AM:</strong> Return ski rentals, final village walk</p><p><strong>12:00 PM:</strong> Lunch in Alta Badia (last Italian meal, make it count)</p><p><strong>1:30 PM:</strong> Start drive to Milan (or Venice) airport</p><p>Don't book an early flight. Give yourself 5 to 6 hours door-to-gate. Traffic near airports during Olympics will be worse than normal.</p><p><strong>Alternative:</strong> Add a night in Verona or Venice for a softer landing. Both are on the route to Milan and offer non-ski cultural experiences.</p>"
                },
                {
                    "type": "checklist",
                    "title": "5-Day Trip Packing Essentials",
                    "items": [
                        {"text": "Ski gear OR confirm rental reservations"},
                        {"text": "Warm layers for Olympics outdoor viewing"},
                        {"text": "Comfortable walking shoes for Cortina"},
                        {"text": "Portable phone chargers (2+ per family)"},
                        {"text": "Snacks for travel and Olympics days"},
                        {"text": "Kids' tablets loaded with shows"},
                        {"text": "Printed tickets and confirmations"},
                        {"text": "Cash (Euros) for mountain rifugios"},
                        {"text": "Small backpack for on-mountain essentials"},
                        {"text": "Camera with good zoom for Olympic events"}
                    ]
                },
                {
                    "type": "text",
                    "title": "Budget for 5 Days (Family of 4)",
                    "content": "<p><strong>Mid-range estimate:</strong></p><ul><li>Accommodation (4 nights): €1,600-2,400</li><li>Rental car + fuel + tolls: €400-500</li><li>Ski passes (4 days): €600-800</li><li>Ski rentals: €300-400</li><li>Ski school (2 days): €200-300</li><li>Olympic tickets (1 event): €200-400</li><li>Food & dining: €600-800</li><li>Misc (parking, souvenirs): €200-300</li></ul><p><strong>Total: approximately €4,100-5,900</strong></p><p>This is 20-30% higher than non-Olympics pricing due to accommodation premiums. Worth it for a once-in-a-lifetime experience.</p>"
                },
                {
                    "type": "faq",
                    "title": "Itinerary FAQ",
                    "items": [
                        {
                            "question": "Can this work with toddlers?",
                            "answer": "Yes, but adjust expectations. Skip the Sella Ronda, use childcare on Olympics day, and build in more rest time. Consider 6 days instead of 5."
                        },
                        {
                            "question": "What if weather is bad?",
                            "answer": "Swap ski and Olympics days. Bad weather skiing is miserable; Olympic events often continue in snow. Alta Badia has indoor pools and museums as backup."
                        },
                        {
                            "question": "Can we fit in Milan sightseeing?",
                            "answer": "Only on arrival or departure day, and only if you have 4+ hours. Consider adding a Milan overnight instead of cramming it. The Duomo with tired kids is not fun."
                        },
                        {
                            "question": "What's the biggest mistake families make?",
                            "answer": "Trying to see too many Olympic events. One event, experienced fully, beats three events with exhausted, cranky kids. Quality over quantity."
                        },
                        {
                            "question": "Do we need to speak Italian?",
                            "answer": "The Dolomites are bilingual (Italian and German/Ladin). Most hotel staff and ski school instructors speak English. During the Olympics, English will be widely supported. Learn 'grazie' and 'prego' and you'll be fine."
                        }
                    ]
                }
            ]
        },
        "seo_meta": {
            "title": "2026 Olympics With Kids - 5-Day Italy Itinerary | Family Guide",
            "description": "Day-by-day family itinerary for the 2026 Milan-Cortina Winter Olympics. Realistic planning for skiing + Olympics with children, including budgets and tips.",
            "keywords": ["Olympics with kids itinerary", "Milan Cortina family trip", "2026 Winter Olympics planning", "Italy ski vacation Olympics", "Dolomites family itinerary"]
        }
    },
    {
        "slug": "ski-like-an-olympian-resorts",
        "title": "Ski Like an Olympian: Resorts Where You Can Ski the Olympic Runs",
        "guide_type": "comparison",
        "category": "olympics",
        "excerpt": "Ski the same runs as Olympic champions. These resorts hosted Winter Olympics skiing events, and you can still ski them today.",
        "author": "Snowthere Team",
        "content": {
            "sections": [
                {
                    "type": "intro",
                    "content": "<p>There's something magical about skiing the same run where Lindsey Vonn won gold or where legends like Franz Klammer made history. The best part? <strong>Many Olympic downhill courses are open to the public.</strong> You don't need to be an Olympian to ski them.</p><p>Here are the top resorts where families can ski actual Olympic venues, ranked by accessibility, family-friendliness, and how easy it is to find the famous runs.</p><p><strong>Note:</strong> Olympic downhill courses are typically expert terrain. But every Olympic resort also has family-friendly skiing, and kids love saying they skied \"where the Olympics happened.\"</p>"
                },
                {
                    "type": "list",
                    "title": "Top 10 Resorts to Ski Olympic Runs",
                    "items": [
                        {
                            "name": "Whistler Blackcomb, Canada (2010)",
                            "description": "<strong>Olympic Runs:</strong> Dave Murray Downhill (men's), Franz's Run (women's downhill)<br><strong>Family-Friendly?</strong> Yes! Massive beginner area, excellent ski school.<br><strong>The Run:</strong> Dave Murray Downhill starts at 5,280 ft elevation with 3,248 ft of vertical. It's a genuine expert run, but the resort has terrain for everyone.<br>The Peak 2 Peak Gondola is a must for non-skiers. Views of where history was made.",
                            "resort_slug": "canada/whistler-blackcomb"
                        },
                        {
                            "name": "Park City, USA (2002)",
                            "description": "<strong>Olympic Runs:</strong> Champions Run (giant slalom), 3000 (men's GS), plus Utah Olympic Park nearby<br><strong>Family-Friendly?</strong> Excellent. Purpose-built family zones, kids ski free under 6.<br><strong>The Run:</strong> Champion run is an intermediate cruiser, one of the few Olympic runs families can actually ski together.<br>Don't miss Utah Olympic Park for the bobsled experience. Kids can also ski their youth programs.",
                            "resort_slug": "united-states/park-city"
                        },
                        {
                            "name": "Cortina d'Ampezzo, Italy (1956 & 2026)",
                            "description": "<strong>Olympic Runs:</strong> Tofana Schuss (1956), Olympia delle Tofane (2026 women's downhill)<br><strong>Family-Friendly?</strong> Very good. Beautiful village, excellent Italian ski schools.<br><strong>The Run:</strong> The 1956 course is intermediate-friendly. The 2026 course will be more challenging. Both accessible via lifts.<br>The move: Come after February 2026 for the \"freshly Olympic\" experience without the crowds.",
                            "resort_slug": "italy/cortina-dampezzo"
                        },
                        {
                            "name": "Val d'Isère, France (1992 & 2009 Worlds)",
                            "description": "<strong>Olympic Runs:</strong> La Face de Bellevarde (men's downhill), one of the most famous in skiing history<br><strong>Family-Friendly?</strong> Yes, with excellent beginner areas separate from expert terrain.<br><strong>The Run:</strong> La Face is STEEP (average 34% grade). Black run, experts only. But standing at the top where Jean-Claude Killy won? Incredible.<br>La Daille sector has gentler slopes while parents take turns attempting La Face.",
                            "resort_slug": "france/val-disere"
                        },
                        {
                            "name": "Lake Placid, USA (1932 & 1980)",
                            "description": "<strong>Olympic Runs:</strong> Whiteface Mountain, site of the \"Miracle on Ice\" era downhill events<br><strong>Family-Friendly?</strong> Good. Classic East Coast resort with family programs.<br><strong>The Run:</strong> The original Olympic trails are mostly intermediate. Cloudspin and Excelsior trace the 1980 routes.<br>The Olympic Center in town has public skating on the 1980 rink. Kids love it.",
                            "resort_slug": "united-states/lake-placid"
                        },
                        {
                            "name": "Innsbruck/Axamer Lizum, Austria (1964 & 1976)",
                            "description": "<strong>Olympic Runs:</strong> Multiple venues across the region: Patscherkofel, Axamer Lizum<br><strong>Family-Friendly?</strong> Excellent. Austrian ski schools are world-class.<br><strong>The Run:</strong> Patscherkofel's Olympic downhill is accessible to strong intermediates. Historic signage marks the route.<br>Stay in Innsbruck for the city + ski combo. Tram goes directly to slopes.",
                            "resort_slug": "austria/innsbruck"
                        },
                        {
                            "name": "St. Moritz, Switzerland (1928 & 1948)",
                            "description": "<strong>Olympic Runs:</strong> Corviglia (slalom, GS), the birthplace of Alpine ski racing<br><strong>Family-Friendly?</strong> Yes, though expensive. Excellent ski school, gentle upper slopes.<br><strong>The Run:</strong> The original Olympic courses are intermediate-friendly. Ski where the sport began.<br>The Cresta Run toboggan is a different kind of Olympic thrill (16+ only).",
                            "resort_slug": "switzerland/st-moritz"
                        },
                        {
                            "name": "Sestriere, Italy (2006)",
                            "description": "<strong>Olympic Runs:</strong> Kandahar Giovanni Alberto Agnelli (men's downhill), Kandahar Banchetta (women's)<br><strong>Family-Friendly?</strong> Good. Connected to the large Via Lattea ski area.<br><strong>The Run:</strong> The Kandahar runs are genuine expert terrain. But the resort has plenty of blues and greens.<br>The Olympic gondola gives amazing views even for non-skiers. Sauze d'Oulx nearby is more family-oriented.",
                            "resort_slug": "italy/sestriere"
                        },
                        {
                            "name": "Hakuba, Japan (1998)",
                            "description": "<strong>Olympic Runs:</strong> Happo-one, site of men's and women's downhill/Super-G<br><strong>Family-Friendly?</strong> Very. Japanese hospitality is unmatched. Ski schools in English available.<br><strong>The Run:</strong> The Olympic downhill course on Happo-one is challenging but skiable by strong intermediates. Stunning views of Japanese Alps.<br>Combine skiing with onsen (hot spring) visits. Kids love the snow monkeys nearby.",
                            "resort_slug": "japan/hakuba-valley"
                        },
                        {
                            "name": "Lillehammer/Kvitfjell, Norway (1994)",
                            "description": "<strong>Olympic Runs:</strong> Kvitfjell hosted downhill/Super-G; Hafjell hosted slalom/GS<br><strong>Family-Friendly?</strong> Excellent. Norwegian resorts are designed around families.<br><strong>The Run:</strong> The Kvitfjell Olympic downhill is genuinely steep, but signposted. Hafjell's slalom hill is more approachable.<br>Visit the Lillehammer Olympic Museum with kids. Interactive and engaging.",
                            "resort_slug": "norway/lillehammer"
                        }
                    ]
                },
                {
                    "type": "comparison_table",
                    "title": "Quick Reference: Olympic Resorts",
                    "columns": ["Resort", "Olympics Year", "Famous Run", "Difficulty", "Family Rating"],
                    "rows": [
                        ["Whistler", "2010", "Dave Murray Downhill", "Expert", "⭐⭐⭐⭐⭐"],
                        ["Park City", "2002", "Champions Run", "Intermediate", "⭐⭐⭐⭐⭐"],
                        ["Cortina", "1956/2026", "Tofana Schuss", "Int/Expert", "⭐⭐⭐⭐"],
                        ["Val d'Isère", "1992", "La Face de Bellevarde", "Expert", "⭐⭐⭐⭐"],
                        ["Lake Placid", "1980", "Cloudspin/Excelsior", "Intermediate", "⭐⭐⭐⭐"],
                        ["Innsbruck", "1964/1976", "Patscherkofel", "Intermediate", "⭐⭐⭐⭐⭐"],
                        ["St. Moritz", "1928/1948", "Corviglia", "Intermediate", "⭐⭐⭐"],
                        ["Sestriere", "2006", "Kandahar", "Expert", "⭐⭐⭐"],
                        ["Hakuba", "1998", "Happo-one Downhill", "Int/Expert", "⭐⭐⭐⭐⭐"],
                        ["Lillehammer", "1994", "Kvitfjell Downhill", "Expert", "⭐⭐⭐⭐"]
                    ]
                },
                {
                    "type": "text",
                    "title": "Easiest Olympic Runs for Families",
                    "content": "<p>Most Olympic downhill courses are expert terrain. They're designed to challenge the world's best. But some are actually skiable by strong intermediates:</p><ol><li><strong>Park City's Champions Run</strong> - Wide, groomed, intermediate-friendly. Your whole family can ski this.</li><li><strong>Lake Placid's Cloudspin</strong> - East Coast blue/black. Manageable for confident intermediates.</li><li><strong>St. Moritz's Corviglia</strong> - The original Olympic venue is surprisingly accessible.</li><li><strong>Cortina's 1956 Tofana Schuss</strong> - Historic and intermediate-friendly.</li><li><strong>Hakuba's Happo-one</strong> - The upper sections are doable; lower sections get steeper.</li></ol><p><strong>What about the really famous ones?</strong> Runs like Val d'Isère's La Face, Kitzbühel's Streif, and Wengen's Lauberhorn are genuinely dangerous. Admire from the lift or watch from the bottom.</p>"
                },
                {
                    "type": "text",
                    "title": "Non-Family-Friendly (But Famous) Olympic Runs",
                    "content": "<p>For context, here are legendary Olympic venues that exist but aren't great for families:</p><ul><li><strong>Rosa Khutor, Russia (2014)</strong> - Great resort, but travel currently complicated</li><li><strong>Pyeongchang, South Korea (2018)</strong> - Purpose-built, limited terrain variety</li><li><strong>Sarajevo, Bosnia (1984)</strong> - Historic but infrastructure is dated</li><li><strong>Garmisch-Partenkirchen, Germany (1936)</strong> - Kandahar run is expert only; family terrain limited</li></ul><p>These are interesting for ski history buffs but not first choices for family vacations.</p>"
                },
                {
                    "type": "faq",
                    "title": "Olympic Skiing FAQ",
                    "items": [
                        {
                            "question": "Can regular skiers actually ski Olympic downhill courses?",
                            "answer": "Yes, at most resorts they're open to the public as marked black runs. They're challenging but skiable by experts. The start gates are usually accessible via lift."
                        },
                        {
                            "question": "Are Olympic runs marked at the resorts?",
                            "answer": "Usually yes. Most resorts have signage, plaques, or trail names honoring their Olympic history. Park City and Whistler have excellent Olympic heritage markers."
                        },
                        {
                            "question": "Which resort is best for kids who want the 'Olympic experience'?",
                            "answer": "Park City. The Champions Run is skiable by intermediate kids, Utah Olympic Park offers bobsled rides and youth programs, and there's tons of Olympic memorabilia around town."
                        },
                        {
                            "question": "What's the steepest Olympic downhill run?",
                            "answer": "Kitzbühel's Hahnenkamm (World Championships, not Olympics) and Val d'Isère's La Face are among the steepest race courses in the world. La Face averages 34% grade with sections over 60%."
                        },
                        {
                            "question": "Which Olympic resort offers the best value?",
                            "answer": "Hakuba, Japan offers excellent value when you factor in food costs (amazing Japanese dining at reasonable prices), quality of skiing, and the unique cultural experience. Lake Placid is most affordable in North America."
                        }
                    ]
                },
                {
                    "type": "cta",
                    "cta": {
                        "text": "Browse All Resorts",
                        "href": "/resorts",
                        "variant": "primary"
                    }
                }
            ]
        },
        "seo_meta": {
            "title": "Ski Olympic Runs - Resorts Where You Can Ski Like a Champion",
            "description": "Ski the same runs as Olympic champions. 10 resorts where families can ski actual Olympic downhill courses, with difficulty and family ratings.",
            "keywords": ["ski Olympic runs", "Olympic ski resorts", "ski like an Olympian", "famous ski runs", "Olympic downhill courses", "family ski Olympic venues"]
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
