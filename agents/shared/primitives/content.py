"""Content generation primitives using Claude."""

from typing import Any

import anthropic

from ..config import settings
from ..voice_profiles import VoiceProfile, get_voice_profile


def get_claude_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


async def write_section(
    section_name: str,
    context: dict[str, Any],
    voice_profile: str = "snowthere_guide",
    max_tokens: int = 2500,
) -> str:
    """
    Generate a content section for a resort guide.

    Args:
        section_name: The section to write (quick_take, getting_there, etc.)
        context: Research data and resort info
        voice_profile: Voice profile to use
        max_tokens: Maximum tokens for response

    Returns:
        Generated content as HTML string
    """
    profile = get_voice_profile(voice_profile)
    client = get_claude_client()

    section_prompts = {
        "quick_take": """Write a single flowing paragraph of 50-90 words about {resort_name} for families.
Include: the resort's most distinctive feature, the ideal kid age range, one honest catch, and a memorable punchline.
Reference the {family_score}/10 family score.
No bullet points in the paragraph. Sound like a friend talking, not a travel brochure.
Then provide 2-3 "Perfect if..." and 1-2 "Skip it if..." bullets separately.""",
        "getting_there": """Write the "Getting There" section for {resort_name} in {country}.

Lead with whatever is most interesting about getting here: the scenic drive, the surprising shortcut, the chaos of a specific airport with car seats, the fact that it's shockingly close or annoyingly far. DON'T start with "Getting to X is..." That's what every guide writes. What would you text your friend first?

Cover these essentials (in whatever order serves the story):
- Nearest major airports with drive times. ALWAYS include the 3-letter IATA code: <strong>Zurich Airport (ZRH)</strong>
- Car vs shuttle vs train, and which you'd actually pick with kids
- Specific transfer companies or shuttle services if known, with <strong> tags
- Mountain road warnings or winter tire requirements
- One genuinely useful tip that saves time or money (not "bring snacks")

Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: an opinion, a moment, a comparison that only YOU would write.""",
        "where_to_stay": """Write the "Where to Stay" section for {resort_name}.

Lead with a take. Is this a town with amazing slopeside options? A place where apartments crush hotels for families? Somewhere with one standout property everyone should know about? Start with YOUR opinion, then back it up with specifics.

Cover these essentials (in whatever order serves the story):
- At least 3 named properties with <strong> tags on first mention
- Budget, mid-range, and higher-end tiers
- Ski-in/ski-out options if they exist
- What matters most for families with young kids (proximity to lifts, pool, kitchen)
- Nightly rates with context, vary how you introduce prices across paragraphs

Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: tell them which one YOU'D book and why.""",
        "lift_tickets": """Write the "Lift Tickets & Passes" section for {resort_name}.

Give the verdict fast. Is this a screaming deal or a premium price worth paying? How does the sticker shock (or lack of it) compare to resorts parents know? Commit to the numbers, no hedging.

Cover these essentials (in whatever order serves the story):
- Adult, child, and family day pass prices. Vary how you introduce them
- Multi-day discount patterns
- Applicable passes (Epic, Ikon, regional) and whether they're worth it here
- Kids ski free deals if applicable
- Your honest take: is the pricing fair for what you get?

IMPORTANT: Child prices are typically 50-70% of adult. If a child price looks suspiciously low (under €10/$10), it's likely an age number, not a price. Omit it.

Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: compare the value to something the reader already knows.""",
        "on_mountain": """Write the "On the Mountain" section for {resort_name}.

What's the one thing about skiing here that parents need to know? Maybe it's the incredible beginner area. Maybe it's that the terrain is honestly too advanced for little kids. Maybe it's the ski school that transforms non-skiers in 3 days. Lead with the thing that matters most, not a terrain percentage breakdown.

Cover these essentials (in whatever order serves the story):
- Beginner areas and how they compare to other resorts
- Named ski schools with <strong> tags, what ages they take, and whether they're good
- Named rental shops if known
- On-mountain lunch spots with <strong> tags. Use "think [dish], [dish], and [dish]" for food
- Foreign names with English translation in parentheses on first use

Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: what would your kid remember about skiing here?""",
        "off_mountain": """Write the "Off the Mountain" section for {resort_name}.

What's the vibe when the lifts close? Is this a one-street town where bedtime happens at 8pm? A lively village with actual things to do? A resort where you'll never leave the hotel complex? Paint the picture, then get specific.

Cover these essentials (in whatever order serves the story):
- Named restaurants with <strong> tags. Use "think [dish], [dish], and [dish]" for menus
- Non-ski activities for families
- Evening options (or honest lack thereof)
- Named grocery stores (<strong>SPAR</strong>, <strong>Coop</strong>, etc.) for self-catering
- Activity and meal prices with varied intros
- Foreign activity names with English in parentheses: Rodelbahn (toboggan run)
- Village walkability with kids

Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: what's the moment your kid will talk about at school on Monday?""",
        "parent_reviews_summary": """Write a "What Parents Say" summary for {resort_name}.

What's the real consensus? What do parents consistently say that matches (or contradicts) our take? This is where honest tension lives. If parents love something we think is overrated, say so and explain why. If there's a universal complaint, own it.

Cover these essentials (in whatever order serves the story):
- The consistent praise (what keeps coming up)
- The consistent complaints (don't hide these)
- Specific tips from experienced families
- Where parent opinion differs from the official line

Use direct quotes where they're genuinely impactful.
Every paragraph must stand alone (self-contained for AI extraction).
One personality beat: your honest reaction to what parents are saying.""",
    }

    prompt_template = section_prompts.get(section_name, "Write helpful content about {resort_name}.")
    formatted_prompt = prompt_template.format(**context)

    system_prompt = f"""You are writing for Snowthere, a family ski resort guide.

# YOUR VOICE
{profile.description}

Write like the parent in the school WhatsApp group who's already been everywhere,
is genuinely funny without trying hard, saves everyone money because they've done
the research, and occasionally says something that makes you think "finally, someone said it."

Your writing should be 70% perspective and personality, 30% pure information delivery.
If a paragraph could appear in any ski guide unchanged, it needs more you.

# PERSONALITY (internalize these, don't mechanically apply)
Have opinions. Don't present three hotels neutrally, tell them which one you'd book.
Don't list activities, tell them which one is worth the cold.
Your personality includes honest asides, dry humor, and real tension about tradeoffs
that emerge NATURALLY, never forced, never formulaic.

PERSONALITY TOOLKIT:
{chr(10).join(f'- {p}' for p in profile.patterns)}

TONE:
{chr(10).join(f'- {t}' for t in profile.tone)}

CONTENT STANDARDS:
{chr(10).join(f'- {i}' for i in profile.include)}

NEVER:
{chr(10).join(f'- {a}' for a in profile.avoid)}
- ZERO em-dashes (\u2014) or en-dashes (\u2013) anywhere. This is non-negotiable.
- For ranges: "\u20ac180 to \u20ac250" not "\u20ac180\u2013\u20ac250" or "\u20ac180-\u20ac250"

# CONTENT THAT GETS CITED
- Lead every section with your TAKE, not a description. Your first sentence
  should be the thing someone would quote when sharing this page.
- Every paragraph should be self-contained, make sense without the headline.
  AI systems extract paragraphs independently.
- Use the resort's full name (not "it") in key paragraphs. Named entities
  anchor AI embeddings.
- Include specific numbers with context and personality:
  "\u20ac180/night for slopeside four-star, in Meribel that gets you a studio apartment."
  Never write a bare price number without context.
- Cite sources when possible: "According to the tourism office" or "Based on
  2025-26 season pricing." Source attribution improves citation rates.
- Compare prices to reference points ("that's half what Vail charges").
- Wrap named businesses in <strong> tags on first mention (hotels, restaurants,
  ski schools, airports, NOT generic terms like "the resort" or "ski school").
- Translate foreign terms on first use: Rodelbahn (toboggan run).

# ANTI-REPETITION
- NEVER repeat the same fact, number, or observation twice on the page.
  If you've mentioned the access road, don't mention it again.
- Vary your vocabulary: don't use the same adjective in consecutive paragraphs.
- Each section should introduce NEW information, not rephrase earlier sections.

# PROSE QUALITY
- Every sentence must read naturally aloud. Don't drop articles (a, the, an).
- Use short sentences as punctuation. "That's the play." "Skip it." "Worth every cent."
  Then the evidence in longer sentences. The contrast is what creates energy.
- Pick a number and commit. "90 minutes from Geneva" not "roughly 1 hour and
  45 minutes from Geneva." Confidence = fewer qualifiers.
- Write in second person ("you'll find", "your kids will"), readers
  should see themselves in the scene.
- Put the reader in the moment. Not "the views are spectacular" but "your kids
  are looking at snow-covered peaks instead of the back of an airplane seat."
- One honest tension/tradeoff per section minimum. Don't sugarcoat.
- One pressure-release moment per section: a parenthetical aside, a vivid detail, or a deadpan observation.
- This should flow like a well-edited magazine piece, not a corporate email.

# FORMATTING
- Use <p>, <ul>/<li>, <h3> for structure
- Do NOT include the section title, it's added by the template
- Fewer sub-headers, more flowing narrative. This is a friend's advice, not a wiki article.

# WHEN DATA IS SPARSE
- Describe the TYPE of options with regional pricing context.
- Use country/region knowledge to fill gaps with honest guidance.
- Never write a section shorter than 200 words. If data is thin, provide regional context.
"""

    message = client.messages.create(
        model=settings.content_model,
        max_tokens=max_tokens,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Write the {section_name} section for this resort:\n\n{formatted_prompt}\n\nResearch context:\n{_format_context(context)}",
            }
        ],
    )

    return message.content[0].text


async def generate_faq(
    resort_name: str,
    country: str,
    context: dict[str, Any],
    num_questions: int = 6,
    voice_profile: str = "snowthere_guide",
) -> list[dict[str, str]]:
    """
    Generate FAQ section with Schema.org compatible Q&A pairs.

    Returns list of {"question": "...", "answer": "..."} dicts.
    """
    profile = get_voice_profile(voice_profile)
    client = get_claude_client()

    system_prompt = f"""You are writing FAQs for Snowthere, a family ski resort guide.

VOICE: {profile.name} - {profile.description}

Generate {num_questions} frequently asked questions that families would actually ask about {resort_name}.

Focus on:
- Practical family concerns (childcare, ski school, costs)
- Logistics (getting there, best time to visit)
- Value considerations (passes, deals)
- Kid-specific questions (terrain, age minimums)

Format as JSON array:
[
  {{"question": "Is {resort_name} good for beginners?", "answer": "..."}},
  ...
]

Answers should be concise (2-4 sentences) but helpful. Use the {profile.name} voice.

CRITICAL: Use exact numbers, never hedge. Say "$85" not "roughly $85" or "around $85" or "approximately $85". If you don't know the exact number, give a specific realistic estimate without hedging qualifiers.
"""

    message = client.messages.create(
        model=settings.content_model,
        max_tokens=2000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Generate {num_questions} FAQs for {resort_name}, {country}.\n\nContext:\n{_format_context(context)}",
            }
        ],
    )

    # Parse JSON from response
    import json

    response_text = message.content[0].text

    # Handle potential markdown code blocks
    if "```json" in response_text:
        response_text = response_text.split("```json")[1].split("```")[0]
    elif "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]

    try:
        faqs = json.loads(response_text.strip())
        return faqs
    except json.JSONDecodeError:
        # Return empty list if parsing fails
        return []


async def apply_voice(
    content: str,
    voice_profile: str = "snowthere_guide",
) -> str:
    """
    Transform existing content to match a voice profile.

    Use this to adjust tone of externally sourced or AI-generated content.
    """
    profile = get_voice_profile(voice_profile)
    client = get_claude_client()

    system_prompt = f"""Rewrite the following content to match this voice profile:

VOICE: {profile.name}
{profile.description}

TONE: {', '.join(profile.tone)}
PATTERNS: {', '.join(profile.patterns)}
AVOID: {', '.join(profile.avoid)}

Keep all factual information but adjust the tone and phrasing.
Output HTML formatted content.
"""

    message = client.messages.create(
        model=settings.content_model,
        max_tokens=2000,
        system=system_prompt,
        messages=[
            {
                "role": "user",
                "content": f"Rewrite this content:\n\n{content}",
            }
        ],
    )

    return message.content[0].text


async def generate_seo_meta(
    resort_name: str,
    country: str,
    quick_take: str,
) -> dict[str, str]:
    """
    Generate SEO metadata for a resort page.

    Returns {"title": "...", "description": "..."}.
    """
    client = get_claude_client()

    message = client.messages.create(
        model=settings.default_model,
        max_tokens=300,
        system="Generate SEO metadata. Be concise and include key terms families search for.",
        messages=[
            {
                "role": "user",
                "content": f"""Generate SEO title and meta description for this ski resort page:

Resort: {resort_name}, {country}
Quick Take: {quick_take[:500]}

Format as JSON: {{"title": "...", "description": "..."}}

Title: 50-60 chars, format "Family Ski Guide: [Resort] with Kids" (do NOT include "| Snowthere" — it's added by the frontend)
Description: 150-160 chars, focus on family value prop""",
            }
        ],
    )

    import json

    response_text = message.content[0].text
    if "```" in response_text:
        response_text = response_text.split("```")[1].split("```")[0]
        if response_text.startswith("json"):
            response_text = response_text[4:]

    try:
        return json.loads(response_text.strip())
    except json.JSONDecodeError:
        return {
            "title": f"Family Ski Guide: {resort_name} with Kids",
            "description": f"Complete family guide to skiing at {resort_name}. Kid-friendly terrain, costs, and honest parent reviews.",
        }


def _format_context(context: dict[str, Any]) -> str:
    """Format context dict as readable string for prompts."""
    lines = []
    for key, value in context.items():
        if isinstance(value, list):
            if value and isinstance(value[0], dict):
                # List of search results or similar
                lines.append(f"\n{key.upper()}:")
                for i, item in enumerate(value[:5], 1):  # Limit to 5 items
                    if hasattr(item, "title"):
                        lines.append(f"  {i}. {item.title}: {item.snippet[:200]}")
                    elif isinstance(item, dict):
                        lines.append(f"  {i}. {item.get('title', 'N/A')}: {item.get('snippet', str(item))[:200]}")
            else:
                lines.append(f"{key}: {', '.join(str(v) for v in value)}")
        elif isinstance(value, dict):
            lines.append(f"\n{key.upper()}:")
            for k, v in value.items():
                lines.append(f"  {k}: {v}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


# =============================================================================
# COUNTRY PAGE CONTENT
# =============================================================================


def generate_country_intro(
    country_name: str,
    resort_data: list[dict[str, Any]],
    voice_profile: str = "snowthere_guide",
) -> str:
    """
    Generate an intro paragraph for a country index page.

    Addresses the parent question: "Should we ski in [Country]?"
    Includes price comparison, standout resorts, and practical tips.

    Args:
        country_name: Country name (e.g., "Austria")
        resort_data: List of dicts with keys: name, family_score, daily_cost, best_ages
        voice_profile: Voice profile to use

    Returns:
        200-300 word intro as plain text (not HTML)
    """
    profile = get_voice_profile(voice_profile)
    client = get_claude_client()

    # Build resort summary for context
    resort_summaries = []
    for r in resort_data[:10]:  # Limit context to 10 resorts
        parts = [r.get("name", "Unknown")]
        if r.get("family_score"):
            parts.append(f"score {r['family_score']}/10")
        if r.get("daily_cost"):
            parts.append(f"~${r['daily_cost']}/day")
        if r.get("best_ages"):
            parts.append(f"ages {r['best_ages']}")
        resort_summaries.append(" | ".join(parts))

    resorts_context = "\n".join(resort_summaries) if resort_summaries else "No resorts yet"

    avg_cost = None
    costs = [r["daily_cost"] for r in resort_data if r.get("daily_cost")]
    if costs:
        avg_cost = sum(costs) / len(costs)

    system_prompt = f"""You are writing content for Snowthere, a family ski resort guide.

VOICE PROFILE: {profile.name}
{profile.description}

TONE:
{chr(10).join(f'- {t}' for t in profile.tone)}

PATTERNS TO USE:
{chr(10).join(f'- {p}' for p in profile.patterns)}

AVOID:
{chr(10).join(f'- {a}' for a in profile.avoid)}

Write a 200-300 word flowing paragraph. No headings, bullet points, or HTML tags. Plain text only."""

    prompt = f"""Write a 200-300 word intro for a page listing family ski resorts in {country_name}.

CONTEXT:
- {len(resort_data)} family ski resorts in {country_name}
{f'- Average daily family cost: ~${avg_cost:.0f}' if avg_cost else ''}
- Resort details:
{resorts_context}

REQUIREMENTS:
1. Answer the parent's question: "Should we ski in {country_name}?"
2. If European: mention the value angle (often cheaper than US resorts when you include lodging/food)
3. Call out 2-3 standout resorts by name with why they're notable
4. Include one practical tip (e.g., best time to visit, booking tip)
5. End with an encouraging, actionable sentence
6. Do NOT be generic — reference specific data from the resort list"""

    message = client.messages.create(
        model=settings.default_model,
        max_tokens=500,
        system=system_prompt,
        messages=[{"role": "user", "content": prompt}],
    )

    return message.content[0].text.strip()
