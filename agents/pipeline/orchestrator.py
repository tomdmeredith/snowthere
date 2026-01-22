"""Daily pipeline orchestrator - the main entry point for autonomous operation.

This is what Railway cron calls daily. It:
1. Checks budget availability
2. Optionally runs discovery to find new resort opportunities
3. Generates system context (what exists, what's stale, what's discovered)
4. Selects work items from multiple sources (discovery, quality, stale, queue)
5. Runs the full pipeline for each resort
6. Compiles and sends a daily digest

Design Decision (MCP vs Direct Code):
We chose direct Python + Claude API over MCP because:
- MCP is designed for interactive Claude Code sessions
- Autonomous cron jobs don't need the MCP protocol overhead
- Direct code is simpler, faster, and easier to debug
- We keep MCP server as optional CLI tool for manual intervention

Work Item Selection Strategy:
- 30% from discovery_candidates (high priority discoveries)
- 20% from quality fixes (audit issues) - when QualityAgent is integrated
- 30% from stale resorts (refresh)
- 20% from manual queue

This module is the "brain" that decides WHAT to do.
The runner.py module handles HOW to do each individual resort.
"""

import asyncio
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from shared.config import settings
from shared.primitives import (
    check_budget,
    get_daily_spend,
    get_queue_stats,
    get_stale_resorts,
    list_queue,
    log_reasoning,
    log_cost,
    alert_pipeline_summary,
)
from shared.supabase_client import get_supabase_client

from .decision_maker import pick_resorts_to_research, generate_context
from .runner import run_resort_pipeline


# =============================================================================
# Work Item Selection from Multiple Sources
# =============================================================================


def get_discovery_candidates(limit: int = 5) -> list[dict[str, Any]]:
    """Get high-priority candidates from discovery_candidates table.

    Returns resorts that have been identified through keyword research,
    gap analysis, trending topics, or exploration discovery.

    Args:
        limit: Maximum candidates to return

    Returns:
        List of resort dicts with name, country, reasoning, source
    """
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_candidates")\
            .select("*")\
            .eq("status", "pending")\
            .order("opportunity_score", desc=True)\
            .order("priority_rank", desc=True)\
            .limit(limit)\
            .execute()

        candidates = []
        for row in result.data:
            candidates.append({
                "name": row["resort_name"],
                "country": row["country"],
                "region": row.get("region"),
                "reasoning": row.get("reasoning", "High opportunity score from discovery"),
                "source": "discovery",
                "opportunity_score": row.get("opportunity_score", 0.0),
                "discovery_source": row.get("discovery_source"),
                "candidate_id": row["id"],
            })

        return candidates

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="get_discovery_candidates_error",
            reasoning=f"Failed to get discovery candidates: {e}",
            metadata={"error": str(e)},
        )
        return []


def get_stale_work_items(limit: int = 5) -> list[dict[str, Any]]:
    """Get stale resorts that need content refresh.

    Args:
        limit: Maximum items to return

    Returns:
        List of resort dicts needing refresh
    """
    try:
        stale = get_stale_resorts(days_threshold=30, limit=limit)

        items = []
        for resort in stale:
            # Use `or` to coerce None to fallback (dict.get returns None if key exists with None value)
            items.append({
                "name": resort.get("name") or "Unknown",
                "country": resort.get("country") or "Unknown",
                "region": resort.get("region") or "",
                "reasoning": f"Content stale - last refreshed {resort.get('days_since_refresh', 30)}+ days ago",
                "source": "stale_refresh",
                "resort_id": resort.get("id"),
            })

        return items

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="get_stale_items_error",
            reasoning=f"Failed to get stale items: {e}",
            metadata={"error": str(e)},
        )
        return []


def get_queue_work_items(limit: int = 5) -> list[dict[str, Any]]:
    """Get manually queued tasks.

    Args:
        limit: Maximum items to return

    Returns:
        List of resort dicts from manual queue
    """
    try:
        queue = list_queue(status="pending", limit=limit)

        items = []
        for task in queue:
            # Extract resort info from task payload
            # Use `or` to coerce None to fallback (dict.get returns None if key exists with None value)
            payload = task.get("payload") or {}
            items.append({
                "name": payload.get("resort_name") or task.get("resort_name") or "Unknown",
                "country": payload.get("country") or task.get("country") or "Unknown",
                "reasoning": f"Manually queued: {task.get('task_type', 'research')}",
                "source": "manual_queue",
                "task_id": task.get("id"),
            })

        return items

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="get_queue_items_error",
            reasoning=f"Failed to get queue items: {e}",
            metadata={"error": str(e)},
        )
        return []


def get_quality_improvement_items(limit: int = 5, max_attempts: int = 5) -> list[dict[str, Any]]:
    """Get resorts queued for quality improvement.

    These are resorts that were published with the publish-first model
    but had concerns from the approval panel.

    Args:
        limit: Maximum items to return
        max_attempts: Skip items that have been tried this many times

    Returns:
        List of resort dicts needing quality improvement
    """
    try:
        # Query the content_queue for quality_improvement tasks
        supabase = get_supabase_client()

        result = supabase.table("content_queue")\
            .select("*, resorts(name, country)")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "pending")\
            .lt("attempts", max_attempts)\
            .order("priority", desc=True)\
            .order("created_at", desc=False)\
            .limit(limit)\
            .execute()

        items = []
        for task in result.data:
            metadata = task.get("metadata", {})
            issues = metadata.get("issues", [])
            priority = task.get("priority", 5)
            attempts = task.get("attempts", 0)

            # Get resort info from join or metadata fallback
            resort_info = task.get("resorts", {}) or {}
            resort_name = resort_info.get("name") or metadata.get("resort_name", "Unknown")
            country = resort_info.get("country") or metadata.get("country", "Unknown")

            priority_label = "high" if priority >= 7 else "medium" if priority >= 4 else "low"
            attempts_info = f" (attempt {attempts + 1})" if attempts > 0 else ""

            items.append({
                "name": resort_name,
                "country": country,
                "reasoning": f"Quality improvement ({priority_label}){attempts_info}: {issues[0] if issues else 'Issues identified'}",
                "source": "quality_improvement",
                "task_id": task.get("id"),
                "resort_id": task.get("resort_id"),
                "issues": issues,
                "priority": priority,
                "attempts": attempts,
            })

        return items

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="get_quality_items_error",
            reasoning=f"Failed to get quality improvement items: {e}",
            metadata={"error": str(e)},
        )
        return []


def escalate_stuck_quality_items(max_attempts: int = 5) -> dict[str, Any]:
    """Escalate quality items that have hit max attempts to needs_review status.

    This prevents quality items from being silently skipped forever.
    Items marked as needs_review should be manually reviewed.

    Args:
        max_attempts: Items with this many or more attempts get escalated

    Returns:
        Summary of escalated items
    """
    try:
        supabase = get_supabase_client()

        # Find items that have hit max attempts
        result = supabase.table("content_queue")\
            .select("id, resort_id, metadata")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "pending")\
            .gte("attempts", max_attempts)\
            .execute()

        if not result.data:
            return {"escalated": 0, "items": []}

        escalated = []
        for task in result.data:
            # Update status to needs_review
            supabase.table("content_queue")\
                .update({
                    "status": "needs_review",
                    "metadata": {
                        **task.get("metadata", {}),
                        "escalated_at": datetime.utcnow().isoformat(),
                        "escalation_reason": f"Reached {max_attempts} attempts without resolution",
                    },
                })\
                .eq("id", task["id"])\
                .execute()

            escalated.append({
                "task_id": task["id"],
                "resort_id": task.get("resort_id"),
            })

            log_reasoning(
                task_id=task["id"],
                agent_name="orchestrator",
                action="quality_item_escalated",
                reasoning=f"Quality item escalated to needs_review after {max_attempts} attempts",
                metadata={"task_id": task["id"], "resort_id": task.get("resort_id")},
            )

        return {"escalated": len(escalated), "items": escalated}

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="escalation_error",
            reasoning=f"Failed to escalate stuck quality items: {e}",
            metadata={"error": str(e)},
        )
        return {"escalated": 0, "error": str(e)}


def get_quality_metrics() -> dict[str, Any]:
    """Get current quality queue metrics for the daily digest.

    Returns:
        Dict with counts of pending, stuck, needs_review, and resolved items
    """
    try:
        supabase = get_supabase_client()

        # Count pending quality items
        pending_result = supabase.table("content_queue")\
            .select("id", count="exact")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "pending")\
            .execute()

        # Count items with 2+ attempts (struggling)
        struggling_result = supabase.table("content_queue")\
            .select("id", count="exact")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "pending")\
            .gte("attempts", 2)\
            .execute()

        # Count items needing review
        review_result = supabase.table("content_queue")\
            .select("id", count="exact")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "needs_review")\
            .execute()

        # Count resolved today
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        resolved_result = supabase.table("content_queue")\
            .select("id", count="exact")\
            .eq("task_type", "quality_improvement")\
            .eq("status", "completed")\
            .gte("completed_at", today_start.isoformat())\
            .execute()

        return {
            "pending": pending_result.count or 0,
            "struggling": struggling_result.count or 0,  # 2+ attempts
            "needs_review": review_result.count or 0,
            "resolved_today": resolved_result.count or 0,
        }

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="quality_metrics_error",
            reasoning=f"Failed to get quality metrics: {e}",
            metadata={"error": str(e)},
        )
        return {"error": str(e)}


def get_work_items_mixed(
    max_items: int = 4,
    discovery_pct: float = 0.30,
    quality_pct: float = 0.20,
    stale_pct: float = 0.30,
    queue_pct: float = 0.20,
) -> list[dict[str, Any]]:
    """Get balanced work items from multiple sources.

    This is the primary work selection function for the daily pipeline.
    It balances between:
    - Discovery candidates (new opportunities)
    - Quality fixes (issues found by audit)
    - Stale content (needs refresh)
    - Manual queue (explicitly requested)

    Args:
        max_items: Total items to return
        discovery_pct: Percentage from discovery candidates
        quality_pct: Percentage from quality issues (future)
        stale_pct: Percentage from stale content
        queue_pct: Percentage from manual queue

    Returns:
        List of work items with source attribution
    """
    # Calculate counts per source (minimum 1 if percentage > 0)
    discovery_count = max(1, int(max_items * discovery_pct)) if discovery_pct > 0 else 0
    quality_count = max(1, int(max_items * quality_pct)) if quality_pct > 0 else 0
    stale_count = max(1, int(max_items * stale_pct)) if stale_pct > 0 else 0
    queue_count = max(1, int(max_items * queue_pct)) if queue_pct > 0 else 0

    items = []
    sources_used = {}

    # 1. Discovery candidates (highest priority for new content)
    if discovery_count > 0:
        discovery_items = get_discovery_candidates(limit=discovery_count)
        items.extend(discovery_items)
        sources_used["discovery"] = len(discovery_items)

    # 2. Quality improvement items (from publish-first model)
    # These are resorts that were published but had approval panel concerns
    if quality_count > 0:
        quality_items = get_quality_improvement_items(limit=quality_count)
        items.extend(quality_items)
        sources_used["quality"] = len(quality_items)
    else:
        sources_used["quality"] = 0

    # 3. Stale content refresh
    if stale_count > 0:
        stale_items = get_stale_work_items(limit=stale_count)
        items.extend(stale_items)
        sources_used["stale"] = len(stale_items)

    # 4. Manual queue
    if queue_count > 0:
        queue_items = get_queue_work_items(limit=queue_count)
        items.extend(queue_items)
        sources_used["queue"] = len(queue_items)

    # Deduplicate by resort name (keep first occurrence = higher priority source)
    seen = set()
    unique_items = []
    for item in items:
        # Skip None items and handle None values in dict with `or` pattern
        if item is None:
            continue

        name = item.get("name") or ""
        country = item.get("country") or ""

        key = (name.lower(), country.lower())
        if key not in seen and name:
            seen.add(key)
            unique_items.append(item)

    # Trim to max_items
    final_items = unique_items[:max_items]

    log_reasoning(
        task_id=None,
        agent_name="orchestrator",
        action="work_items_selected",
        reasoning=f"Selected {len(final_items)} work items from mixed sources",
        metadata={
            "sources": sources_used,
            "total_before_dedup": len(items),
            "final_count": len(final_items),
        },
    )

    return final_items


def mark_discovery_candidate_queued(candidate_id: str) -> bool:
    """Mark a discovery candidate as queued for processing.

    Args:
        candidate_id: UUID of the candidate

    Returns:
        Success boolean
    """
    try:
        supabase = get_supabase_client()

        supabase.table("discovery_candidates")\
            .update({
                "status": "queued",
                "queued_at": datetime.utcnow().isoformat(),
            })\
            .eq("id", candidate_id)\
            .execute()

        return True

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="mark_candidate_queued_error",
            reasoning=f"Failed to mark candidate as queued: {e}",
            metadata={"candidate_id": candidate_id, "error": str(e)},
        )
        return False


def mark_discovery_candidate_processed(
    candidate_id: str,
    status: str = "researched",
) -> bool:
    """Mark a discovery candidate as processed.

    Args:
        candidate_id: UUID of the candidate
        status: New status (researched, published, rejected)

    Returns:
        Success boolean
    """
    try:
        supabase = get_supabase_client()

        supabase.table("discovery_candidates")\
            .update({
                "status": status,
                "processed_at": datetime.utcnow().isoformat(),
            })\
            .eq("id", candidate_id)\
            .execute()

        return True

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="mark_candidate_processed_error",
            reasoning=f"Failed to mark candidate as processed: {e}",
            metadata={"candidate_id": candidate_id, "error": str(e)},
        )
        return False


# =============================================================================
# Discovery Integration
# =============================================================================


def run_discovery_if_needed(
    force: bool = False,
    days_since_last: int = 7,
) -> dict[str, Any]:
    """Run discovery agent if it hasn't run recently.

    Args:
        force: Force run even if ran recently
        days_since_last: Days threshold for auto-run

    Returns:
        Discovery result or skip message
    """
    # Check when discovery last ran
    try:
        supabase = get_supabase_client()

        result = supabase.table("discovery_runs")\
            .select("started_at")\
            .eq("status", "completed")\
            .order("started_at", desc=True)\
            .limit(1)\
            .execute()

        if result.data and not force:
            last_run = datetime.fromisoformat(result.data[0]["started_at"].replace("Z", "+00:00"))
            days_ago = (datetime.utcnow().replace(tzinfo=last_run.tzinfo) - last_run).days

            if days_ago < days_since_last:
                return {
                    "skipped": True,
                    "reason": f"Discovery ran {days_ago} days ago (threshold: {days_since_last})",
                    "last_run": last_run.isoformat(),
                }

    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="discovery_check_error",
            reasoning=f"Error checking discovery history: {e}",
            metadata={"error": str(e)},
        )
        # Continue with discovery if check fails

    # Run discovery
    try:
        from agent_layer.agents.discovery_agent import run_full_discovery_agent

        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="discovery_start",
            reasoning="Starting full discovery run",
            metadata={"force": force},
        )

        # Run discovery asynchronously
        result = asyncio.run(run_full_discovery_agent(max_candidates=20))

        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="discovery_complete",
            reasoning=f"Discovery complete: {result.get('candidates_saved', 0)} candidates saved",
            metadata=result,
        )

        return result

    except ImportError:
        return {
            "skipped": True,
            "reason": "Discovery agent not available (import failed)",
        }
    except Exception as e:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="discovery_error",
            reasoning=f"Discovery failed: {e}",
            metadata={"error": str(e)},
        )
        return {
            "error": True,
            "reason": str(e),
        }


# =============================================================================
# Main Pipeline
# =============================================================================


def run_daily_pipeline(
    max_resorts: int = 4,
    dry_run: bool = False,
    use_mixed_selection: bool = False,
    run_discovery: bool = False,
    force_discovery: bool = False,
) -> dict[str, Any]:
    """Run the daily content generation pipeline.

    This is the main entry point called by Railway cron.

    Args:
        max_resorts: Maximum resorts to process today (default 4)
        dry_run: If True, log what would happen but don't execute
        use_mixed_selection: If True, use balanced selection from multiple sources
                            (discovery, stale, queue) instead of Claude-based selection
        run_discovery: If True, optionally run discovery agent before selection
        force_discovery: If True, force discovery run even if ran recently

    Returns:
        Daily digest with results for all processed resorts
    """
    run_id = str(uuid4())
    started_at = datetime.utcnow()

    digest = {
        "run_id": run_id,
        "started_at": started_at.isoformat(),
        "max_resorts": max_resorts,
        "dry_run": dry_run,
        "use_mixed_selection": use_mixed_selection,
        "status": "started",
        "resorts_processed": [],
        "discovery_result": None,
        "summary": {},
    }

    log_reasoning(
        task_id=None,  # Orchestrator-level logging, not tied to queue task
        agent_name="orchestrator",
        action="daily_pipeline_start",
        reasoning=f"Starting daily pipeline. Max resorts: {max_resorts}. Dry run: {dry_run}. Mixed selection: {use_mixed_selection}",
        metadata={"run_id": run_id, "max_resorts": max_resorts, "use_mixed_selection": use_mixed_selection},
    )

    # =========================================================================
    # STEP 1: Check Budget
    # =========================================================================
    daily_spend = get_daily_spend()
    remaining_budget = settings.daily_budget_limit - daily_spend

    log_reasoning(
        task_id=None,
        agent_name="orchestrator",
        action="budget_check",
        reasoning=f"Daily spend: ${daily_spend:.2f}. Remaining: ${remaining_budget:.2f}",
        metadata={"run_id": run_id, "daily_spend": daily_spend, "remaining": remaining_budget},
    )

    # =========================================================================
    # STEP 1.1: Escalate Stuck Quality Items
    # =========================================================================
    escalation_result = escalate_stuck_quality_items(max_attempts=5)
    if escalation_result.get("escalated", 0) > 0:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="quality_items_escalated",
            reasoning=f"Escalated {escalation_result['escalated']} stuck quality items to needs_review",
            metadata={"run_id": run_id, "escalated": escalation_result},
        )

    # Need at least $1.50 for one resort
    if remaining_budget < 1.5:
        digest["status"] = "budget_exhausted"
        digest["summary"] = {
            "message": f"Budget exhausted. Spent ${daily_spend:.2f} of ${settings.daily_budget_limit:.2f}",
            "resorts_completed": 0,
        }

        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="pipeline_stopped",
            reasoning="Daily budget exhausted - stopping pipeline",
            metadata={"run_id": run_id},
        )

        return digest

    # =========================================================================
    # STEP 1.5: Optionally Run Discovery
    # =========================================================================
    if run_discovery:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="discovery_check",
            reasoning=f"Checking if discovery should run (force={force_discovery})",
            metadata={"run_id": run_id},
        )

        discovery_result = run_discovery_if_needed(force=force_discovery)
        digest["discovery_result"] = discovery_result

        if discovery_result.get("error"):
            log_reasoning(
                task_id=None,
                agent_name="orchestrator",
                action="discovery_failed",
                reasoning=f"Discovery failed: {discovery_result.get('reason')}",
                metadata={"run_id": run_id},
            )
        elif discovery_result.get("skipped"):
            log_reasoning(
                task_id=None,
                agent_name="orchestrator",
                action="discovery_skipped",
                reasoning=discovery_result.get("reason"),
                metadata={"run_id": run_id},
            )

    # =========================================================================
    # STEP 2: Generate Context (for Claude-based selection)
    # =========================================================================
    if not use_mixed_selection:
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="generating_context",
            reasoning="Gathering system context for resort selection",
            metadata={"run_id": run_id},
        )

        context = generate_context()

    # =========================================================================
    # STEP 3: Select Resorts (Claude-based OR Mixed-source)
    # =========================================================================
    if use_mixed_selection:
        # Use balanced selection from multiple sources
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="mixed_selection",
            reasoning=f"Using mixed selection strategy for up to {max_resorts} resorts",
            metadata={"run_id": run_id},
        )

        resorts_to_process = get_work_items_mixed(max_items=max_resorts)

        # Mark discovery candidates as queued
        for resort in resorts_to_process:
            if resort.get("source") == "discovery" and resort.get("candidate_id"):
                mark_discovery_candidate_queued(resort["candidate_id"])

        selection_reasoning = f"Mixed selection: {len(resorts_to_process)} items from discovery/stale/queue sources"

    else:
        # Use Claude-based intelligent selection
        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="picking_resorts",
            reasoning=f"Asking Claude to select up to {max_resorts} resorts to research",
            metadata={"run_id": run_id},
        )

        selection = pick_resorts_to_research(max_resorts=max_resorts, task_id=None)

        if selection.get("error"):
            digest["status"] = "selection_failed"
            digest["summary"] = {
                "message": "Failed to select resorts",
                "error": selection.get("overall_reasoning", "Unknown error"),
            }
            return digest

        resorts_to_process = selection.get("resorts", [])
        selection_reasoning = selection.get("overall_reasoning", "No reasoning provided")

        # Log the cost of the selection call (~$0.01 for Sonnet)
        log_cost("anthropic", 0.01, None, {"run_id": run_id, "stage": "resort_selection"})

    log_reasoning(
        task_id=None,
        agent_name="orchestrator",
        action="resorts_selected",
        reasoning=selection_reasoning,
        metadata={"run_id": run_id, "resorts": resorts_to_process, "count": len(resorts_to_process)},
    )

    if dry_run:
        digest["status"] = "dry_run_complete"
        digest["summary"] = {
            "message": "Dry run complete - no resorts processed",
            "would_process": resorts_to_process,
            "selection_reasoning": selection_reasoning,
        }
        return digest

    # =========================================================================
    # STEP 4: Process Each Resort
    # =========================================================================
    results = []
    published_count = 0
    draft_count = 0
    failed_count = 0

    for i, resort_info in enumerate(resorts_to_process):
        resort_name = resort_info.get("name")
        country = resort_info.get("country")
        source = resort_info.get("source", "claude_selection")
        candidate_id = resort_info.get("candidate_id")  # For discovery candidates

        log_reasoning(
            task_id=None,
            agent_name="orchestrator",
            action="processing_resort",
            reasoning=f"Processing resort {i+1}/{len(resorts_to_process)}: {resort_name}, {country} (source: {source})",
            metadata={
                "run_id": run_id,
                "resort": resort_name,
                "country": country,
                "index": i,
                "source": source,
                "candidate_id": candidate_id,
            },
        )

        # Check budget before each resort
        current_spend = get_daily_spend()
        if current_spend + 1.5 > settings.daily_budget_limit:
            log_reasoning(
                task_id=None,
                agent_name="orchestrator",
                action="budget_limit_reached",
                reasoning=f"Budget limit reached mid-pipeline. Processed {i} of {len(resorts_to_process)} resorts.",
                metadata={"run_id": run_id},
            )
            break

        # Run the pipeline for this resort
        try:
            result = run_resort_pipeline(
                resort_name=resort_name,
                country=country,
                task_id=None,  # No queue task - run_id tracked in metadata
                auto_publish=True,
            )

            # Determine status for discovery candidate update
            status = result.get("status")
            if status == "published":
                published_count += 1
                candidate_status = "published"
            elif status == "draft":
                draft_count += 1
                candidate_status = "researched"
            elif status in ("failed", "budget_exceeded"):
                failed_count += 1
                candidate_status = "rejected"
            else:
                candidate_status = "researched"

            # Update discovery candidate status if applicable
            if candidate_id:
                mark_discovery_candidate_processed(candidate_id, status=candidate_status)
                log_reasoning(
                    task_id=None,
                    agent_name="orchestrator",
                    action="candidate_status_updated",
                    reasoning=f"Updated discovery candidate {candidate_id} to status: {candidate_status}",
                    metadata={"candidate_id": candidate_id, "status": candidate_status},
                )

            results.append({
                "resort": resort_name,
                "country": country,
                "status": status,
                "confidence": result.get("confidence"),
                "resort_id": result.get("resort_id"),
                "reasoning": resort_info.get("reasoning"),
                "source": source,
                "candidate_id": candidate_id,
            })

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name="orchestrator",
                action="resort_error",
                reasoning=f"Error processing {resort_name}: {e}",
                metadata={"run_id": run_id, "resort": resort_name, "error": str(e)},
            )

            # Mark discovery candidate as rejected on error
            if candidate_id:
                mark_discovery_candidate_processed(candidate_id, status="rejected")

            results.append({
                "resort": resort_name,
                "country": country,
                "status": "error",
                "error": str(e),
                "source": source,
                "candidate_id": candidate_id,
            })
            failed_count += 1

        # Small delay between resorts to avoid rate limits
        if i < len(resorts_to_process) - 1:
            time.sleep(2)

    # =========================================================================
    # STEP 5: Compile Digest
    # =========================================================================
    completed_at = datetime.utcnow()
    duration = (completed_at - started_at).total_seconds()
    final_spend = get_daily_spend()

    # Determine actual status based on outcomes
    # This is CRITICAL - don't report "completed" when everything failed
    total_attempted = len(results)
    if total_attempted == 0:
        status = "no_resorts"
    elif failed_count == total_attempted:
        status = "all_failed"
    elif failed_count > 0:
        status = "partial_failure"
    elif published_count == 0 and draft_count == 0:
        status = "no_content"
    else:
        status = "completed"

    digest["status"] = status
    digest["completed_at"] = completed_at.isoformat()
    digest["duration_seconds"] = duration
    digest["resorts_processed"] = results

    # Count sources
    source_counts = {}
    for r in results:
        src = r.get("source", "unknown")
        source_counts[src] = source_counts.get(src, 0) + 1

    # Get quality queue metrics
    quality_metrics = get_quality_metrics()

    digest["summary"] = {
        "total_attempted": total_attempted,
        "published": published_count,
        "drafts": draft_count,
        "failed": failed_count,
        "daily_spend": f"${final_spend:.2f}",
        "duration": f"{duration:.1f}s",
        "selection_method": "mixed" if use_mixed_selection else "claude",
        "source_breakdown": source_counts,
        "selection_reasoning": selection_reasoning,
        "quality_queue": quality_metrics,
    }

    # Log with appropriate severity
    log_action = "pipeline_complete" if status == "completed" else f"pipeline_{status}"
    log_reasoning(
        task_id=None,
        agent_name="orchestrator",
        action=log_action,
        reasoning=f"Daily pipeline {status}. Published: {published_count}, Drafts: {draft_count}, Failed: {failed_count}. Total spend: ${final_spend:.2f}",
        metadata={**digest["summary"], "run_id": run_id, "status": status},
    )

    # Send Slack summary alert
    alert_pipeline_summary(
        total_processed=total_attempted,
        successful=published_count + draft_count,
        failed=failed_count,
        resorts=[r["resort"] for r in results],
    )

    return digest


def run_single_resort(
    resort_name: str,
    country: str,
    auto_publish: bool = True,
) -> dict[str, Any]:
    """Run pipeline for a single resort (manual trigger).

    Use this when you want to process a specific resort outside
    of the daily cron job.

    Args:
        resort_name: Name of the resort
        country: Country the resort is in
        auto_publish: Whether to auto-publish if confidence is high

    Returns:
        Pipeline result
    """
    run_id = str(uuid4())

    log_reasoning(
        task_id=None,
        agent_name="orchestrator",
        action="manual_trigger",
        reasoning=f"Manual pipeline trigger for {resort_name}, {country}",
        metadata={"run_id": run_id},
    )

    return run_resort_pipeline(
        resort_name=resort_name,
        country=country,
        task_id=None,  # No queue task for manual triggers
        auto_publish=auto_publish,
    )
