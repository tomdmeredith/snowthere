"""Three-Agent Approval Panel - Content quality evaluation system.

This module implements the agent-native approval panel that replaces
simple confidence thresholds with diverse AI perspectives aligned with
our mission: helping overwhelmed families discover achievable skiing.

Three agents evaluate content:
- TrustGuard: Accuracy and fact-checking
- FamilyValue: Completeness and actionability (includes mobile-friendliness)
- VoiceCoach: Tone and brand alignment

Publication requires 2/3 majority approval. Content iterates until approved
(max 3 iterations) or goes to draft with agent notes.

Design Principles:
- GRANULARITY: Atomic primitives for each evaluation type
- COMPOSABILITY: Panel can be run alone or in iteration loop
- IMPROVEMENT OVER TIME: Learning from approval patterns
"""

import asyncio
import json
from dataclasses import dataclass, field
from typing import Any, Literal

import anthropic

from ..config import settings
from ..voice_profiles import get_voice_profile


# =============================================================================
# Data Structures
# =============================================================================


@dataclass
class EvaluationResult:
    """Result from a single agent evaluation."""

    agent_name: str  # "TrustGuard", "FamilyValue", "VoiceCoach"
    verdict: Literal["approve", "improve", "reject"]
    confidence: float  # 0.0-1.0
    issues: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)
    reasoning: str = ""


@dataclass
class PanelResult:
    """Aggregated result from all three agents."""

    votes: list[EvaluationResult]
    approved: bool  # 2/3 majority
    approve_count: int
    improve_count: int
    reject_count: int
    combined_issues: list[str] = field(default_factory=list)
    combined_suggestions: list[str] = field(default_factory=list)


@dataclass
class ApprovalLoopResult:
    """Result of the full approval iteration loop."""

    final_content: dict[str, Any]
    approved: bool
    iterations: int
    panel_history: list[PanelResult] = field(default_factory=list)
    final_issues: list[str] = field(default_factory=list)


# =============================================================================
# Constants
# =============================================================================


REQUIRED_SECTIONS = [
    "quick_take",
    "family_metrics",
    "getting_there",
    "where_to_stay",
    "lift_tickets",
    "on_mountain",
    "off_mountain",
    "ski_calendar",
    "faq",
]


# =============================================================================
# Voice Pattern Post-Processing (Deterministic Cleanup)
# =============================================================================
# These patterns slip through Claude's voice coaching. We catch them here
# with deterministic regex to ensure zero tolerance for forbidden patterns.
# =============================================================================

import re

FORBIDDEN_PATTERNS = [
    # Performative openers - only truly cringeworthy ones
    # NOTE: "Here's the thing", "Here's the deal", "Real talk" are now ALLOWED
    # sparingly (max 1 per page) when followed by genuine substance.
    ("I'm not gonna lie", ""),
    ("Let me tell you", ""),
    ("Confession:", ""),
    ("Truth bomb:", ""),
    ("Hot take:", ""),
    # LLM transition markers - dead giveaways of AI content
    ("Additionally,", ""),
    ("Furthermore,", ""),
    ("Moreover,", ""),
    ("Subsequently,", ""),
    ("In addition,", ""),
    ("It's worth noting", "Note:"),
    ("It's important to note", "Note:"),
    ("It should be noted", "Note:"),
    ("That being said,", ""),
    ("With that being said,", ""),
    ("Having said that,", ""),
    # Corporate/generic filler
    ("At the end of the day,", ""),
    ("When all is said and done,", ""),
    ("For what it's worth,", ""),
]


def apply_voice_post_processing(content: dict[str, Any]) -> dict[str, Any]:
    """Apply deterministic pattern fixes to content sections.

    This catches voice violations that slip through the approval panel.
    Called after improve_content() and at all return points in approval_loop().

    The function is idempotent - safe to call multiple times on same content.
    """
    processed = {}

    for key, value in content.items():
        if isinstance(value, str):
            text = value
            for pattern, replacement in FORBIDDEN_PATTERNS:
                # Case-insensitive replacement
                text = re.sub(re.escape(pattern), replacement, text, flags=re.IGNORECASE)

            # Clean up artifacts from removals
            text = re.sub(r'\s+', ' ', text)  # Multiple spaces → single space
            text = re.sub(r'\s+([.,!?])', r'\1', text)  # Space before punctuation
            text = re.sub(r'^\s+', '', text)  # Leading whitespace
            text = re.sub(r'\s+$', '', text)  # Trailing whitespace
            text = re.sub(r'^[.,!?]\s*', '', text)  # Leading punctuation from removals

            processed[key] = text.strip()
        else:
            # Pass through non-string values unchanged
            processed[key] = value

    return processed


# =============================================================================
# Helper Functions
# =============================================================================


def _get_client() -> anthropic.Anthropic:
    """Get Anthropic client instance."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def _call_claude(
    prompt: str,
    system: str | None = None,
    model: str | None = None,
    max_tokens: int = 1500,
) -> str:
    """Make a Claude API call and return the text response."""
    client = _get_client()

    # Use default_model for evaluations (fast, cheap)
    model = model or settings.default_model

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


def _format_content_for_eval(content: dict[str, Any]) -> str:
    """Format content dict for evaluation prompts."""
    lines = []
    for key, value in content.items():
        if isinstance(value, str):
            # Truncate long content
            display = value[:2000] + "..." if len(value) > 2000 else value
            lines.append(f"\n## {key.upper()}\n{display}")
        elif isinstance(value, list):
            lines.append(f"\n## {key.upper()}")
            for item in value[:10]:  # Limit list items
                if isinstance(item, dict):
                    lines.append(f"  - {json.dumps(item)[:200]}")
                else:
                    lines.append(f"  - {item}")
        elif isinstance(value, dict):
            lines.append(f"\n## {key.upper()}")
            for k, v in value.items():
                lines.append(f"  {k}: {str(v)[:200]}")
        else:
            lines.append(f"{key}: {value}")
    return "\n".join(lines)


def _format_sources_for_eval(sources: list[dict[str, Any]]) -> str:
    """Format sources list for evaluation prompts."""
    if not sources:
        return "No sources provided"

    lines = []
    for i, source in enumerate(sources[:15], 1):  # Limit to 15 sources
        title = source.get("title", "Untitled")
        url = source.get("url", "")
        snippet = source.get("snippet", source.get("text", ""))[:300]
        lines.append(f"{i}. [{title}]({url})\n   {snippet}")
    return "\n".join(lines)


# =============================================================================
# Atomic Evaluation Primitives (GRANULARITY)
# =============================================================================


async def evaluate_trust(
    content: dict[str, Any],
    sources: list[dict[str, Any]],
    resort_data: dict[str, Any],
) -> EvaluationResult:
    """
    TrustGuard evaluation - fact-checking and accuracy.

    Mission: Protect families from misinformation. They're making expensive,
    complex trip decisions. Inaccurate info could ruin their vacation.

    Evaluates:
    - Source verification: Are facts backed by provided sources?
    - Price realism: Are costs realistic for this region/tier?
    - Consistency: Do metrics match narrative? Trail percentages add up?
    - Red flags: Outdated info? Claims without evidence? Suspicious scores?

    Args:
        content: The generated content to evaluate
        sources: Research sources used to generate content
        resort_data: Resort metadata (country, scores, etc.)

    Returns:
        EvaluationResult with verdict, issues, and suggestions
    """
    country = resort_data.get("country", "Unknown")
    family_score = resort_data.get("family_overall_score", "N/A")
    resort_name = resort_data.get("name", "Unknown Resort")

    prompt = f"""You are TrustGuard, the fact-checker for Snowthere family ski guides.

Your mission: Protect families from misinformation. They're making expensive
trip decisions. Inaccurate info could ruin their vacation.

RESORT: {resort_name} ({country})
FAMILY SCORE: {family_score}/10

SOURCES PROVIDED:
{_format_sources_for_eval(sources)}

CONTENT TO EVALUATE:
{_format_content_for_eval(content)}

Evaluate for TRUST:
1. Are facts backed by sources? Look for specific claims that should have evidence.
2. Are prices realistic for {country}? European Alps: €40-70 adult tickets. US: $100-200+.
3. Do family metrics (score: {family_score}/10) match the description?
4. Any red flags? Outdated venues, impossible claims, suspicious scores?

Output JSON:
{{
    "verdict": "approve" | "improve" | "reject",
    "confidence": 0.0-1.0,
    "issues": ["specific issue"],
    "suggestions": ["how to fix"],
    "reasoning": "2-3 sentence assessment"
}}

Be conservative: When uncertain, flag for improvement."""

    system = """You are TrustGuard, a meticulous fact-checker protecting families from misinformation.
Your standards are high because families are making expensive decisions based on this content.
When in doubt, flag for improvement rather than approve.
Focus on verifiable facts, not style or tone (that's VoiceCoach's job)."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return EvaluationResult(
            agent_name="TrustGuard",
            verdict=parsed.get("verdict", "improve"),
            confidence=float(parsed.get("confidence", 0.5)),
            issues=parsed.get("issues", []),
            suggestions=parsed.get("suggestions", []),
            reasoning=parsed.get("reasoning", "Evaluation completed"),
        )
    except (json.JSONDecodeError, KeyError) as e:
        return EvaluationResult(
            agent_name="TrustGuard",
            verdict="improve",
            confidence=0.3,
            issues=[f"Failed to parse TrustGuard response: {e}"],
            suggestions=["Re-run evaluation"],
            reasoning="Evaluation parsing failed",
        )


async def evaluate_completeness(
    content: dict[str, Any],
    resort_data: dict[str, Any],
    required_sections: list[str] | None = None,
) -> EvaluationResult:
    """
    FamilyValue evaluation - completeness and actionability.

    Mission: Ensure families can actually PLAN A TRIP from this guide.
    They're overwhelmed—we must be actionable, not just informative.

    Evaluates:
    - Completeness: All required sections present and substantive?
    - Specificity: Named hotels, actual prices, specific restaurants?
    - Mobile-friendliness: Short paragraphs, scannable, tables not too wide?
    - GEO optimization: Tables for data, FAQs with natural questions?

    Args:
        content: The generated content to evaluate
        resort_data: Resort metadata
        required_sections: Override default required sections

    Returns:
        EvaluationResult with verdict, issues, and suggestions
    """
    sections = required_sections or REQUIRED_SECTIONS
    resort_name = resort_data.get("name", "Unknown Resort")

    # Check which sections are present
    present_sections = [s for s in sections if s in content and content[s]]
    missing_sections = [s for s in sections if s not in content or not content[s]]

    prompt = f"""You are FamilyValue, the product manager for Snowthere.

Your mission: Ensure families can PLAN A TRIP from this guide.
They're overwhelmed. We need actionable, not just informative.

RESORT: {resort_name}

CONTENT TO EVALUATE:
{_format_content_for_eval(content)}

SECTION CHECK:
- Present: {', '.join(present_sections) or 'None'}
- Missing: {', '.join(missing_sections) or 'None'}

Required sections (all must be substantive):
□ quick_take (BLUF verdict with "Perfect if/Skip if")
□ family_metrics (table with scores)
□ getting_there (airports, transfers, times)
□ where_to_stay (3 tiers with NAMED properties)
□ lift_tickets (ACTUAL prices + pass info)
□ on_mountain (terrain breakdown, ski school with ages)
□ off_mountain (NAMED restaurants, activities)
□ ski_calendar (monthly table)
□ faq (5-8 natural questions)

Mobile-friendliness checklist:
□ Paragraphs ≤3 sentences (scannable on phone)
□ Tables ≤5 columns (no horizontal scroll)
□ Clear headers for skimming
□ Bullet points where appropriate

Specificity checklist:
□ Named hotels (not just "budget options")
□ Actual prices (not just "affordable")
□ Named restaurants/activities
□ Specific ages for kids programs

Output JSON:
{{
    "verdict": "approve" | "improve" | "reject",
    "confidence": 0.0-1.0,
    "issues": ["missing section or vague content"],
    "suggestions": ["what specific info to add"],
    "reasoning": "assessment"
}}

The test: Could a family book this trip with just this guide?"""

    system = """You are FamilyValue, ensuring content is complete and actionable for families.
Your bar is high: content must be USEFUL, not just informative.
Missing sections or vague content = improvement needed.
If families can't plan their trip from this guide, it's not ready."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return EvaluationResult(
            agent_name="FamilyValue",
            verdict=parsed.get("verdict", "improve"),
            confidence=float(parsed.get("confidence", 0.5)),
            issues=parsed.get("issues", []),
            suggestions=parsed.get("suggestions", []),
            reasoning=parsed.get("reasoning", "Evaluation completed"),
        )
    except (json.JSONDecodeError, KeyError) as e:
        return EvaluationResult(
            agent_name="FamilyValue",
            verdict="improve",
            confidence=0.3,
            issues=[f"Failed to parse FamilyValue response: {e}"],
            suggestions=["Re-run evaluation"],
            reasoning="Evaluation parsing failed",
        )


async def evaluate_voice(
    content: dict[str, Any],
    voice_profile: str = "snowthere_guide",
) -> EvaluationResult:
    """
    VoiceCoach evaluation - tone and brand alignment.

    Mission: Smart, practical, and clear. Expert advice that respects
    the reader's time and intelligence.

    Evaluates:
    - Personality: Does it have personality without being performative?
    - Jargon: Technical terms explained? Not assuming expert knowledge?
    - Brand alignment: Smart, witty, efficient (Morning Brew for ski trips)?
    - Pattern match: Uses appropriate voice patterns?

    Args:
        content: The generated content to evaluate
        voice_profile: Target voice profile name

    Returns:
        EvaluationResult with verdict, issues, and suggestions
    """
    profile = get_voice_profile(voice_profile)

    prompt = f"""You are VoiceCoach, editorial director for Snowthere.

Your mission: Smart, practical, and clear. Expert advice that
respects the reader's time and intelligence.

TARGET VOICE: {profile.name}
{profile.description}

TONE:
{chr(10).join(f'- {t}' for t in profile.tone)}

PATTERNS TO USE (sparingly, only when valuable):
{chr(10).join(f'- {p}' for p in profile.patterns) if profile.patterns else '- None specific'}

AVOID:
{chr(10).join(f'- {a}' for a in profile.avoid)}

ALWAYS INCLUDE:
{chr(10).join(f'- {i}' for i in profile.include)}

CONTENT TO EVALUATE:
{_format_content_for_eval(content)}

Evaluate for VOICE:
1. Does it sound like expert advice from a trusted source?
2. Does it have personality without being performative? (honest asides, dry humor, sentence rhythm variety)
3. Technical terms explained for non-skiers?
4. Quick Take: Would a parent feel informed and confident?
5. Conversational patterns used sparingly and earned (not as empty filler)?

Output JSON:
{{
    "verdict": "approve" | "improve" | "reject",
    "confidence": 0.0-1.0,
    "issues": ["phrase or section that misses voice"],
    "suggestions": ["how to improve"],
    "reasoning": "voice assessment"
}}

The test: Would a parent feel informed and confident after reading this?"""

    system = """You are VoiceCoach, guardian of the Snowthere brand voice.
Content should be expert and clear without being performative or corporate.
Flag: jargon, intimidating tone, corporate-speak, excessive enthusiasm, forced warmth.
Approve: confident expertise, clear guidance, personality that earns its place."""

    response = _call_claude(prompt, system=system)

    try:
        parsed = _parse_json_response(response)
        return EvaluationResult(
            agent_name="VoiceCoach",
            verdict=parsed.get("verdict", "improve"),
            confidence=float(parsed.get("confidence", 0.5)),
            issues=parsed.get("issues", []),
            suggestions=parsed.get("suggestions", []),
            reasoning=parsed.get("reasoning", "Evaluation completed"),
        )
    except (json.JSONDecodeError, KeyError) as e:
        return EvaluationResult(
            agent_name="VoiceCoach",
            verdict="improve",
            confidence=0.3,
            issues=[f"Failed to parse VoiceCoach response: {e}"],
            suggestions=["Re-run evaluation"],
            reasoning="Evaluation parsing failed",
        )


# =============================================================================
# Panel Orchestration (COMPOSABILITY)
# =============================================================================


async def run_approval_panel(
    content: dict[str, Any],
    sources: list[dict[str, Any]],
    resort_data: dict[str, Any],
    voice_profile: str = "snowthere_guide",
) -> PanelResult:
    """
    Run all three evaluators in parallel and aggregate results.

    This is the core panel orchestration that composes the atomic primitives.
    Uses asyncio.gather for parallel execution (~$0.15-0.20 per run).

    Args:
        content: Generated content to evaluate
        sources: Research sources used
        resort_data: Resort metadata
        voice_profile: Target voice profile

    Returns:
        PanelResult with aggregated votes and combined feedback
    """
    # Run all three evaluations in parallel
    results = await asyncio.gather(
        evaluate_trust(content, sources, resort_data),
        evaluate_completeness(content, resort_data),
        evaluate_voice(content, voice_profile),
        return_exceptions=True,
    )

    # Handle any exceptions that occurred
    votes: list[EvaluationResult] = []
    for result in results:
        if isinstance(result, Exception):
            # Create a failed evaluation result
            votes.append(
                EvaluationResult(
                    agent_name="Unknown",
                    verdict="improve",
                    confidence=0.0,
                    issues=[f"Evaluation failed: {result}"],
                    suggestions=["Re-run panel"],
                    reasoning="Evaluation threw an exception",
                )
            )
        else:
            votes.append(result)

    # Count verdicts
    approve_count = sum(1 for v in votes if v.verdict == "approve")
    improve_count = sum(1 for v in votes if v.verdict == "improve")
    reject_count = sum(1 for v in votes if v.verdict == "reject")

    # 2/3 majority required for approval
    approved = approve_count >= 2

    # Combine issues and suggestions from non-approving agents
    combined_issues = []
    combined_suggestions = []
    for vote in votes:
        if vote.verdict != "approve":
            combined_issues.extend(vote.issues)
            combined_suggestions.extend(vote.suggestions)

    return PanelResult(
        votes=votes,
        approved=approved,
        approve_count=approve_count,
        improve_count=improve_count,
        reject_count=reject_count,
        combined_issues=combined_issues,
        combined_suggestions=combined_suggestions,
    )


# =============================================================================
# Content Improvement
# =============================================================================


async def improve_content(
    content: dict[str, Any],
    issues: list[str],
    suggestions: list[str],
    sources: list[dict[str, Any]] | None = None,
    voice_profile: str = "snowthere_guide",
) -> dict[str, Any]:
    """
    Apply improvements based on panel feedback.

    Uses Claude to revise content addressing specific issues and suggestions
    while maintaining the target voice profile.

    Args:
        content: Current content to improve
        issues: List of issues identified by the panel
        suggestions: List of suggestions for improvement
        sources: Original sources (for fact-checking improvements)
        voice_profile: Target voice profile

    Returns:
        Improved content dict
    """
    profile = get_voice_profile(voice_profile)

    issues_str = "\n".join(f"- {issue}" for issue in issues) if issues else "None"
    suggestions_str = (
        "\n".join(f"- {suggestion}" for suggestion in suggestions)
        if suggestions
        else "None"
    )
    sources_str = _format_sources_for_eval(sources) if sources else "Not provided"

    prompt = f"""Improve this content based on panel feedback.

CURRENT CONTENT:
{_format_content_for_eval(content)}

ISSUES TO FIX:
{issues_str}

SUGGESTIONS:
{suggestions_str}

SOURCES (for fact-checking):
{sources_str}

TARGET VOICE: {profile.name}
{profile.description}

Instructions:
1. Address each issue specifically
2. Incorporate suggestions where possible
3. Maintain the target voice profile
4. Keep all accurate information
5. Add specificity where content is vague
6. Ensure mobile-friendliness (short paragraphs, scannable)

Return the improved content as JSON with the same structure as the input.
Only include sections that exist in the input. Do not add new sections.

Return JSON:
{{
    "quick_take": "...",
    "getting_there": "...",
    ... (only sections from input)
}}"""

    system = f"""You are an expert content editor improving family ski resort guides.
Your goal is to address specific issues while maintaining quality and voice.

Voice Profile: {profile.name}
- {profile.description}
- Tone: {', '.join(profile.tone)}
- Avoid: {', '.join(profile.avoid[:5])}

Be surgical: fix the issues without rewriting content that's already good.
Preserve all accurate factual information."""

    # Use content model for better quality improvements
    response = _call_claude(
        prompt, system=system, model=settings.content_model, max_tokens=4000
    )

    try:
        improved = _parse_json_response(response)
        # Preserve any keys from original content not in response
        for key, value in content.items():
            if key not in improved:
                improved[key] = value
        # Apply voice pattern cleanup before returning
        return apply_voice_post_processing(improved)
    except json.JSONDecodeError:
        # Return original content if parsing fails (still apply cleanup)
        return apply_voice_post_processing(content)


# =============================================================================
# Full Approval Loop (EMERGENT CAPABILITY)
# =============================================================================


async def approval_loop(
    content: dict[str, Any],
    sources: list[dict[str, Any]],
    resort_data: dict[str, Any],
    voice_profile: str = "snowthere_guide",
    max_iterations: int = 3,
) -> ApprovalLoopResult:
    """
    Run the full approval iteration loop.

    This is the "feature as prompt" - the complete autonomous approval workflow
    that iterates until content is approved or max iterations reached.

    Flow:
    1. Run approval panel
    2. If approved (2/3 majority), return success
    3. If not approved, apply improvements based on feedback
    4. Repeat until approved or max iterations

    Args:
        content: Initial content to evaluate
        sources: Research sources
        resort_data: Resort metadata
        voice_profile: Target voice profile
        max_iterations: Maximum improvement iterations (default 3)

    Returns:
        ApprovalLoopResult with final content and approval status
    """
    current_content = content.copy()
    panel_history: list[PanelResult] = []

    for iteration in range(1, max_iterations + 1):
        # Run the approval panel
        panel_result = await run_approval_panel(
            current_content,
            sources,
            resort_data,
            voice_profile,
        )
        panel_history.append(panel_result)

        if panel_result.approved:
            # Success! Content approved by 2/3 majority
            # Apply voice post-processing as final cleanup
            return ApprovalLoopResult(
                final_content=apply_voice_post_processing(current_content),
                approved=True,
                iterations=iteration,
                panel_history=panel_history,
                final_issues=[],
            )

        # Not approved - check if we should iterate
        if iteration < max_iterations:
            # Apply improvements based on panel feedback
            current_content = await improve_content(
                current_content,
                panel_result.combined_issues,
                panel_result.combined_suggestions,
                sources,
                voice_profile,
            )
        else:
            # Max iterations reached - return as not approved
            # Still apply voice post-processing for consistency
            return ApprovalLoopResult(
                final_content=apply_voice_post_processing(current_content),
                approved=False,
                iterations=iteration,
                panel_history=panel_history,
                final_issues=panel_result.combined_issues,
            )

    # Should not reach here, but handle edge case
    return ApprovalLoopResult(
        final_content=apply_voice_post_processing(current_content),
        approved=False,
        iterations=max_iterations,
        panel_history=panel_history,
        final_issues=["Max iterations reached without approval"],
    )


# =============================================================================
# Utility Functions
# =============================================================================


def format_panel_summary(panel_result: PanelResult) -> str:
    """Format panel result as human-readable summary."""
    lines = [
        f"Panel Result: {'✅ APPROVED' if panel_result.approved else '❌ NOT APPROVED'}",
        f"Votes: {panel_result.approve_count} approve, {panel_result.improve_count} improve, {panel_result.reject_count} reject",
        "",
        "Agent Verdicts:",
    ]

    for vote in panel_result.votes:
        emoji = "✅" if vote.verdict == "approve" else "⚠️" if vote.verdict == "improve" else "❌"
        lines.append(f"  {emoji} {vote.agent_name}: {vote.verdict} ({vote.confidence:.0%})")
        lines.append(f"     {vote.reasoning}")

    if panel_result.combined_issues:
        lines.append("")
        lines.append("Combined Issues:")
        for issue in panel_result.combined_issues:
            lines.append(f"  - {issue}")

    return "\n".join(lines)


def format_loop_summary(loop_result: ApprovalLoopResult) -> str:
    """Format approval loop result as human-readable summary."""
    status = "✅ PUBLISHED" if loop_result.approved else "📝 SAVED AS DRAFT"
    lines = [
        f"Approval Loop Result: {status}",
        f"Iterations: {loop_result.iterations}",
        "",
    ]

    for i, panel in enumerate(loop_result.panel_history, 1):
        lines.append(f"Iteration {i}:")
        lines.append(f"  Votes: {panel.approve_count}/{len(panel.votes)} approved")
        for vote in panel.votes:
            emoji = "✅" if vote.verdict == "approve" else "⚠️"
            lines.append(f"    {emoji} {vote.agent_name}: {vote.verdict}")

    if loop_result.final_issues:
        lines.append("")
        lines.append("Final Issues (for human review):")
        for issue in loop_result.final_issues:
            lines.append(f"  - {issue}")

    return "\n".join(lines)
