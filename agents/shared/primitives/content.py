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
    voice_profile: str = "instagram_mom",
    max_tokens: int = 1500,
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
        "getting_there": """Open with a self-contained sentence about what getting to {resort_name} is actually like. Don't assume the reader sees the section headline. Use future-casting: "You'll fly into...", "You'll want to..."

Write the "Getting There" section for {resort_name} in {country}.
Include:
- Nearest major airports with typical drive times. ALWAYS include the 3-letter IATA code in parentheses after the airport name, e.g., <strong>Zurich Airport (ZRH)</strong>, <strong>Innsbruck Airport (INN)</strong>
- Whether to rent a car or use shuttles. Use "from...to" for time ranges and "Expect to pay" before transfer costs
- Name specific transfer companies or shuttle services if known (e.g., "Four Seasons Travel", "Resort Express")
- Any tricky navigation tips (mountain roads, winter conditions)
- Pro tips for making travel easier with kids

Write as if talking to a friend planning their trip. Use "you'll" frequently.
Use <strong> tags around business/service names AND airport names on first mention.""",
        "where_to_stay": """Open with a self-contained sentence about the lodging situation at {resort_name}. Don't assume the reader sees the headline. Use "There's a [property] that..." to introduce standout options with personality.

Write the "Where to Stay" section for {resort_name}.
Include:
- Name at least 3 specific hotels, lodges, or apartment complexes by their actual name
- Ski-in/ski-out options (if available)
- Budget-friendly picks (name the property)
- Mid-range family favorites (name the property)
- Best options for families with young kids (proximity to lifts, amenities)
- Use "Expect to pay" before nightly rates. Compare to reference points when possible

Use future-casting: "You'll be [distance] from the lifts", "Your kids will love the [feature]".
Focus on practical advice for families, not luxury seekers.
Use <strong> tags around hotel/property names on first mention.""",
        "lift_tickets": """Open with a self-contained sentence about lift ticket pricing at {resort_name}. Don't assume the reader sees the headline. Compare to a well-known reference point so the reader immediately knows if this is cheap or expensive.

Write the "Lift Tickets & Passes" section for {resort_name}.
Include:
- Use "Expect to pay" before ALL prices (e.g., "Expect to pay around €55 for an adult day pass")
- Current lift ticket prices (adult/child/family if available)
- Multi-day discount patterns with "from...to" ranges
- Any applicable passes (Epic, Ikon, regional passes)
- Kids ski free details if applicable
- Best value tips

IMPORTANT: Double-check that child prices make sense (typically 50-70% of adult price). If child price looks suspiciously low (under €10/$10), it's likely an age number, not a price. Omit it.
Use specific prices from the research where available.""",
        "on_mountain": """Open with a self-contained sentence about what skiing at {resort_name} is actually like for families. Don't assume the reader sees the headline. Help parents visualize their family's actual day using future-casting.

Write the "On the Mountain" section for {resort_name}.
Include:
- "You'll find..." to introduce terrain variety
- Best areas for beginners/kids with "Your kids will..." predictions
- Name specific ski schools by name. Use "There's a [school] that [what makes it special]" to introduce them
- Name specific rental shops if known
- Name specific on-mountain lunch spots. Use "think [dish], [dish], and [dish]" for food descriptions
- Any must-know tips about the mountain
- Foreign names followed by English translation in parentheses on first use

Focus on family-relevant details, not expert terrain.
Use <strong> tags around business names on first mention.""",
        "off_mountain": """Open with a self-contained sentence about what {resort_name}'s town/village is actually like when you're off the slopes. Don't assume the reader sees the headline. This is where personality shines: apres-ski, village life, the stuff kids remember.

Write the "Off the Mountain" section for {resort_name}.
Include:
- Non-ski activities introduced with "There's a [activity] that..." or "You'll find..."
- Name specific restaurants. Use "think [dish], [dish], and [dish]" for menu descriptions
- Evening entertainment — what will your family actually do after skiing?
- Name specific grocery stores (e.g., "SPAR", "Coop", "Billa") for self-catering families
- Use "Expect to pay" before meal/activity prices
- Foreign activity names with English translation in parentheses (e.g., Rodelbahn (toboggan run))
- Village walkability

Help families envision their non-ski time. Use "you'll" and "your kids will" frequently.
Use <strong> tags around business names on first mention.""",
        "parent_reviews_summary": """Open with a self-contained sentence summarizing what parents actually say about {resort_name}. Don't assume the reader sees the headline. Synthesize like a friend summarizing what they've heard.

Write a "What Parents Say" summary for {resort_name}.
Based on the review snippets provided, synthesize the key themes:
- What parents consistently love — use "You'll hear..." to introduce common praise
- Common concerns or complaints — be honest
- Specific tips from experienced families
- Overall sentiment

Use direct quotes where impactful. Be honest about both positives and negatives.
Use future-casting: "You'll notice...", "Your kids will...".""",
    }

    prompt_template = section_prompts.get(section_name, "Write helpful content about {resort_name}.")
    formatted_prompt = prompt_template.format(**context)

    system_prompt = f"""You are writing for Snowthere, a family ski resort guide.

# YOUR VOICE
{profile.description}

You write like a smart, well-traveled friend who's done this trip and respects
the reader's time. You have personality: honest asides, dry humor, real tension
about tradeoffs. You're not a brochure. You're not clinical. People enjoy reading you.

# PERSONALITY (internalize these, don't mechanically apply)
Your writing personality includes honest asides ("Pro tip:", "Locals know:",
parenthetical humor) that emerge NATURALLY, never forced, never formulaic.
Use them when they genuinely add value, not as decoration.

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
- Include specific numbers with context: "Expect to pay around \u20ac180 per night"
  not just "\u20ac180." Never write a bare price number.
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
- Vary sentence length naturally. Long sentences carry evidence.
  Short ones carry verdicts. Let rhythm emerge, don't force a ratio.
- Write in second person ("you'll find", "your kids will"), readers
  should see themselves in the scene.
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
    voice_profile: str = "instagram_mom",
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
    voice_profile: str = "instagram_mom",
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

Title: 50-60 chars, format "Family Ski Guide: [Resort] with Kids | Snowthere"
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
            "title": f"Family Ski Guide: {resort_name} with Kids | Snowthere",
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
    voice_profile: str = "instagram_mom",
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
