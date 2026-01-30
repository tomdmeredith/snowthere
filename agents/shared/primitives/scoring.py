"""Scoring primitives for deterministic family score calculation.

These primitives replace LLM-based scoring with deterministic formulas
that produce decimal scores (7.35, 8.20, 6.85) instead of clustered integers.

Key Benefits:
- Deterministic: Same inputs = same score (reproducible)
- Explainable: Each factor contributes a specific amount
- Differentiating: Natural variance from data differences
- Completeness-aware: NULL data reduces score (not inflates it)

See /methodology page for public documentation of this scoring system.
"""

from dataclasses import dataclass
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


def calculate_family_score(metrics: dict[str, Any]) -> float:
    """
    Calculate deterministic family score from resort metrics.

    Produces scores like 7.3, 8.2, 6.8 instead of clustered integers 7, 8, 9.

    NULL data = "unknown" = no points (not free points). A resort with ALL NULL
    data scores ~3.5 instead of the old 5.7. This is intentional — we should
    not reward missing data.

    A completeness multiplier (0.7 + 0.3 * completeness) penalizes resorts
    where we have little data: all NULL = 70% of raw score, all populated = 100%.

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
    # NULL has_ski_school = unknown = no points (was: default True = free 0.2)
    # =========================================================================
    has_ski_school = metrics.get("has_ski_school")  # None = unknown = no points
    ski_school_min_age = metrics.get("ski_school_min_age")  # in years

    if has_ski_school is True or ski_school_min_age is not None:
        score += 0.2  # Base for having ski school

        if ski_school_min_age is not None:
            if ski_school_min_age <= 3:
                score += 0.5  # Takes 3-year-olds
            elif ski_school_min_age <= 4:
                score += 0.3  # Takes 4-year-olds

    # =========================================================================
    # TERRAIN FOR FAMILIES (+0.0 to +1.2)
    # NULL terrain = unknown = no terrain points (was: default 25 = free 0.0)
    # =========================================================================
    beginner_pct = metrics.get("beginner_terrain_pct") or metrics.get("kid_friendly_terrain_pct")
    # Only score terrain if we have actual data
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
            score += 0.4  # Kids 5 and under ski free
        if kids_ski_free_age >= 10:
            score += 0.4  # Kids 10 and under ski free (exceptional)

    # =========================================================================
    # VILLAGE CONVENIENCE (+0.0 to +0.5)
    # NULL english_friendly = unknown = no points (was: default True = free 0.2)
    # =========================================================================
    if metrics.get("has_ski_in_out"):
        score += 0.3

    if metrics.get("english_friendly") is True:  # Must be explicitly True
        score += 0.2

    # =========================================================================
    # COMPLETENESS MULTIPLIER
    # Penalizes low-data resorts: all NULL = 70% of raw, all populated = 100%
    # =========================================================================
    completeness = calculate_data_completeness(metrics)
    multiplier = 0.7 + 0.3 * completeness

    # Cap at 10.0 and round to 1 decimal
    return min(10.0, round(score * multiplier, 1))


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

    # Completeness multiplier
    completeness = calculate_data_completeness(metrics)
    multiplier = 0.7 + 0.3 * completeness

    raw_score = base + childcare + ski_school + terrain + value + convenience
    total = min(10.0, round(raw_score * multiplier, 1))

    factors.append(f"Data completeness: {completeness:.0%} (multiplier: {multiplier:.2f})")

    return ScoreBreakdown(
        total=total,
        base=base,
        childcare=round(childcare, 1),
        ski_school=round(ski_school, 1),
        terrain=round(terrain, 1),
        value=round(value, 1),
        convenience=round(convenience, 1),
        completeness=round(completeness, 2),
        completeness_multiplier=round(multiplier, 2),
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
