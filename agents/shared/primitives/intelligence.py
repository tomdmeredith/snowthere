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
