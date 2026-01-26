"""Quick Take generation primitive - Editorial Verdict Model.

Quick Takes are the BLUF (Bottom Line Up Front) for each resort.
Parents read this first to decide if they should keep reading.

Design Philosophy (Round 8):
- Specific over generic - no "amazing views" or "great for families"
- Honest tensions - every resort has catches, be upfront
- Declarative confidence - clear recommendations, not hedging
- Numbers that matter - specific ages, costs, percentages
- Family-specific insights - not general ski info

Structure (Editorial Verdict Model):
1. THE HOOK (1 sentence) - Specific, memorable insight
2. THE CONTEXT (1-2 sentences) - Why this matters for YOUR family
3. THE TENSION (1-2 sentences) - What's the catch?
4. THE VERDICT (1 sentence) - Clear recommendation

Quality Gates:
- Word count: 80-120 words
- Specificity score > 0.6
- No forbidden phrases
- At least 2 "Perfect if" conditions
- At least 1 "Skip if" condition (required)
"""

import re
from dataclasses import dataclass, field
from typing import Any

import anthropic

from ..config import settings


# =============================================================================
# FORBIDDEN PHRASES - These kill the authenticity
# =============================================================================

FORBIDDEN_PHRASES = [
    # Generic openers
    "here's the thing",
    "let's be real",
    "let me tell you",
    "the truth is",
    "honestly",
    "to be honest",
    # Empty superlatives
    "world-class",
    "world class",
    "legendary",
    "iconic",
    "breathtaking",
    "stunning",
    "amazing",
    "incredible",
    "spectacular",
    "magnificent",
    "perfect for families",
    "great for families",
    "ideal for families",
    "family-friendly destination",
    # Filler phrases
    "it goes without saying",
    "needless to say",
    "at the end of the day",
    "when all is said and done",
    "in conclusion",
    # Marketing speak
    "hidden gem",
    "best-kept secret",
    "must-visit",
    "bucket list",
    "unforgettable experience",
    "memories that last a lifetime",
]


@dataclass
class QuickTakeContext:
    """Input context for Quick Take generation.

    These fields should be extracted during research phase
    via extract_quick_take_context().
    """

    resort_name: str
    country: str
    region: str | None = None

    # Core research (required)
    family_score: float | None = None
    best_age_min: int | None = None
    best_age_max: int | None = None

    # Editorial inputs (from intelligence.py extraction)
    unique_angle: str | None = None  # What makes this different?
    signature_experience: str | None = None  # The ONE thing families remember
    primary_strength: str | None = None  # Best thing about this resort
    primary_weakness: str | None = None  # REQUIRED - no resort is perfect
    who_should_skip: str | None = None  # Clear "not for you if..."
    memorable_detail: str | None = None  # Sensory/experiential hook

    # Context
    price_context: str | None = None  # "Half the cost of Aspen"
    terrain_pct_beginner: float | None = None
    has_ski_school: bool = True
    ski_school_min_age: int | None = None
    has_childcare: bool = False
    kids_ski_free_age: int | None = None


@dataclass
class QuickTakeResult:
    """Result of Quick Take generation."""

    # Generated content
    quick_take_html: str
    perfect_if: list[str]
    skip_if: list[str]

    # Quality metrics
    word_count: int
    specificity_score: float
    forbidden_phrases_found: list[str]

    # Validation
    is_valid: bool
    validation_errors: list[str] = field(default_factory=list)

    # Metadata
    model_used: str = "claude-opus-4-20250514"
    generation_reasoning: str = ""


def _get_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def check_forbidden_phrases(text: str) -> list[str]:
    """Check text for forbidden phrases.

    Returns list of found forbidden phrases (empty if none).
    """
    text_lower = text.lower()
    found = []

    for phrase in FORBIDDEN_PHRASES:
        if phrase in text_lower:
            found.append(phrase)

    return found


def calculate_specificity_score(text: str) -> float:
    """Calculate how specific vs generic the content is.

    Factors that increase score:
    - Numbers (ages, percentages, prices, distances)
    - Specific place names (hotels, restaurants, lifts)
    - Time references (seasons, months, hours)
    - Comparisons to other resorts
    - Specific activities or features

    Factors that decrease score:
    - Generic adjectives (great, nice, beautiful)
    - Vague phrases (many options, various activities)
    - Passive voice
    - Hedge words (might, could, perhaps)

    Returns: 0.0 - 1.0
    """
    if not text:
        return 0.0

    score = 0.5  # Start neutral

    # Positive signals (increase score)
    # Numbers
    number_matches = re.findall(r'\b\d+(?:\.\d+)?(?:%|km|miles?|hours?|minutes?|years?|CHF|EUR|USD|\$|€)?\b', text)
    score += min(len(number_matches) * 0.05, 0.2)  # Up to +0.2

    # Age references
    age_patterns = [
        r'\bage(?:s)?\s+\d+',
        r'\b\d+(?:\s*-\s*|\s+to\s+)\d+\s*(?:year|yr)',
        r'under\s+\d+',
        r'over\s+\d+',
    ]
    for pattern in age_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.05

    # Specific comparisons
    comparison_patterns = [
        r'compared to',
        r'unlike',
        r'half the (?:price|cost)',
        r'cheaper than',
        r'more (?:expensive|affordable) than',
        r'similar to',
    ]
    for pattern in comparison_patterns:
        if re.search(pattern, text, re.IGNORECASE):
            score += 0.05

    # Concrete details (capitalized proper nouns that aren't resort name)
    proper_nouns = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', text)
    # Filter out common non-specific words
    non_specific = {'The', 'This', 'That', 'Here', 'There', 'When', 'Where', 'What', 'Why', 'How'}
    specific_nouns = [n for n in proper_nouns if n not in non_specific]
    score += min(len(specific_nouns) * 0.02, 0.1)

    # Negative signals (decrease score)
    # Generic adjectives
    generic_adjectives = [
        'great', 'nice', 'good', 'beautiful', 'wonderful', 'excellent',
        'fantastic', 'awesome', 'perfect', 'ideal', 'best', 'top',
    ]
    for adj in generic_adjectives:
        if re.search(rf'\b{adj}\b', text, re.IGNORECASE):
            score -= 0.03

    # Vague quantifiers
    vague_words = [
        'many', 'various', 'several', 'numerous', 'lots of', 'plenty of',
        'some', 'most', 'often', 'usually', 'typically', 'generally',
    ]
    for word in vague_words:
        if re.search(rf'\b{word}\b', text, re.IGNORECASE):
            score -= 0.02

    # Hedge words
    hedge_words = [
        'might', 'could', 'perhaps', 'maybe', 'possibly', 'potentially',
        'somewhat', 'fairly', 'quite', 'rather',
    ]
    for word in hedge_words:
        if re.search(rf'\b{word}\b', text, re.IGNORECASE):
            score -= 0.03

    # Clamp to valid range
    return max(0.0, min(1.0, score))


def validate_quick_take(result: QuickTakeResult, context: QuickTakeContext) -> QuickTakeResult:
    """Validate Quick Take meets quality gates.

    Quality Gates:
    - Word count: 80-120 words
    - Specificity score > 0.6
    - No forbidden phrases
    - At least 2 "Perfect if" conditions
    - At least 1 "Skip if" condition
    """
    errors = []

    # Word count check
    if result.word_count < 80:
        errors.append(f"Too short: {result.word_count} words (min 80)")
    elif result.word_count > 120:
        errors.append(f"Too long: {result.word_count} words (max 120)")

    # Specificity check
    if result.specificity_score < 0.6:
        errors.append(f"Low specificity: {result.specificity_score:.2f} (min 0.6)")

    # Forbidden phrases check
    if result.forbidden_phrases_found:
        errors.append(f"Forbidden phrases: {', '.join(result.forbidden_phrases_found[:3])}")

    # Perfect if count
    if len(result.perfect_if) < 2:
        errors.append(f"Need at least 2 'Perfect if' conditions (got {len(result.perfect_if)})")

    # Skip if count (REQUIRED)
    if len(result.skip_if) < 1:
        errors.append("REQUIRED: At least 1 'Skip if' condition")

    result.validation_errors = errors
    result.is_valid = len(errors) == 0

    return result


async def generate_quick_take(
    context: QuickTakeContext,
    voice_profile: str = "snowthere_guide",
) -> QuickTakeResult:
    """Generate a Quick Take using the Editorial Verdict Model.

    This is the new approach for Round 8, replacing the generic
    write_section("quick_take") approach.

    The Editorial Verdict Model structure:
    1. THE HOOK - Specific, memorable insight
    2. THE CONTEXT - Why this matters for YOUR family
    3. THE TENSION - What's the catch?
    4. THE VERDICT - Clear recommendation

    Args:
        context: QuickTakeContext with research data
        voice_profile: Voice profile to use

    Returns:
        QuickTakeResult with generated content and quality metrics
    """
    client = _get_client()

    # Build the prompt with all available context
    context_section = f"""
RESORT: {context.resort_name}, {context.country}
{f"REGION: {context.region}" if context.region else ""}

FAMILY DATA:
- Family Score: {context.family_score}/10 {f"(best for ages {context.best_age_min}-{context.best_age_max})" if context.best_age_min else ""}
- Ski School: {"Yes" if context.has_ski_school else "No"}{f" (from age {context.ski_school_min_age})" if context.ski_school_min_age else ""}
- Childcare: {"Yes" if context.has_childcare else "No"}
- Kids Ski Free: {f"Under {context.kids_ski_free_age}" if context.kids_ski_free_age else "No/Unknown"}
- Beginner Terrain: {f"{context.terrain_pct_beginner:.0f}%" if context.terrain_pct_beginner else "Unknown"}

EDITORIAL INPUTS:
- Unique Angle: {context.unique_angle or "Not yet researched"}
- Signature Experience: {context.signature_experience or "Not yet researched"}
- Primary Strength: {context.primary_strength or "Not yet researched"}
- Primary Weakness: {context.primary_weakness or "REQUIRED - must identify"}
- Who Should Skip: {context.who_should_skip or "REQUIRED - must identify"}
- Memorable Detail: {context.memorable_detail or "Not yet researched"}
- Price Context: {context.price_context or "Not yet researched"}
"""

    prompt = f"""Write a Quick Take for this ski resort using the Editorial Verdict Model.

{context_section}

STRUCTURE (Follow exactly):

1. THE HOOK (1 sentence)
   A specific, memorable insight that captures THIS resort's essence.
   NOT generic ("beautiful views"). Must be specific to this place.

2. THE CONTEXT (1-2 sentences)
   Why this matters for YOUR family specifically.
   Reference ages, skill levels, trip types.

3. THE TENSION (1-2 sentences)
   What's the catch? Be honest - families trust honest assessments.
   Every resort has downsides. Name them.

4. THE VERDICT (1 sentence)
   Clear recommendation: Who should book this?

Then provide:
- 3-4 "Perfect if..." bullets (specific conditions, not generic)
- 2-3 "Skip if..." bullets (honest deal-breakers - REQUIRED)

VOICE:
- Smart, witty, efficient like a well-traveled friend
- Declarative confidence - don't hedge
- Numbers that matter (ages, percentages, costs)
- No generic superlatives

FORBIDDEN:
- "Here's the thing..."
- "Let's be real..."
- Generic adjectives (amazing, stunning, incredible)
- "Perfect for families" without specifics
- "Hidden gem" or "best-kept secret"

Word count: 80-120 words for the main Quick Take (not including bullets).

Return as JSON:
{{
    "quick_take_html": "<p>The hook...</p><p>The context...</p><p>The tension...</p><p>The verdict...</p>",
    "perfect_if": ["specific condition 1", "specific condition 2", ...],
    "skip_if": ["deal-breaker 1", "deal-breaker 2", ...],
    "reasoning": "Brief explanation of editorial choices"
}}"""

    system = f"""You are a travel editor writing Quick Takes for Snowthere, a family ski resort guide.

Your job: Help parents decide in 30 seconds if this resort is right for THEIR family.

Voice: {voice_profile} - Smart, witty, efficient. Like a well-traveled friend who's skied everywhere and tells it straight.

Critical rules:
1. NEVER start with "Here's the thing" or similar phrases
2. NEVER use generic superlatives (amazing, stunning, incredible)
3. ALWAYS include specific numbers (ages, percentages, costs)
4. ALWAYS include honest downsides/tensions
5. ALWAYS provide at least 1 "Skip if" condition

Your Quick Takes should make parents feel confident they understand what they're getting into.
"""

    try:
        message = client.messages.create(
            model=settings.content_model,  # Use Opus for quality
            max_tokens=1500,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = message.content[0].text

        # Parse JSON response
        import json

        # Handle markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        parsed = json.loads(response_text.strip())

        quick_take_html = parsed.get("quick_take_html", "")
        perfect_if = parsed.get("perfect_if", [])
        skip_if = parsed.get("skip_if", [])
        reasoning = parsed.get("reasoning", "")

        # Calculate metrics
        # Strip HTML for word count and analysis
        plain_text = re.sub(r'<[^>]+>', ' ', quick_take_html)
        plain_text = re.sub(r'\s+', ' ', plain_text).strip()
        word_count = len(plain_text.split())

        specificity = calculate_specificity_score(plain_text)
        forbidden = check_forbidden_phrases(plain_text)

        result = QuickTakeResult(
            quick_take_html=quick_take_html,
            perfect_if=perfect_if,
            skip_if=skip_if,
            word_count=word_count,
            specificity_score=specificity,
            forbidden_phrases_found=forbidden,
            is_valid=True,  # Will be updated by validation
            model_used=settings.content_model,
            generation_reasoning=reasoning,
        )

        # Validate against quality gates
        result = validate_quick_take(result, context)

        return result

    except Exception as e:
        # Return failed result
        return QuickTakeResult(
            quick_take_html="",
            perfect_if=[],
            skip_if=[],
            word_count=0,
            specificity_score=0.0,
            forbidden_phrases_found=[],
            is_valid=False,
            validation_errors=[f"Generation failed: {str(e)}"],
        )


async def regenerate_quick_take_if_invalid(
    context: QuickTakeContext,
    previous_result: QuickTakeResult,
    max_attempts: int = 2,
) -> QuickTakeResult:
    """Attempt to regenerate Quick Take if validation failed.

    Provides feedback on what went wrong to guide the next attempt.
    """
    if previous_result.is_valid:
        return previous_result

    # Build feedback for retry
    feedback = "PREVIOUS ATTEMPT FAILED. Issues:\n"
    for error in previous_result.validation_errors:
        feedback += f"- {error}\n"

    if previous_result.forbidden_phrases_found:
        feedback += f"\nRemove these phrases: {', '.join(previous_result.forbidden_phrases_found)}"

    if previous_result.specificity_score < 0.6:
        feedback += f"\nIncrease specificity (current: {previous_result.specificity_score:.2f}). Add more:"
        feedback += "\n- Specific numbers (ages, costs, distances)"
        feedback += "\n- Named places (hotels, restaurants, lifts)"
        feedback += "\n- Concrete comparisons to other resorts"

    # For now, just return the original - actual retry would need modified prompt
    # This is a placeholder for the full implementation
    return previous_result
