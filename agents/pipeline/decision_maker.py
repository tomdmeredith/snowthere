"""Decision maker - Claude API for intelligent choices.

Uses Claude to make decisions about:
- Which resorts to research
- Whether to publish content
- How to handle errors
- Priority ordering

This is the "brain" of the autonomous system.

Agent-Native Design:
- Uses SUMMARY context instead of listing all 3000 resorts
- Two-phase validation: Claude suggests, then database validates
- Atomic primitives for existence checking
"""

import asyncio
import json
from typing import Any

import anthropic

from shared.config import settings
from shared.primitives import (
    list_resorts,
    get_stale_resorts,
    list_queue,
    get_queue_stats,
    get_daily_spend,
    log_reasoning,
    count_resorts,
    get_country_coverage_summary,
    alert_pipeline_error,
)
from shared.primitives.intelligence import validate_resort_selection


def get_claude_client() -> anthropic.Anthropic:
    """Get Anthropic client."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def get_discovery_candidates_count() -> tuple[int, list[dict]]:
    """Get count and top discovery candidates.

    Returns:
        Tuple of (total_count, top_candidates)
    """
    try:
        from shared.supabase_client import get_supabase_client
        supabase = get_supabase_client()

        # Get count
        result = supabase.table("discovery_candidates")\
            .select("id", count="exact")\
            .eq("status", "pending")\
            .execute()

        total = result.count if result.count else 0

        # Get top candidates
        top_result = supabase.table("discovery_candidates")\
            .select("resort_name, country, opportunity_score, discovery_source")\
            .eq("status", "pending")\
            .order("opportunity_score", desc=True)\
            .limit(5)\
            .execute()

        top_candidates = top_result.data if top_result.data else []

        return total, top_candidates

    except Exception:
        return 0, []


def generate_context() -> str:
    """Generate SUMMARY context about current system state.

    Agent-Native Design:
    - Uses efficient count/summary primitives instead of loading all data
    - Does NOT list all 3000 resorts (that would waste tokens)
    - Validation happens AFTER Claude suggests candidates

    This is injected into decision prompts so Claude knows
    what exists and what needs attention.
    """
    # Get current state using efficient primitives
    try:
        # Use count primitives instead of loading all data
        published_count = count_resorts(status="published")
        draft_count = count_resorts(status="draft")
        country_coverage = get_country_coverage_summary()

        # These still load some data, but limited
        stale = get_stale_resorts(days_threshold=30, limit=20)
        queue_stats = get_queue_stats()
        daily_spend = get_daily_spend()
        discovery_count, top_discoveries = get_discovery_candidates_count()
    except Exception as e:
        # If DB not connected, return minimal context
        return f"[Database not connected: {e}. Starting fresh.]"

    # Build SUMMARY context (no full resort list)
    context = f"""# Snowthere System Context

## Coverage Summary
- Published resorts: {published_count}
- Draft resorts: {draft_count}
- Countries covered: {len(country_coverage)}

## Top Countries by Coverage
"""

    # Show top 10 countries only
    for country, count in sorted(country_coverage.items(), key=lambda x: -x[1])[:10]:
        context += f"- {country}: {count} resorts\n"

    context += f"""
## Content Needing Attention
- Stale (>30 days old): {len(stale)} resorts
- Queue pending: {queue_stats.get('by_status', {}).get('pending', 0)} tasks
- Discovery candidates: {discovery_count} pending
"""

    # Add top discoveries if available
    if top_discoveries:
        context += "\n## Top Discovery Candidates (by opportunity score)\n"
        for d in top_discoveries:
            score = d.get('opportunity_score', 0)
            source = d.get('discovery_source', 'unknown')
            context += f"- {d.get('resort_name')}, {d.get('country')} (score: {score:.2f}, source: {source})\n"

    context += f"""
## Budget Status
- Daily spend so far: ${daily_spend:.2f}
- Daily limit: $5.00
- Remaining: ${5.0 - daily_spend:.2f}

## Priority Guidance
1. **Discovery candidates** - High-scoring resorts from search demand analysis
2. High-demand resorts families are searching for
3. Value skiing destinations (Europe, often cheaper than US)
4. Stale content needing refresh
5. Geographic diversity (not just US/Alps)

## Important: Validation Process
You don't need to memorize existing resorts - just suggest good candidates.
Each resort you select will be validated against our database AFTER your selection.
Duplicates will be automatically filtered out.

## Voice Reminder
All content should be in 'snowthere_guide' voice - smart, witty, efficient,
like a well-traveled friend who respects your time. Make international
skiing feel doable for families.
"""

    return context


def pick_resorts_to_research(
    max_resorts: int = 4,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Ask Claude to pick resorts to research today.

    Agent-Native Two-Phase Approach:
    1. Claude suggests candidates (without seeing full 3000-resort list)
    2. Database validates each candidate against existing resorts
    3. Duplicates are filtered out automatically

    Returns:
        {
            "resorts": [
                {"name": "Zermatt", "country": "Switzerland", "reasoning": "..."},
                ...
            ],
            "overall_reasoning": "...",
            "filtered_count": int  # How many duplicates were filtered
        }
    """
    client = get_claude_client()
    context = generate_context()

    # Phase 1: Get Claude's suggestions (request 2x to account for filtering)
    suggestions_needed = max_resorts * 2

    prompt = f"""You are the autonomous content strategist for Snowthere, a family ski resort directory.

Your task: Suggest {suggestions_needed} resorts to potentially research and generate content for.

{context}

## Selection Criteria (in order of importance)
1. **Discovery candidates** - If listed above, prioritize these high-scoring opportunities
2. **Search demand** - Resorts families are actively searching for
3. **Value angle** - International resorts that offer better value than US (our unique angle)
4. **Content gaps** - Major resorts we haven't covered
5. **Freshness** - Stale content needing update
6. **Diversity** - Geographic spread, not just the same countries

## Important Notes
- Suggest {suggestions_needed} resorts (we'll validate and filter to {max_resorts})
- Each suggestion will be validated against our database
- Duplicates will be automatically filtered - suggest freely
- Include both well-known AND hidden gem resorts

## Output Format
Return a JSON object with:
- "resorts": array of {{name, country, reasoning}} objects
- "overall_reasoning": 1-2 sentences on today's strategy

Think step by step about what would be most valuable, then respond with ONLY the JSON.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",  # Fast, capable, cheaper
        max_tokens=1500,
        messages=[{"role": "user", "content": prompt}],
    )

    # Parse response
    response_text = response.content[0].text

    # Try to extract JSON
    try:
        # Handle if wrapped in markdown code blocks
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        claude_result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        # Fallback if parsing fails
        return {
            "resorts": [],
            "overall_reasoning": f"Failed to parse response: {response_text[:200]}",
            "error": True,
            "filtered_count": 0,
        }

    suggestions = claude_result.get("resorts", [])

    # Phase 2: Validate each suggestion against database
    if suggestions:
        validated = asyncio.run(validate_resort_selection(suggestions))

        # Filter to valid (non-existing) resorts
        valid_resorts = []
        skipped_resorts = []

        for i, v in enumerate(validated):
            original = suggestions[i] if i < len(suggestions) else {}
            if not v.should_skip:
                valid_resorts.append({
                    "name": v.name,
                    "country": v.country,
                    "reasoning": original.get("reasoning", "Selected by Claude, validated as new"),
                })
            else:
                skipped_resorts.append({
                    "name": v.name,
                    "country": v.country,
                    "skip_reason": v.reason,
                })

        # Log filtered duplicates
        if task_id and skipped_resorts:
            log_reasoning(
                task_id=task_id,
                agent_name="decision_maker",
                action="filtered_duplicates",
                reasoning=f"Filtered {len(skipped_resorts)} existing/duplicate resorts",
                metadata={"skipped": skipped_resorts},
            )

        result = {
            "resorts": valid_resorts[:max_resorts],
            "overall_reasoning": claude_result.get("overall_reasoning", "No reasoning provided"),
            "filtered_count": len(skipped_resorts),
        }
    else:
        result = {
            "resorts": [],
            "overall_reasoning": claude_result.get("overall_reasoning", "No resorts suggested"),
            "filtered_count": 0,
        }

    # Log the final decision
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="decision_maker",
            action="pick_resorts",
            reasoning=f"{result['overall_reasoning']} (Filtered {result['filtered_count']} duplicates)",
            metadata={"resorts": result.get("resorts", [])},
        )

    return result


def decide_to_publish(
    resort_name: str,
    content_summary: str,
    confidence_score: float,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Ask Claude whether to publish content.

    For borderline cases (0.6-0.8 confidence), uses Claude to decide.
    """
    # High confidence - auto approve
    if confidence_score >= 0.8:
        return {
            "should_publish": True,
            "reasoning": f"High confidence ({confidence_score:.2f}) - auto-approved",
        }

    # Low confidence - auto reject
    if confidence_score < 0.6:
        return {
            "should_publish": False,
            "reasoning": f"Low confidence ({confidence_score:.2f}) - needs human review",
            "needs_review": True,
        }

    # Borderline - ask Claude
    client = get_claude_client()

    prompt = f"""You are the quality gatekeeper for Snowthere, a family ski resort directory.

## Task
Decide whether to publish this content or flag it for human review.

## Content Summary
Resort: {resort_name}
Confidence Score: {confidence_score:.2f} (borderline - 0.6-0.8 range)

Content Preview:
{content_summary[:2000]}

## Quality Criteria
- Accuracy: Do the facts seem reliable? Any obvious errors?
- Voice: Does it sound like a helpful mom friend, not generic AI?
- Completeness: Are key sections present (prices, terrain, family info)?
- Value: Would this help a family plan their trip?

## Decision Rules
- Publish if quality is good despite borderline confidence
- Flag for review if there are specific concerns
- Never publish if safety info (childcare ages, terrain) seems wrong

Respond with JSON:
{{
    "should_publish": true/false,
    "reasoning": "1-2 sentences explaining decision",
    "concerns": ["list", "of", "specific", "concerns"] // empty if none
}}
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=512,
        messages=[{"role": "user", "content": prompt}],
    )

    response_text = response.content[0].text

    try:
        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        result = {
            "should_publish": False,
            "reasoning": "Failed to parse quality check response",
            "needs_review": True,
        }

    # Log the decision
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="decision_maker",
            action="publish_decision",
            reasoning=result.get("reasoning", ""),
            metadata={
                "resort": resort_name,
                "confidence": confidence_score,
                "decision": result.get("should_publish"),
            },
        )

    return result


def handle_error(
    error: Exception,
    resort_name: str,
    stage: str,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Ask Claude how to handle an error.

    Returns recommended action: retry, skip, or alert_human.
    """
    client = get_claude_client()

    prompt = f"""You are the error handler for Snowthere's content pipeline.

## Error Details
Resort: {resort_name}
Stage: {stage}
Error: {type(error).__name__}: {str(error)[:500]}

## Available Actions
1. "retry" - Try again (good for transient errors like rate limits)
2. "skip" - Skip this resort (good for data quality issues)
3. "alert_human" - Stop and alert (good for system issues)

## Error Categories
- API rate limits → retry after delay
- No data found → skip (resort may be too small/obscure)
- Database errors → alert_human
- Content generation failure → retry once, then skip
- Budget exceeded → alert_human

Respond with JSON:
{{
    "action": "retry" | "skip" | "alert_human",
    "reasoning": "brief explanation",
    "retry_delay_seconds": 60 // only if action is retry
}}
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=256,
            messages=[{"role": "user", "content": prompt}],
        )

        response_text = response.content[0].text

        if "```json" in response_text:
            response_text = response_text.split("```json")[1].split("```")[0]
        elif "```" in response_text:
            response_text = response_text.split("```")[1].split("```")[0]

        result = json.loads(response_text.strip())

    except Exception:
        # If error handling itself fails, be conservative
        result = {
            "action": "skip",
            "reasoning": "Error handler failed - skipping to be safe",
        }

    # Log the decision
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="decision_maker",
            action="handle_error",
            reasoning=result.get("reasoning", ""),
            metadata={
                "resort": resort_name,
                "stage": stage,
                "error": str(error)[:200],
                "decision": result.get("action"),
            },
        )

    # Send Slack alert if action requires human attention
    if result.get("action") == "alert_human":
        alert_pipeline_error(
            error_type=f"{stage} failure",
            error_message=f"{type(error).__name__}: {str(error)[:300]}",
            resort_name=resort_name,
            task_id=task_id,
        )

    return result
