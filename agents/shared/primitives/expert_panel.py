"""Generalized Expert Review Panel - Content-agnostic quality evaluation.

This module implements a content-agnostic expert panel that can review any
content type (guides, resorts, newsletters) using configurable expert roles.

Design Principles (Agent-Native):
- GRANULARITY: Experts defined as data (prompts), not code
- COMPOSABILITY: Mix and match experts per content type
- PARITY: Same review quality for all content types
- IMPROVEMENT OVER TIME: Panel results feed back into generation prompts

The existing approval.py handles resort-specific evaluation. This module
generalizes the pattern for any content type while reusing the same
infrastructure (voice profiles, forbidden patterns, Claude API).

Usage:
    # Define experts for a content type
    experts = get_experts_for_content_type("guide")

    # Run panel
    result = await run_expert_panel(content, experts, voice_profile="snowthere_guide")

    # Use result
    if result.approved:
        publish(content)
    else:
        improved = await improve_from_panel(content, result)
"""

import asyncio
import json
import logging
from dataclasses import dataclass, field
from typing import Any, Literal

import anthropic

from ..config import settings
from ..supabase_client import get_supabase_client
from ..voice_profiles import get_voice_profile
from .approval import (
    FORBIDDEN_PATTERNS,
    EvaluationResult,
    PanelResult,
    _call_claude,
    _parse_json_response,
    apply_voice_post_processing,
)


# =============================================================================
# Expert Role Definitions (Data, Not Code)
# =============================================================================


@dataclass
class ExpertRole:
    """An expert perspective for content evaluation.

    Experts are defined as data: a name, a perspective, and evaluation
    criteria expressed as prompts. Adding a new expert means adding a new
    ExpertRole instance, not writing new evaluation code.
    """

    name: str
    system_prompt: str
    evaluation_criteria: list[str]
    content_focus: str  # What aspect of content this expert cares about
    advisory_only: bool = False  # If True, feedback included but vote doesn't count


# --- Expert Definitions ---

ACCURACY_EXPERT = ExpertRole(
    name="AccuracyExpert",
    system_prompt=(
        "You are a meticulous fact-checker for family travel content. "
        "Your job is to catch inaccuracies, outdated information, and "
        "unsupported claims before they mislead families making expensive "
        "trip decisions."
    ),
    evaluation_criteria=[
        "Are dates, prices, and distances factually correct?",
        "Are claims about resort features supported by common knowledge or stated sources?",
        "Are there any time-sensitive claims that could become outdated quickly?",
        "Do numbers add up (percentages, distances, costs)?",
        "Are resort names and geographic details accurate?",
    ],
    content_focus="factual accuracy and verifiability",
)

FAMILY_USEFULNESS_EXPERT = ExpertRole(
    name="FamilyUsefulnessExpert",
    system_prompt=(
        "You evaluate content from the perspective of a parent planning "
        "a family ski trip. You care about actionability: can a family "
        "actually use this information to make decisions? Vague advice "
        "is worse than no advice."
    ),
    evaluation_criteria=[
        "Are there specific, actionable recommendations (not vague generalities)?",
        "Does this help a family DECIDE or DO something concrete?",
        "Are age-specific considerations addressed where relevant?",
        "Are costs and logistics practical (not aspirational)?",
        "Would a busy parent scanning this get what they need in 2 minutes?",
    ],
    content_focus="actionability and practical value for families",
)

VOICE_EXPERT = ExpertRole(
    name="VoiceExpert",
    system_prompt=(
        "You are the editorial voice guardian for Snowthere. Content should "
        "sound like a smart, well-traveled friend who respects the reader's "
        "time. Not a brochure, not a blog post, not a sales pitch."
    ),
    evaluation_criteria=[
        "Does the content match the target voice profile?",
        "Are there any banned patterns (em-dashes, performative openers, LLM markers)?",
        "Is the tone consistent throughout (no shifts from casual to formal)?",
        "Does it avoid talking down to the reader?",
        "Is it scannable (short paragraphs, clear headers, bullets where useful)?",
    ],
    content_focus="brand voice alignment and readability",
)

SEO_GEO_EXPERT = ExpertRole(
    name="SEOGEOExpert",
    system_prompt=(
        "You evaluate content for both traditional SEO and GEO (Generative "
        "Engine Optimization). Content must be structured for AI citation: "
        "tables, FAQ schema, specific numbers, and BLUF format."
    ),
    evaluation_criteria=[
        "Are there table-structured data elements AI can cite?",
        "Do FAQ items use natural question phrasing?",
        "Are specific numbers included (prices, distances, ages) vs vague descriptions?",
        "Is the content structured with clear headings for scraping?",
        "Is the meta description between 150-160 characters?",
    ],
    content_focus="search engine and AI discoverability",
)

SKEPTIC_EXPERT = ExpertRole(
    name="SkepticExpert",
    system_prompt=(
        "You are the devil's advocate. You look for what's missing, what "
        "could go wrong, and what a critical reader would question. Your job "
        "is to find the gaps everyone else overlooked."
    ),
    evaluation_criteria=[
        "What important information is missing that a family would need?",
        "What assumptions does this content make that might not hold?",
        "Are there risks or downsides not mentioned?",
        "Would a skeptical reader trust this content? Why or why not?",
        "Is there anything that feels like filler rather than substance?",
    ],
    content_focus="completeness gaps and unstated assumptions",
    advisory_only=True,  # Feedback informs improvement but doesn't block publication
)

BUSY_PARENT_EXPERT = ExpertRole(
    name="BusyParentExpert",
    system_prompt=(
        "You are a parent with 10 minutes to plan a family ski trip. You're "
        "reading this on your phone while your kid eats breakfast. You need "
        "the important stuff fast, and you need to trust it."
    ),
    evaluation_criteria=[
        "Can you get the key takeaway in the first 30 seconds of reading?",
        "Is the most important info at the top (BLUF)?",
        "Are there clear next steps or calls to action?",
        "Does anything feel like padding or wasted time?",
        "Would you share this with another parent?",
    ],
    content_focus="reader experience and time-to-value",
)


# =============================================================================
# Expert Registry (Content Type → Expert Roles)
# =============================================================================

# Maps content types to which experts should review them.
# Adding a new content type = adding a new entry here. No code changes.
EXPERT_PANELS: dict[str, list[ExpertRole]] = {
    "guide": [
        ACCURACY_EXPERT,
        FAMILY_USEFULNESS_EXPERT,
        VOICE_EXPERT,
        SEO_GEO_EXPERT,
        SKEPTIC_EXPERT,
    ],
    "resort": [
        ACCURACY_EXPERT,
        FAMILY_USEFULNESS_EXPERT,
        VOICE_EXPERT,
        SEO_GEO_EXPERT,
    ],
    "newsletter": [
        VOICE_EXPERT,
        FAMILY_USEFULNESS_EXPERT,
        BUSY_PARENT_EXPERT,
    ],
    "guide_seed": [
        ACCURACY_EXPERT,
        VOICE_EXPERT,
        SEO_GEO_EXPERT,
        SKEPTIC_EXPERT,
        BUSY_PARENT_EXPERT,
    ],
}


def get_experts_for_content_type(content_type: str) -> list[ExpertRole]:
    """Get the expert panel for a content type.

    Returns default panel (all experts) if content type not registered.
    """
    return EXPERT_PANELS.get(
        content_type,
        [ACCURACY_EXPERT, FAMILY_USEFULNESS_EXPERT, VOICE_EXPERT],
    )


# =============================================================================
# Evaluation Engine (Generic, Prompt-Driven)
# =============================================================================


def _format_content_for_review(content: Any) -> str:
    """Format any content structure for expert review.

    Handles dicts, lists, strings, and nested JSONB structures.
    """
    if isinstance(content, str):
        return content[:5000]

    if isinstance(content, list):
        lines = []
        for i, item in enumerate(content[:20]):
            if isinstance(item, dict):
                lines.append(f"\n--- Item {i + 1} ---")
                for k, v in item.items():
                    val_str = str(v)[:500]
                    lines.append(f"  {k}: {val_str}")
            else:
                lines.append(f"  - {str(item)[:500]}")
        return "\n".join(lines)

    if isinstance(content, dict):
        lines = []
        for key, value in content.items():
            if isinstance(value, str):
                display = value[:2000] + "..." if len(value) > 2000 else value
                lines.append(f"\n## {key.upper()}\n{display}")
            elif isinstance(value, list):
                lines.append(f"\n## {key.upper()}")
                for item in value[:10]:
                    if isinstance(item, dict):
                        lines.append(f"  - {json.dumps(item, default=str)[:300]}")
                    else:
                        lines.append(f"  - {item}")
            elif isinstance(value, dict):
                lines.append(f"\n## {key.upper()}")
                for k, v in value.items():
                    lines.append(f"  {k}: {str(v)[:300]}")
            else:
                lines.append(f"{key}: {value}")
        return "\n".join(lines)

    return str(content)[:5000]


async def evaluate_with_expert(
    expert: ExpertRole,
    content: Any,
    voice_profile_name: str | None = None,
    context: str = "",
) -> EvaluationResult:
    """Run a single expert evaluation on content.

    This is the atomic primitive. One expert, one piece of content, one verdict.

    Args:
        expert: The expert role to use
        content: Content to evaluate (any structure)
        voice_profile_name: Optional voice profile for voice-aware experts
        context: Additional context (e.g., "This is a guide about Olympics skiing")

    Returns:
        EvaluationResult with verdict, issues, and suggestions
    """
    # Build voice context if relevant
    voice_context = ""
    if voice_profile_name and "voice" in expert.name.lower():
        profile = get_voice_profile(voice_profile_name)
        voice_context = f"""
TARGET VOICE: {profile.name}
{profile.description}

TONE: {', '.join(profile.tone)}

AVOID: {', '.join(profile.avoid)}

INCLUDE: {', '.join(profile.include)}
"""

    criteria_text = "\n".join(
        f"{i + 1}. {c}" for i, c in enumerate(expert.evaluation_criteria)
    )

    formatted_content = _format_content_for_review(content)

    prompt = f"""You are {expert.name}.
{voice_context}
{f"CONTEXT: {context}" if context else ""}

CONTENT TO EVALUATE:
{formatted_content}

Evaluate this content for {expert.content_focus}:
{criteria_text}

For each criterion, note if it passes or fails with a brief explanation.

Output JSON:
{{
    "verdict": "approve" | "improve" | "reject",
    "confidence": 0.0-1.0,
    "issues": ["specific issue found"],
    "suggestions": ["specific fix"],
    "reasoning": "2-3 sentence summary"
}}

Standards: "approve" means ready to publish. "improve" means good but needs fixes.
"reject" means fundamentally flawed."""

    response = _call_claude(prompt, system=expert.system_prompt)

    try:
        parsed = _parse_json_response(response)
        return EvaluationResult(
            agent_name=expert.name,
            verdict=parsed.get("verdict", "improve"),
            confidence=float(parsed.get("confidence", 0.5)),
            issues=parsed.get("issues", []),
            suggestions=parsed.get("suggestions", []),
            reasoning=parsed.get("reasoning", "Evaluation completed"),
        )
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        return EvaluationResult(
            agent_name=expert.name,
            verdict="improve",
            confidence=0.3,
            issues=[f"Failed to parse {expert.name} response: {e}"],
            suggestions=["Re-run evaluation"],
            reasoning="Evaluation parsing failed",
        )


# =============================================================================
# Panel Orchestration
# =============================================================================


async def run_expert_panel(
    content: Any,
    experts: list[ExpertRole] | None = None,
    content_type: str = "guide",
    voice_profile: str = "snowthere_guide",
    context: str = "",
) -> PanelResult:
    """Run a panel of experts in parallel and aggregate results.

    Args:
        content: Content to evaluate
        experts: List of expert roles (defaults to content_type's panel)
        content_type: Type of content for default expert selection
        voice_profile: Voice profile name for voice-aware experts
        context: Additional context for evaluation

    Returns:
        PanelResult with aggregated votes and combined feedback
    """
    if experts is None:
        experts = get_experts_for_content_type(content_type)

    # Run all evaluations in parallel
    results = await asyncio.gather(
        *[
            evaluate_with_expert(expert, content, voice_profile, context)
            for expert in experts
        ],
        return_exceptions=True,
    )

    # Handle exceptions
    votes: list[EvaluationResult] = []
    for i, result in enumerate(results):
        if isinstance(result, Exception):
            votes.append(
                EvaluationResult(
                    agent_name=experts[i].name,
                    verdict="improve",
                    confidence=0.0,
                    issues=[f"Evaluation failed: {result}"],
                    suggestions=["Re-run panel"],
                    reasoning="Exception during evaluation",
                )
            )
        else:
            votes.append(result)

    # Aggregate — exclude advisory_only experts from vote count
    advisory_names = {e.name for e in experts if e.advisory_only}
    voting = [v for v in votes if v.agent_name not in advisory_names]

    approve_count = sum(1 for v in voting if v.verdict == "approve")
    improve_count = sum(1 for v in voting if v.verdict == "improve")
    reject_count = sum(1 for v in voting if v.verdict == "reject")

    # Majority approval: more approves than non-approves (among voting experts)
    total = len(voting)
    approved = approve_count > total / 2 if total > 0 else False

    # Combine issues and suggestions
    all_issues = []
    all_suggestions = []
    for v in votes:
        all_issues.extend(v.issues)
        all_suggestions.extend(v.suggestions)

    return PanelResult(
        votes=votes,
        approved=approved,
        approve_count=approve_count,
        improve_count=improve_count,
        reject_count=reject_count,
        combined_issues=all_issues,
        combined_suggestions=all_suggestions,
    )


# =============================================================================
# Review + Improve Loop
# =============================================================================


@dataclass
class ExpertPanelResult:
    """Full result of expert panel review with optional improvement."""

    content: Any
    panel_result: PanelResult
    improved: bool
    improvement_summary: str | None = None
    iterations: int = 1


async def review_and_summarize(
    content: Any,
    content_type: str = "guide",
    voice_profile: str = "snowthere_guide",
    context: str = "",
) -> ExpertPanelResult:
    """Run expert panel and return structured review.

    This is the primary entry point for autonomous review. It runs the
    panel, aggregates findings, and returns a structured result that
    can be logged, displayed, or used to trigger improvement.

    Args:
        content: Content to evaluate
        content_type: Type for expert selection
        voice_profile: Voice profile name
        context: Additional context

    Returns:
        ExpertPanelResult with panel findings and summary
    """
    panel = await run_expert_panel(
        content=content,
        content_type=content_type,
        voice_profile=voice_profile,
        context=context,
    )

    # Build summary
    summary_parts = []
    for vote in panel.votes:
        emoji = {"approve": "OK", "improve": "FIX", "reject": "NO"}[vote.verdict]
        summary_parts.append(
            f"  [{emoji}] {vote.agent_name} ({vote.confidence:.0%}): {vote.reasoning}"
        )

    verdict = "APPROVED" if panel.approved else "NEEDS IMPROVEMENT"
    total_voting = panel.approve_count + panel.improve_count + panel.reject_count
    summary = (
        f"Panel verdict: {verdict} "
        f"({panel.approve_count}/{total_voting} voting approved)\n"
        + "\n".join(summary_parts)
    )

    if panel.combined_issues:
        summary += "\n\nIssues found:\n" + "\n".join(
            f"  - {issue}" for issue in panel.combined_issues
        )

    return ExpertPanelResult(
        content=content,
        panel_result=panel,
        improved=False,
        improvement_summary=summary,
    )


# =============================================================================
# Deterministic Voice Cleanup (Reuse from approval.py)
# =============================================================================


def apply_voice_cleanup(content: Any) -> Any:
    """Apply deterministic voice cleanup to content.

    Works on strings, dicts, and nested structures. Reuses the
    FORBIDDEN_PATTERNS from approval.py for consistency.
    """
    if isinstance(content, str):
        return _cleanup_text(content)
    elif isinstance(content, dict):
        return apply_voice_post_processing(content)
    elif isinstance(content, list):
        return [apply_voice_cleanup(item) for item in content]
    return content


def _cleanup_text(text: str) -> str:
    """Clean a single string of voice violations."""
    import re

    for pattern, replacement in FORBIDDEN_PATTERNS:
        text = re.sub(re.escape(pattern), replacement, text, flags=re.IGNORECASE)

    # Clean artifacts
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"\s+([.,!?])", r"\1", text)
    text = text.strip()
    return text


# =============================================================================
# Approval Loop (Mirrors approval.py's approval_loop for any content type)
# =============================================================================


@dataclass
class ExpertApprovalLoopResult:
    """Result of the expert panel approval iteration loop."""

    final_content: Any
    approved: bool
    iterations: int
    panel_history: list[PanelResult] = field(default_factory=list)
    final_issues: list[str] = field(default_factory=list)
    low_confidence: bool = False  # True if published despite not reaching full approval


async def improve_content_from_panel(
    content: Any,
    issues: list[str],
    suggestions: list[str],
    content_type: str = "guide",
    voice_profile: str = "snowthere_guide",
) -> Any:
    """Improve content based on expert panel feedback.

    Works on both dict and string content. Uses Claude to revise
    content addressing specific issues while maintaining voice.

    Args:
        content: Content to improve (dict or string)
        issues: Issues identified by the panel
        suggestions: Suggested improvements
        content_type: Type of content being improved
        voice_profile: Target voice profile

    Returns:
        Improved content (same type as input)
    """
    profile = get_voice_profile(voice_profile)
    formatted = _format_content_for_review(content)

    issues_str = "\n".join(f"- {issue}" for issue in issues) if issues else "None"
    suggestions_str = (
        "\n".join(f"- {s}" for s in suggestions) if suggestions else "None"
    )

    prompt = f"""Improve this {content_type} content based on expert panel feedback.

CURRENT CONTENT:
{formatted}

ISSUES TO FIX:
{issues_str}

SUGGESTIONS:
{suggestions_str}

TARGET VOICE: {profile.name}
{profile.description}

Instructions:
1. Address each issue specifically
2. Incorporate suggestions where possible
3. Maintain the target voice profile
4. Keep all accurate information
5. Be surgical: fix issues without rewriting content that's already good

Return the improved content as JSON with the same structure as the input.
Only include sections that exist in the input."""

    system = f"""You are an expert editor improving {content_type} content.
Fix specific issues while maintaining quality and voice.
Voice: {profile.name} - {', '.join(profile.tone[:3])}
Avoid: {', '.join(profile.avoid[:3])}"""

    response = _call_claude(prompt, system=system)

    try:
        improved = _parse_json_response(response)
        if isinstance(content, dict):
            # Preserve keys not in response
            for key, value in content.items():
                if key not in improved:
                    improved[key] = value
            return apply_voice_cleanup(improved)
        return apply_voice_cleanup(improved)
    except (json.JSONDecodeError, ValueError):
        # Return original with voice cleanup if parsing fails
        return apply_voice_cleanup(content)


async def expert_approval_loop(
    content: Any,
    content_type: str = "guide",
    voice_profile: str = "snowthere_guide",
    context: str = "",
    max_iterations: int = 3,
) -> ExpertApprovalLoopResult:
    """Run the full expert panel approval iteration loop.

    Mirrors approval.py's approval_loop but works for any content type
    using configurable expert panels instead of hardcoded reviewers.

    Flow:
    1. Run expert panel (5 experts for guides, 3 for newsletters)
    2. If approved (majority), return success
    3. If not approved, improve content from feedback
    4. Repeat until approved or max iterations

    Args:
        content: Content to evaluate and improve
        content_type: Type for expert panel selection
        voice_profile: Target voice profile
        context: Additional context for evaluation
        max_iterations: Maximum improvement iterations (default 3)

    Returns:
        ExpertApprovalLoopResult with final content and approval status
    """
    current_content = content
    panel_history: list[PanelResult] = []

    for iteration in range(1, max_iterations + 1):
        # Run the expert panel
        panel_result = await run_expert_panel(
            content=current_content,
            content_type=content_type,
            voice_profile=voice_profile,
            context=context,
        )
        panel_history.append(panel_result)

        if panel_result.approved:
            # Apply voice cleanup as final pass
            final = apply_voice_cleanup(current_content)
            return ExpertApprovalLoopResult(
                final_content=final,
                approved=True,
                iterations=iteration,
                panel_history=panel_history,
                final_issues=[],
            )

        # Not approved - check if we should iterate
        if iteration < max_iterations:
            current_content = await improve_content_from_panel(
                current_content,
                panel_result.combined_issues,
                panel_result.combined_suggestions,
                content_type=content_type,
                voice_profile=voice_profile,
            )
        else:
            # Max iterations reached — check for low-confidence publish
            # If at least half the voting experts approved, publish with low_confidence flag
            final = apply_voice_cleanup(current_content)
            total_voting = panel_result.approve_count + panel_result.improve_count + panel_result.reject_count
            near_majority = total_voting > 0 and panel_result.approve_count >= total_voting / 2
            if near_majority and panel_result.approve_count >= 2:
                logger.info(
                    f"[expert_panel] Low-confidence publish: {panel_result.approve_count} approvals "
                    f"after {iteration} iterations"
                )
                return ExpertApprovalLoopResult(
                    final_content=final,
                    approved=True,
                    low_confidence=True,
                    iterations=iteration,
                    panel_history=panel_history,
                    final_issues=panel_result.combined_issues,
                )
            return ExpertApprovalLoopResult(
                final_content=final,
                approved=False,
                iterations=iteration,
                panel_history=panel_history,
                final_issues=panel_result.combined_issues,
            )

    # Edge case fallback
    return ExpertApprovalLoopResult(
        final_content=apply_voice_cleanup(current_content),
        approved=False,
        iterations=max_iterations,
        panel_history=panel_history,
        final_issues=["Max iterations reached without approval"],
    )


def log_panel_result(
    content_type: str,
    content_id: str,
    result: ExpertApprovalLoopResult,
) -> None:
    """Log expert panel result to agent_audit_log for unified quality tracking.

    Args:
        content_type: Type of content reviewed (guide, newsletter, resort)
        content_id: ID of the content item
        result: The approval loop result
    """
    try:
        supabase = get_supabase_client()

        # Build summary from panel history
        summaries = []
        for i, panel in enumerate(result.panel_history):
            votes = ", ".join(
                f"{v.agent_name}:{v.verdict}" for v in panel.votes
            )
            summaries.append(f"Iteration {i+1}: {votes}")

        supabase.table("agent_audit_log").insert({
            "task_id": content_id,
            "action": f"expert_panel_{content_type}",
            "reasoning": (
                f"Expert panel review: {'APPROVED' if result.approved else 'NOT APPROVED'} "
                f"after {result.iterations} iteration(s). "
                + "; ".join(summaries)
            ),
            "metadata": {
                "content_type": content_type,
                "approved": result.approved,
                "iterations": result.iterations,
                "final_issues": result.final_issues,
            },
        }).execute()
    except Exception as e:
        logging.getLogger(__name__).warning(f"Failed to log panel result: {e}")
