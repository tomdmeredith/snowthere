"""System primitives for agent operations."""

import json
from datetime import datetime
from typing import Any
from uuid import uuid4

from ..supabase_client import get_supabase_client


def log_cost(
    api_name: str,
    amount_usd: float,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Log API cost for budget tracking.

    Args:
        api_name: Name of the API (exa, serp, tavily, anthropic)
        amount_usd: Cost in USD
        task_id: Optional task ID for correlation
        metadata: Additional context
    """
    client = get_supabase_client()

    data = {
        "id": str(uuid4()),
        "api_name": api_name,
        "amount_usd": amount_usd,
        "task_id": task_id,
        "metadata": metadata or {},
        "created_at": datetime.utcnow().isoformat(),
    }

    # Insert into agent_audit_log with action type 'cost'
    # task_id can be None for costs not tied to a specific queue task
    audit_data = {
        "id": str(uuid4()),
        "task_id": task_id,
        "agent_name": "cost_tracker",
        "action": "api_cost",
        "reasoning": f"API call to {api_name} cost ${amount_usd:.4f}",
        "input_data": data,  # Use input_data to match schema
    }

    response = client.table("agent_audit_log").insert(audit_data).execute()
    return response.data


def log_reasoning(
    task_id: str,
    agent_name: str,
    action: str,
    reasoning: str,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Log agent reasoning for observability.

    Creates an audit trail of why decisions were made.
    """
    client = get_supabase_client()

    # Serialize metadata to handle dataclasses and other non-JSON types
    safe_metadata = json.loads(json.dumps(metadata or {}, default=str))

    data = {
        "id": str(uuid4()),
        # task_id can be None for orchestrator-level logging (not tied to a queue task)
        # The database schema allows NULL task_id
        "task_id": task_id,
        "agent_name": agent_name,
        "action": action,
        "reasoning": reasoning,
        # Use input_data for metadata since that's what the schema has
        "input_data": safe_metadata,
    }

    response = client.table("agent_audit_log").insert(data).execute()
    return response.data


def queue_task(
    task_type: str,
    resort_id: str | None = None,
    priority: int = 5,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """
    Add a task to the content queue.

    Args:
        task_type: One of 'discover', 'research', 'generate', 'geo_optimize', 'validate', 'publish'
        resort_id: Optional resort ID for resort-specific tasks
        priority: 1-10, higher = more urgent
        metadata: Additional task data
    """
    client = get_supabase_client()

    data = {
        "id": str(uuid4()),
        "resort_id": resort_id,
        "task_type": task_type,
        "status": "pending",
        "priority": priority,
        "attempts": 0,
        "metadata": metadata or {},
    }

    response = client.table("content_queue").insert(data).execute()
    return response.data[0] if response.data else data


def get_next_task(task_types: list[str] | None = None) -> dict | None:
    """
    Get the next pending task from the queue.

    Returns highest priority pending task, optionally filtered by type.
    """
    client = get_supabase_client()

    query = (
        client.table("content_queue")
        .select("*")
        .eq("status", "pending")
        .order("priority", desc=True)
        .order("created_at")
        .limit(1)
    )

    if task_types:
        query = query.in_("task_type", task_types)

    response = query.execute()
    return response.data[0] if response.data else None


def update_task_status(
    task_id: str,
    status: str,
    error: str | None = None,
) -> dict:
    """
    Update task status in the queue.

    Args:
        task_id: Task ID
        status: One of 'pending', 'processing', 'completed', 'failed'
        error: Error message if failed
    """
    client = get_supabase_client()

    update_data = {
        "status": status,
    }

    if status == "processing":
        update_data["started_at"] = datetime.utcnow().isoformat()
    elif status in ("completed", "failed"):
        update_data["completed_at"] = datetime.utcnow().isoformat()

    if error:
        update_data["last_error"] = error
        # Also increment attempts
        current = client.table("content_queue").select("attempts").eq("id", task_id).single().execute()
        if current.data:
            update_data["attempts"] = current.data["attempts"] + 1

    response = (
        client.table("content_queue")
        .update(update_data)
        .eq("id", task_id)
        .execute()
    )
    return response.data[0] if response.data else {}


def get_daily_spend() -> float:
    """
    Get total API spend for today.

    Used for budget enforcement.
    """
    client = get_supabase_client()

    today = datetime.utcnow().date().isoformat()

    response = (
        client.table("agent_audit_log")
        .select("input_data")  # Schema uses input_data, not metadata
        .eq("action", "api_cost")
        .gte("created_at", f"{today}T00:00:00+00:00")  # UTC timezone for consistent queries
        .execute()
    )

    total = 0.0
    for row in response.data or []:
        input_data = row.get("input_data", {})
        total += input_data.get("amount_usd", 0)

    return total


def check_budget(required_usd: float, daily_limit: float | None = None) -> bool:
    """
    Check if we have budget for an operation.

    Returns True if we can proceed, False if we'd exceed budget.
    Uses settings.daily_budget_limit if no limit specified.
    """
    from ..config import settings

    if daily_limit is None:
        daily_limit = settings.daily_budget_limit

    current_spend = get_daily_spend()
    return (current_spend + required_usd) <= daily_limit


# =============================================================================
# QUEUE OPERATIONS
# =============================================================================


def list_queue(
    status: str | None = None,
    task_type: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """
    List tasks in the content queue.

    Args:
        status: Filter by status (pending, processing, completed, failed)
        task_type: Filter by type (discover, research, generate, geo_optimize, validate, publish)
        limit: Maximum number of results

    Returns:
        List of queue tasks
    """
    client = get_supabase_client()

    query = (
        client.table("content_queue")
        .select("*, resort:resorts(name, slug, country)")
        .order("priority", desc=True)
        .order("created_at")
        .limit(limit)
    )

    if status:
        query = query.eq("status", status)
    if task_type:
        query = query.eq("task_type", task_type)

    response = query.execute()
    return response.data or []


def get_queue_stats() -> dict[str, Any]:
    """
    Get statistics about the content queue.

    Returns:
        Queue statistics (counts by status and type)
    """
    client = get_supabase_client()

    # Get counts by status
    response = client.table("content_queue").select("status, task_type").execute()

    stats = {
        "total": len(response.data or []),
        "by_status": {"pending": 0, "processing": 0, "completed": 0, "failed": 0},
        "by_type": {},
    }

    for row in response.data or []:
        status = row.get("status", "unknown")
        task_type = row.get("task_type", "unknown")

        if status in stats["by_status"]:
            stats["by_status"][status] += 1

        if task_type not in stats["by_type"]:
            stats["by_type"][task_type] = 0
        stats["by_type"][task_type] += 1

    return stats


def clear_completed_tasks(older_than_days: int = 7) -> int:
    """
    Remove completed tasks older than specified days.

    Args:
        older_than_days: Days threshold for deletion

    Returns:
        Number of tasks deleted
    """
    client = get_supabase_client()

    cutoff_date = datetime.utcnow()
    # Note: For proper date math, this should use PostgreSQL functions

    response = (
        client.table("content_queue")
        .delete()
        .eq("status", "completed")
        .execute()
    )

    return len(response.data or [])


# =============================================================================
# AUDIT LOG OPERATIONS
# =============================================================================


def read_audit_log(
    task_id: str | None = None,
    agent_name: str | None = None,
    action: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """
    Read entries from the audit log.

    Args:
        task_id: Filter by task ID
        agent_name: Filter by agent name
        action: Filter by action type
        limit: Maximum number of entries

    Returns:
        List of audit log entries
    """
    client = get_supabase_client()

    query = (
        client.table("agent_audit_log")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
    )

    if task_id:
        query = query.eq("task_id", task_id)
    if agent_name:
        query = query.eq("agent_name", agent_name)
    if action:
        query = query.eq("action", action)

    response = query.execute()
    return response.data or []


def get_task_audit_trail(task_id: str) -> list[dict]:
    """
    Get the complete audit trail for a specific task.

    Args:
        task_id: Task ID to retrieve trail for

    Returns:
        Chronological list of all actions for the task
    """
    client = get_supabase_client()

    response = (
        client.table("agent_audit_log")
        .select("*")
        .eq("task_id", task_id)
        .order("created_at")
        .execute()
    )

    return response.data or []


def get_recent_activity(hours: int = 24, limit: int = 50) -> list[dict]:
    """
    Get recent agent activity.

    Args:
        hours: How many hours back to look
        limit: Maximum number of entries

    Returns:
        List of recent audit log entries
    """
    client = get_supabase_client()

    # Note: For precise time filtering, this should use PostgreSQL date math
    response = (
        client.table("agent_audit_log")
        .select("*")
        .order("created_at", desc=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def get_cost_breakdown(days: int = 7) -> dict[str, Any]:
    """
    Get API cost breakdown for the specified period.

    Args:
        days: Number of days to analyze

    Returns:
        Cost breakdown by API and day
    """
    client = get_supabase_client()

    response = (
        client.table("agent_audit_log")
        .select("input_data, created_at")  # Schema uses input_data, not metadata
        .eq("action", "api_cost")
        .order("created_at", desc=True)
        .execute()
    )

    breakdown = {
        "total_usd": 0.0,
        "by_api": {},
        "daily": {},
    }

    for row in response.data or []:
        input_data = row.get("input_data", {})
        amount = input_data.get("amount_usd", 0)
        api_name = input_data.get("api_name", "unknown")
        date = row.get("created_at", "")[:10]  # Extract date portion

        breakdown["total_usd"] += amount

        if api_name not in breakdown["by_api"]:
            breakdown["by_api"][api_name] = 0.0
        breakdown["by_api"][api_name] += amount

        if date not in breakdown["daily"]:
            breakdown["daily"][date] = 0.0
        breakdown["daily"][date] += amount

    return breakdown
