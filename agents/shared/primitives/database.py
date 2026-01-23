"""Database primitives for resort and ski pass CRUD operations.

These primitives provide atomic database operations that agents can compose
to achieve any outcome. Following Agent Native principles, these are the
building blocks that enable parity between human editors and agents.
"""

from datetime import datetime
from typing import Any
from uuid import uuid4

from ..supabase_client import get_supabase_client


# =============================================================================
# SCHEMA WHITELISTS (Single Source of Truth)
# =============================================================================
# These define what columns exist in the database. Any fields not in these sets
# will be filtered out before upsert operations to prevent schema mismatch errors.

RESORT_COSTS_COLUMNS = frozenset({
    "resort_id",
    "currency",
    "lift_adult_daily",
    "lift_child_daily",
    "lift_family_daily",
    "lodging_budget_nightly",
    "lodging_mid_nightly",
    "lodging_luxury_nightly",
    "meal_family_avg",
    "estimated_family_daily",
    "price_level",
    # Added in migration 016 (family-critical costs):
    "lesson_group_child",
    "lesson_private_hour",
    "rental_adult_daily",
    "rental_child_daily",
    "lift_under6",
})

RESORT_FAMILY_METRICS_COLUMNS = frozenset({
    "resort_id",
    "family_overall_score",
    "best_age_min",
    "best_age_max",
    "kid_friendly_terrain_pct",
    "has_childcare",
    "childcare_min_age",  # in months
    "ski_school_min_age",  # in years
    "kids_ski_free_age",
    "has_magic_carpet",
    "has_terrain_park_kids",
    "perfect_if",
    "skip_if",
})

# Field name mappings (extraction layer name -> database column name)
FAMILY_METRICS_FIELD_MAP = {
    "childcare_min_age_months": "childcare_min_age",
    "ski_school_min_age_years": "ski_school_min_age",
}


def sanitize_for_schema(
    data: dict[str, Any],
    allowed_columns: frozenset[str],
    field_map: dict[str, str] | None = None,
) -> tuple[dict[str, Any], list[str]]:
    """
    Filter and map data to only columns that exist in the DB schema.

    This prevents schema mismatch errors when the extraction layer produces
    fields that don't exist in the database yet (or have different names).

    Args:
        data: Raw data dictionary
        allowed_columns: Set of valid column names for this table
        field_map: Optional dict to rename fields (extraction_name -> db_name)

    Returns:
        Tuple of (sanitized_data, dropped_fields)
    """
    field_map = field_map or {}
    sanitized = {}
    dropped = []

    for key, value in data.items():
        # Apply field name mapping first
        mapped_key = field_map.get(key, key)

        if mapped_key in allowed_columns:
            sanitized[mapped_key] = value
        else:
            dropped.append(key)

    return sanitized, dropped


# =============================================================================
# RESORT CRUD OPERATIONS
# =============================================================================


def list_resorts(
    country: str | None = None,
    region: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """
    List all resorts with optional filtering.

    Args:
        country: Filter by country
        region: Filter by region
        status: Filter by status (draft, published, archived)
        limit: Maximum results to return
        offset: Pagination offset

    Returns:
        List of resort records
    """
    client = get_supabase_client()

    query = client.table("resorts").select("*")

    if country:
        query = query.eq("country", country)
    if region:
        query = query.eq("region", region)
    if status:
        query = query.eq("status", status)

    query = query.order("name").range(offset, offset + limit - 1)

    response = query.execute()
    return response.data or []


def get_resort(resort_id: str) -> dict | None:
    """
    Get a single resort by ID.

    Args:
        resort_id: UUID of the resort

    Returns:
        Resort record or None if not found
    """
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select("*")
        .eq("id", resort_id)
        .single()
        .execute()
    )
    return response.data


def get_resort_by_slug(slug: str, country: str) -> dict | None:
    """
    Get a resort by its slug and country.

    Args:
        slug: URL slug (e.g., 'park-city')
        country: Country name (e.g., 'USA')

    Returns:
        Resort record or None if not found
    """
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select("*")
        .eq("slug", slug)
        .eq("country", country)
        .limit(1)
        .execute()
    )
    # Return first result or None if no matches
    return response.data[0] if response.data else None


def create_resort(
    name: str,
    country: str,
    region: str,
    slug: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Create a new resort entry.

    Args:
        name: Resort display name
        country: Country name
        region: Region/state name
        slug: URL slug (auto-generated if not provided)
        latitude: Latitude coordinate
        longitude: Longitude coordinate
        metadata: Additional data

    Returns:
        Created resort record

    Raises:
        ValueError: If name or country is empty/invalid
    """
    # Safety net: Reject invalid resort data to prevent ghost resorts
    if not name or not name.strip() or name.strip().lower() == "unknown":
        raise ValueError(f"Resort name cannot be empty or 'Unknown': got '{name}'")
    if not country or not country.strip() or country.strip().lower() == "unknown":
        raise ValueError(f"Resort country cannot be empty or 'Unknown': got '{country}'")

    client = get_supabase_client()

    # Auto-generate slug if not provided
    if not slug:
        slug = name.lower().replace(" ", "-").replace("'", "")

    data = {
        "id": str(uuid4()),
        "name": name,
        "country": country,
        "region": region,
        "slug": slug,
        "status": "draft",
        "created_at": datetime.utcnow().isoformat(),
        "updated_at": datetime.utcnow().isoformat(),
    }

    if latitude is not None:
        data["latitude"] = latitude
    if longitude is not None:
        data["longitude"] = longitude

    response = client.table("resorts").insert(data).execute()
    return response.data[0] if response.data else data


def update_resort(resort_id: str, updates: dict[str, Any]) -> dict:
    """
    Update a resort record.

    Args:
        resort_id: UUID of the resort
        updates: Fields to update

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    updates["updated_at"] = datetime.utcnow().isoformat()

    response = (
        client.table("resorts")
        .update(updates)
        .eq("id", resort_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def delete_resort(resort_id: str, hard_delete: bool = False) -> bool:
    """
    Delete a resort.

    By default, performs a soft delete (sets status to 'archived').
    Use hard_delete=True to permanently remove.

    Args:
        resort_id: UUID of the resort
        hard_delete: If True, permanently removes the record

    Returns:
        True if successful
    """
    client = get_supabase_client()

    if hard_delete:
        # Hard delete - remove from database
        # Note: This will cascade delete related records
        response = (
            client.table("resorts")
            .delete()
            .eq("id", resort_id)
            .execute()
        )
    else:
        # Soft delete - just archive
        response = (
            client.table("resorts")
            .update({"status": "archived", "updated_at": datetime.utcnow().isoformat()})
            .eq("id", resort_id)
            .execute()
        )

    return bool(response.data)


def search_resorts(
    query: str,
    filters: dict[str, Any] | None = None,
    limit: int = 20,
) -> list[dict]:
    """
    Search resorts by name, country, or region.

    Args:
        query: Search term
        filters: Additional filters (country, region, status)
        limit: Maximum results

    Returns:
        List of matching resort records
    """
    client = get_supabase_client()

    # Use ilike for case-insensitive partial matching
    search_query = (
        client.table("resorts")
        .select("*")
        .or_(f"name.ilike.%{query}%,country.ilike.%{query}%,region.ilike.%{query}%")
    )

    if filters:
        if filters.get("country"):
            search_query = search_query.eq("country", filters["country"])
        if filters.get("region"):
            search_query = search_query.eq("region", filters["region"])
        if filters.get("status"):
            search_query = search_query.eq("status", filters["status"])

    response = search_query.limit(limit).execute()
    return response.data or []


# =============================================================================
# RESORT CONTENT OPERATIONS
# =============================================================================


def get_resort_content(resort_id: str) -> dict | None:
    """
    Get content for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        Content record or None
    """
    client = get_supabase_client()
    response = (
        client.table("resort_content")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )
    return response.data


def update_resort_content(resort_id: str, content: dict[str, Any]) -> dict:
    """
    Update resort content (upsert).

    Args:
        resort_id: UUID of the resort
        content: Content fields to update

    Returns:
        Updated content record
    """
    client = get_supabase_client()

    data = {"resort_id": resort_id, **content}
    response = client.table("resort_content").upsert(data).execute()
    return response.data[0] if response.data else data


# =============================================================================
# RESORT COSTS OPERATIONS
# =============================================================================


def get_resort_costs(resort_id: str) -> dict | None:
    """
    Get cost information for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        Costs record or None
    """
    client = get_supabase_client()
    response = (
        client.table("resort_costs")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )
    return response.data


def update_resort_costs(resort_id: str, costs: dict[str, Any]) -> dict:
    """
    Update resort costs (upsert).

    Automatically filters out any fields not in the database schema to prevent
    schema mismatch errors. Dropped fields are logged for debugging.

    Args:
        resort_id: UUID of the resort
        costs: Cost fields to update (lift_adult_daily, lodging_budget_nightly, etc.)

    Returns:
        Updated costs record (includes _dropped_fields for debugging)
    """
    client = get_supabase_client()

    # Sanitize data to only include valid columns
    sanitized_costs, dropped = sanitize_for_schema(costs, RESORT_COSTS_COLUMNS)

    if dropped:
        print(f"[sanitize] Dropped {len(dropped)} fields from resort_costs: {dropped}")

    data = {"resort_id": resort_id, **sanitized_costs}
    response = client.table("resort_costs").upsert(data).execute()

    result = response.data[0] if response.data else data
    if dropped:
        result["_dropped_fields"] = dropped
    return result


# =============================================================================
# RESORT FAMILY METRICS OPERATIONS
# =============================================================================


def get_resort_family_metrics(resort_id: str) -> dict | None:
    """
    Get family metrics for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        Family metrics record or None
    """
    client = get_supabase_client()
    response = (
        client.table("resort_family_metrics")
        .select("*")
        .eq("resort_id", resort_id)
        .single()
        .execute()
    )
    return response.data


def update_resort_family_metrics(resort_id: str, metrics: dict[str, Any]) -> dict:
    """
    Update resort family metrics (upsert).

    Automatically filters out any fields not in the database schema and maps
    field names from extraction format to database format.

    Field mappings:
    - childcare_min_age_months -> childcare_min_age
    - ski_school_min_age_years -> ski_school_min_age

    Args:
        resort_id: UUID of the resort
        metrics: Metrics to update (family_overall_score, childcare_min_age, etc.)

    Returns:
        Updated metrics record (includes _dropped_fields for debugging)
    """
    client = get_supabase_client()

    # Sanitize data with field name mapping
    sanitized_metrics, dropped = sanitize_for_schema(
        metrics,
        RESORT_FAMILY_METRICS_COLUMNS,
        FAMILY_METRICS_FIELD_MAP,
    )

    if dropped:
        print(f"[sanitize] Dropped {len(dropped)} fields from family_metrics: {dropped}")

    data = {"resort_id": resort_id, **sanitized_metrics}
    response = client.table("resort_family_metrics").upsert(data).execute()

    result = response.data[0] if response.data else data
    if dropped:
        result["_dropped_fields"] = dropped
    return result


# =============================================================================
# SKI PASS OPERATIONS
# =============================================================================


def list_ski_passes(pass_type: str | None = None) -> list[dict]:
    """
    List all ski passes.

    Args:
        pass_type: Filter by type (mega, regional, single)

    Returns:
        List of ski pass records
    """
    client = get_supabase_client()

    query = client.table("ski_passes").select("*")

    if pass_type:
        query = query.eq("type", pass_type)

    response = query.order("name").execute()
    return response.data or []


def get_ski_pass(pass_id: str) -> dict | None:
    """
    Get a ski pass by ID.

    Args:
        pass_id: UUID of the pass

    Returns:
        Ski pass record or None
    """
    client = get_supabase_client()
    response = (
        client.table("ski_passes")
        .select("*")
        .eq("id", pass_id)
        .single()
        .execute()
    )
    return response.data


def get_resort_passes(resort_id: str) -> list[dict]:
    """
    Get all passes that include a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        List of pass records with access_type
    """
    client = get_supabase_client()
    response = (
        client.table("resort_passes")
        .select("access_type, pass:ski_passes(*)")
        .eq("resort_id", resort_id)
        .execute()
    )
    return response.data or []


def add_resort_pass(
    resort_id: str,
    pass_id: str,
    access_type: str = "full",
) -> dict:
    """
    Add a ski pass to a resort.

    Args:
        resort_id: UUID of the resort
        pass_id: UUID of the ski pass
        access_type: Type of access (full, limited, blackout)

    Returns:
        Created resort_passes record
    """
    client = get_supabase_client()

    data = {
        "resort_id": resort_id,
        "pass_id": pass_id,
        "access_type": access_type,
    }

    response = client.table("resort_passes").upsert(data).execute()
    return response.data[0] if response.data else data


def remove_resort_pass(resort_id: str, pass_id: str) -> bool:
    """
    Remove a ski pass from a resort.

    Args:
        resort_id: UUID of the resort
        pass_id: UUID of the ski pass

    Returns:
        True if successful
    """
    client = get_supabase_client()
    response = (
        client.table("resort_passes")
        .delete()
        .eq("resort_id", resort_id)
        .eq("pass_id", pass_id)
        .execute()
    )
    return bool(response.data)


# =============================================================================
# SKI QUALITY CALENDAR OPERATIONS
# =============================================================================


def get_resort_calendar(resort_id: str) -> list[dict]:
    """
    Get ski quality calendar for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        List of monthly quality records
    """
    client = get_supabase_client()
    response = (
        client.table("ski_quality_calendar")
        .select("*")
        .eq("resort_id", resort_id)
        .order("month")
        .execute()
    )
    return response.data or []


def update_resort_calendar(resort_id: str, month: int, data: dict[str, Any]) -> dict:
    """
    Update a month's ski quality data for a resort.

    Args:
        resort_id: UUID of the resort
        month: Month number (1-12)
        data: Quality data (snow_quality_score, crowd_level, etc.)

    Returns:
        Updated calendar record
    """
    client = get_supabase_client()

    record = {
        "resort_id": resort_id,
        "month": month,
        **data,
    }

    # Check if record exists
    existing = (
        client.table("ski_quality_calendar")
        .select("id")
        .eq("resort_id", resort_id)
        .eq("month", month)
        .execute()
    )

    if existing.data:
        response = (
            client.table("ski_quality_calendar")
            .update(record)
            .eq("resort_id", resort_id)
            .eq("month", month)
            .execute()
        )
    else:
        record["id"] = str(uuid4())
        response = client.table("ski_quality_calendar").insert(record).execute()

    return response.data[0] if response.data else record


# =============================================================================
# FULL RESORT DATA OPERATIONS
# =============================================================================


def get_resort_full(resort_id: str) -> dict | None:
    """
    Get a resort with all related data (metrics, content, costs, calendar, passes).

    Args:
        resort_id: UUID of the resort

    Returns:
        Complete resort record with all relations
    """
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select(
            """
            *,
            family_metrics:resort_family_metrics(*),
            content:resort_content(*),
            costs:resort_costs(*),
            calendar:ski_quality_calendar(*),
            passes:resort_passes(
                access_type,
                pass:ski_passes(*)
            )
            """
        )
        .eq("id", resort_id)
        .single()
        .execute()
    )
    return response.data


# =============================================================================
# AGENT-NATIVE EXISTENCE CHECKING PRIMITIVES
# =============================================================================


def _slugify(name: str) -> str:
    """Convert resort name to URL-safe slug."""
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def _generate_name_variants(name: str) -> list[str]:
    """
    Generate common name variants for fuzzy matching.

    Handles:
    - St./Sankt/Saint variants
    - Core name extraction (Whistler Blackcomb -> Whistler)
    """
    variants = [name]
    name_lower = name.lower()

    # St./Sankt/Saint variants
    if name_lower.startswith("st. "):
        base = name[4:].strip()
        variants.extend([f"Sankt {base}", f"Saint {base}", f"St {base}"])
    elif name_lower.startswith("st "):
        base = name[3:].strip()
        variants.extend([f"Sankt {base}", f"Saint {base}", f"St. {base}"])
    elif name_lower.startswith("sankt "):
        base = name[6:].strip()
        variants.extend([f"St. {base}", f"St {base}", f"Saint {base}"])
    elif name_lower.startswith("saint "):
        base = name[6:].strip()
        variants.extend([f"St. {base}", f"St {base}", f"Sankt {base}"])

    # Core name extraction ("Whistler Blackcomb" -> "Whistler")
    if " " in name:
        core = name.split()[0]
        if core.lower() != name_lower:
            variants.append(core)

    return list(set(variants))


def _calculate_name_similarity(name1: str, name2: str) -> float:
    """
    Calculate token overlap similarity (Jaccard index).

    Returns value 0-1, where 1 = exact match.
    """
    # Normalize: lowercase, remove punctuation
    tokens1 = set(name1.lower().replace(".", "").replace("-", " ").split())
    tokens2 = set(name2.lower().replace(".", "").replace("-", " ").split())

    if not tokens1 or not tokens2:
        return 0.0

    intersection = tokens1 & tokens2
    union = tokens1 | tokens2

    return len(intersection) / len(union)


def check_resort_exists(name: str, country: str) -> dict[str, Any] | None:
    """
    Check if a resort already exists (exact or case-insensitive match).

    This is the agent-native way to check for duplicates before creating.

    Strategies:
    1. Exact slug match: slugify(name) + country
    2. Case-insensitive name match: ilike query

    Args:
        name: Resort name (any casing/format)
        country: Country name

    Returns:
        Resort dict if found, None if not exists
    """
    client = get_supabase_client()

    # Strategy 1: Exact slug match
    slug = _slugify(name)
    response = (
        client.table("resorts")
        .select("id, name, country, slug, status")
        .eq("slug", slug)
        .ilike("country", country)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    # Strategy 2: Case-insensitive name match
    response = (
        client.table("resorts")
        .select("id, name, country, slug, status")
        .ilike("name", name)
        .ilike("country", country)
        .limit(1)
        .execute()
    )

    if response.data:
        return response.data[0]

    return None


def find_similar_resorts(
    name: str,
    country: str | None = None,
    threshold: float = 0.6,
) -> list[dict[str, Any]]:
    """
    Find resorts with similar names (fuzzy match).

    Catches name variants like:
    - "St. Anton" vs "Sankt Anton" vs "Saint Anton"
    - "Zermatt" vs "Zermatt-Matterhorn"
    - "Whistler" vs "Whistler Blackcomb"

    Args:
        name: Resort name to search for
        country: Optional country filter
        threshold: Minimum similarity score (0-1), default 0.6

    Returns:
        List of similar resorts with similarity_score, sorted by score descending
    """
    client = get_supabase_client()

    # Generate name variants to search
    variants = _generate_name_variants(name)

    results = []
    seen_ids: set[str] = set()

    for variant in variants:
        query = (
            client.table("resorts")
            .select("id, name, country, slug, status")
            .ilike("name", f"%{variant}%")
        )

        if country:
            query = query.ilike("country", country)

        response = query.limit(10).execute()

        for r in response.data or []:
            if r["id"] not in seen_ids:
                seen_ids.add(r["id"])
                score = _calculate_name_similarity(name, r["name"])
                if score >= threshold:
                    results.append({**r, "similarity_score": round(score, 3)})

    # Sort by similarity score descending
    return sorted(results, key=lambda x: x["similarity_score"], reverse=True)


def count_resorts(status: str | None = None) -> int:
    """
    Get count of resorts by status (efficient, no data transfer).

    This is the agent-native way to get summary stats without loading all data.

    Args:
        status: Filter by status (draft, published, archived), or None for all

    Returns:
        Count of resorts
    """
    client = get_supabase_client()

    query = client.table("resorts").select("id", count="exact")

    if status:
        query = query.eq("status", status)

    response = query.execute()
    return response.count or 0


def get_country_coverage_summary() -> dict[str, int]:
    """
    Get resort counts by country (aggregated summary).

    This is the agent-native way to understand coverage without loading all resorts.

    Returns:
        Dict of {country: count} for published resorts
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .select("country")
        .eq("status", "published")
        .execute()
    )

    counts: dict[str, int] = {}
    for r in response.data or []:
        country = r.get("country", "Unknown")
        counts[country] = counts.get(country, 0) + 1

    return counts
