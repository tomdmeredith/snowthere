"""Pipeline runner - executes the full content generation pipeline for a resort.

This is the core execution logic that:
1. Researches a resort using multiple APIs
2. Generates content in instagram_mom voice
3. Optimizes for GEO (tables, FAQs, schema)
4. Stores in database
5. Optionally publishes based on confidence

Design Decisions:
- Uses existing primitives directly (no MCP overhead)
- Calculates confidence score from research quality
- Logs all reasoning for observability
- Handles errors gracefully with retry logic
"""

import time
from datetime import datetime
from typing import Any
from uuid import uuid4

from shared.primitives import (
    # Research
    search_resort_info,
    # Content
    write_section,
    generate_faq,
    generate_seo_meta,
    # Database
    create_resort,
    get_resort_by_slug,
    update_resort_content,
    update_resort_costs,
    update_resort_family_metrics,
    update_resort_calendar,
    # Publishing
    publish_resort,
    # System
    log_cost,
    log_reasoning,
    queue_task,
    update_task_status,
    check_budget,
)

from .decision_maker import decide_to_publish, handle_error


def slugify(name: str) -> str:
    """Convert resort name to URL slug."""
    return name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def calculate_confidence(research_data: dict[str, Any]) -> float:
    """Calculate confidence score from research quality.

    Factors:
    - Number of sources found
    - Presence of official resort data
    - Price data completeness
    - Review data quality

    Returns: 0.0 - 1.0
    """
    score = 0.0

    # Source count (max 0.3)
    sources = research_data.get("sources", [])
    source_score = min(len(sources) / 10, 0.3)
    score += source_score

    # Official data present (0.2)
    if research_data.get("official_site_data"):
        score += 0.2

    # Price data completeness (max 0.2)
    costs = research_data.get("costs", {})
    price_fields = ["lift_adult_daily", "lodging_budget_nightly", "lodging_mid_nightly"]
    price_completeness = sum(1 for f in price_fields if costs.get(f)) / len(price_fields)
    score += price_completeness * 0.2

    # Family metrics completeness (max 0.15)
    metrics = research_data.get("family_metrics", {})
    metric_fields = ["family_overall_score", "childcare_min_age", "ski_school_min_age"]
    metric_completeness = sum(1 for f in metric_fields if metrics.get(f)) / len(metric_fields)
    score += metric_completeness * 0.15

    # Review data (max 0.15)
    reviews = research_data.get("reviews", [])
    if len(reviews) >= 5:
        score += 0.15
    elif len(reviews) >= 2:
        score += 0.08

    return min(score, 1.0)


def run_resort_pipeline(
    resort_name: str,
    country: str,
    task_id: str | None = None,
    auto_publish: bool = True,
) -> dict[str, Any]:
    """Run the full pipeline for a single resort.

    Steps:
    1. Check budget
    2. Research resort
    3. Generate content
    4. Store in database
    5. Decide whether to publish

    Args:
        resort_name: Name of the resort
        country: Country the resort is in
        task_id: Optional task ID for audit logging
        auto_publish: Whether to auto-publish if confidence is high

    Returns:
        Pipeline result with status, confidence, and any errors
    """
    task_id = task_id or str(uuid4())
    result = {
        "task_id": task_id,
        "resort_name": resort_name,
        "country": country,
        "status": "started",
        "started_at": datetime.utcnow().isoformat(),
        "stages": {},
    }

    # Log start
    log_reasoning(
        task_id=task_id,
        agent_name="pipeline_runner",
        action="start_pipeline",
        reasoning=f"Starting content generation for {resort_name}, {country}",
        metadata={"resort": resort_name, "country": country},
    )

    # =========================================================================
    # STAGE 1: Budget Check
    # =========================================================================
    if not check_budget(1.5):  # ~$1.50 per resort
        result["status"] = "budget_exceeded"
        result["error"] = "Daily budget exceeded"
        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="budget_check_failed",
            reasoning="Stopping: daily budget would be exceeded",
        )
        return result

    result["stages"]["budget_check"] = "passed"

    # =========================================================================
    # STAGE 2: Research
    # =========================================================================
    try:
        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="start_research",
            reasoning=f"Researching {resort_name} using Exa, SerpAPI, and Tavily",
        )

        research_data = search_resort_info(resort_name, country)

        # Log research cost (~$0.20 for 3 API calls)
        log_cost("research_apis", 0.20, task_id, {"stage": "research"})

        # Calculate confidence
        confidence = calculate_confidence(research_data)
        result["confidence"] = confidence

        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="research_complete",
            reasoning=f"Research complete. Confidence: {confidence:.2f}. Sources: {len(research_data.get('sources', []))}",
            metadata={"confidence": confidence, "source_count": len(research_data.get("sources", []))},
        )

        result["stages"]["research"] = {"status": "complete", "confidence": confidence}

    except Exception as e:
        error_decision = handle_error(e, resort_name, "research", task_id)
        result["status"] = "failed"
        result["error"] = f"Research failed: {e}"
        result["stages"]["research"] = {"status": "failed", "error": str(e)}

        if error_decision.get("action") == "retry":
            time.sleep(error_decision.get("retry_delay_seconds", 60))
            return run_resort_pipeline(resort_name, country, task_id, auto_publish)

        return result

    # =========================================================================
    # STAGE 3: Content Generation
    # =========================================================================
    try:
        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="start_content_generation",
            reasoning="Generating content sections in instagram_mom voice",
        )

        content = {}

        # Generate each section
        sections = [
            "quick_take",
            "getting_there",
            "where_to_stay",
            "lift_tickets",
            "on_mountain",
            "off_mountain",
            "parent_reviews_summary",
        ]

        for section in sections:
            content[section] = write_section(
                section_name=section,
                resort_name=resort_name,
                context=research_data,
                voice_profile="instagram_mom",
            )

        # Generate FAQs
        content["faqs"] = generate_faq(resort_name, research_data, num_questions=6)

        # Generate SEO meta
        content["seo_meta"] = generate_seo_meta(
            resort_name=resort_name,
            country=country,
            quick_take=content["quick_take"],
        )

        # Log content generation cost (~$0.80 for Claude API)
        log_cost("anthropic", 0.80, task_id, {"stage": "content_generation"})

        result["stages"]["content"] = {"status": "complete", "sections": len(sections)}

        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="content_complete",
            reasoning=f"Generated {len(sections)} content sections + FAQs + SEO meta",
        )

    except Exception as e:
        error_decision = handle_error(e, resort_name, "content_generation", task_id)
        result["status"] = "failed"
        result["error"] = f"Content generation failed: {e}"
        result["stages"]["content"] = {"status": "failed", "error": str(e)}
        return result

    # =========================================================================
    # STAGE 4: Database Storage
    # =========================================================================
    try:
        log_reasoning(
            task_id=task_id,
            agent_name="pipeline_runner",
            action="start_storage",
            reasoning="Storing resort data in Supabase",
        )

        slug = slugify(resort_name)

        # Check if resort exists
        existing = get_resort_by_slug(slug, country)

        if existing:
            resort_id = existing["id"]
            log_reasoning(
                task_id=task_id,
                agent_name="pipeline_runner",
                action="updating_existing",
                reasoning=f"Found existing resort (ID: {resort_id}), updating content",
            )
        else:
            # Create new resort
            resort = create_resort(
                name=resort_name,
                country=country,
                region=research_data.get("region", ""),
                slug=slug,
            )
            resort_id = resort["id"]
            log_reasoning(
                task_id=task_id,
                agent_name="pipeline_runner",
                action="created_new",
                reasoning=f"Created new resort entry (ID: {resort_id})",
            )

        # Update content
        update_resort_content(resort_id, content)

        # Update costs if available
        if research_data.get("costs"):
            update_resort_costs(resort_id, research_data["costs"])

        # Update family metrics if available
        if research_data.get("family_metrics"):
            update_resort_family_metrics(resort_id, research_data["family_metrics"])

        # Update calendar if available
        if research_data.get("calendar"):
            for month_data in research_data["calendar"]:
                update_resort_calendar(resort_id, month_data["month"], month_data)

        result["resort_id"] = resort_id
        result["stages"]["storage"] = {"status": "complete", "resort_id": resort_id}

    except Exception as e:
        result["status"] = "failed"
        result["error"] = f"Storage failed: {e}"
        result["stages"]["storage"] = {"status": "failed", "error": str(e)}
        return result

    # =========================================================================
    # STAGE 5: Publication Decision
    # =========================================================================
    if auto_publish:
        try:
            # Get content summary for quality check
            content_summary = f"""
Resort: {resort_name}, {country}
Quick Take: {content.get('quick_take', '')[:500]}
Sections: {', '.join(sections)}
FAQs: {len(content.get('faqs', []))} questions
            """

            decision = decide_to_publish(
                resort_name=resort_name,
                content_summary=content_summary,
                confidence_score=result.get("confidence", 0),
                task_id=task_id,
            )

            if decision.get("should_publish"):
                publish_resort(resort_id, task_id)
                result["status"] = "published"
                result["stages"]["publish"] = {
                    "status": "published",
                    "reasoning": decision.get("reasoning"),
                }
            else:
                result["status"] = "draft"
                result["stages"]["publish"] = {
                    "status": "held_for_review",
                    "reasoning": decision.get("reasoning"),
                    "concerns": decision.get("concerns", []),
                }

        except Exception as e:
            result["status"] = "draft"
            result["stages"]["publish"] = {"status": "skipped", "error": str(e)}
    else:
        result["status"] = "draft"
        result["stages"]["publish"] = {"status": "skipped", "reason": "auto_publish=False"}

    # =========================================================================
    # Complete
    # =========================================================================
    result["completed_at"] = datetime.utcnow().isoformat()

    log_reasoning(
        task_id=task_id,
        agent_name="pipeline_runner",
        action="pipeline_complete",
        reasoning=f"Pipeline complete. Status: {result['status']}. Confidence: {result.get('confidence', 'N/A')}",
        metadata=result,
    )

    return result
