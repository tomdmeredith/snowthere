"""Linking primitives for resort similarity and internal links.

These primitives enable:
- Similar resorts feature (content recommendations)
- Internal linking for SEO
- Cross-resort navigation

Similarity Algorithm Weights:
- Family score: 25%
- Price tier: 20%
- Country/region: 15%
- Best age range: 15%
- Pass network: 10%
- Terrain mix: 15%

Part of P7: Link Primitives implementation.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any
import math
from uuid import UUID

from shared.supabase_client import get_supabase_client


# ============================================================================
# CONSTANTS
# ============================================================================

# Similarity algorithm weights (must sum to 1.0)
SIMILARITY_WEIGHTS = {
    "family_score": 0.25,      # Family-friendliness alignment
    "price_tier": 0.20,        # Budget similarity
    "region": 0.15,            # Geographic proximity/similarity
    "age_range": 0.15,         # Target age range overlap
    "pass_network": 0.10,      # Ski pass compatibility
    "terrain_mix": 0.15,       # Terrain distribution similarity
}

# Price tier definitions (USD per day, family of 4)
PRICE_TIERS = {
    "budget": (0, 400),
    "mid": (400, 700),
    "premium": (700, 1000),
    "luxury": (1000, float("inf")),
}

# Region groupings for similarity
REGION_GROUPS = {
    "alps_west": ["France", "Switzerland"],
    "alps_east": ["Austria", "Italy", "Germany", "Slovenia"],
    "scandinavia": ["Norway", "Sweden", "Finland"],
    "rockies": ["Colorado", "Utah", "Wyoming", "Montana", "Idaho"],
    "pacific_west": ["California", "Oregon", "Washington", "British Columbia"],
    "northeast_us": ["Vermont", "New Hampshire", "Maine", "New York"],
    "japan": ["Japan"],
    "other_europe": ["Spain", "Andorra", "Bulgaria", "Czech Republic", "Poland"],
    "other_americas": ["Chile", "Argentina", "Canada"],
    "oceania": ["Australia", "New Zealand"],
}


class LinkType(str, Enum):
    """Types of internal links between resorts."""
    SIMILAR = "similar"
    SAME_PASS = "same_pass"
    SAME_REGION = "same_region"
    SAME_COUNTRY = "same_country"
    COMPARISON = "comparison"
    ALTERNATIVE = "alternative"
    NEARBY = "nearby"


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class SimilarityResult:
    """Result of similarity calculation between two resorts."""
    resort_a_id: str
    resort_b_id: str
    overall_score: float
    family_score_similarity: float
    price_tier_similarity: float
    region_similarity: float
    age_range_similarity: float
    pass_network_similarity: float
    terrain_mix_similarity: float


@dataclass
class SimilarResort:
    """A resort that is similar to another."""
    resort_id: str
    name: str
    country: str
    slug: str
    similarity_score: float
    family_overall_score: int | None = None
    shared_features: list[str] = field(default_factory=list)


@dataclass
class InternalLink:
    """An internal link suggestion between resorts."""
    source_resort_id: str
    target_resort_id: str
    target_name: str
    target_country: str
    target_slug: str
    link_type: LinkType
    anchor_text: str
    relevance_score: float


# ============================================================================
# SIMILARITY CALCULATION HELPERS
# ============================================================================

def _normalize_score(score: float | None, max_score: float = 10.0) -> float:
    """Normalize a score to 0-1 range."""
    if score is None:
        return 0.5  # Default to middle value if missing
    return min(max(score / max_score, 0.0), 1.0)


def _calculate_score_similarity(score_a: float | None, score_b: float | None) -> float:
    """Calculate similarity between two scores (0-1 scale).

    Returns 1.0 for identical scores, decreasing as they differ.
    """
    norm_a = _normalize_score(score_a)
    norm_b = _normalize_score(score_b)
    return 1.0 - abs(norm_a - norm_b)


def _get_price_tier(daily_cost: float | None) -> str:
    """Determine price tier from daily family cost."""
    if daily_cost is None:
        return "unknown"
    for tier, (low, high) in PRICE_TIERS.items():
        if low <= daily_cost < high:
            return tier
    return "luxury"


def _calculate_price_similarity(cost_a: float | None, cost_b: float | None) -> float:
    """Calculate similarity between two price points.

    Same tier = 1.0, adjacent tier = 0.5, two tiers apart = 0.25, etc.
    """
    tier_a = _get_price_tier(cost_a)
    tier_b = _get_price_tier(cost_b)

    if tier_a == "unknown" or tier_b == "unknown":
        return 0.5  # Default if missing data

    if tier_a == tier_b:
        return 1.0

    tier_order = ["budget", "mid", "premium", "luxury"]
    try:
        idx_a = tier_order.index(tier_a)
        idx_b = tier_order.index(tier_b)
        distance = abs(idx_a - idx_b)
        return max(1.0 - (distance * 0.25), 0.0)
    except ValueError:
        return 0.5


def _get_region_group(country: str, region: str | None = None) -> str:
    """Get the region group for a country/region."""
    # Check if region is a US state
    if country == "United States" and region:
        for group, members in REGION_GROUPS.items():
            if region in members:
                return group

    # Check by country
    for group, members in REGION_GROUPS.items():
        if country in members:
            return group

    return "other"


def _calculate_region_similarity(
    country_a: str, region_a: str | None,
    country_b: str, region_b: str | None,
) -> float:
    """Calculate geographic similarity.

    Same country = 1.0, same region group = 0.7, different = 0.3
    """
    if country_a == country_b:
        if region_a and region_b and region_a == region_b:
            return 1.0  # Same exact region
        return 0.9  # Same country, different region

    group_a = _get_region_group(country_a, region_a)
    group_b = _get_region_group(country_b, region_b)

    if group_a == group_b:
        return 0.7  # Same geographic group

    # Give partial credit for similar continents/hemispheres
    alps = {"alps_west", "alps_east"}
    us = {"rockies", "pacific_west", "northeast_us"}

    if group_a in alps and group_b in alps:
        return 0.6
    if group_a in us and group_b in us:
        return 0.5

    return 0.3


def _calculate_age_range_overlap(
    min_a: int | None, max_a: int | None,
    min_b: int | None, max_b: int | None,
) -> float:
    """Calculate overlap between two age ranges.

    Returns 1.0 for identical ranges, decreasing based on overlap.
    """
    # Default age ranges if missing (0-18 for general family)
    min_a = min_a if min_a is not None else 0
    max_a = max_a if max_a is not None else 18
    min_b = min_b if min_b is not None else 0
    max_b = max_b if max_b is not None else 18

    # Calculate overlap
    overlap_start = max(min_a, min_b)
    overlap_end = min(max_a, max_b)

    if overlap_start > overlap_end:
        return 0.2  # No overlap, but not zero (still family resorts)

    overlap = overlap_end - overlap_start
    range_a = max_a - min_a
    range_b = max_b - min_b
    max_range = max(range_a, range_b, 1)

    return min(overlap / max_range, 1.0)


def _calculate_pass_network_similarity(
    passes_a: list[str],
    passes_b: list[str],
) -> float:
    """Calculate similarity based on shared ski passes.

    Having shared major passes (Epic, Ikon) indicates similar market positioning.
    """
    if not passes_a or not passes_b:
        return 0.5  # No data

    set_a = set(p.lower() for p in passes_a)
    set_b = set(p.lower() for p in passes_b)

    # Check for shared major passes
    major_passes = {"epic", "ikon", "mountain collective", "indy pass"}
    shared_major = (set_a & major_passes) & (set_b & major_passes)

    if shared_major:
        return 1.0  # Same major pass network

    # Check for any shared passes
    shared = set_a & set_b
    if shared:
        return 0.7

    # Both have major passes but different ones
    if (set_a & major_passes) and (set_b & major_passes):
        return 0.4  # Competing networks

    return 0.3


def _calculate_terrain_similarity(
    beginner_a: int | None, intermediate_a: int | None, advanced_a: int | None,
    beginner_b: int | None, intermediate_b: int | None, advanced_b: int | None,
) -> float:
    """Calculate similarity of terrain distribution.

    Compares the percentage breakdown of beginner/intermediate/advanced terrain.
    """
    # Default to balanced if missing
    def norm(b, i, a):
        total = (b or 33) + (i or 34) + (a or 33)
        if total == 0:
            return 33, 34, 33
        return ((b or 33) / total, (i or 34) / total, (a or 33) / total)

    b1, i1, a1 = norm(beginner_a, intermediate_a, advanced_a)
    b2, i2, a2 = norm(beginner_b, intermediate_b, advanced_b)

    # Calculate Euclidean distance in terrain space
    distance = math.sqrt((b1 - b2)**2 + (i1 - i2)**2 + (a1 - a2)**2)

    # Max distance is sqrt(2) when one has 100% beginner and other has 100% advanced
    max_distance = math.sqrt(2)

    return 1.0 - (distance / max_distance)


# ============================================================================
# MAIN SIMILARITY FUNCTION
# ============================================================================

def calculate_similarity(
    resort_a: dict[str, Any],
    resort_b: dict[str, Any],
    metrics_a: dict[str, Any] | None = None,
    metrics_b: dict[str, Any] | None = None,
    costs_a: dict[str, Any] | None = None,
    costs_b: dict[str, Any] | None = None,
    passes_a: list[str] | None = None,
    passes_b: list[str] | None = None,
) -> SimilarityResult:
    """Calculate comprehensive similarity between two resorts.

    Args:
        resort_a: Resort data dict with name, country, region
        resort_b: Resort data dict
        metrics_a: Family metrics for resort A
        metrics_b: Family metrics for resort B
        costs_a: Cost data for resort A
        costs_b: Cost data for resort B
        passes_a: List of ski pass names for resort A
        passes_b: List of ski pass names for resort B

    Returns:
        SimilarityResult with overall and component scores
    """
    metrics_a = metrics_a or {}
    metrics_b = metrics_b or {}
    costs_a = costs_a or {}
    costs_b = costs_b or {}
    passes_a = passes_a or []
    passes_b = passes_b or []

    # Calculate component similarities
    family_sim = _calculate_score_similarity(
        metrics_a.get("family_overall_score"),
        metrics_b.get("family_overall_score"),
    )

    price_sim = _calculate_price_similarity(
        costs_a.get("estimated_family_daily"),
        costs_b.get("estimated_family_daily"),
    )

    region_sim = _calculate_region_similarity(
        resort_a.get("country", ""),
        resort_a.get("region"),
        resort_b.get("country", ""),
        resort_b.get("region"),
    )

    age_sim = _calculate_age_range_overlap(
        metrics_a.get("best_age_min"),
        metrics_a.get("best_age_max"),
        metrics_b.get("best_age_min"),
        metrics_b.get("best_age_max"),
    )

    pass_sim = _calculate_pass_network_similarity(passes_a, passes_b)

    terrain_sim = _calculate_terrain_similarity(
        metrics_a.get("beginner_terrain_pct"),
        metrics_a.get("intermediate_terrain_pct"),
        metrics_a.get("advanced_terrain_pct"),
        metrics_b.get("beginner_terrain_pct"),
        metrics_b.get("intermediate_terrain_pct"),
        metrics_b.get("advanced_terrain_pct"),
    )

    # Calculate weighted overall score
    overall = (
        family_sim * SIMILARITY_WEIGHTS["family_score"] +
        price_sim * SIMILARITY_WEIGHTS["price_tier"] +
        region_sim * SIMILARITY_WEIGHTS["region"] +
        age_sim * SIMILARITY_WEIGHTS["age_range"] +
        pass_sim * SIMILARITY_WEIGHTS["pass_network"] +
        terrain_sim * SIMILARITY_WEIGHTS["terrain_mix"]
    )

    return SimilarityResult(
        resort_a_id=resort_a.get("id", ""),
        resort_b_id=resort_b.get("id", ""),
        overall_score=round(overall, 4),
        family_score_similarity=round(family_sim, 4),
        price_tier_similarity=round(price_sim, 4),
        region_similarity=round(region_sim, 4),
        age_range_similarity=round(age_sim, 4),
        pass_network_similarity=round(pass_sim, 4),
        terrain_mix_similarity=round(terrain_sim, 4),
    )


# ============================================================================
# DATABASE OPERATIONS
# ============================================================================

def store_similarity(result: SimilarityResult) -> bool:
    """Store a similarity result in the database.

    Ensures resort_a_id < resort_b_id to maintain uniqueness constraint.
    """
    try:
        supabase = get_supabase_client()

        # Ensure correct ordering
        if result.resort_a_id > result.resort_b_id:
            a_id, b_id = result.resort_b_id, result.resort_a_id
        else:
            a_id, b_id = result.resort_a_id, result.resort_b_id

        data = {
            "resort_a_id": a_id,
            "resort_b_id": b_id,
            "similarity_score": result.overall_score,
            "family_score_similarity": result.family_score_similarity,
            "price_tier_similarity": result.price_tier_similarity,
            "region_similarity": result.region_similarity,
            "age_range_similarity": result.age_range_similarity,
            "pass_network_similarity": result.pass_network_similarity,
            "terrain_mix_similarity": result.terrain_mix_similarity,
        }

        supabase.table("resort_similarities").upsert(
            data,
            on_conflict="resort_a_id,resort_b_id"
        ).execute()

        return True
    except Exception as e:
        print(f"Failed to store similarity: {e}")
        return False


def get_similar_resorts(
    resort_id: str,
    limit: int = 5,
    min_score: float = 0.3,
) -> list[SimilarResort]:
    """Get similar resorts for a given resort.

    Uses the database function for efficiency.
    """
    try:
        supabase = get_supabase_client()

        result = supabase.rpc(
            "get_similar_resorts",
            {
                "p_resort_id": resort_id,
                "p_limit": limit,
                "p_min_score": min_score,
            }
        ).execute()

        return [
            SimilarResort(
                resort_id=r["resort_id"],
                name=r["name"],
                country=r["country"],
                slug=r["slug"],
                similarity_score=r["similarity_score"],
                family_overall_score=r.get("family_overall_score"),
            )
            for r in (result.data or [])
        ]
    except Exception as e:
        print(f"Failed to get similar resorts: {e}")
        return []


def get_similarity_score(resort_a_id: str, resort_b_id: str) -> float | None:
    """Get the similarity score between two specific resorts."""
    try:
        supabase = get_supabase_client()

        # Ensure correct ordering
        if resort_a_id > resort_b_id:
            a_id, b_id = resort_b_id, resort_a_id
        else:
            a_id, b_id = resort_a_id, resort_b_id

        result = supabase.table("resort_similarities")\
            .select("similarity_score")\
            .eq("resort_a_id", a_id)\
            .eq("resort_b_id", b_id)\
            .limit(1)\
            .execute()

        if result.data:
            return result.data[0]["similarity_score"]
        return None
    except Exception:
        return None


# ============================================================================
# INTERNAL LINK OPERATIONS
# ============================================================================

def create_internal_link(
    source_resort_id: str,
    target_resort_id: str,
    link_type: LinkType,
    anchor_text: str | None = None,
    context_snippet: str | None = None,
    relevance_score: float = 0.5,
) -> bool:
    """Create an internal link suggestion between resorts."""
    try:
        supabase = get_supabase_client()

        data = {
            "source_resort_id": source_resort_id,
            "target_resort_id": target_resort_id,
            "link_type": link_type.value,
            "anchor_text": anchor_text,
            "context_snippet": context_snippet,
            "relevance_score": relevance_score,
        }

        supabase.table("resort_internal_links").upsert(
            data,
            on_conflict="source_resort_id,target_resort_id,link_type"
        ).execute()

        return True
    except Exception as e:
        print(f"Failed to create internal link: {e}")
        return False


def get_internal_links(
    resort_id: str,
    link_type: LinkType | None = None,
    limit: int = 10,
) -> list[InternalLink]:
    """Get internal link suggestions for a resort."""
    try:
        supabase = get_supabase_client()

        result = supabase.rpc(
            "get_link_suggestions",
            {
                "p_resort_id": resort_id,
                "p_link_type": link_type.value if link_type else None,
                "p_limit": limit,
            }
        ).execute()

        return [
            InternalLink(
                source_resort_id=resort_id,
                target_resort_id=r["target_resort_id"],
                target_name=r["target_name"],
                target_country=r["target_country"],
                target_slug=r["target_slug"],
                link_type=LinkType(r["link_type"]),
                anchor_text=r["anchor_text"] or r["target_name"],
                relevance_score=r["relevance_score"] or 0.5,
            )
            for r in (result.data or [])
        ]
    except Exception as e:
        print(f"Failed to get internal links: {e}")
        return []


def generate_anchor_text(
    target_name: str,
    target_country: str,
    link_type: LinkType,
) -> str:
    """Generate natural anchor text for a link."""
    templates = {
        LinkType.SIMILAR: f"{target_name}",
        LinkType.SAME_PASS: f"{target_name} (same pass)",
        LinkType.SAME_REGION: f"{target_name}",
        LinkType.SAME_COUNTRY: f"{target_name}",
        LinkType.COMPARISON: f"{target_name}",
        LinkType.ALTERNATIVE: f"{target_name} as an alternative",
        LinkType.NEARBY: f"nearby {target_name}",
    }
    return templates.get(link_type, target_name)


# ============================================================================
# BATCH OPERATIONS
# ============================================================================

def calculate_similarities_for_resort(
    resort_id: str,
    limit: int = 50,
) -> int:
    """Calculate similarities between a resort and all other published resorts.

    Returns the number of similarities calculated.
    """
    try:
        supabase = get_supabase_client()

        # Get the target resort with all data
        resort_result = supabase.table("resorts")\
            .select("*")\
            .eq("id", resort_id)\
            .limit(1)\
            .execute()

        if not resort_result.data:
            return 0

        resort_a = resort_result.data[0]

        # Get metrics and costs for resort A
        metrics_a_result = supabase.table("resort_family_metrics")\
            .select("*")\
            .eq("resort_id", resort_id)\
            .limit(1)\
            .execute()
        metrics_a = metrics_a_result.data[0] if metrics_a_result.data else {}

        costs_a_result = supabase.table("resort_costs")\
            .select("*")\
            .eq("resort_id", resort_id)\
            .limit(1)\
            .execute()
        costs_a = costs_a_result.data[0] if costs_a_result.data else {}

        # Get passes for resort A
        passes_a_result = supabase.table("resort_passes")\
            .select("ski_passes(name)")\
            .eq("resort_id", resort_id)\
            .execute()
        passes_a = [p["ski_passes"]["name"] for p in (passes_a_result.data or []) if p.get("ski_passes")]

        # Get all other published resorts
        other_resorts_result = supabase.table("resorts")\
            .select("*")\
            .eq("status", "published")\
            .neq("id", resort_id)\
            .limit(limit)\
            .execute()

        count = 0
        for resort_b in (other_resorts_result.data or []):
            # Get metrics and costs for resort B
            metrics_b_result = supabase.table("resort_family_metrics")\
                .select("*")\
                .eq("resort_id", resort_b["id"])\
                .limit(1)\
                .execute()
            metrics_b = metrics_b_result.data[0] if metrics_b_result.data else {}

            costs_b_result = supabase.table("resort_costs")\
                .select("*")\
                .eq("resort_id", resort_b["id"])\
                .limit(1)\
                .execute()
            costs_b = costs_b_result.data[0] if costs_b_result.data else {}

            # Get passes for resort B
            passes_b_result = supabase.table("resort_passes")\
                .select("ski_passes(name)")\
                .eq("resort_id", resort_b["id"])\
                .execute()
            passes_b = [p["ski_passes"]["name"] for p in (passes_b_result.data or []) if p.get("ski_passes")]

            # Calculate similarity
            similarity = calculate_similarity(
                resort_a, resort_b,
                metrics_a, metrics_b,
                costs_a, costs_b,
                passes_a, passes_b,
            )

            # Store if above threshold
            if similarity.overall_score >= 0.2:
                if store_similarity(similarity):
                    count += 1

        return count
    except Exception as e:
        print(f"Failed to calculate similarities: {e}")
        return 0


def generate_links_for_resort(resort_id: str) -> int:
    """Generate internal link suggestions for a resort based on similarities.

    Returns the number of links generated.
    """
    try:
        supabase = get_supabase_client()

        # Get the source resort
        resort_result = supabase.table("resorts")\
            .select("*")\
            .eq("id", resort_id)\
            .limit(1)\
            .execute()

        if not resort_result.data:
            return 0

        resort = resort_result.data[0]
        count = 0

        # 1. Generate "similar" links from similarity scores
        similar = get_similar_resorts(resort_id, limit=5, min_score=0.5)
        for s in similar:
            anchor = generate_anchor_text(s.name, s.country, LinkType.SIMILAR)
            if create_internal_link(
                resort_id, s.resort_id, LinkType.SIMILAR,
                anchor_text=anchor,
                relevance_score=s.similarity_score,
            ):
                count += 1

        # 2. Generate "same country" links
        same_country_result = supabase.table("resorts")\
            .select("id, name, country, slug")\
            .eq("country", resort["country"])\
            .eq("status", "published")\
            .neq("id", resort_id)\
            .limit(3)\
            .execute()

        for r in (same_country_result.data or []):
            anchor = generate_anchor_text(r["name"], r["country"], LinkType.SAME_COUNTRY)
            if create_internal_link(
                resort_id, r["id"], LinkType.SAME_COUNTRY,
                anchor_text=anchor,
                relevance_score=0.6,
            ):
                count += 1

        # 3. Generate "same pass" links
        passes_result = supabase.table("resort_passes")\
            .select("pass_id, ski_passes(name)")\
            .eq("resort_id", resort_id)\
            .execute()

        for pass_data in (passes_result.data or []):
            if not pass_data.get("ski_passes"):
                continue

            pass_name = pass_data["ski_passes"]["name"]
            pass_id = pass_data["pass_id"]

            # Find other resorts with same pass
            same_pass_result = supabase.table("resort_passes")\
                .select("resort_id, resorts(id, name, country, slug, status)")\
                .eq("pass_id", pass_id)\
                .neq("resort_id", resort_id)\
                .limit(3)\
                .execute()

            for rp in (same_pass_result.data or []):
                if not rp.get("resorts") or rp["resorts"].get("status") != "published":
                    continue
                r = rp["resorts"]
                anchor = f"{r['name']} ({pass_name})"
                if create_internal_link(
                    resort_id, r["id"], LinkType.SAME_PASS,
                    anchor_text=anchor,
                    relevance_score=0.7,
                ):
                    count += 1

        return count
    except Exception as e:
        print(f"Failed to generate links: {e}")
        return 0


def refresh_all_similarities(
    batch_size: int = 10,
    max_resorts: int = 100,
) -> dict[str, int]:
    """Refresh similarities for all published resorts.

    Returns statistics about the refresh operation.
    """
    try:
        supabase = get_supabase_client()

        # Get all published resorts
        resorts_result = supabase.table("resorts")\
            .select("id, name")\
            .eq("status", "published")\
            .limit(max_resorts)\
            .execute()

        resorts = resorts_result.data or []
        total_similarities = 0
        total_links = 0
        processed = 0

        for resort in resorts:
            # Calculate similarities
            sim_count = calculate_similarities_for_resort(
                resort["id"],
                limit=batch_size,
            )
            total_similarities += sim_count

            # Generate links
            link_count = generate_links_for_resort(resort["id"])
            total_links += link_count

            processed += 1

        return {
            "resorts_processed": processed,
            "similarities_calculated": total_similarities,
            "links_generated": total_links,
        }
    except Exception as e:
        print(f"Failed to refresh similarities: {e}")
        return {
            "resorts_processed": 0,
            "similarities_calculated": 0,
            "links_generated": 0,
            "error": str(e),
        }


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_shared_features(
    resort_a_id: str,
    resort_b_id: str,
) -> list[str]:
    """Get a list of shared features between two resorts for display."""
    try:
        supabase = get_supabase_client()
        features = []

        # Get both resorts
        resorts = supabase.table("resorts")\
            .select("*")\
            .in_("id", [resort_a_id, resort_b_id])\
            .execute()

        if len(resorts.data or []) != 2:
            return []

        r_a, r_b = resorts.data[0], resorts.data[1]

        # Same country
        if r_a["country"] == r_b["country"]:
            features.append(f"Both in {r_a['country']}")

        # Check for shared passes
        passes_a = supabase.table("resort_passes")\
            .select("pass_id, ski_passes(name)")\
            .eq("resort_id", resort_a_id)\
            .execute()

        passes_b = supabase.table("resort_passes")\
            .select("pass_id, ski_passes(name)")\
            .eq("resort_id", resort_b_id)\
            .execute()

        pass_ids_a = {p["pass_id"] for p in (passes_a.data or [])}
        pass_ids_b = {p["pass_id"] for p in (passes_b.data or [])}
        shared_pass_ids = pass_ids_a & pass_ids_b

        if shared_pass_ids:
            for p in (passes_a.data or []):
                if p["pass_id"] in shared_pass_ids and p.get("ski_passes"):
                    features.append(f"Both on {p['ski_passes']['name']}")

        # Get family metrics
        metrics = supabase.table("resort_family_metrics")\
            .select("*")\
            .in_("resort_id", [resort_a_id, resort_b_id])\
            .execute()

        if len(metrics.data or []) == 2:
            m_a, m_b = metrics.data[0], metrics.data[1]

            # Similar family scores
            if m_a.get("family_overall_score") and m_b.get("family_overall_score"):
                diff = abs(m_a["family_overall_score"] - m_b["family_overall_score"])
                if diff <= 1:
                    features.append("Similar family rating")

            # Both have childcare
            if m_a.get("has_childcare") and m_b.get("has_childcare"):
                features.append("Both have childcare")

        return features[:4]  # Limit to 4 features
    except Exception:
        return []


def delete_stale_similarities(days_old: int = 30) -> int:
    """Delete similarity records older than specified days.

    Returns the number of records deleted.
    """
    try:
        from datetime import datetime, timedelta
        supabase = get_supabase_client()

        cutoff = datetime.utcnow() - timedelta(days=days_old)

        result = supabase.table("resort_similarities")\
            .delete()\
            .lt("calculated_at", cutoff.isoformat())\
            .execute()

        return len(result.data or [])
    except Exception as e:
        print(f"Failed to delete stale similarities: {e}")
        return 0
