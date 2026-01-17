"""Decision maker - Claude API for intelligent choices.

Uses Claude to make decisions about:
- Which resorts to research
- Whether to publish content
- How to handle errors
- Priority ordering

This is the "brain" of the autonomous system.
"""

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
)


def get_claude_client() -> anthropic.Anthropic:
    """Get Anthropic client."""
    return anthropic.Anthropic(api_key=settings.anthropic_api_key)


def generate_context() -> str:
    """Generate context about current system state.

    This is injected into decision prompts so Claude knows
    what exists and what needs attention.
    """
    # Get current state
    try:
        published = list_resorts(status="published", limit=500)
        drafts = list_resorts(status="draft", limit=100)
        stale = get_stale_resorts(days_threshold=30, limit=20)
        queue_stats = get_queue_stats()
        daily_spend = get_daily_spend()
    except Exception as e:
        # If DB not connected, return minimal context
        return f"[Database not connected: {e}. Starting fresh.]"

    # Build context
    context = f"""# Snowthere System Context

## What Exists
- Published resorts: {len(published)}
- Draft resorts: {len(drafts)}
- Countries covered: {len(set(r.get('country', '') for r in published))}

## Top Countries by Coverage
"""

    # Count by country
    country_counts = {}
    for r in published:
        c = r.get('country', 'Unknown')
        country_counts[c] = country_counts.get(c, 0) + 1

    for country, count in sorted(country_counts.items(), key=lambda x: -x[1])[:10]:
        context += f"- {country}: {count} resorts\n"

    context += f"""
## Content Needing Attention
- Stale (>30 days old): {len(stale)} resorts
- Queue pending: {queue_stats.get('by_status', {}).get('pending', 0)} tasks

## Budget Status
- Daily spend so far: ${daily_spend:.2f}
- Daily limit: $5.00
- Remaining: ${5.0 - daily_spend:.2f}

## Priority Guidance
1. High-demand resorts families are searching for
2. Value skiing destinations (Europe, often cheaper than US)
3. Stale content needing refresh
4. Geographic diversity (not just US/Alps)

## Voice Reminder
All content should be in 'instagram_mom' voice - encouraging, practical,
like a helpful friend who's done all the research. Make international
skiing feel doable for families.
"""

    return context


def pick_resorts_to_research(
    max_resorts: int = 4,
    task_id: str | None = None,
) -> dict[str, Any]:
    """Ask Claude to pick resorts to research today.

    Returns:
        {
            "resorts": [
                {"name": "Zermatt", "country": "Switzerland", "reasoning": "..."},
                ...
            ],
            "overall_reasoning": "..."
        }
    """
    client = get_claude_client()
    context = generate_context()

    prompt = f"""You are the autonomous content strategist for Snowthere, a family ski resort directory.

Your task: Pick 1-{max_resorts} resorts to research and generate content for today.

{context}

## Selection Criteria (in order of importance)
1. **Search demand** - Resorts families are actively searching for
2. **Value angle** - International resorts that offer better value than US (our unique angle)
3. **Content gaps** - Major resorts we haven't covered
4. **Freshness** - Stale content needing update
5. **Diversity** - Geographic spread, not just the same countries

## Constraints
- Budget allows ~3-4 new resorts today (at ~$1.20/resort)
- Prefer quality over quantity
- Don't duplicate what we already have unless it's stale

## Output Format
Return a JSON object with:
- "resorts": array of {{name, country, reasoning}} objects
- "overall_reasoning": 1-2 sentences on today's strategy

Think step by step about what would be most valuable, then respond with ONLY the JSON.
"""

    response = client.messages.create(
        model="claude-sonnet-4-20250514",  # Fast, capable, cheaper
        max_tokens=1024,
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

        result = json.loads(response_text.strip())
    except json.JSONDecodeError:
        # Fallback if parsing fails
        result = {
            "resorts": [],
            "overall_reasoning": f"Failed to parse response: {response_text[:200]}",
            "error": True,
        }

    # Log the decision
    if task_id:
        log_reasoning(
            task_id=task_id,
            agent_name="decision_maker",
            action="pick_resorts",
            reasoning=result.get("overall_reasoning", "No reasoning provided"),
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

    return result
