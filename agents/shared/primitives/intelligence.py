"""Intelligence primitives - LLM-based reasoning for Agent Native decisions.

These primitives wrap Claude calls for common decision patterns, enabling
flexible, context-aware reasoning instead of rigid formulas.

Design Principle: Use fast models (Haiku) for routine decisions to keep
costs low (~$0.002 per call) while maintaining intelligence.
"""

import json
from dataclasses import dataclass, field
from typing import Any

import anthropic

from ..config import settings


@dataclass
class QualityAssessment:
    """Result of data quality assessment."""

    confidence: float  # 0.0 - 1.0
    reasoning: str
    missing_critical: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    red_flags: list[str] = field(default_factory=list)
    strengths: list[str] = field(default_factory=list)


@dataclass
class Decision:
    """Result of a decision-making call."""

    choice: str
    reasoning: str
    confidence: float
    alternatives_considered: list[str] = field(default_factory=list)
    risks: list[str] = field(default_factory=list)


@dataclass
class PrioritizedItem:
    """An item with priority score and reasoning."""

    item: Any
    priority_score: float
    reasoning: str


@dataclass
class ErrorHandling:
    """Result of intelligent error handling."""

    action: str  # "retry", "skip", "escalate", "fallback"
    reasoning: str
    retry_delay_seconds: int | None = None
    fallback_value: Any = None
    should_alert: bool = False


@dataclass
class LearningOutcome:
    """Extracted pattern from an action-result pair."""

    pattern_type: str  # "success", "failure", "optimization"
    description: str
    confidence: float
    applicable_contexts: list[str] = field(default_factory=list)
    recommendation: str = ""


def _get_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _call_claude(
    prompt: str,
    system: str | None = None,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 1000,
) -> str:
    """Make a Claude API call and return the text response."""
    client = _get_client()

    messages = [{"role": "user", "content": prompt}]

    kwargs = {
        "model": model,
        "max_tokens": max_tokens,
        "messages": messages,
    }
    if system:
        kwargs["system"] = system

    response = client.messages.create(**kwargs)
    return response.content[0].text


def _parse_json_response(response: str) -> dict[str, Any]:
    """Parse JSON from Claude response, handling markdown code blocks."""
    text = response.strip()

    # Handle markdown code blocks
    if "```json" in text:
        text = text.split("```json")[1].split("```")[0]
    elif "```" in text:
        text = text.split("```")[1].split("```")[0]

    return json.loads(text.strip())


async def assess_data_quality(
    data: dict[str, Any],
    context: str,
    required_fields: list[str] | None = None,
) -> QualityAssessment:
    """
    LLM-based quality assessment that adapts to any data shape.

    Unlike formula-based confidence scoring, this can reason about:
    - Source authority (official vs user-generated)
    - Data consistency across sources
    - Completeness relative to the use case
    - Subtle quality signals humans would notice

    Args:
        data: The data to assess (any structure)
        context: What this data will be used for (e.g., "family ski resort guide")
        required_fields: Optional list of must-have fields

    Returns:
        QualityAssessment with confidence score and detailed reasoning

    Cost: ~$0.002 per call with Haiku
    """
    required_str = f"\n- Required fields: {required_fields}" if required_fields else ""

    prompt = f"""Assess the quality of this data for: {context}

Data:
{json.dumps(data, indent=2, default=str)[:8000]}

Consider:
- Completeness: What's present vs missing for this use case?
- Accuracy signals: Do multiple sources agree? Any contradictions?
- Recency: How fresh does this information appear to be?
- Authority: Official sources vs aggregators vs social/user content?
- Red flags: Anything suspicious, outdated, or potentially wrong?{required_str}

Return JSON:
{{
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence explanation",
    "missing_critical": ["field1", "field2"],
    "missing_optional": ["field3"],
    "red_flags": ["concern1"],
    "strengths": ["strength1", "strength2"]
}}"""

    system = """You are a data quality analyst. Assess data objectively.
Be calibrated: 0.8+ means very reliable, 0.5-0.7 means usable with caveats, <0.5 means significant concerns.
Focus on what matters for the stated context."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return QualityAssessment(
            confidence=float(parsed.get("confidence", 0.5)),
            reasoning=parsed.get("reasoning", "Assessment completed"),
            missing_critical=parsed.get("missing_critical", []),
            missing_optional=parsed.get("missing_optional", []),
            red_flags=parsed.get("red_flags", []),
            strengths=parsed.get("strengths", []),
        )
    except (json.JSONDecodeError, KeyError) as e:
        # Graceful fallback - still return a usable result
        return QualityAssessment(
            confidence=0.5,
            reasoning=f"Assessment parsing failed: {e}. Raw response available.",
            red_flags=["Failed to parse quality assessment"],
        )


async def synthesize_to_schema(
    raw_data: dict[str, Any],
    target_schema: dict[str, str],
    context: str = "",
) -> dict[str, Any]:
    """
    Extract and transform raw data to match a target schema.

    This is the Agent Native alternative to rigid field mapping. The LLM
    can find equivalent data even when field names don't match, handle
    unit conversions, and flag when data doesn't exist.

    Args:
        raw_data: Unstructured or differently-structured source data
        target_schema: Dict mapping field names to descriptions
        context: Additional context about what we're building

    Returns:
        Dict matching target schema with extracted values

    Example:
        raw = {"pricing": {"adult": "€50"}, "kids_info": {"free_under": 6}}
        schema = {"lift_adult_daily": "Adult daily lift ticket price in USD"}
        result = await synthesize_to_schema(raw, schema)
        # {"lift_adult_daily": 55.0, ...}
    """
    prompt = f"""Extract data from the source to match the target schema.

SOURCE DATA:
{json.dumps(raw_data, indent=2, default=str)[:6000]}

TARGET SCHEMA (field: description):
{json.dumps(target_schema, indent=2)}

{f"CONTEXT: {context}" if context else ""}

Instructions:
- Find equivalent data even if field names differ
- Convert units if needed (e.g., EUR to USD estimate)
- Use null for fields with no available data
- Prefer specific values over ranges

Return JSON matching the target schema exactly."""

    system = """You are a data extraction specialist. Map source data to target schemas accurately.
When converting currencies, use approximate rates (1 EUR ≈ 1.10 USD, 1 CHF ≈ 1.15 USD).
Never fabricate data - use null when information isn't available."""

    response = _call_claude(prompt, system=system, max_tokens=2000)

    try:
        return _parse_json_response(response)
    except json.JSONDecodeError:
        # Return schema with nulls as fallback
        return {field: None for field in target_schema}


async def make_decision(
    context: str,
    options: list[str],
    criteria: list[str],
    constraints: list[str] | None = None,
) -> Decision:
    """
    Make a reasoned decision between options based on criteria.

    This replaces hardcoded if/else logic with LLM reasoning that can
    weigh tradeoffs, consider context, and explain its choice.

    Args:
        context: What decision needs to be made and why
        options: List of available choices
        criteria: What factors matter (in priority order)
        constraints: Hard requirements that must be met

    Returns:
        Decision with chosen option and reasoning

    Example:
        decision = await make_decision(
            context="Choosing which resort to research next",
            options=["Zermatt", "St. Anton", "Park City"],
            criteria=["content gap (no existing page)", "search demand", "family-friendliness"],
            constraints=["must have ski school for ages 3+"]
        )
    """
    constraints_str = f"\nCONSTRAINTS (must be satisfied):\n" + "\n".join(
        f"- {c}" for c in constraints
    ) if constraints else ""

    prompt = f"""Make a decision.

CONTEXT: {context}

OPTIONS:
{chr(10).join(f'{i+1}. {opt}' for i, opt in enumerate(options))}

CRITERIA (in priority order):
{chr(10).join(f'{i+1}. {c}' for i, c in enumerate(criteria))}{constraints_str}

Evaluate each option against the criteria. Choose the best option.

Return JSON:
{{
    "choice": "the selected option exactly as listed",
    "reasoning": "2-3 sentence explanation of why this choice",
    "confidence": 0.0-1.0,
    "alternatives_considered": ["option2", "option3"],
    "risks": ["potential downside of this choice"]
}}"""

    system = """You are a decision-making assistant. Make clear, reasoned choices.
Always choose one option - don't hedge. Explain your reasoning concisely.
Confidence reflects how clear-cut the decision is, not certainty about outcomes."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return Decision(
            choice=parsed.get("choice", options[0] if options else ""),
            reasoning=parsed.get("reasoning", "Decision made"),
            confidence=float(parsed.get("confidence", 0.7)),
            alternatives_considered=parsed.get("alternatives_considered", []),
            risks=parsed.get("risks", []),
        )
    except (json.JSONDecodeError, KeyError):
        # Fallback to first option
        return Decision(
            choice=options[0] if options else "",
            reasoning="Decision parsing failed, defaulted to first option",
            confidence=0.3,
        )


async def prioritize_items(
    items: list[dict[str, Any]],
    criteria: str,
    limit: int | None = None,
) -> list[PrioritizedItem]:
    """
    Intelligently prioritize a list of items based on criteria.

    Unlike sorting by a single field, this can weigh multiple factors
    and understand nuanced criteria like "most valuable for families".

    Args:
        items: List of items to prioritize (dicts with identifying info)
        criteria: Natural language description of prioritization criteria
        limit: Optional max number of items to return

    Returns:
        List of PrioritizedItem with scores and reasoning, sorted by priority
    """
    items_str = json.dumps(items[:20], indent=2, default=str)  # Limit for context

    prompt = f"""Prioritize these items based on the criteria.

ITEMS:
{items_str}

CRITERIA: {criteria}

{f"Return the top {limit} items." if limit else "Rank all items."}

Return JSON array:
[
    {{"item": {{...original item...}}, "priority_score": 0.0-1.0, "reasoning": "why this rank"}},
    ...
]

Sort by priority_score descending (highest priority first)."""

    system = """You are a prioritization expert. Rank items thoughtfully.
Consider all aspects of the criteria. Spread scores across the range - don't cluster."""

    response = _call_claude(prompt, system=system, max_tokens=3000)

    try:
        parsed = _parse_json_response(response)
        results = [
            PrioritizedItem(
                item=p.get("item", {}),
                priority_score=float(p.get("priority_score", 0.5)),
                reasoning=p.get("reasoning", ""),
            )
            for p in parsed
        ]
        # Sort by priority score descending
        results.sort(key=lambda x: x.priority_score, reverse=True)
        if limit:
            results = results[:limit]
        return results
    except (json.JSONDecodeError, TypeError):
        # Return items with default scores
        return [
            PrioritizedItem(item=item, priority_score=0.5, reasoning="Parsing failed")
            for item in (items[:limit] if limit else items)
        ]


async def handle_error_intelligently(
    error: Exception,
    context: dict[str, Any],
) -> ErrorHandling:
    """
    Determine the best way to handle an error based on context.

    Instead of catch-all retry logic, this reasons about:
    - Is this error transient or permanent?
    - What's at stake if we skip vs retry?
    - Should a human be alerted?
    - Is there a reasonable fallback?

    Args:
        error: The exception that occurred
        context: Dict with keys like "operation", "resort_name", "stage", "attempt"

    Returns:
        ErrorHandling with recommended action and reasoning
    """
    error_info = {
        "type": type(error).__name__,
        "message": str(error),
        "context": context,
    }

    prompt = f"""Determine how to handle this error.

ERROR:
{json.dumps(error_info, indent=2, default=str)}

Consider:
- Is this likely transient (network, rate limit) or permanent (bad data, auth)?
- What's the impact of skipping vs retrying?
- Should a human be notified?
- Is there a sensible fallback value?

Return JSON:
{{
    "action": "retry" | "skip" | "escalate" | "fallback",
    "reasoning": "why this action",
    "retry_delay_seconds": 60,  // if action is retry
    "fallback_value": null,     // if action is fallback
    "should_alert": false       // true if human should know
}}"""

    system = """You are an error handling specialist. Choose actions pragmatically.
- retry: For transient errors (network, rate limits)
- skip: When the item isn't critical and we can continue
- escalate: When human judgment is needed
- fallback: When we have a reasonable default value"""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return ErrorHandling(
            action=parsed.get("action", "skip"),
            reasoning=parsed.get("reasoning", "Error handling determined"),
            retry_delay_seconds=parsed.get("retry_delay_seconds"),
            fallback_value=parsed.get("fallback_value"),
            should_alert=parsed.get("should_alert", False),
        )
    except json.JSONDecodeError:
        # Conservative fallback - skip and alert
        return ErrorHandling(
            action="skip",
            reasoning="Failed to determine error handling, skipping safely",
            should_alert=True,
        )


async def learn_from_outcome(
    action: str,
    inputs: dict[str, Any],
    result: dict[str, Any],
    success: bool,
) -> LearningOutcome:
    """
    Extract patterns and lessons from an action-result pair.

    This enables agents to improve over time by identifying what
    works and what doesn't in different contexts.

    Args:
        action: What action was taken (e.g., "research_resort", "generate_content")
        inputs: The inputs to the action
        result: The outcome/output
        success: Whether this was considered successful

    Returns:
        LearningOutcome with extracted pattern and recommendations
    """
    prompt = f"""Analyze this action-result pair to extract learnable patterns.

ACTION: {action}
SUCCESS: {success}

INPUTS:
{json.dumps(inputs, indent=2, default=str)[:2000]}

RESULT:
{json.dumps(result, indent=2, default=str)[:2000]}

What pattern can we learn from this? Consider:
- What made this succeed/fail?
- In what other situations would this pattern apply?
- What should we do differently next time?

Return JSON:
{{
    "pattern_type": "success" | "failure" | "optimization",
    "description": "concise description of the pattern",
    "confidence": 0.0-1.0,
    "applicable_contexts": ["context1", "context2"],
    "recommendation": "what to do based on this learning"
}}"""

    system = """You are a machine learning pattern extractor. Identify actionable patterns.
Focus on patterns that would generalize to similar situations.
Be specific enough to be useful, but general enough to apply broadly."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return LearningOutcome(
            pattern_type=parsed.get("pattern_type", "optimization"),
            description=parsed.get("description", "Pattern extracted"),
            confidence=float(parsed.get("confidence", 0.5)),
            applicable_contexts=parsed.get("applicable_contexts", []),
            recommendation=parsed.get("recommendation", ""),
        )
    except json.JSONDecodeError:
        return LearningOutcome(
            pattern_type="optimization",
            description="Failed to extract pattern",
            confidence=0.0,
        )


# =============================================================================
# AGENT-NATIVE RESORT VALIDATION
# =============================================================================


@dataclass
class ResortValidationResult:
    """Result of validating a resort candidate against existing data."""

    name: str
    country: str
    exists_in_resorts: bool
    exists_in_candidates: bool
    similar_resorts: list[dict[str, Any]]
    should_skip: bool
    reason: str


async def validate_resort_selection(
    resorts: list[dict[str, str]],
) -> list[ResortValidationResult]:
    """
    Validate a list of resort selections against existing data.

    This is the Agent Native way: check each candidate individually
    using atomic primitives rather than putting 3000 names in a prompt.

    The two-phase approach:
    1. Claude suggests candidates (without seeing full list)
    2. This function validates each against the database

    Args:
        resorts: List of {"name": "...", "country": "..."} dicts

    Returns:
        List of validation results with should_skip flag and reason
    """
    # Import atomic primitives
    from .database import check_resort_exists, find_similar_resorts
    from .discovery import check_discovery_candidate_exists

    results = []

    for resort in resorts:
        name = resort.get("name", "")
        country = resort.get("country", "")

        if not name or not country:
            results.append(ResortValidationResult(
                name=name,
                country=country,
                exists_in_resorts=False,
                exists_in_candidates=False,
                similar_resorts=[],
                should_skip=True,
                reason="Missing name or country",
            ))
            continue

        # Check 1: Exact match in resorts table
        existing = check_resort_exists(name, country)

        # Check 2: Already in discovery candidates queue
        in_candidates = check_discovery_candidate_exists(name, country)

        # Check 3: Similar resorts (fuzzy match)
        similar = find_similar_resorts(name, country, threshold=0.7)

        # Determine if we should skip this resort
        should_skip = False
        reason = ""

        if existing:
            should_skip = True
            reason = f"Already exists as '{existing['name']}' ({existing.get('status', 'unknown')})"
        elif in_candidates and in_candidates.get("status") in ("queued", "researched", "published"):
            should_skip = True
            reason = f"Already in discovery queue (status: {in_candidates['status']})"
        elif similar and similar[0]["similarity_score"] > 0.85:
            should_skip = True
            reason = f"Very similar to existing resort '{similar[0]['name']}' (score: {similar[0]['similarity_score']})"

        results.append(ResortValidationResult(
            name=name,
            country=country,
            exists_in_resorts=existing is not None,
            exists_in_candidates=in_candidates is not None,
            similar_resorts=similar[:3] if similar else [],
            should_skip=should_skip,
            reason=reason,
        ))

    return results


async def generate_tagline(
    resort_name: str,
    country: str,
    context: str | dict[str, Any],
    voice_profile: str = "snowthere_guide",
) -> str:
    """
    Generate a unique tagline for a resort (8-12 words).

    This captures the resort's essence in a punchy, memorable hook.
    Not generic - specific to what makes this resort special for families.

    Args:
        resort_name: Name of the resort
        country: Country where resort is located
        context: Research context about the resort (string or dict)
        voice_profile: Voice profile to use

    Returns:
        A unique tagline string

    Examples:
        - "Matterhorn views meet family magic"
        - "Where powder meets playful adventure"
        - "Europe's best-kept family ski secret"
    """
    # Convert dict context to string for prompt
    if isinstance(context, dict):
        context = json.dumps(context, indent=2, default=str)

    prompt = f"""Generate a unique tagline for {resort_name}, {country}.

CONTEXT:
{context[:3000]}

VOICE: {voice_profile} - smart, witty, efficient like a well-traveled friend

REQUIREMENTS:
- 8-12 words maximum
- Captures what makes THIS resort special for families
- Not generic ("great for families!") - specific to this resort
- Punchy, memorable, shareable
- Can use wordplay, alliteration, or clever phrasing

Good examples:
- "Matterhorn views meet family magic" (Zermatt)
- "Powder paradise meets kids' paradise" (Utah resort)
- "Where value skiing meets family fun" (budget resort)
- "Alpine charm without the premium price" (Austrian village)

Return ONLY the tagline, no quotes or explanation."""

    system = """You are a travel copywriter specializing in ski resort marketing.
Write punchy, memorable taglines that make families want to visit.
Be specific to each resort - generic phrases are a failure."""

    try:
        response = _call_claude(prompt, system=system, max_tokens=100)
        # Clean up the response
        tagline = response.strip().strip('"').strip("'")
        # Ensure it's not too long
        if len(tagline.split()) > 15:
            # Truncate to first 12 words
            words = tagline.split()[:12]
            tagline = " ".join(words)
        return tagline
    except Exception as e:
        print(f"Tagline generation failed: {e}")
        return f"Your family adventure starts in {resort_name}"


# =============================================================================
# RESORT DATA EXTRACTION
# =============================================================================


@dataclass
class ExtractedResortData:
    """Result of extracting structured costs and family metrics."""

    costs: dict[str, Any]
    family_metrics: dict[str, Any]
    confidence: float
    reasoning: str
    missing_fields: list[str] = field(default_factory=list)


async def extract_resort_data(
    raw_research: dict[str, Any],
    resort_name: str,
    country: str,
) -> ExtractedResortData:
    """
    Extract structured costs and family metrics from raw research data.

    This is the missing layer between research and storage - raw data goes in,
    structured costs/family_metrics come out ready for database insertion.

    Args:
        raw_research: Raw research data from search_resort_info()
        resort_name: Name of the resort
        country: Country where resort is located

    Returns:
        ExtractedResortData with costs, family_metrics, and confidence

    Cost: ~$0.01 per call with Sonnet
    """
    # Schema aligned with database columns (016_extend_costs_for_families.sql)
    # Field names MUST match exactly to avoid schema mismatch errors
    target_schema = {
        "costs": {
            # Core lift costs
            "lift_adult_daily": "Adult daily lift ticket in local currency (number)",
            "lift_child_daily": "Child (6-12) daily lift ticket (number)",
            "lift_under6": "Price for under 6 (number, use 0 if free)",
            "lift_family_daily": "Family bundle lift ticket if available (number or null)",
            # Lodging tiers
            "lodging_budget_nightly": "Budget family lodging per night (number)",
            "lodging_mid_nightly": "Mid-range family lodging per night (number)",
            "lodging_luxury_nightly": "Luxury family lodging per night (number)",
            # Ski school costs (often largest budget item for families!)
            "lesson_group_child": "Child group lesson per day (number)",
            "lesson_private_hour": "Private lesson per hour (number)",
            # Rental costs (most families rent)
            "rental_adult_daily": "Adult ski/boot rental per day (number)",
            "rental_child_daily": "Child ski/boot rental per day (number)",
            # Meals and totals
            "meal_family_avg": "Average meal cost for family of 4 (number)",
            "estimated_family_daily": "Total estimated daily cost for family of 4 (number)",
            "currency": "Currency code (USD, EUR, CHF, etc.)",
        },
        "family_metrics": {
            # Scores
            "family_overall_score": "1-10 score for families with kids under 12",
            # Age ranges
            "best_age_min": "Minimum ideal child age in years (number)",
            "best_age_max": "Maximum ideal child age in years (number)",
            # Childcare
            "has_childcare": "Boolean - does resort offer childcare",
            "childcare_min_age": "Minimum age for childcare in months (number)",
            # Ski school
            "ski_school_min_age": "Minimum age for ski school in years (number)",
            "kids_ski_free_age": "Age under which kids ski free (number or null)",
            # Terrain
            "kid_friendly_terrain_pct": "Percentage of kid-friendly terrain (0-100)",
            "has_magic_carpet": "Boolean - does resort have magic carpet lifts",
            "has_terrain_park_kids": "Boolean - does resort have kids terrain park",
            # Decision helpers (arrays)
            "perfect_if": "Array of reasons this resort is perfect for a family",
            "skip_if": "Array of reasons a family might want to skip this resort",
        },
    }

    prompt = f"""Extract costs and family metrics from this resort research data.

RESORT: {resort_name}, {country}

RESEARCH DATA:
{json.dumps(raw_research, indent=2, default=str)[:8000]}

TARGET SCHEMA:
{json.dumps(target_schema, indent=2)}

EXTRACTION RULES:
- Extract exact values where available in the research
- For price ranges, use the midpoint
- For family_overall_score: Consider childcare quality, beginner terrain %, terrain park safety, crowds, ski school reputation
- Use null for truly unavailable data - do NOT fabricate
- Be conservative - only extract what you can verify from the source
- Convert all prices to the local currency of the resort

Return JSON:
{{
    "costs": {{ ... }},
    "family_metrics": {{ ... }},
    "confidence": 0.0-1.0,
    "reasoning": "Brief quality assessment of extraction",
    "missing_fields": ["field1", "field2"]
}}"""

    system = """You are a data extraction specialist for ski resort information.
Extract structured data from raw research accurately and conservatively.
Never fabricate data - use null when information isn't available.
Be especially careful with family metrics - these help parents make decisions."""

    response = _call_claude(
        prompt,
        system=system,
        model="claude-sonnet-4-20250514",
        max_tokens=1500,
    )

    try:
        parsed = _parse_json_response(response)
        return ExtractedResortData(
            costs=parsed.get("costs", {}),
            family_metrics=parsed.get("family_metrics", {}),
            confidence=float(parsed.get("confidence", 0.5)),
            reasoning=parsed.get("reasoning", "Extraction completed"),
            missing_fields=parsed.get("missing_fields", []),
        )
    except Exception as e:
        return ExtractedResortData(
            costs={},
            family_metrics={},
            confidence=0.3,
            reasoning=f"Extraction failed: {e}",
            missing_fields=["all"],
        )


# ============================================================================
# REGION EXTRACTION - Determine the region/state for a ski resort
# ============================================================================


async def extract_region(
    resort_name: str,
    country: str,
) -> str | None:
    """
    Extract the region/state for a ski resort.

    For families, knowing the region helps with:
    - Trip planning (airports, road conditions)
    - Cost expectations (Colorado vs Vermont pricing)
    - Weather patterns and snow reliability

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located

    Returns:
        Region/state name or None if unknown

    Cost: ~$0.002 per call with Haiku
    """
    prompt = f"""What region, state, or province is the ski resort "{resort_name}" located in?

Country: {country}

Return ONLY the region name, nothing else. Examples:
- For Vail, United States → Colorado
- For Zermatt, Switzerland → Valais
- For Chamonix, France → Haute-Savoie
- For Niseko, Japan → Hokkaido
- For Whistler, Canada → British Columbia

If you don't know, return "Unknown"."""

    system = "You are a geography expert. Return only the region/state/province name, nothing else."

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-3-5-haiku-20241022",  # Fast and cheap for simple lookups
            max_tokens=50,
        )
        region = response.strip().strip('"').strip("'")
        if region.lower() == "unknown" or not region:
            return None
        return region
    except Exception:
        return None


# ============================================================================
# LINK CURATION - Extract and categorize useful links from research sources
# ============================================================================


@dataclass
class CuratedLink:
    """A curated link with category and description."""

    title: str
    url: str
    category: str  # official, lodging, dining, activity, transport, rental, ski_school, childcare
    description: str


@dataclass
class LinkCurationResult:
    """Result of link curation."""

    success: bool
    links: list[CuratedLink] = field(default_factory=list)
    has_official: bool = False
    error: str | None = None


async def curate_resort_links(
    resort_name: str,
    country: str,
    research_sources: list[dict[str, Any]],
) -> LinkCurationResult:
    """
    Extract family-relevant links from research sources.

    Uses Claude to classify URLs into useful categories for families:
    - official: Resort's official website
    - lodging: Hotels, vacation rentals, lodges
    - dining: Family-friendly restaurants
    - activity: Off-mountain activities (sledding, ice skating, etc.)
    - transport: Airport shuttles, car rentals, transfer services
    - rental: Ski/snowboard rental shops
    - ski_school: Ski school and lesson providers
    - childcare: Daycare, kids clubs, babysitting services

    Args:
        resort_name: Name of the resort
        country: Country where resort is located
        research_sources: List of source dicts with 'url', 'title', 'snippet' keys

    Returns:
        LinkCurationResult with categorized links

    Quality Gate: Requires at least 1 official link + 2 other links.
    """
    if not research_sources:
        return LinkCurationResult(
            success=False,
            error="No research sources provided",
        )

    # Build a summary of sources for Claude
    sources_summary = []
    for source in research_sources[:20]:  # Limit to avoid token issues
        sources_summary.append({
            "url": source.get("url", ""),
            "title": source.get("title", ""),
            "snippet": source.get("snippet", source.get("content", ""))[:300],
        })

    prompt = f"""Curate family-relevant links for {resort_name}, {country} from these research sources.

SOURCES:
{json.dumps(sources_summary, indent=2)}

CATEGORIES:
- official: Resort's official website (exactly 1)
- lodging: Family-friendly hotels, vacation rentals
- dining: Restaurants good for kids
- activity: Off-mountain activities (sledding, pool, etc.)
- transport: Airport shuttles, transfers
- rental: Ski/snowboard equipment rental
- ski_school: Ski lessons for kids
- childcare: Daycare, kids clubs

REQUIREMENTS:
- Select 1 official link (required)
- Select 3-8 other useful links for families
- Prefer URLs that are direct (not search results, aggregators)
- Write brief, helpful descriptions (1 sentence max)

Return JSON:
{{
    "links": [
        {{
            "title": "Resort Name Official",
            "url": "https://...",
            "category": "official",
            "description": "Official website with tickets, conditions, and reservations"
        }},
        ...
    ]
}}"""

    system = """You are a travel curator for ski families.
Select the most useful, trustworthy links for parents planning ski trips with kids.
Prioritize official sources and well-known brands over unknown sites.
Skip paywalled, login-required, or spam sites."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
        )

        parsed = _parse_json_response(response)
        raw_links = parsed.get("links", [])

        curated_links = []
        has_official = False

        for link_data in raw_links:
            link = CuratedLink(
                title=link_data.get("title", ""),
                url=link_data.get("url", ""),
                category=link_data.get("category", "activity"),
                description=link_data.get("description", ""),
            )

            # Validate URL
            if not link.url or not link.url.startswith("http"):
                continue

            curated_links.append(link)

            if link.category == "official":
                has_official = True

        return LinkCurationResult(
            success=len(curated_links) >= 1,
            links=curated_links,
            has_official=has_official,
        )

    except Exception as e:
        return LinkCurationResult(
            success=False,
            error=f"Link curation failed: {e}",
        )


# ============================================================================
# ENTITY EXTRACTION - Find linkable entities in resort content
# ============================================================================


@dataclass
class ExtractedEntity:
    """An entity extracted from content that could be linked."""

    name: str
    entity_type: str  # hotel, restaurant, ski_school, rental, activity, grocery
    context_snippet: str  # The sentence where it was found
    confidence: float  # How confident we are this is a real entity
    first_mention_offset: int  # Character offset of first mention


@dataclass
class EntityExtractionResult:
    """Result of entity extraction from content."""

    entities: list[ExtractedEntity]
    entity_count: int
    extraction_confidence: float


async def extract_linkable_entities(
    content: str,
    resort_name: str,
    country: str,
    section_name: str | None = None,
) -> EntityExtractionResult:
    """
    Extract linkable entities from resort content.

    Identifies hotels, restaurants, ski schools, rental shops, and other
    entities that could be linked to external sites or Google Maps.

    Part of Round 7: External Linking & Affiliate System.

    Args:
        content: HTML or plain text content to analyze
        resort_name: Name of the resort for context
        country: Country for context/disambiguation
        section_name: Optional section name for better context

    Returns:
        EntityExtractionResult with list of extracted entities

    Cost: ~$0.005 per call with Sonnet
    """
    # Strip HTML tags for analysis but preserve structure hints
    import re
    clean_content = re.sub(r'<[^>]+>', ' ', content)
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()

    if len(clean_content) < 50:
        return EntityExtractionResult(
            entities=[],
            entity_count=0,
            extraction_confidence=0.0,
        )

    prompt = f"""Extract linkable entities from this resort content.

RESORT: {resort_name}, {country}
{f"SECTION: {section_name}" if section_name else ""}

CONTENT:
{clean_content[:5000]}

ENTITY TYPES TO FIND:
- hotel: Specific hotels, lodges, chalets by name (e.g., "Hotel Schweizerhof", "The Lodge at Vail")
- restaurant: Restaurants, cafes, mountain huts by name (e.g., "Chez Vrony", "Mid-Mountain Lodge")
- ski_school: Named ski school programs (e.g., "Ski School Zermatt", "Burton Learn to Ride")
- rental: Named rental shops (e.g., "Julen Sport", "Christy Sports")
- activity: Named activity providers (e.g., "Glacier Paradise", "Snowmass Tubing Hill")
- grocery: Named grocery/convenience stores (e.g., "Coop", "SPAR")

RULES:
- Only extract SPECIFIC NAMED entities (not generic mentions like "ski school" or "restaurants")
- Include the surrounding sentence as context_snippet
- Set confidence based on how certain this is a real, linkable business
- Report the character position of first mention
- Do NOT extract the resort name itself

Return JSON:
{{
    "entities": [
        {{
            "name": "Hotel Schweizerhof",
            "entity_type": "hotel",
            "context_snippet": "Families love staying at the Hotel Schweizerhof for its central location.",
            "confidence": 0.9,
            "first_mention_offset": 45
        }},
        ...
    ],
    "extraction_confidence": 0.8
}}"""

    system = """You are an entity extraction specialist for travel content.
Find specific, named businesses and locations that could be linked to Google Maps or websites.
Be conservative - only extract entities you're confident are real, named businesses.
Generic mentions like "the ski school" or "local restaurants" should NOT be extracted."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
        )

        parsed = _parse_json_response(response)
        raw_entities = parsed.get("entities", [])

        entities = []
        for e in raw_entities:
            if not e.get("name") or not e.get("entity_type"):
                continue
            entities.append(ExtractedEntity(
                name=e["name"],
                entity_type=e["entity_type"],
                context_snippet=e.get("context_snippet", ""),
                confidence=float(e.get("confidence", 0.5)),
                first_mention_offset=int(e.get("first_mention_offset", 0)),
            ))

        return EntityExtractionResult(
            entities=entities,
            entity_count=len(entities),
            extraction_confidence=float(parsed.get("extraction_confidence", 0.7)),
        )

    except Exception as e:
        print(f"Entity extraction failed: {e}")
        return EntityExtractionResult(
            entities=[],
            entity_count=0,
            extraction_confidence=0.0,
        )


# ============================================================================
# QUICK TAKE CONTEXT EXTRACTION - Editorial inputs for Quick Take generation
# ============================================================================


@dataclass
class QuickTakeContextResult:
    """Editorial inputs extracted from research for Quick Take generation.

    These are the "soul" of the Quick Take - specific, memorable details
    that make the content authentic rather than generic.
    """

    # Core editorial inputs (all should be specific, not generic)
    unique_angle: str | None = None  # What makes this resort DIFFERENT?
    signature_experience: str | None = None  # The ONE thing families remember
    primary_strength: str | None = None  # Best thing about this resort
    primary_weakness: str | None = None  # REQUIRED - every resort has one
    who_should_skip: str | None = None  # Clear "not for you if..."
    memorable_detail: str | None = None  # Sensory/experiential hook

    # Comparative context
    price_context: str | None = None  # "Half the cost of Aspen"
    similar_to: str | None = None  # "Similar vibe to X, but..."
    better_than_for: str | None = None  # "Better than X for families because..."

    # Quality
    extraction_confidence: float = 0.0
    extraction_reasoning: str = ""


async def extract_quick_take_context(
    resort_name: str,
    country: str,
    research_data: dict[str, Any],
) -> QuickTakeContextResult:
    """Extract editorial context for Quick Take generation.

    This is the intelligence layer that turns raw research into
    the specific, memorable details that make Quick Takes authentic.

    Part of Round 8: Quick Takes Redesign.

    Args:
        resort_name: Name of the resort
        country: Country where resort is located
        research_data: Raw research data from search_resort_info()

    Returns:
        QuickTakeContextResult with editorial inputs

    Cost: ~$0.01 per call with Sonnet
    """
    # Build a summary of research for Claude to analyze
    research_summary = json.dumps(research_data, indent=2, default=str)[:8000]

    prompt = f"""Extract editorial context for a Quick Take about {resort_name}, {country}.

RESEARCH DATA:
{research_summary}

I need you to extract SPECIFIC, MEMORABLE details - not generic observations.

REQUIRED OUTPUTS:

1. UNIQUE_ANGLE: What makes this resort DIFFERENT from others?
   - NOT: "Great views" or "Family-friendly"
   - YES: "Car-free village where kids can roam safely" or "Access to Italian ski area for lunch"

2. SIGNATURE_EXPERIENCE: The ONE thing families remember years later
   - NOT: "Fun skiing" or "Nice slopes"
   - YES: "The fondue hut at the top of the gondola" or "Skiing through the covered bridge"

3. PRIMARY_STRENGTH: The best thing about this resort for families
   - Be specific about WHY it's a strength
   - Include numbers/data when available

4. PRIMARY_WEAKNESS: What's the honest downside? (REQUIRED - every resort has one)
   - NOT: "Nothing" or "Could be better"
   - YES: "30-minute transfer from village to main ski area" or "Expensive on-mountain dining"

5. WHO_SHOULD_SKIP: Clear "not for you if..." statement
   - Be direct about deal-breakers
   - Example: "Families wanting slope-side lodging" or "Budget travelers ($$$ terrain)"

6. MEMORABLE_DETAIL: A sensory or experiential hook
   - Something they can visualize or feel
   - Example: "Cobblestone streets lit by gas lamps" or "Hot chocolate stop with Matterhorn views"

7. PRICE_CONTEXT: How does cost compare? (if data available)
   - Example: "Half the cost of Aspen" or "Premium pricing, premium experience"

Return JSON:
{{
    "unique_angle": "...",
    "signature_experience": "...",
    "primary_strength": "...",
    "primary_weakness": "...",
    "who_should_skip": "...",
    "memorable_detail": "...",
    "price_context": "...",
    "similar_to": "Resort it's most like, if applicable",
    "better_than_for": "Better than [X] for families because...",
    "confidence": 0.0-1.0,
    "reasoning": "Brief explanation of extraction quality"
}}

If information isn't available in the research, use null (not a generic placeholder).
"""

    system = """You are an editorial researcher extracting the SOUL of a ski resort.

Your job: Find the specific, memorable details that make authentic travel writing.

Rules:
- Be SPECIFIC, not generic. "Beautiful views" is useless. "Matterhorn views from every lift" is specific.
- Be HONEST about weaknesses. Families trust honest assessments.
- Use NUMBERS when available. "35% beginner terrain" beats "lots of beginner terrain."
- Capture SENSORY details. What will they see, feel, experience?
- Think COMPARATIVELY. How is this different from other resorts?

Generic output is a failure. Specific, memorable output is success."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-sonnet-4-20250514",
            max_tokens=1500,
        )

        parsed = _parse_json_response(response)

        return QuickTakeContextResult(
            unique_angle=parsed.get("unique_angle"),
            signature_experience=parsed.get("signature_experience"),
            primary_strength=parsed.get("primary_strength"),
            primary_weakness=parsed.get("primary_weakness"),
            who_should_skip=parsed.get("who_should_skip"),
            memorable_detail=parsed.get("memorable_detail"),
            price_context=parsed.get("price_context"),
            similar_to=parsed.get("similar_to"),
            better_than_for=parsed.get("better_than_for"),
            extraction_confidence=float(parsed.get("confidence", 0.5)),
            extraction_reasoning=parsed.get("reasoning", ""),
        )

    except Exception as e:
        print(f"Quick Take context extraction failed: {e}")
        return QuickTakeContextResult(
            extraction_confidence=0.0,
            extraction_reasoning=f"Extraction failed: {e}",
        )
