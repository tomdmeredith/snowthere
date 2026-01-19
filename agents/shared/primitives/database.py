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
    """
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

    Args:
        resort_id: UUID of the resort
        costs: Cost fields to update (lift_adult_daily, lodging_budget_nightly, etc.)

    Returns:
        Updated costs record
    """
    client = get_supabase_client()

    data = {"resort_id": resort_id, **costs}
    response = client.table("resort_costs").upsert(data).execute()
    return response.data[0] if response.data else data


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

    Args:
        resort_id: UUID of the resort
        metrics: Metrics to update (family_overall_score, childcare_min_age, etc.)

    Returns:
        Updated metrics record
    """
    client = get_supabase_client()

    data = {"resort_id": resort_id, **metrics}
    response = client.table("resort_family_metrics").upsert(data).execute()
    return response.data[0] if response.data else data


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
