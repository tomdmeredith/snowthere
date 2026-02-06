"""Scoring primitives for family score calculation.

Three-layer hybrid scoring system (Round 20):
  structural_score (30%) + content_score (50%) + review_score (20%)
  If no reviews: structural (35%) + content (65%)

Structural score is deterministic from resort metrics.
Content score and review score come from LLM assessment (intelligence.py).

See /methodology page for public documentation of this scoring system.
"""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


# Fields used to measure data completeness — these are the key family metrics
# that should be populated for a resort to be considered "well-researched."
KEY_COMPLETENESS_FIELDS = [
    "has_childcare", "childcare_min_age", "ski_school_min_age",
    "kid_friendly_terrain_pct", "has_magic_carpet", "has_terrain_park_kids",
    "kids_ski_free_age", "best_age_min", "best_age_max",
]


@dataclass
class ScoreBreakdown:
    """Detailed breakdown of how a family score was calculated."""

    total: float
    base: float
    childcare: float
    ski_school: float
    terrain: float
    value: float
    convenience: float
    completeness: float  # 0.0-1.0 data completeness ratio
    completeness_multiplier: float  # Applied multiplier (0.7-1.0)
    factors: list[str]  # Human-readable explanation of each factor


def calculate_data_completeness(metrics: dict[str, Any]) -> float:
    """
    Calculate data completeness ratio for family metrics.

    Returns the fraction of KEY_COMPLETENESS_FIELDS that have non-None values.
    This is a pure, atomic primitive — no side effects, no business logic.

    Args:
        metrics: Dict containing resort family metrics

    Returns:
        Float between 0.0 (no data) and 1.0 (fully populated)
    """
    fields_present = sum(
        1 for f in KEY_COMPLETENESS_FIELDS if metrics.get(f) is not None
    )
    return fields_present / len(KEY_COMPLETENESS_FIELDS)


def calculate_structural_score(metrics: dict[str, Any]) -> float:
    """
    Calculate deterministic structural score from resort metrics.

    This is one layer of the three-layer hybrid scoring system.
    Missing data = no bonus, but no penalty either (no completeness multiplier).

    Args:
        metrics: Dict containing resort family metrics from database

    Returns:
        Structural score as float (1.0 - 10.0)
    """
    score = 5.0  # Start neutral

    # =========================================================================
    # CHILDCARE QUALITY (+0.0 to +1.5)
    # =========================================================================
    if metrics.get("has_childcare") or metrics.get("childcare_available"):
        score += 0.8

        childcare_min_age = metrics.get("childcare_min_age")
        if childcare_min_age is not None:
            if childcare_min_age <= 6:
                score += 0.4
            if childcare_min_age <= 3:
                score += 0.3

    # =========================================================================
    # SKI SCHOOL QUALITY (+0.0 to +1.0)
    # =========================================================================
    has_ski_school = metrics.get("has_ski_school")
    ski_school_min_age = metrics.get("ski_school_min_age")

    if has_ski_school is True or ski_school_min_age is not None:
        score += 0.2

        if ski_school_min_age is not None:
            if ski_school_min_age <= 3:
                score += 0.5
            elif ski_school_min_age <= 4:
                score += 0.3

    # =========================================================================
    # TERRAIN FOR FAMILIES (+0.0 to +1.2)
    # =========================================================================
    beginner_pct = metrics.get("beginner_terrain_pct") or metrics.get("kid_friendly_terrain_pct")
    if beginner_pct is not None:
        if beginner_pct >= 30:
            score += 0.3
        if beginner_pct >= 40:
            score += 0.3

    if metrics.get("has_magic_carpet"):
        score += 0.3

    if metrics.get("has_terrain_park_kids"):
        score += 0.3

    # =========================================================================
    # VALUE FACTORS (+0.0 to +0.8)
    # =========================================================================
    kids_ski_free_age = metrics.get("kids_ski_free_age")
    if kids_ski_free_age is not None:
        if kids_ski_free_age >= 5:
            score += 0.4
        if kids_ski_free_age >= 10:
            score += 0.4

    # =========================================================================
    # VILLAGE CONVENIENCE (+0.0 to +0.5)
    # =========================================================================
    if metrics.get("has_ski_in_out"):
        score += 0.3

    if metrics.get("english_friendly") is True:
        score += 0.2

    # Cap at 10.0 and round to 1 decimal (no completeness multiplier)
    return min(10.0, round(score, 1))


# Backwards-compatible alias
calculate_family_score = calculate_structural_score


def calculate_family_score_with_breakdown(metrics: dict[str, Any]) -> ScoreBreakdown:
    """
    Calculate family score with detailed breakdown of contributing factors.

    Useful for:
    - Debugging why a resort got a particular score
    - Showing users methodology transparency
    - Generating llms.txt explanations
    - Data quality audits (see completeness ratio)

    Args:
        metrics: Dict containing resort family metrics from database

    Returns:
        ScoreBreakdown with total score and component breakdown
    """
    base = 5.0
    childcare = 0.0
    ski_school = 0.0
    terrain = 0.0
    value = 0.0
    convenience = 0.0
    factors: list[str] = []

    # Childcare
    if metrics.get("has_childcare") or metrics.get("childcare_available"):
        childcare += 0.8
        factors.append("Has childcare (+0.8)")

        childcare_min_age = metrics.get("childcare_min_age")
        if childcare_min_age is not None:
            if childcare_min_age <= 6:
                childcare += 0.4
                factors.append(f"Childcare from {childcare_min_age}mo (+0.4)")
            if childcare_min_age <= 3:
                childcare += 0.3
                factors.append("Infant care available (+0.3)")

    # Ski school — NULL = unknown = no points
    has_ski_school = metrics.get("has_ski_school")
    ski_school_min_age = metrics.get("ski_school_min_age")

    if has_ski_school is True or ski_school_min_age is not None:
        ski_school += 0.2
        factors.append("Has ski school (+0.2)")

        if ski_school_min_age is not None:
            if ski_school_min_age <= 3:
                ski_school += 0.5
                factors.append(f"Ski school from age {ski_school_min_age} (+0.5)")
            elif ski_school_min_age <= 4:
                ski_school += 0.3
                factors.append(f"Ski school from age {ski_school_min_age} (+0.3)")

    # Terrain — only score if we have actual data
    beginner_pct = metrics.get("beginner_terrain_pct") or metrics.get("kid_friendly_terrain_pct")

    if beginner_pct is not None:
        if beginner_pct >= 30:
            terrain += 0.3
            factors.append(f"{beginner_pct}% beginner terrain (+0.3)")
        if beginner_pct >= 40:
            terrain += 0.3
            factors.append("40%+ beginner terrain (+0.3)")

    if metrics.get("has_magic_carpet"):
        terrain += 0.3
        factors.append("Magic carpet (+0.3)")

    if metrics.get("has_terrain_park_kids"):
        terrain += 0.3
        factors.append("Kids terrain park (+0.3)")

    # Value
    kids_ski_free_age = metrics.get("kids_ski_free_age")

    if kids_ski_free_age is not None:
        if kids_ski_free_age >= 5:
            value += 0.4
            factors.append(f"Kids {kids_ski_free_age}& under ski free (+0.4)")
        if kids_ski_free_age >= 10:
            value += 0.4
            factors.append("Exceptional kids-free-age policy (+0.4)")

    # Convenience — NULL english_friendly = unknown = no points
    if metrics.get("has_ski_in_out"):
        convenience += 0.3
        factors.append("Ski-in/ski-out options (+0.3)")

    if metrics.get("english_friendly") is True:
        convenience += 0.2
        factors.append("English friendly (+0.2)")

    completeness = calculate_data_completeness(metrics)

    raw_score = base + childcare + ski_school + terrain + value + convenience
    total = min(10.0, round(raw_score, 1))

    factors.append(f"Data completeness: {completeness:.0%}")

    return ScoreBreakdown(
        total=total,
        base=base,
        childcare=round(childcare, 1),
        ski_school=round(ski_school, 1),
        terrain=round(terrain, 1),
        value=round(value, 1),
        convenience=round(convenience, 1),
        completeness=round(completeness, 2),
        completeness_multiplier=1.0,  # No longer applied
        factors=factors,
    )


def format_score_explanation(breakdown: ScoreBreakdown) -> str:
    """
    Format a score breakdown as human-readable text.

    Useful for llms.txt, methodology pages, etc.

    Args:
        breakdown: ScoreBreakdown from calculate_family_score_with_breakdown

    Returns:
        Multi-line string explaining the score
    """
    lines = [
        f"Family Score: {breakdown.total}/10",
        "",
        "Breakdown:",
        f"  Base score: {breakdown.base}",
        f"  Childcare: +{breakdown.childcare}",
        f"  Ski school: +{breakdown.ski_school}",
        f"  Terrain: +{breakdown.terrain}",
        f"  Value: +{breakdown.value}",
        f"  Convenience: +{breakdown.convenience}",
        f"  Data completeness: {breakdown.completeness:.0%} (×{breakdown.completeness_multiplier:.2f})",
        "",
        "Factors:",
    ]

    for factor in breakdown.factors:
        lines.append(f"  • {factor}")

    return "\n".join(lines)


# =============================================================================
# COMPOSITE SCORING (Three-Layer Hybrid)
# =============================================================================


@dataclass
class CompositeScore:
    """Result of the three-layer hybrid scoring system."""

    family_score: float  # Final composite score (1.0-10.0)
    structural_score: float
    content_score: float | None  # From LLM assessment
    review_score: float | None  # From LLM review sentiment
    confidence: str  # "high", "medium", "low"
    reasoning: str
    dimensions: dict[str, float] = field(default_factory=dict)
    scored_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))


def calculate_composite_family_score(
    structural: float,
    content: float | None = None,
    review: float | None = None,
    content_dimensions: dict[str, float] | None = None,
    content_reasoning: str = "",
) -> CompositeScore:
    """
    Calculate composite family score from three layers.

    Weights:
      - With reviews: structural (30%) + content (50%) + review (20%)
      - Without reviews: structural (35%) + content (65%)
      - Without content assessment: structural score only (low confidence)

    Args:
        structural: Deterministic score from metrics (1.0-10.0)
        content: LLM-assessed content score (1.0-10.0) or None
        review: LLM-assessed review sentiment score (1.0-10.0) or None
        content_dimensions: Per-dimension scores from content assessment
        content_reasoning: LLM reasoning for content score

    Returns:
        CompositeScore with all components and confidence level
    """
    reasoning_parts = [f"Structural: {structural:.1f}"]

    if content is not None and review is not None:
        score = structural * 0.30 + content * 0.50 + review * 0.20
        confidence = "high"
        reasoning_parts.append(f"Content: {content:.1f}")
        reasoning_parts.append(f"Review: {review:.1f}")
        reasoning_parts.append("Weights: 30/50/20")
    elif content is not None:
        score = structural * 0.35 + content * 0.65
        confidence = "medium"
        reasoning_parts.append(f"Content: {content:.1f}")
        reasoning_parts.append("No reviews — weights: 35/65")
    else:
        score = structural
        confidence = "low"
        reasoning_parts.append("Structural only — limited data")

    if content_reasoning:
        reasoning_parts.append(content_reasoning)

    return CompositeScore(
        family_score=min(10.0, round(score, 1)),
        structural_score=structural,
        content_score=content,
        review_score=review,
        confidence=confidence,
        reasoning=" | ".join(reasoning_parts),
        dimensions=content_dimensions or {},
    )
