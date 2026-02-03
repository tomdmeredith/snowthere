"""Intelligence primitives - LLM-based reasoning for Agent Native decisions.

These primitives wrap Claude calls for common decision patterns, enabling
flexible, context-aware reasoning instead of rigid formulas.

Design Principle: Use fast models (Haiku) for routine decisions to keep
costs low (~$0.002 per call) while maintaining intelligence.
"""

import json
import re
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
    temperature: float | None = None,
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
    if temperature is not None:
        kwargs["temperature"] = temperature

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

=== CALIBRATION EXAMPLES ===
Use these verified resorts as reference points for extraction quality:

Example 1 — Serfaus-Fiss-Ladis (Austria):
Research mentions: "Murmli childcare from 3 months, Bertas Kinderland, magic carpet in kids area"
Correct extraction:
  has_childcare: true, childcare_min_age: 3, has_magic_carpet: true,
  ski_school_min_age: 3, kids_ski_free_age: 10, has_terrain_park_kids: true

Example 2 — St. Anton (Austria):
Research mentions: "Kids ski school from age 4, no dedicated kids terrain park, ski-in/out hotels"
Correct extraction:
  has_childcare: true, childcare_min_age: 12, has_magic_carpet: true,
  ski_school_min_age: 4, has_terrain_park_kids: false, has_ski_in_out: true

Example 3 — Zermatt (Switzerland):
Research mentions: "Kinderparadies from 6 months, Stoked Swiss Ski School from age 4, Wolli's Park"
Correct extraction:
  has_childcare: true, childcare_min_age: 6, has_magic_carpet: true,
  ski_school_min_age: 4, has_terrain_park_kids: false, kids_ski_free_age: 9

=== BOOLEAN RULES (STRICT) ===
- TRUE: Clear evidence in research data (named facility, explicit statement)
- FALSE: Research covers the topic area but confirms absence, OR official site
  lists amenities and this is NOT among them
- NULL: Topic not mentioned at all in any research source
IMPORTANT: Ski school is NOT childcare. "Kids club at ski school" ≠ has_childcare.
Only set has_childcare=true if there is actual daycare/nursery/babysitting.

=== COST SANITY CHECK (flag if outside) ===
- European lift tickets: EUR 30-85 adult daily
- US lift tickets: USD 80-300 adult daily
- Swiss lift tickets: CHF 50-100 adult daily
- Budget lodging: 30-60% of mid-range
- Luxury lodging: 150-400% of mid-range
- If an extracted price falls outside these ranges, double-check the source.

=== CRITICAL: FAMILY METRICS DATA EXTRACTION ===

You MUST actively search for and report on EACH of these family-critical fields:

1. **has_childcare** (boolean): Does the resort offer childcare/daycare/nursery?
   - Look for: "childcare", "daycare", "nursery", "kids club", "crèche", "kinderland"
   - Many resorts have this but call it different names
   - Answer: true/false/null (only null if truly not mentioned anywhere)

2. **childcare_min_age** (number in MONTHS): What's the youngest age accepted?
   - Look for: "from 3 months", "6 weeks", "2 years", "12 months"
   - Convert years to months: 2 years = 24 months, 18 months = 18
   - This is CRUCIAL for families with babies/toddlers

3. **ski_school_min_age** (number in YEARS): What's the minimum age for ski lessons?
   - Look for: "ski school from age 3", "lessons for 4+", "kids classes start at 5"
   - Most resorts accept ages 3-4, some as young as 2.5
   - Report in YEARS (e.g., 3, 4, 5)

4. **has_magic_carpet** (boolean): Does resort have magic carpet/conveyor lifts?
   - Look for: "magic carpet", "conveyor belt lift", "moving carpet", "beginner conveyor"
   - Essential for toddlers and first-time skiers

5. **kids_ski_free_age** (number): Up to what age do kids ski FREE?
   - Look for: "kids under 6 ski free", "free for under 5", "children 5 and under"
   - Report the age limit (e.g., 5 means kids 5 and under are free)

6. **has_terrain_park_kids** (boolean): Is there a kids-specific terrain park?
   - Look for: "kids park", "family park", "beginner terrain park", "mini park"
   - Not the main terrain park - specifically for children

7. **has_ski_in_out** (boolean): Are there ski-in/ski-out lodging options?
   - Look for: "ski-in ski-out", "slopeside lodging", "ski to your door"
   - Game-changer for families with gear and tired kids

WHERE TO FIND THIS DATA:
- Resort official website content
- Ski school pages
- Kids/family sections
- Childcare/daycare information
- Lift ticket pricing pages (for free ages)
- Village/lodging descriptions

=== EXTRACTION RULES ===
- ACTIVELY SEARCH for each field - don't just passively extract
- For price ranges, use the midpoint
- For family_overall_score: Consider childcare quality, beginner terrain %, terrain park safety, crowds, ski school reputation
- Use null ONLY for truly unavailable data after searching
- Be conservative with prices - only extract verified amounts
- Convert all prices to the local currency of the resort

Return JSON:
{{
    "costs": {{ ... }},
    "family_metrics": {{ ... }},
    "confidence": 0.0-1.0,
    "reasoning": "Brief quality assessment of extraction - note which family fields you found vs couldn't find",
    "missing_fields": ["field1", "field2"]
}}"""

    system = """You are a data extraction specialist for ski resort FAMILY information.

Your PRIMARY mission is extracting family-critical metrics:
- has_childcare, childcare_min_age (crucial for families with babies)
- ski_school_min_age (when can kids start lessons?)
- has_magic_carpet (essential for tiny beginners)
- kids_ski_free_age (big cost saver!)
- has_terrain_park_kids, has_ski_in_out

ACTIVELY SEARCH the research data for these. They're often buried in:
- "Kids Club" or "Kinderland" sections
- Ski school pages
- Lift ticket FAQs
- Village amenity lists

Never fabricate data - use null when information isn't available.
But DON'T be lazy - search thoroughly before reporting null.
These metrics directly affect family vacation decisions and our scoring algorithm."""

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

CATEGORIES (match content section names parents see):
- official: Resort's official website (exactly 1)
- lodging: "Where to Stay" — Hotels, vacation rentals, lodges
- dining: "Where to Eat" — Family-friendly restaurants
- activity: "Things to Do" — Off-mountain activities (sledding, pool, etc.)
- transport: "Getting There" — Airport shuttles, transfers, car rentals
- rental: "Rent Gear" — Ski/snowboard equipment rental
- ski_school: "Ski Lessons" — Ski school and lesson providers
- childcare: "Kids Care" — Daycare, kids clubs, babysitting

REQUIREMENTS:
- Select 1 official link (required)
- Select 8-15 other useful links for families (aim for comprehensive coverage)
- MINIMUM per category: at least 2 lodging, 1 dining, 1 ski_school
- Include a Google Maps link for the resort area as a transport link
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
- hotel: Specific hotels, lodges, chalets, pensions by name (e.g., "Hotel Schweizerhof", "The Lodge at Vail")
- restaurant: Restaurants, mountain huts by name (e.g., "Chez Vrony", "Mid-Mountain Lodge")
- bar: Bars, pubs, apres-ski venues by name (e.g., "MooserWirt", "Krazy Kanguruh")
- cafe: Cafes, bakeries, coffee shops by name (e.g., "Cafe Dorfplatz", "Boulangerie Alpine")
- ski_school: Named ski school programs (e.g., "Ski School Zermatt", "NISS", "GoSnow")
- rental: Named rental shops (e.g., "Julen Sport", "Christy Sports", "Intersport")
- activity: Named activity providers (e.g., "Glacier Paradise", "Snowmass Tubing Hill")
- grocery: Named grocery/convenience stores (e.g., "Coop", "SPAR", "Lawson", "Seicomart")
- childcare: Named childcare/nursery/kids clubs (e.g., "Kinderland", "Niseko Kids Club", "Murmli")
- airport: Airports by name (e.g., "Innsbruck Airport", "Zurich Airport", "Chitose Airport")
- transport: Named transport services (e.g., "Swiss Federal Railways", "Niseko United Shuttle")
- retail: Named retail shops (e.g., "Julen Sport", "Matterhorn Terminal Store")
- village: Small ski villages that are part of the resort experience (e.g., "Hirafu", "Lech", "St. Christoph")

RULES:
- Extract ALL specifically named businesses, services, and locations
- Include convenience stores, childcare, small ski villages, transport — anything a parent might want to look up
- Do NOT extract major cities, metropolitan areas, or regions (e.g., "Salt Lake City", "Vancouver", "Denver", "Sandy", "Draper" are NOT linkable entities)
- Do NOT extract states, provinces, or countries
- Generic mentions ("the ski school", "local restaurants") should NOT be extracted
- Named ones ("NISS ski school", "Restaurant Walliserkanne") always SHOULD be extracted
- Do NOT extract the resort name itself or ski pass brand names (Ikon, Epic, etc.)
- Include the surrounding sentence as context_snippet
- Set confidence HIGH (0.8-0.95) for any specifically named business, venue, or service
- Only use LOW confidence (0.4-0.6) if the name is ambiguous or might be generic
- When in doubt, use 0.8 — downstream validation handles false positives
- Report the character position of first mention

Return JSON:
{{
    "entities": [
        {{
            "name": "Kandahar Lodge",
            "entity_type": "hotel",
            "context_snippet": "Kandahar Lodge is your only true ski-in option.",
            "confidence": 0.9,
            "first_mention_offset": 120
        }},
        {{
            "name": "Grouse Mountain Lodge",
            "entity_type": "hotel",
            "context_snippet": "Grouse Mountain Lodge is where most families land.",
            "confidence": 0.85,
            "first_mention_offset": 380
        }},
        {{
            "name": "Logan's Bar & Grill",
            "entity_type": "restaurant",
            "context_snippet": "The lodge has an on-site restaurant, Logan's Bar & Grill.",
            "confidence": 0.9,
            "first_mention_offset": 520
        }}
    ],
    "extraction_confidence": 0.85
}}"""

    system = """You are an entity extraction specialist for family ski resort content.
Your job is to find EVERY specifically named business, service, and location.

CRITICAL: Assign HIGH confidence (0.8+) to any named entity that appears to be a real business.
- "Kandahar Lodge" → confidence 0.9 (clear hotel name)
- "Grouse Mountain Lodge" → confidence 0.85 (clear hotel name)
- "Logan's Bar & Grill" → confidence 0.9 (clear restaurant name)
- "Whitefish Mountain Resort Kids Center" → confidence 0.85 (clear ski school)

The downstream system validates entities via Google Places — your job is to FIND them, not filter them.
Missing a real entity is worse than including an ambiguous one.
Generic mentions like "the ski school" or "local restaurants" should NOT be extracted.
Named mentions like "NISS ski school" or "Coop supermarket" SHOULD always be extracted.

NEVER extract major cities, metro areas, or regions as entities. "Salt Lake City", "Vancouver", "Denver", "Kamloops", "Sandy", "Draper" are geographic references, NOT linkable businesses."""

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


# =============================================================================
# TAGLINE GENERATION - AGENT NATIVE APPROACH
# =============================================================================
# Uses "store atoms, compute molecules" principle:
# 1. Extract atomic facts (numbers, landmarks, unique features)
# 2. Provide structural diversity through examples, not rules
# 3. Use LLM-based quality evaluation (rubric scoring, not regex)
# 4. Portfolio awareness via database query for diversity
# =============================================================================

import random


@dataclass
class TaglineAtoms:
    """Atomic facts for tagline synthesis - specific, not generic.

    These atoms are the building blocks from which taglines are synthesized.
    Each atom should be concrete and unique to this specific resort.
    """

    # Numbers that differentiate (not "great terrain" - "93% beginner terrain")
    numbers: list[str] = field(default_factory=list)

    # Unique identifiers (not "beautiful views" - "Matterhorn views")
    landmark_or_icon: str | None = None

    # Sensory/emotional hooks
    signature_feeling: str | None = None

    # Comparative positioning
    value_angle: str | None = None
    unexpected_fact: str | None = None

    # From existing extraction (reuse QuickTakeContextResult)
    unique_angle: str | None = None
    signature_experience: str | None = None
    memorable_detail: str | None = None

    # What makes this resort NOT like others (differentiation)
    anti_pattern: str | None = None

    extraction_confidence: float = 0.0


@dataclass
class TaglineQualityScore:
    """Probabilistic quality assessment for taglines.

    Uses LLM-based rubric scoring rather than deterministic regex matching.
    """

    overall_score: float  # 0.0-1.0

    # Dimensional scores (each 0.0-1.0)
    specificity: float  # Does it include concrete facts? (numbers, names, places)
    differentiation: float  # Could this ONLY apply to this resort?
    structure_novelty: float  # Is the structure different from common patterns?
    emotional_resonance: float  # Does it make families feel something?
    voice_alignment: float  # Does it match snowthere_guide voice?

    # Qualitative feedback
    strongest_element: str = ""
    weakest_element: str = ""
    improvement_suggestion: str | None = None

    # Portfolio context
    similar_to: str | None = None  # If resembles another tagline, which one?

    passes_threshold: bool = False  # overall_score >= 0.7


# Structural examples for diverse tagline generation
# These are rotated (3 shown per call) to guide variety, not rules
TAGLINE_STRUCTURAL_EXAMPLES: dict[str, list[str]] = {
    "number_lead": [
        "93% beginner terrain, 100% family focus",
        "Three mountains, one car-free village, zero stress",
        "3 magic carpets, 2 terrain parks, 1 very tired kid",
    ],
    "contrast": [
        "Big mountain thrills with a soft landing",
        "Premium terrain, mid-range prices",
        "Small village, huge confidence-builder",
    ],
    "question": [
        "What if powder days came with babysitters?",
        "Remember when ski trips were actually relaxing?",
        "What if the bunny slope had Matterhorn views?",
    ],
    "sensory": [
        "Fondue at 10,000 feet, hot chocolate by 3",
        "Cobblestone streets, powder mornings, content kids",
        "Ski through the village, stop for strudel, ski home",
    ],
    "comparative": [
        "Austria's answer to Colorado, at half the price",
        "Like Verbier, if Verbier remembered families exist",
        "Half the cost of Vail, none of the altitude headaches",
    ],
    "identity": [
        "Europe's best-kept family secret",
        "The gentle giant that makes skiing feel easy",
        "Japan's most toddler-friendly powder paradise",
    ],
    "action": [
        "Ski the Dolomites, lunch in Italy",
        "Learn by morning, explore by afternoon",
        "First tracks by 8am, cocoa by 10",
    ],
    "parent_benefit": [
        "Kids exhausted by 3pm. You're welcome.",
        "Ski school pickup on the slopes, not in a parking lot",
        "The ski school your 3-year-old actually wants to return to",
    ],
}


async def extract_tagline_atoms(
    resort_name: str,
    country: str,
    research_data: dict[str, Any],
    quick_take_context: dict[str, Any] | None = None,
) -> TaglineAtoms:
    """
    Extract specific, concrete facts that make taglines memorable.

    This primitive extracts the "atoms" from research data - specific facts,
    numbers, landmarks, and unique features that can be synthesized into
    a memorable tagline.

    Args:
        resort_name: Name of the resort
        country: Country where resort is located
        research_data: Raw research data about the resort
        quick_take_context: Optional existing QuickTakeContextResult data

    Returns:
        TaglineAtoms with extracted facts

    Cost: ~$0.003 with Haiku
    """
    # Prepare context from research
    context_parts = []

    # Add family metrics if available
    if "family_metrics" in research_data:
        fm = research_data["family_metrics"]
        context_parts.append(f"Family metrics: {json.dumps(fm, default=str)}")

    # Add costs if available
    if "costs" in research_data:
        context_parts.append(f"Costs: {json.dumps(research_data['costs'], default=str)}")

    # Add raw research summaries
    if "exa_results" in research_data:
        context_parts.append(f"Research: {str(research_data['exa_results'])[:2000]}")

    # Add quick take context if available
    if quick_take_context:
        context_parts.append(f"Quick take context: {json.dumps(quick_take_context, default=str)}")

    context = "\n\n".join(context_parts)[:4000]

    prompt = f"""Extract TAGLINE ATOMS for {resort_name}, {country}.

Tagline atoms are the SPECIFIC, CONCRETE facts that make memorable taglines.
NOT generic adjectives - actual facts, numbers, names, unique features.

RESEARCH DATA:
{context}

Extract these atoms (use null if not available):

{{
    "numbers": ["list of specific numbers that differentiate this resort",
                "e.g., '93% beginner terrain', 'ski school from age 2.5', 'under-6s ski free'"],
    "landmark_or_icon": "unique visual/geographic identifier (Matterhorn, car-free village, etc.) or null",
    "signature_feeling": "the emotional experience unique to this resort or null",
    "value_angle": "how this compares on price/value to alternatives or null",
    "unexpected_fact": "something surprising about this resort or null",
    "unique_angle": "what makes this resort different from all others or null",
    "signature_experience": "the one thing families will remember or null",
    "memorable_detail": "a sensory detail that sticks or null",
    "anti_pattern": "what this resort is NOT (for differentiation) or null",
    "confidence": 0.0-1.0
}}

Rules:
- SPECIFIC over generic. "Beautiful views" = useless. "Matterhorn from the bunny slope" = gold.
- NUMBERS are powerful. Find them.
- COMPARISONS help. "Half the price of..." "Unlike Vail..."
- If something isn't clearly in the data, use null.

Return only valid JSON."""

    system = """You extract concrete, specific facts from research data.
Your output becomes the building blocks of memorable taglines.
Generic output is failure. Specific output is success."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-3-5-haiku-20241022",
            max_tokens=500,
        )

        parsed = _parse_json_response(response)

        return TaglineAtoms(
            numbers=parsed.get("numbers", []) or [],
            landmark_or_icon=parsed.get("landmark_or_icon"),
            signature_feeling=parsed.get("signature_feeling"),
            value_angle=parsed.get("value_angle"),
            unexpected_fact=parsed.get("unexpected_fact"),
            unique_angle=parsed.get("unique_angle"),
            signature_experience=parsed.get("signature_experience"),
            memorable_detail=parsed.get("memorable_detail"),
            anti_pattern=parsed.get("anti_pattern"),
            extraction_confidence=float(parsed.get("confidence", 0.5)),
        )

    except Exception as e:
        print(f"Tagline atom extraction failed: {e}")
        return TaglineAtoms(extraction_confidence=0.0)


def _format_atoms_for_prompt(atoms: TaglineAtoms) -> str:
    """Format tagline atoms into a prompt-friendly string."""
    parts = []

    if atoms.numbers:
        parts.append(f"NUMBERS: {', '.join(atoms.numbers)}")
    if atoms.landmark_or_icon:
        parts.append(f"LANDMARK: {atoms.landmark_or_icon}")
    if atoms.signature_feeling:
        parts.append(f"FEELING: {atoms.signature_feeling}")
    if atoms.value_angle:
        parts.append(f"VALUE: {atoms.value_angle}")
    if atoms.unexpected_fact:
        parts.append(f"SURPRISE: {atoms.unexpected_fact}")
    if atoms.unique_angle:
        parts.append(f"UNIQUE: {atoms.unique_angle}")
    if atoms.signature_experience:
        parts.append(f"EXPERIENCE: {atoms.signature_experience}")
    if atoms.memorable_detail:
        parts.append(f"DETAIL: {atoms.memorable_detail}")
    if atoms.anti_pattern:
        parts.append(f"NOT: {atoms.anti_pattern}")

    return "\n".join(parts) if parts else "No specific atoms extracted"


def _sample_structural_examples(n: int = 3) -> str:
    """Sample n diverse structural examples for the tagline prompt."""
    categories = list(TAGLINE_STRUCTURAL_EXAMPLES.keys())
    sampled_categories = random.sample(categories, min(n, len(categories)))

    examples = []
    for cat in sampled_categories:
        example = random.choice(TAGLINE_STRUCTURAL_EXAMPLES[cat])
        examples.append(f"- {example} ({cat} structure)")

    return "\n".join(examples)


async def generate_diverse_tagline(
    resort_name: str,
    country: str,
    atoms: TaglineAtoms,
    recent_taglines: list[dict[str, str]] | None = None,
    temperature: float = 0.8,
) -> str:
    """
    Generate a tagline with structural diversity through examples, not rules.

    This uses the extracted atoms and rotated structural examples to produce
    unique, specific taglines. Temperature controls variety.

    Args:
        resort_name: Name of the resort
        country: Country where resort is located
        atoms: Extracted TaglineAtoms for this resort
        recent_taglines: Recent portfolio taglines (for diversity awareness)
        temperature: Claude temperature (0.7-1.0 recommended for variety)

    Returns:
        Generated tagline string

    Cost: ~$0.008 with Sonnet
    """
    # Format atoms for prompt
    atoms_text = _format_atoms_for_prompt(atoms)

    # Sample structural examples (3 different structures each call)
    structural_examples = _sample_structural_examples(3)

    # Format recent taglines for context
    recent_text = ""
    if recent_taglines:
        recent_list = [f"- {t['tagline']} ({t.get('resort', 'unknown')})" for t in recent_taglines[:7]]
        recent_text = f"""
RECENT PORTFOLIO TAGLINES (for awareness - do NOT repeat these structures):
{chr(10).join(recent_list)}
"""

    prompt = f"""Generate a unique tagline for {resort_name}, {country}.

TAGLINE ATOMS (use at least ONE of these specifics):
{atoms_text}

STRUCTURAL VARIETY (use ONE of these patterns, or invent a fresh one):
{structural_examples}
{recent_text}
REQUIREMENTS:
- 8-12 words maximum
- Must include at least ONE specific from the atoms above
- Must NOT use the same structure as recent taglines
- Punchy, memorable, makes families want to visit

Return ONLY the tagline, nothing else."""

    system = """You are a travel copywriter who writes memorable taglines.
Each tagline must be SPECIFIC to this resort - not generic.
Use the atoms provided - don't make up facts.
Vary your structure - don't repeat patterns."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-sonnet-4-20250514",
            max_tokens=100,
            temperature=temperature,
        )

        # Clean up the response
        tagline = response.strip().strip('"').strip("'")

        # Ensure it's not too long
        words = tagline.split()
        if len(words) > 15:
            tagline = " ".join(words[:12])

        return tagline

    except Exception as e:
        print(f"Diverse tagline generation failed: {e}")
        return f"Your family adventure starts in {resort_name}"


async def evaluate_tagline_quality(
    tagline: str,
    atoms: TaglineAtoms,
    resort_name: str,
    recent_taglines: list[dict[str, str]] | None = None,
) -> TaglineQualityScore:
    """
    LLM-based quality assessment using rubric scoring.

    Evaluates tagline on multiple dimensions using a calibrated rubric.
    No regex patterns - pure model judgment.

    Args:
        tagline: The tagline to evaluate
        atoms: The TaglineAtoms that were available for this resort
        resort_name: Name of the resort
        recent_taglines: Recent portfolio taglines for similarity check

    Returns:
        TaglineQualityScore with dimensional scores and feedback

    Cost: ~$0.003 with Haiku
    """
    atoms_text = _format_atoms_for_prompt(atoms)

    recent_text = ""
    if recent_taglines:
        recent_list = [t["tagline"] for t in recent_taglines[:10]]
        recent_text = f"EXISTING PORTFOLIO: {recent_list}"

    prompt = f"""Evaluate this tagline for {resort_name}:

TAGLINE: "{tagline}"

AVAILABLE ATOMS FOR THIS RESORT:
{atoms_text}

{recent_text}

Score each dimension 0.0-1.0:

SPECIFICITY (does it include concrete facts?):
- 0.2: Generic ("great for families", "perfect destination")
- 0.5: Some specificity ("beginner-friendly", "Austrian charm")
- 0.8: Concrete facts ("93% beginner terrain", "Matterhorn views")
- 1.0: Multiple specifics unique to this resort

DIFFERENTIATION (could this ONLY apply to this resort?):
- 0.2: Could apply to 50+ resorts
- 0.5: Could apply to 5-10 similar resorts
- 0.8: Could only apply to 2-3 resorts
- 1.0: Unmistakably THIS resort

STRUCTURE_NOVELTY (is the structure fresh?):
- 0.2: "X meets Y" or other overused patterns
- 0.5: Common but not cliche structure
- 0.8: Fresh structure rarely seen
- 1.0: Inventive structure that surprises

EMOTIONAL_RESONANCE (does it make families feel something?):
- 0.2: Informational only, no feeling
- 0.5: Mild interest
- 0.8: "That sounds nice" reaction
- 1.0: "I need to go there" reaction

VOICE_ALIGNMENT (does it match smart, witty travel friend tone?):
- 0.2: Corporate/brochure feel
- 0.5: Generic travel writing
- 0.8: Matches casual expert tone
- 1.0: Perfectly captures "smart friend" voice

Return JSON:
{{
    "specificity": 0.0-1.0,
    "differentiation": 0.0-1.0,
    "structure_novelty": 0.0-1.0,
    "emotional_resonance": 0.0-1.0,
    "voice_alignment": 0.0-1.0,
    "strongest_element": "brief description",
    "weakest_element": "brief description",
    "improvement_suggestion": "how to improve or null if good",
    "similar_to": "if similar to existing tagline, which one, else null"
}}"""

    system = """You evaluate tagline quality using a calibrated rubric.
Be honest and specific in your assessment.
Overused patterns like "X meets Y" score LOW on structure_novelty."""

    try:
        response = _call_claude(
            prompt,
            system=system,
            model="claude-3-5-haiku-20241022",
            max_tokens=400,
        )

        parsed = _parse_json_response(response)

        # Extract scores
        specificity = float(parsed.get("specificity", 0.5))
        differentiation = float(parsed.get("differentiation", 0.5))
        structure_novelty = float(parsed.get("structure_novelty", 0.5))
        emotional_resonance = float(parsed.get("emotional_resonance", 0.5))
        voice_alignment = float(parsed.get("voice_alignment", 0.5))

        # Calculate overall score (weighted average)
        overall = (
            specificity * 0.25
            + differentiation * 0.25
            + structure_novelty * 0.20
            + emotional_resonance * 0.15
            + voice_alignment * 0.15
        )

        return TaglineQualityScore(
            overall_score=round(overall, 2),
            specificity=specificity,
            differentiation=differentiation,
            structure_novelty=structure_novelty,
            emotional_resonance=emotional_resonance,
            voice_alignment=voice_alignment,
            strongest_element=parsed.get("strongest_element", ""),
            weakest_element=parsed.get("weakest_element", ""),
            improvement_suggestion=parsed.get("improvement_suggestion"),
            similar_to=parsed.get("similar_to"),
            passes_threshold=overall >= 0.7,
        )

    except Exception as e:
        print(f"Tagline quality evaluation failed: {e}")
        return TaglineQualityScore(
            overall_score=0.5,
            specificity=0.5,
            differentiation=0.5,
            structure_novelty=0.5,
            emotional_resonance=0.5,
            voice_alignment=0.5,
            passes_threshold=False,
        )
