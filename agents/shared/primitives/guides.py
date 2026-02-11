"""Guide primitives for autonomous guide content generation.

Agent-native design principles:
- Atomic, composable operations
- Claude generates content, database validates structure
- Topic discovery → planning → generation → approval flow

Usage:
    from shared.primitives.guides import discover_topics, create_guide, publish_guide

    # Discover topics
    topics = await discover_topics(max_topics=5)

    # Create a guide
    guide = await create_guide(
        title="Best Resorts for Toddlers",
        guide_type="comparison",
        category="toddlers",
    )

    # Publish when ready
    await publish_guide(guide["id"])
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import anthropic

from ..config import settings
from ..supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

PT_TIMEZONE = ZoneInfo("America/Los_Angeles")


# =============================================================================
# DATA CLASSES
# =============================================================================


@dataclass
class GuideCandidate:
    """A potential guide topic discovered from various sources."""

    title: str
    guide_type: str  # comparison, how-to, regional, pass, seasonal, gear
    category: str | None = None
    priority_score: float = 0.5
    source: str = "unknown"  # keyword, gap, seasonal, cluster
    reasoning: str = ""
    suggested_resorts: list[str] = field(default_factory=list)


@dataclass
class GuideOutline:
    """Planned structure for a guide."""

    title: str
    guide_type: str
    category: str | None
    sections: list[dict[str, Any]]
    featured_resort_ids: list[str] = field(default_factory=list)
    seo_meta: dict[str, Any] = field(default_factory=dict)
    excerpt: str = ""


@dataclass
class GuideSection:
    """A section of guide content."""

    section_type: str  # intro, list, checklist, comparison_table, faq, cta, text
    title: str | None = None
    content: str | None = None  # HTML content for intro/text
    items: list[dict[str, Any]] = field(default_factory=list)  # For list/checklist/faq
    columns: list[str] = field(default_factory=list)  # For comparison tables
    rows: list[list[str]] = field(default_factory=list)  # For comparison tables


@dataclass
class GuideGenerationResult:
    """Result of guide generation."""

    success: bool
    message: str
    guide_id: str | None = None
    slug: str | None = None
    title: str | None = None
    error: str | None = None


# =============================================================================
# GUIDE CRUD
# =============================================================================


def create_guide(
    title: str,
    guide_type: str,
    content: dict[str, Any],
    category: str | None = None,
    excerpt: str | None = None,
    featured_image_url: str | None = None,
    seo_meta: dict[str, Any] | None = None,
    featured_resort_ids: list[str] | None = None,
    author: str = "Snowthere Team",
    status: str = "draft",
) -> dict[str, Any]:
    """
    Create a new guide in the database.

    Args:
        title: Guide title
        guide_type: One of: comparison, how-to, regional, pass, seasonal, gear
        content: JSONB content with sections array
        category: Optional category for grouping
        excerpt: Short description for listings
        featured_image_url: Hero image URL
        seo_meta: SEO metadata dict
        featured_resort_ids: Array of resort UUIDs
        author: Author name
        status: draft, published, or archived

    Returns:
        Created guide record
    """
    supabase = get_supabase_client()

    # Generate slug from title
    slug = _slugify(title)

    # Check for existing slug
    existing = supabase.table("guides").select("id").eq("slug", slug).execute()
    if existing.data:
        # Append number to make unique
        base_slug = slug
        counter = 2
        while True:
            slug = f"{base_slug}-{counter}"
            check = supabase.table("guides").select("id").eq("slug", slug).execute()
            if not check.data:
                break
            counter += 1

    data = {
        "slug": slug,
        "title": title,
        "guide_type": guide_type,
        "content": content,
        "category": category,
        "excerpt": excerpt,
        "featured_image_url": featured_image_url,
        "seo_meta": seo_meta or {},
        "featured_resort_ids": featured_resort_ids or [],
        "author": author,
        "status": status,
    }

    result = supabase.table("guides").insert(data).execute()

    if result.data:
        return result.data[0]

    raise Exception("Failed to create guide")


def update_guide(
    guide_id: str,
    **updates: Any,
) -> dict[str, Any]:
    """
    Update a guide.

    Args:
        guide_id: UUID of the guide
        **updates: Fields to update

    Returns:
        Updated guide record
    """
    supabase = get_supabase_client()

    # Filter to allowed fields
    allowed = {
        "title", "content", "category", "excerpt", "featured_image_url",
        "seo_meta", "featured_resort_ids", "author", "status", "published_at",
    }
    filtered = {k: v for k, v in updates.items() if k in allowed}

    if not filtered:
        raise ValueError("No valid fields to update")

    result = supabase.table("guides").update(filtered).eq("id", guide_id).execute()

    if result.data:
        return result.data[0]

    raise Exception(f"Failed to update guide {guide_id}")


def get_guide(guide_id: str) -> dict[str, Any] | None:
    """Get a guide by ID."""
    supabase = get_supabase_client()
    result = supabase.table("guides").select("*").eq("id", guide_id).execute()
    return result.data[0] if result.data else None


def get_guide_by_slug(slug: str) -> dict[str, Any] | None:
    """Get a guide by slug."""
    supabase = get_supabase_client()
    result = supabase.table("guides").select("*").eq("slug", slug).execute()
    return result.data[0] if result.data else None


def list_guides(
    status: str | None = None,
    guide_type: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    """List guides with optional filters."""
    supabase = get_supabase_client()

    query = supabase.table("guides").select("*")

    if status:
        query = query.eq("status", status)
    if guide_type:
        query = query.eq("guide_type", guide_type)

    result = query.order("created_at", desc=True).limit(limit).execute()
    return result.data or []


def publish_guide(guide_id: str) -> dict[str, Any]:
    """
    Publish a guide.

    Args:
        guide_id: UUID of the guide

    Returns:
        Updated guide record
    """
    return update_guide(
        guide_id,
        status="published",
        published_at=datetime.now(PT_TIMEZONE).isoformat(),
    )


def archive_guide(guide_id: str) -> dict[str, Any]:
    """Archive a guide."""
    return update_guide(guide_id, status="archived")


# =============================================================================
# GUIDE-RESORT RELATIONSHIPS
# =============================================================================


def link_resorts_to_guide(
    guide_id: str,
    resort_links: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """
    Link resorts to a guide with optional highlight reasons.

    Args:
        guide_id: UUID of the guide
        resort_links: List of dicts with resort_id, display_order, highlight_reason

    Returns:
        Created link records
    """
    supabase = get_supabase_client()

    # Clear existing links
    supabase.table("guide_resorts").delete().eq("guide_id", guide_id).execute()

    # Insert new links
    links = []
    for i, link in enumerate(resort_links):
        links.append({
            "guide_id": guide_id,
            "resort_id": link["resort_id"],
            "display_order": link.get("display_order", i),
            "highlight_reason": link.get("highlight_reason"),
        })

    if links:
        result = supabase.table("guide_resorts").insert(links).execute()
        return result.data or []

    return []


def get_guide_resorts(guide_id: str) -> list[dict[str, Any]]:
    """Get resorts linked to a guide."""
    supabase = get_supabase_client()

    result = supabase.table("guide_resorts").select(
        "*, resort:resorts(id, name, slug, country, tagline)"
    ).eq("guide_id", guide_id).order("display_order").execute()

    return result.data or []


# =============================================================================
# TOPIC DISCOVERY
# =============================================================================


def _get_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _call_claude(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 2000,
) -> str:
    """Make a Claude API call and return the text response."""
    client = _get_client()
    messages = [{"role": "user", "content": prompt}]
    kwargs = {"model": model, "max_tokens": max_tokens, "messages": messages}
    if system:
        kwargs["system"] = system
    response = client.messages.create(**kwargs)
    return response.content[0].text


def _parse_json_response(response: str) -> dict[str, Any]:
    """Parse JSON from Claude response, handling markdown code blocks."""
    text = response.strip()
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]
    return json.loads(text.strip())


async def discover_topics(max_topics: int = 10) -> list[GuideCandidate]:
    """
    Discover potential guide topics from multiple sources.

    Sources:
    1. Content gaps - What guides don't exist yet?
    2. Seasonal opportunities - What's timely?
    3. Resort clusters - What groups of resorts could be compared?
    4. Search demand signals - What are families searching for?

    Args:
        max_topics: Maximum number of topics to return

    Returns:
        List of GuideCandidate objects ranked by priority
    """
    supabase = get_supabase_client()
    candidates = []

    # 1. Identify content gaps
    existing_guides = list_guides(status="published", limit=100)
    existing_topics = [g["title"].lower() for g in existing_guides]

    # 2. Get seasonal context
    now = datetime.now(PT_TIMEZONE)
    seasonal = _get_seasonal_guide_opportunities(now)
    for s in seasonal:
        if s["title"].lower() not in existing_topics:
            candidates.append(GuideCandidate(
                title=s["title"],
                guide_type=s["guide_type"],
                category=s.get("category"),
                priority_score=s.get("priority", 0.7),
                source="seasonal",
                reasoning=s.get("reasoning", "Timely seasonal content"),
            ))

    # 3. Find resort clusters
    resorts = supabase.table("resorts").select(
        "id, name, country, region"
    ).eq("status", "published").execute()

    if resorts.data:
        clusters = _find_resort_clusters(resorts.data)
        for cluster in clusters:
            title = cluster["suggested_title"]
            if title.lower() not in existing_topics:
                candidates.append(GuideCandidate(
                    title=title,
                    guide_type="comparison",
                    category=cluster.get("category"),
                    priority_score=cluster.get("priority", 0.6),
                    source="cluster",
                    reasoning=cluster.get("reasoning", "Resort cluster opportunity"),
                    suggested_resorts=cluster.get("resort_ids", []),
                ))

    # 4. Use Claude to prioritize and suggest additional topics
    candidates = await _claude_prioritize_topics(candidates, existing_topics, max_topics)

    return candidates[:max_topics]


def _get_seasonal_guide_opportunities(date: datetime) -> list[dict[str, Any]]:
    """Get timely seasonal guide opportunities."""
    month = date.month
    opportunities = []

    # Spring break planning (Jan-Feb)
    if month in [1, 2]:
        opportunities.extend([
            {
                "title": "Spring Break Skiing: Best Resorts for Families",
                "guide_type": "seasonal",
                "category": "spring-break",
                "priority": 0.9,
                "reasoning": "Peak spring break planning season",
            },
            {
                "title": "March Skiing: Best Snow & Fewer Crowds",
                "guide_type": "seasonal",
                "category": "timing",
                "priority": 0.8,
                "reasoning": "March trip planning window",
            },
        ])

    # Next season planning (Apr-Jun)
    elif month in [4, 5, 6]:
        opportunities.extend([
            {
                "title": "Early Bird Passes: Epic vs Ikon 2026-27",
                "guide_type": "pass",
                "category": "ski-passes",
                "priority": 0.9,
                "reasoning": "Pass early-bird sale season",
            },
            {
                "title": "Planning Your Family Ski Trip: 2026-27 Season",
                "guide_type": "how-to",
                "category": "planning",
                "priority": 0.85,
                "reasoning": "Early planning = best deals",
            },
        ])

    # Pre-season (Sep-Nov)
    elif month in [9, 10, 11]:
        opportunities.extend([
            {
                "title": "Holiday Skiing: Best Resorts for Christmas Week",
                "guide_type": "seasonal",
                "category": "holidays",
                "priority": 0.9,
                "reasoning": "Holiday booking season",
            },
            {
                "title": "First-Timer's Guide: Your Kid's First Ski Trip",
                "guide_type": "how-to",
                "category": "beginners",
                "priority": 0.8,
                "reasoning": "Season opener excitement",
            },
        ])

    # Peak season (Dec-Mar)
    elif month in [12, 1, 2, 3]:
        opportunities.extend([
            {
                "title": "Avoiding Crowds: Best Ski Days & Times",
                "guide_type": "how-to",
                "category": "timing",
                "priority": 0.85,
                "reasoning": "Peak season crowd concerns",
            },
        ])

    return opportunities


def _find_resort_clusters(resorts: list[dict]) -> list[dict[str, Any]]:
    """Find clusters of resorts that could make good comparison guides."""
    clusters = []

    # Group by country
    by_country: dict[str, list[dict]] = {}
    for r in resorts:
        country = r.get("country", "Unknown")
        if country not in by_country:
            by_country[country] = []
        by_country[country].append(r)

    # Countries with 3+ resorts = regional guide opportunity
    for country, country_resorts in by_country.items():
        if len(country_resorts) >= 3:
            clusters.append({
                "suggested_title": f"Family Skiing in {country}: Complete Guide",
                "guide_type": "regional",
                "category": country.lower().replace(" ", "-"),
                "priority": 0.7,
                "reasoning": f"{len(country_resorts)} resorts in {country}",
                "resort_ids": [r["id"] for r in country_resorts],
            })

    # Group by region within US
    us_resorts = by_country.get("United States", [])
    if us_resorts:
        by_region: dict[str, list[dict]] = {}
        for r in us_resorts:
            region = r.get("region", "Unknown")
            if region and region != "Unknown":
                if region not in by_region:
                    by_region[region] = []
                by_region[region].append(r)

        for region, region_resorts in by_region.items():
            if len(region_resorts) >= 2:
                clusters.append({
                    "suggested_title": f"{region} Family Ski Resorts Compared",
                    "guide_type": "comparison",
                    "category": region.lower().replace(" ", "-"),
                    "priority": 0.65,
                    "reasoning": f"{len(region_resorts)} resorts in {region}",
                    "resort_ids": [r["id"] for r in region_resorts],
                })

    return clusters


async def _claude_prioritize_topics(
    candidates: list[GuideCandidate],
    existing_topics: list[str],
    max_topics: int,
) -> list[GuideCandidate]:
    """Use Claude to prioritize topics and suggest gaps."""
    if not candidates:
        # Generate some starter topics if we have none
        candidates = _get_evergreen_topics()

    candidate_data = [
        {
            "title": c.title,
            "guide_type": c.guide_type,
            "priority_score": c.priority_score,
            "source": c.source,
        }
        for c in candidates
    ]

    prompt = f"""You are prioritizing guide topics for Snowthere, a family ski directory.

EXISTING GUIDES (don't duplicate):
{json.dumps(existing_topics[:20], indent=2)}

CANDIDATE TOPICS:
{json.dumps(candidate_data, indent=2)}

TASK:
1. Rank these candidates by value to families (0.0-1.0)
2. Suggest 2-3 high-value topics that are missing
3. Explain your reasoning briefly

GUIDE TYPES:
- comparison: Best resorts for X, X vs Y
- how-to: Practical guides, checklists, tips
- regional: Country/state specific guides
- pass: Ski pass guides (Epic, Ikon, etc.)
- seasonal: Timing-based guides (spring break, holidays)
- gear: Equipment and packing guides

Return JSON:
{{
    "ranked_candidates": [
        {{"title": "...", "guide_type": "...", "priority_score": 0.8, "reasoning": "..."}}
    ],
    "suggested_new": [
        {{"title": "...", "guide_type": "...", "priority_score": 0.7, "reasoning": "..."}}
    ]
}}"""

    system = """You are a content strategist for a family ski website.
Prioritize topics that:
1. Help parents make decisions (which resort? when to go?)
2. Save families money (deals, passes, value)
3. Make skiing with kids easier (tips, checklists, age guides)
4. Fill genuine content gaps"""

    try:
        response = _call_claude(prompt, system=system, max_tokens=2000)
        parsed = _parse_json_response(response)

        # Merge prioritized candidates
        result = []

        for item in parsed.get("ranked_candidates", []):
            result.append(GuideCandidate(
                title=item["title"],
                guide_type=item["guide_type"],
                priority_score=float(item.get("priority_score", 0.5)),
                source="prioritized",
                reasoning=item.get("reasoning", ""),
            ))

        for item in parsed.get("suggested_new", []):
            if item["title"].lower() not in existing_topics:
                result.append(GuideCandidate(
                    title=item["title"],
                    guide_type=item["guide_type"],
                    priority_score=float(item.get("priority_score", 0.6)),
                    source="claude_suggested",
                    reasoning=item.get("reasoning", ""),
                ))

        # Sort by priority
        result.sort(key=lambda x: x.priority_score, reverse=True)
        return result[:max_topics]

    except Exception as e:
        logger.error(f"Claude prioritization failed: {e}")
        return candidates


def _get_evergreen_topics() -> list[GuideCandidate]:
    """Get evergreen guide topics that are always relevant."""
    return [
        GuideCandidate(
            title="Best Ski Resorts for Toddlers (Ages 2-5)",
            guide_type="comparison",
            category="toddlers",
            priority_score=0.85,
            source="evergreen",
            reasoning="High-demand evergreen content",
        ),
        GuideCandidate(
            title="Family Ski Trip Packing Checklist",
            guide_type="how-to",
            category="packing",
            priority_score=0.8,
            source="evergreen",
            reasoning="Practical, shareable content",
        ),
        GuideCandidate(
            title="Epic vs Ikon Pass: Which Is Better for Families?",
            guide_type="pass",
            category="ski-passes",
            priority_score=0.75,
            source="evergreen",
            reasoning="Evergreen decision guide",
        ),
        GuideCandidate(
            title="Your First Family Ski Trip: Complete Guide",
            guide_type="how-to",
            category="beginners",
            priority_score=0.8,
            source="evergreen",
            reasoning="Entry point for new ski families",
        ),
        GuideCandidate(
            title="Best Budget Family Ski Resorts",
            guide_type="comparison",
            category="budget",
            priority_score=0.75,
            source="evergreen",
            reasoning="Cost is top family concern",
        ),
    ]


# =============================================================================
# CONTENT GENERATION
# =============================================================================


async def plan_guide_structure(
    topic: GuideCandidate,
    research_data: dict[str, Any] | None = None,
) -> GuideOutline:
    """
    Plan the structure of a guide.

    Args:
        topic: The guide topic to plan
        research_data: Optional research context

    Returns:
        GuideOutline with sections planned
    """
    prompt = f"""Plan the structure for a family ski guide.

GUIDE:
- Title: {topic.title}
- Type: {topic.guide_type}
- Category: {topic.category}
- Context: {topic.reasoning}

{f"RESEARCH DATA: {json.dumps(research_data, indent=2)[:3000]}" if research_data else ""}

SECTION TYPES AVAILABLE:
- intro: Opening paragraph, sets context (required)
- list: Numbered list with name/description (for rankings, recommendations)
- checklist: Checkbox items (for packing lists, to-dos)
- comparison_table: Table with columns and rows (for side-by-side comparisons)
- text: Prose sections with headers (for explanations, tips)
- faq: Question/answer pairs (required for SEO)
- cta: Call-to-action (usually at end)

REQUIREMENTS:
1. Plan 5-8 sections
2. Start with intro, end with faq and/or cta
3. Choose section types that match the guide type
4. For comparison guides: include a comparison_table
5. For how-to guides: include at least one checklist
6. Write a compelling excerpt (1-2 sentences, <160 chars for SEO)

Return JSON:
{{
    "title": "...",
    "guide_type": "...",
    "category": "...",
    "excerpt": "...",
    "sections": [
        {{"type": "intro", "title": null, "description": "What to write"}},
        {{"type": "list", "title": "Section Title", "description": "What to cover"}},
        ...
    ],
    "seo_meta": {{
        "title": "SEO Title | Snowthere",
        "description": "Meta description (<160 chars)",
        "keywords": ["keyword1", "keyword2"]
    }}
}}"""

    system = """You are a content strategist for a family ski website.
Plan practical, actionable guides that help parents make decisions.
Keep sections focused - don't try to cover everything in one guide."""

    try:
        response = _call_claude(prompt, system=system, max_tokens=1500)
        parsed = _parse_json_response(response)

        return GuideOutline(
            title=parsed.get("title", topic.title),
            guide_type=parsed.get("guide_type", topic.guide_type),
            category=parsed.get("category", topic.category),
            sections=parsed.get("sections", []),
            seo_meta=parsed.get("seo_meta", {}),
            excerpt=parsed.get("excerpt", ""),
        )

    except Exception as e:
        logger.error(f"Guide planning failed: {e}")
        # Return a basic outline
        return GuideOutline(
            title=topic.title,
            guide_type=topic.guide_type,
            category=topic.category,
            sections=[
                {"type": "intro", "title": None, "description": "Introduction"},
                {"type": "text", "title": "Overview", "description": "Main content"},
                {"type": "faq", "title": "FAQ", "description": "Common questions"},
            ],
            excerpt=f"A guide to {topic.title.lower()} for family ski trips.",
        )


async def generate_guide_content(
    outline: GuideOutline,
    research_data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Generate full guide content from an outline.

    Args:
        outline: The guide structure to fill
        research_data: Research context for content generation

    Returns:
        Complete content dict ready for database
    """
    sections = []

    for section_plan in outline.sections:
        section = await _generate_section(
            section_plan,
            outline,
            research_data,
        )
        sections.append(section)

    return {
        "sections": sections,
    }


async def _generate_section(
    section_plan: dict[str, Any],
    outline: GuideOutline,
    research_data: dict[str, Any] | None,
) -> dict[str, Any]:
    """Generate a single section of content."""
    section_type = section_plan.get("type", "text")
    title = section_plan.get("title")
    description = section_plan.get("description", "")

    prompt = f"""Generate content for a guide section.

GUIDE: {outline.title} ({outline.guide_type})
SECTION: {section_type}
{f"TITLE: {title}" if title else ""}
DESCRIPTION: {description}

{f"RESEARCH DATA: {json.dumps(research_data, indent=2)[:2000]}" if research_data else ""}

VOICE: Snowthere - smart, practical, encouraging. Like a well-traveled friend who respects your time.
- Write in second person ("you", "your family")
- Lead with your take, not a description. First sentence should be independently quotable.
- Be specific: real numbers, real names, real tips
- Cite sources when known ("According to...", "Based on 2025-26 pricing")
- Never repeat information across sections

FORMAT REQUIREMENTS FOR {section_type.upper()}:

"""

    if section_type == "intro":
        prompt += """Return JSON:
{"type": "intro", "content": "<p>HTML paragraph(s) here</p>"}

- 2-3 paragraphs
- Hook the reader immediately
- Set expectations for what they'll learn
- Use <p> tags"""

    elif section_type == "list":
        prompt += """Return JSON:
{"type": "list", "title": "Section Title", "items": [
    {"name": "Item Name", "description": "1-2 sentence description", "resort_slug": "country/resort-slug or null"},
    ...
]}

- 3-7 items
- Include resort_slug if mentioning a specific resort (format: country/resort-slug)
- Descriptions should be specific and actionable"""

    elif section_type == "checklist":
        prompt += """Return JSON:
{"type": "checklist", "title": "Section Title", "items": [
    {"text": "Checklist item text"},
    ...
]}

- 8-15 items
- Start each with action verb when appropriate
- Group logically (but flat list, not nested)"""

    elif section_type == "comparison_table":
        prompt += """Return JSON:
{"type": "comparison_table", "title": "Section Title", "columns": ["Column1", "Column2", ...], "rows": [
    ["Row1 Col1", "Row1 Col2", ...],
    ...
]}

- 3-5 columns
- 4-8 rows
- First column usually is the item being compared
- Keep cells concise"""

    elif section_type == "faq":
        prompt += """Return JSON:
{"type": "faq", "title": "Frequently Asked Questions", "items": [
    {"question": "Question text?", "answer": "Answer text"},
    ...
]}

- 4-6 questions
- Real questions families ask
- Concise but complete answers"""

    elif section_type == "cta":
        prompt += """Return JSON:
{"type": "cta", "cta": {
    "text": "Button text",
    "href": "/path",
    "variant": "primary"
}}

- Link to quiz, resorts, or specific guide
- Compelling action-oriented text"""

    else:  # text
        prompt += """Return JSON:
{"type": "text", "title": "Section Title", "content": "<p>HTML content</p>"}

- 2-4 paragraphs
- Use <p>, <strong>, <ul>/<li> as needed
- Practical, actionable content"""

    system = "You are writing content for Snowthere. Be smart, practical, and specific. Lead with your take, not a description. Return valid JSON only."

    try:
        response = _call_claude(prompt, system=system, max_tokens=1500)
        return _parse_json_response(response)
    except Exception as e:
        logger.error(f"Section generation failed: {e}")
        return {"type": section_type, "title": title, "content": "<p>Content generation failed.</p>"}


# =============================================================================
# HELPERS
# =============================================================================


def _slugify(text: str) -> str:
    """Convert text to URL-safe slug."""
    import re
    from unidecode import unidecode

    # Transliterate unicode to ASCII
    text = unidecode(text)

    # Convert to lowercase
    text = text.lower()

    # Replace spaces and special chars with hyphens
    text = re.sub(r'[^a-z0-9]+', '-', text)

    # Remove leading/trailing hyphens
    text = text.strip('-')

    # Collapse multiple hyphens
    text = re.sub(r'-+', '-', text)

    return text


def check_guide_exists(title: str) -> bool:
    """Check if a guide with similar title already exists."""
    slug = _slugify(title)
    existing = get_guide_by_slug(slug)
    return existing is not None
