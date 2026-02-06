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
        "quick_take": """Write a single flowing paragraph of 40-65 words about {resort_name} for families.
Include: the resort's most distinctive feature, the ideal kid age range, one honest catch, and a memorable punchline.
Reference the {family_score}/10 family score.
No bullet points in the paragraph. Sound like a friend talking, not a travel brochure.
Then provide 2-3 "Perfect if..." and 1-2 "Skip it if..." bullets separately.""",
        "getting_there": """Write the "Getting There" section for {resort_name} in {country}.
Include:
- Nearest major airports with typical drive times. ALWAYS include the 3-letter IATA code in parentheses after the airport name, e.g., <strong>Zurich Airport (ZRH)</strong>, <strong>Innsbruck Airport (INN)</strong>
- Whether to rent a car or use shuttles
- Name specific transfer companies or shuttle services if known (e.g., "Four Seasons Travel", "Resort Express")
- Any tricky navigation tips (mountain roads, winter conditions)
- Pro tips for making travel easier with kids

Be practical and specific.
Use <strong> tags around business/service names AND airport names on first mention.""",
        "where_to_stay": """Write the "Where to Stay" section for {resort_name}.
Include:
- Name at least 3 specific hotels, lodges, or apartment complexes by their actual name
- Ski-in/ski-out options (if available)
- Budget-friendly picks (name the property)
- Mid-range family favorites (name the property)
- Best options for families with young kids (proximity to lifts, amenities)

Focus on practical advice for families, not luxury seekers.
Use <strong> tags around hotel/property names on first mention.""",
        "lift_tickets": """Write the "Lift Tickets & Passes" section for {resort_name}.
Include:
- Current lift ticket prices (adult/child/family if available)
- Multi-day discount patterns
- Any applicable passes (Epic, Ikon, regional passes)
- Kids ski free details if applicable
- Best value tips

Use specific prices from the research where available.""",
        "on_mountain": """Write the "On the Mountain" section for {resort_name}.
Include:
- Overview of terrain for different skill levels
- Best areas for beginners/kids
- Name specific ski schools by name (e.g., "Ski School Alpendorf", "Burton Learn to Ride")
- Name specific rental shops if known (e.g., "Intersport Bründl", "Christy Sports")
- Name specific on-mountain lunch spots or restaurants (e.g., "Panorama Alm", "Mid-Mountain Lodge")
- Any must-know tips about the mountain

Focus on family-relevant details, not expert terrain.
Use <strong> tags around business names on first mention.""",
        "off_mountain": """Write the "Off the Mountain" section for {resort_name}.
Include:
- Non-ski activities for families (name specific providers if known)
- Name specific restaurants with kid-friendly options (e.g., "Chez Vrony", "The Red Lion")
- Evening entertainment
- Name specific grocery stores (e.g., "SPAR", "Coop", "Billa") for self-catering families
- Village walkability

Help families plan their non-ski time.
Use <strong> tags around business names on first mention.""",
        "parent_reviews_summary": """Write a "What Parents Say" summary for {resort_name}.
Based on the review snippets provided, synthesize the key themes:
- What parents consistently love
- Common concerns or complaints
- Specific tips from experienced families
- Overall sentiment

Use direct quotes where impactful. Be honest about both positives and negatives.""",
    }

    prompt_template = section_prompts.get(section_name, "Write helpful content about {resort_name}.")
    formatted_prompt = prompt_template.format(**context)

    system_prompt = f"""You are writing content for Snowthere, a family ski resort guide.

VOICE PROFILE: {profile.name}
{profile.description}

TONE:
{chr(10).join(f'- {t}' for t in profile.tone)}

PATTERNS TO USE:
{chr(10).join(f'- {p}' for p in profile.patterns)}

AVOID:
{chr(10).join(f'- {a}' for a in profile.avoid)}

ALWAYS INCLUDE:
{chr(10).join(f'- {i}' for i in profile.include)}

CRITICAL BOLDING RULE:
Every business, hotel, restaurant, ski school, rental shop, grocery store, and airport mentioned by name MUST be wrapped in <strong> tags on first mention.
Do NOT bold generic terms like "the resort", "ski school" (generic), or "the village".
Only bold SPECIFIC named businesses (e.g., <strong>Hotel Schweizerhof</strong>, <strong>Intersport Bründl</strong>).

Format your response as HTML that will be rendered on the website. Use:
- <p> for paragraphs
- <strong> for named businesses/entities on first mention
- <ul>/<li> for lists
- <h3> for sub-sections if needed

Do NOT include the section title (like "Quick Take" or "Getting There") - that's added by the template.
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

Answers should be concise (2-4 sentences) but helpful. Use the instagram mom voice.
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

Title: 50-60 chars, include "Family Ski Guide"
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
            "title": f"{resort_name} Family Ski Guide | Snowthere",
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
