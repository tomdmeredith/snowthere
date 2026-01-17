"""Daily pipeline orchestrator - the main entry point for autonomous operation.

This is what Railway cron calls daily. It:
1. Checks budget availability
2. Generates system context (what exists, what's stale)
3. Asks Claude to pick resorts to research
4. Runs the full pipeline for each resort
5. Compiles and sends a daily digest

Design Decision (MCP vs Direct Code):
We chose direct Python + Claude API over MCP because:
- MCP is designed for interactive Claude Code sessions
- Autonomous cron jobs don't need the MCP protocol overhead
- Direct code is simpler, faster, and easier to debug
- We keep MCP server as optional CLI tool for manual intervention

This module is the "brain" that decides WHAT to do.
The runner.py module handles HOW to do each individual resort.
"""

import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from shared.config import settings
from shared.primitives import (
    check_budget,
    get_daily_spend,
    get_queue_stats,
    log_reasoning,
    log_cost,
)

from .decision_maker import pick_resorts_to_research, generate_context
from .runner import run_resort_pipeline


def run_daily_pipeline(
    max_resorts: int = 4,
    dry_run: bool = False,
) -> dict[str, Any]:
    """Run the daily content generation pipeline.

    This is the main entry point called by Railway cron.

    Args:
        max_resorts: Maximum resorts to process today (default 4)
        dry_run: If True, log what would happen but don't execute

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
        "status": "started",
        "resorts_processed": [],
        "summary": {},
    }

    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="daily_pipeline_start",
        reasoning=f"Starting daily pipeline. Max resorts: {max_resorts}. Dry run: {dry_run}",
        metadata={"run_id": run_id, "max_resorts": max_resorts},
    )

    # =========================================================================
    # STEP 1: Check Budget
    # =========================================================================
    daily_spend = get_daily_spend()
    remaining_budget = settings.daily_budget_limit - daily_spend

    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="budget_check",
        reasoning=f"Daily spend: ${daily_spend:.2f}. Remaining: ${remaining_budget:.2f}",
        metadata={"daily_spend": daily_spend, "remaining": remaining_budget},
    )

    # Need at least $1.50 for one resort
    if remaining_budget < 1.5:
        digest["status"] = "budget_exhausted"
        digest["summary"] = {
            "message": f"Budget exhausted. Spent ${daily_spend:.2f} of ${settings.daily_budget_limit:.2f}",
            "resorts_completed": 0,
        }

        log_reasoning(
            task_id=run_id,
            agent_name="orchestrator",
            action="pipeline_stopped",
            reasoning="Daily budget exhausted - stopping pipeline",
        )

        return digest

    # =========================================================================
    # STEP 2: Generate Context
    # =========================================================================
    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="generating_context",
        reasoning="Gathering system context for resort selection",
    )

    context = generate_context()

    # =========================================================================
    # STEP 3: Ask Claude to Pick Resorts
    # =========================================================================
    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="picking_resorts",
        reasoning=f"Asking Claude to select up to {max_resorts} resorts to research",
    )

    selection = pick_resorts_to_research(max_resorts=max_resorts, task_id=run_id)

    if selection.get("error"):
        digest["status"] = "selection_failed"
        digest["summary"] = {
            "message": "Failed to select resorts",
            "error": selection.get("overall_reasoning", "Unknown error"),
        }
        return digest

    resorts_to_process = selection.get("resorts", [])

    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="resorts_selected",
        reasoning=selection.get("overall_reasoning", "No reasoning provided"),
        metadata={"resorts": resorts_to_process},
    )

    # Log the cost of the selection call (~$0.01 for Sonnet)
    log_cost("anthropic", 0.01, run_id, {"stage": "resort_selection"})

    if dry_run:
        digest["status"] = "dry_run_complete"
        digest["summary"] = {
            "message": "Dry run complete - no resorts processed",
            "would_process": resorts_to_process,
            "overall_reasoning": selection.get("overall_reasoning"),
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

        log_reasoning(
            task_id=run_id,
            agent_name="orchestrator",
            action="processing_resort",
            reasoning=f"Processing resort {i+1}/{len(resorts_to_process)}: {resort_name}, {country}",
            metadata={"resort": resort_name, "country": country, "index": i},
        )

        # Check budget before each resort
        current_spend = get_daily_spend()
        if current_spend + 1.5 > settings.daily_budget_limit:
            log_reasoning(
                task_id=run_id,
                agent_name="orchestrator",
                action="budget_limit_reached",
                reasoning=f"Budget limit reached mid-pipeline. Processed {i} of {len(resorts_to_process)} resorts.",
            )
            break

        # Run the pipeline for this resort
        try:
            result = run_resort_pipeline(
                resort_name=resort_name,
                country=country,
                task_id=f"{run_id}-{i}",
                auto_publish=True,
            )

            results.append({
                "resort": resort_name,
                "country": country,
                "status": result.get("status"),
                "confidence": result.get("confidence"),
                "resort_id": result.get("resort_id"),
                "reasoning": resort_info.get("reasoning"),
            })

            # Track outcomes
            status = result.get("status")
            if status == "published":
                published_count += 1
            elif status == "draft":
                draft_count += 1
            elif status in ("failed", "budget_exceeded"):
                failed_count += 1

        except Exception as e:
            log_reasoning(
                task_id=run_id,
                agent_name="orchestrator",
                action="resort_error",
                reasoning=f"Error processing {resort_name}: {e}",
                metadata={"resort": resort_name, "error": str(e)},
            )

            results.append({
                "resort": resort_name,
                "country": country,
                "status": "error",
                "error": str(e),
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

    digest["status"] = "completed"
    digest["completed_at"] = completed_at.isoformat()
    digest["duration_seconds"] = duration
    digest["resorts_processed"] = results
    digest["summary"] = {
        "total_attempted": len(resorts_to_process),
        "published": published_count,
        "drafts": draft_count,
        "failed": failed_count,
        "daily_spend": f"${final_spend:.2f}",
        "duration": f"{duration:.1f}s",
        "overall_strategy": selection.get("overall_reasoning"),
    }

    log_reasoning(
        task_id=run_id,
        agent_name="orchestrator",
        action="pipeline_complete",
        reasoning=f"Daily pipeline complete. Published: {published_count}, Drafts: {draft_count}, Failed: {failed_count}. Total spend: ${final_spend:.2f}",
        metadata=digest["summary"],
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
    task_id = str(uuid4())

    log_reasoning(
        task_id=task_id,
        agent_name="orchestrator",
        action="manual_trigger",
        reasoning=f"Manual pipeline trigger for {resort_name}, {country}",
    )

    return run_resort_pipeline(
        resort_name=resort_name,
        country=country,
        task_id=task_id,
        auto_publish=auto_publish,
    )
