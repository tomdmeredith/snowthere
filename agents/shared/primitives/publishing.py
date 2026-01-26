"""Publishing primitives for content lifecycle management.

These primitives handle the publication status of resorts and trigger
revalidation of static pages. Following Agent Native principles, these
ensure agents have the same publishing capabilities as human editors.
"""

import httpx
from datetime import datetime
from typing import Any

from ..config import settings
from ..supabase_client import get_supabase_client
from .system import log_reasoning
from .alerts import alert_pipeline_error


# =============================================================================
# PUBLICATION STATUS OPERATIONS
# =============================================================================


def publish_resort(
    resort_id: str,
    task_id: str | None = None,
    trigger_revalidation: bool = True,
) -> dict:
    """
    Publish a resort (set status to 'published').

    Args:
        resort_id: UUID of the resort
        task_id: Optional task ID for audit logging
        trigger_revalidation: Whether to trigger Vercel ISR revalidation

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .update({
            "status": "published",
            "updated_at": datetime.utcnow().isoformat(),
            "last_refreshed": datetime.utcnow().isoformat(),
        })
        .eq("id", resort_id)
        .execute()
    )

    resort = response.data[0] if response.data else {}

    # Log the action
    if task_id and resort:
        log_reasoning(
            task_id=task_id,
            agent_name="publisher",
            action="publish_resort",
            reasoning=f"Published resort {resort.get('name', resort_id)}",
            metadata={"resort_id": resort_id, "status": "published"},
        )

    # Trigger revalidation
    if trigger_revalidation and resort:
        revalidate_resort_page(resort["slug"], resort["country"])

    return resort


def unpublish_resort(
    resort_id: str,
    task_id: str | None = None,
    trigger_revalidation: bool = True,
) -> dict:
    """
    Unpublish a resort (set status to 'draft').

    Args:
        resort_id: UUID of the resort
        task_id: Optional task ID for audit logging
        trigger_revalidation: Whether to trigger Vercel ISR revalidation

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .update({
            "status": "draft",
            "updated_at": datetime.utcnow().isoformat(),
        })
        .eq("id", resort_id)
        .execute()
    )

    resort = response.data[0] if response.data else {}

    # Log the action
    if task_id and resort:
        log_reasoning(
            task_id=task_id,
            agent_name="publisher",
            action="unpublish_resort",
            reasoning=f"Unpublished resort {resort.get('name', resort_id)} (moved to draft)",
            metadata={"resort_id": resort_id, "status": "draft"},
        )

    # Trigger revalidation to remove from live site
    if trigger_revalidation and resort:
        revalidate_resort_page(resort["slug"], resort["country"])

    return resort


def archive_resort(
    resort_id: str,
    task_id: str | None = None,
    reason: str | None = None,
) -> dict:
    """
    Archive a resort (soft delete, preserves data).

    Args:
        resort_id: UUID of the resort
        task_id: Optional task ID for audit logging
        reason: Optional reason for archiving

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .update({
            "status": "archived",
            "updated_at": datetime.utcnow().isoformat(),
        })
        .eq("id", resort_id)
        .execute()
    )

    resort = response.data[0] if response.data else {}

    # Log the action
    if task_id and resort:
        log_reasoning(
            task_id=task_id,
            agent_name="publisher",
            action="archive_resort",
            reasoning=f"Archived resort {resort.get('name', resort_id)}. Reason: {reason or 'Not specified'}",
            metadata={"resort_id": resort_id, "status": "archived", "reason": reason},
        )

    return resort


def restore_resort(
    resort_id: str,
    to_status: str = "draft",
    task_id: str | None = None,
) -> dict:
    """
    Restore an archived resort.

    Args:
        resort_id: UUID of the resort
        to_status: Status to restore to ('draft' or 'published')
        task_id: Optional task ID for audit logging

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    if to_status not in ("draft", "published"):
        to_status = "draft"

    response = (
        client.table("resorts")
        .update({
            "status": to_status,
            "updated_at": datetime.utcnow().isoformat(),
        })
        .eq("id", resort_id)
        .eq("status", "archived")  # Only restore if currently archived
        .execute()
    )

    resort = response.data[0] if response.data else {}

    # Log the action
    if task_id and resort:
        log_reasoning(
            task_id=task_id,
            agent_name="publisher",
            action="restore_resort",
            reasoning=f"Restored resort {resort.get('name', resort_id)} to {to_status}",
            metadata={"resort_id": resort_id, "status": to_status},
        )

    return resort


# =============================================================================
# PAGE REVALIDATION
# =============================================================================


def revalidate_resort_page(slug: str, country: str) -> dict[str, Any]:
    """
    Trigger Vercel ISR revalidation for a resort page.

    This ensures the static page is regenerated with fresh content.

    Args:
        slug: Resort URL slug
        country: Country name (used in URL path)

    Returns:
        Revalidation result
    """
    # Construct the page path
    country_slug = country.lower().replace(" ", "-")
    path = f"/resorts/{country_slug}/{slug}"

    return revalidate_page(path)


def revalidate_page(path: str) -> dict[str, Any]:
    """
    Trigger Vercel ISR revalidation for any page.

    Args:
        path: Page path to revalidate (e.g., '/resorts/usa/park-city')

    Returns:
        Revalidation result with status
    """
    # Get Vercel revalidation settings
    vercel_url = getattr(settings, "vercel_url", None)
    revalidate_token = getattr(settings, "vercel_revalidate_token", None)

    if not vercel_url:
        return {
            "success": False,
            "error": "VERCEL_URL not configured - skipping revalidation",
            "path": path,
        }

    if not revalidate_token:
        return {
            "success": False,
            "error": "VERCEL_REVALIDATE_TOKEN not configured - skipping revalidation",
            "path": path,
        }

    # Ensure path starts with /
    if not path.startswith("/"):
        path = "/" + path

    # Construct revalidation URL
    revalidate_url = f"{vercel_url.rstrip('/')}/api/revalidate"

    try:
        with httpx.Client(timeout=30.0) as client:
            # Send JSON body (endpoint expects body, not query params)
            response = client.post(
                revalidate_url,
                json={"secret": revalidate_token, "path": path},
                headers={"Content-Type": "application/json"},
            )

            if response.status_code == 200:
                return {
                    "success": True,
                    "path": path,
                    "revalidated": True,
                }
            else:
                return {
                    "success": False,
                    "path": path,
                    "error": f"Revalidation failed: {response.status_code}",
                    "response": response.text[:500],
                }

    except Exception as e:
        # Send alert for revalidation failure
        alert_pipeline_error(
            error_type="RevalidationFailed",
            error_message=f"Failed to revalidate {path}: {str(e)}",
        )
        return {
            "success": False,
            "path": path,
            "error": str(e),
        }


def revalidate_multiple_pages(paths: list[str]) -> list[dict[str, Any]]:
    """
    Trigger revalidation for multiple pages.

    Args:
        paths: List of page paths to revalidate

    Returns:
        List of revalidation results
    """
    results = []
    for path in paths:
        result = revalidate_page(path)
        results.append(result)
    return results


# =============================================================================
# BULK PUBLISHING OPERATIONS
# =============================================================================


def publish_multiple_resorts(
    resort_ids: list[str],
    task_id: str | None = None,
) -> dict[str, Any]:
    """
    Publish multiple resorts at once.

    Args:
        resort_ids: List of resort UUIDs
        task_id: Optional task ID for audit logging

    Returns:
        Summary of results
    """
    results = {
        "published": [],
        "failed": [],
        "revalidated": [],
    }

    for resort_id in resort_ids:
        try:
            resort = publish_resort(
                resort_id,
                task_id=task_id,
                trigger_revalidation=False,  # We'll batch revalidate
            )
            if resort:
                results["published"].append(resort_id)
                # Queue for batch revalidation
                if resort.get("slug") and resort.get("country"):
                    revalidate_result = revalidate_resort_page(
                        resort["slug"],
                        resort["country"],
                    )
                    if revalidate_result.get("success"):
                        results["revalidated"].append(resort_id)
            else:
                results["failed"].append(resort_id)
        except Exception as e:
            results["failed"].append({"resort_id": resort_id, "error": str(e)})

    return results


def get_publish_candidates(
    min_confidence: float = 0.7,
    limit: int = 10,
) -> list[dict]:
    """
    Get draft resorts that are ready to publish.

    Uses confidence score and content completeness checks.

    Args:
        min_confidence: Minimum confidence score required
        limit: Maximum number of candidates to return

    Returns:
        List of resorts ready for publishing
    """
    client = get_supabase_client()

    # Get draft resorts with content
    response = (
        client.table("resorts")
        .select(
            """
            *,
            content:resort_content(
                quick_take,
                faqs,
                seo_meta
            ),
            metrics:resort_family_metrics(
                family_overall_score
            )
            """
        )
        .eq("status", "draft")
        .not_.is_("content", "null")
        .limit(limit * 2)  # Get extra to filter
        .execute()
    )

    candidates = []
    for resort in response.data or []:
        content = resort.get("content")
        if not content:
            continue

        # Check content completeness
        has_quick_take = bool(content.get("quick_take"))
        has_faqs = bool(content.get("faqs"))
        has_seo = bool(content.get("seo_meta"))

        if has_quick_take and has_faqs and has_seo:
            candidates.append(resort)

        if len(candidates) >= limit:
            break

    return candidates


# =============================================================================
# CONTENT FRESHNESS
# =============================================================================


def get_stale_resorts(days_threshold: int = 30, limit: int = 20) -> list[dict]:
    """
    Get resorts that haven't been refreshed recently.

    Args:
        days_threshold: Number of days after which content is considered stale
        limit: Maximum number of results

    Returns:
        List of stale resort records
    """
    client = get_supabase_client()

    cutoff_date = datetime.utcnow()
    # Calculate cutoff (simplistic - could use PostgreSQL date math)

    response = (
        client.table("resorts")
        .select("*")
        .eq("status", "published")
        .order("last_refreshed", desc=False, nullsfirst=True)
        .limit(limit)
        .execute()
    )

    return response.data or []


def mark_resort_refreshed(resort_id: str) -> dict:
    """
    Update the last_refreshed timestamp for a resort.

    Args:
        resort_id: UUID of the resort

    Returns:
        Updated resort record
    """
    client = get_supabase_client()

    response = (
        client.table("resorts")
        .update({
            "last_refreshed": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat(),
        })
        .eq("id", resort_id)
        .execute()
    )

    return response.data[0] if response.data else {}
