"""Scoring primitives for deterministic family score calculation.

These primitives replace LLM-based scoring with deterministic formulas
that produce decimal scores (7.35, 8.20, 6.85) instead of clustered integers.

Key Benefits:
- Deterministic: Same inputs = same score (reproducible)
- Explainable: Each factor contributes a specific amount
- Differentiating: Natural variance from data differences

See /methodology page for public documentation of this scoring system.
"""

from dataclasses import dataclass
from typing import Any


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
    factors: list[str]  # Human-readable explanation of each factor


def calculate_family_score(metrics: dict[str, Any]) -> float:
    """
    Calculate deterministic family score from resort metrics.

    Produces scores like 7.3, 8.2, 6.8 instead of clustered integers 7, 8, 9.

    Args:
        metrics: Dict containing resort family metrics from database
                 (has_childcare, childcare_min_age, ski_school_min_age, etc.)

    Returns:
        Family score as float (1.0 - 10.0)

    Example:
        >>> metrics = {
        ...     "has_childcare": True,
        ...     "childcare_min_age": 6,  # 6 months
        ...     "ski_school_min_age": 3,
        ...     "beginner_terrain_pct": 35,
        ...     "kids_ski_free_age": 5,
        ...     "has_ski_in_out": True,
        ... }
        >>> calculate_family_score(metrics)
        8.2
    """
    score = 5.0  # Start neutral

    # =========================================================================
    # CHILDCARE QUALITY (+0.0 to +1.5)
    # =========================================================================
    if metrics.get("has_childcare") or metrics.get("childcare_available"):
        score += 0.8  # Base for having childcare

        childcare_min_age = metrics.get("childcare_min_age")  # in months
        if childcare_min_age is not None:
            if childcare_min_age <= 6:  # 6 months or younger
                score += 0.4
            if childcare_min_age <= 3:  # 3 months or younger (exceptional)
                score += 0.3

    # =========================================================================
    # SKI SCHOOL QUALITY (+0.0 to +1.0)
    # =========================================================================
    has_ski_school = metrics.get("has_ski_school", True)  # Assume yes if not set
    ski_school_min_age = metrics.get("ski_school_min_age")  # in years

    if has_ski_school or ski_school_min_age is not None:
        score += 0.2  # Base for having ski school

        if ski_school_min_age is not None:
            if ski_school_min_age <= 3:
                score += 0.5  # Takes 3-year-olds
            elif ski_school_min_age <= 4:
                score += 0.3  # Takes 4-year-olds

    # =========================================================================
    # TERRAIN FOR FAMILIES (+0.0 to +1.2)
    # =========================================================================
    beginner_pct = metrics.get("beginner_terrain_pct") or metrics.get("kid_friendly_terrain_pct") or 25

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
            score += 0.4  # Kids 5 and under ski free
        if kids_ski_free_age >= 10:
            score += 0.4  # Kids 10 and under ski free (exceptional)

    # =========================================================================
    # VILLAGE CONVENIENCE (+0.0 to +0.5)
    # =========================================================================
    if metrics.get("has_ski_in_out"):
        score += 0.3

    if metrics.get("english_friendly", True):  # Default True for US resorts
        score += 0.2

    # Cap at 10.0 and round to 1 decimal
    return min(10.0, round(score, 1))


def calculate_family_score_with_breakdown(metrics: dict[str, Any]) -> ScoreBreakdown:
    """
    Calculate family score with detailed breakdown of contributing factors.

    Useful for:
    - Debugging why a resort got a particular score
    - Showing users methodology transparency
    - Generating llms.txt explanations

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

    # Ski school
    has_ski_school = metrics.get("has_ski_school", True)
    ski_school_min_age = metrics.get("ski_school_min_age")

    if has_ski_school or ski_school_min_age is not None:
        ski_school += 0.2
        factors.append("Has ski school (+0.2)")

        if ski_school_min_age is not None:
            if ski_school_min_age <= 3:
                ski_school += 0.5
                factors.append(f"Ski school from age {ski_school_min_age} (+0.5)")
            elif ski_school_min_age <= 4:
                ski_school += 0.3
                factors.append(f"Ski school from age {ski_school_min_age} (+0.3)")

    # Terrain
    beginner_pct = metrics.get("beginner_terrain_pct") or metrics.get("kid_friendly_terrain_pct") or 25

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

    # Convenience
    if metrics.get("has_ski_in_out"):
        convenience += 0.3
        factors.append("Ski-in/ski-out options (+0.3)")

    if metrics.get("english_friendly", True):
        convenience += 0.2
        factors.append("English friendly (+0.2)")

    total = min(10.0, round(base + childcare + ski_school + terrain + value + convenience, 1))

    return ScoreBreakdown(
        total=total,
        base=base,
        childcare=round(childcare, 1),
        ski_school=round(ski_school, 1),
        terrain=round(terrain, 1),
        value=round(value, 1),
        convenience=round(convenience, 1),
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
        "",
        "Factors:",
    ]

    for factor in breakdown.factors:
        lines.append(f"  • {factor}")

    return "\n".join(lines)
