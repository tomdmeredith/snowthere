"""Supabase client for database operations."""

from functools import lru_cache

from supabase import Client, create_client

from .config import settings


@lru_cache
def get_supabase_client() -> Client:
    """Get cached Supabase client instance."""
    return create_client(
        settings.supabase_url,
        settings.supabase_service_key,
    )


# Type aliases for common operations
def get_resort_by_slug(slug: str, country: str) -> dict | None:
    """Fetch a resort by slug and country."""
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .select("*")
        .eq("slug", slug)
        .eq("country", country)
        .single()
        .execute()
    )
    return response.data if response.data else None


def get_resort_with_details(resort_id: str) -> dict | None:
    """Fetch a resort with all related data."""
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
    return response.data if response.data else None


def upsert_resort_content(resort_id: str, content: dict) -> dict:
    """Insert or update resort content."""
    client = get_supabase_client()
    data = {"resort_id": resort_id, **content}
    response = client.table("resort_content").upsert(data).execute()
    return response.data


def upsert_resort_metrics(resort_id: str, metrics: dict) -> dict:
    """Insert or update resort family metrics."""
    client = get_supabase_client()
    data = {"resort_id": resort_id, **metrics}
    response = client.table("resort_family_metrics").upsert(data).execute()
    return response.data


def upsert_resort_costs(resort_id: str, costs: dict) -> dict:
    """Insert or update resort costs."""
    client = get_supabase_client()
    data = {"resort_id": resort_id, **costs}
    response = client.table("resort_costs").upsert(data).execute()
    return response.data


def log_agent_audit(
    task_id: str,
    agent_name: str,
    action: str,
    reasoning: str | None = None,
    metadata: dict | None = None,
) -> dict:
    """Log an agent action to the audit trail."""
    client = get_supabase_client()
    data = {
        "task_id": task_id,
        "agent_name": agent_name,
        "action": action,
        "reasoning": reasoning,
        "metadata": metadata or {},
    }
    response = client.table("agent_audit_log").insert(data).execute()
    return response.data


def update_resort_status(resort_id: str, status: str) -> dict:
    """Update resort publication status."""
    client = get_supabase_client()
    response = (
        client.table("resorts")
        .update({"status": status})
        .eq("id", resort_id)
        .execute()
    )
    return response.data
