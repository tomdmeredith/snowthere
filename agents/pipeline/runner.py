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

import asyncio
import sys
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

# Agent Layer - Memory for learning from past runs
from agent_layer.memory import AgentMemory

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
    update_resort,
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
    # Trail map
    get_trail_map,
    get_difficulty_breakdown,
    # Image generation (3-tier fallback)
    generate_resort_image_set,
    ImageType,
    # UGC Photos (Google Places)
    fetch_and_store_ugc_photos,
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
    # Generate a run_id for tracking but don't use as task_id (foreign key constraint)
    run_id = task_id or str(uuid4())
    result = {
        "run_id": run_id,
        "resort_name": resort_name,
        "country": country,
        "status": "started",
        "started_at": datetime.utcnow().isoformat(),
        "stages": {},
    }

    # =========================================================================
    # MEMORY: Initialize and retrieve context from past runs
    # =========================================================================
    memory = AgentMemory(agent_name="pipeline_runner")
    objective = {
        "resort_name": resort_name,
        "country": country,
        "task_type": "full_pipeline",
    }

    # Get context from memory (similar episodes, learned patterns)
    memory_context = asyncio.run(memory.get_context_for_objective(objective))
    similar_episodes = memory_context.get("similar_episodes", [])
    learned_patterns = memory_context.get("learned_patterns", [])

    # Store useful insights from memory for content generation
    memory_insights = {
        "similar_resorts_run": [ep.get("objective", {}).get("resort_name") for ep in similar_episodes],
        "success_rate": sum(1 for ep in similar_episodes if ep.get("success")) / max(len(similar_episodes), 1),
        "patterns": [p.get("description") for p in learned_patterns if p.get("confidence", 0) > 0.7],
    }
    result["memory_context"] = memory_insights

    # Log start with memory context
    log_reasoning(
        task_id=None,  # Not tied to a queue task
        agent_name="pipeline_runner",
        action="start_pipeline",
        reasoning=f"Starting content generation for {resort_name}, {country}. Memory: {len(similar_episodes)} similar runs, {len(learned_patterns)} patterns.",
        metadata={
            "run_id": run_id,
            "resort": resort_name,
            "country": country,
            "memory_context": memory_insights,
        },
    )

    # =========================================================================
    # STAGE 1: Budget Check
    # =========================================================================
    if not check_budget(1.5):  # ~$1.50 per resort
        result["status"] = "budget_exceeded"
        result["error"] = "Daily budget exceeded"
        log_reasoning(
            task_id=None,
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
            task_id=None,
            agent_name="pipeline_runner",
            action="start_research",
            reasoning=f"Researching {resort_name} using Exa, SerpAPI, and Tavily",
        )

        research_data = asyncio.run(search_resort_info(resort_name, country))

        # Log research cost (~$0.20 for 3 API calls)
        log_cost("research_apis", 0.20, None, {"run_id": run_id, "stage": "research"})

        # Calculate confidence
        confidence = calculate_confidence(research_data)
        result["confidence"] = confidence

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="research_complete",
            reasoning=f"Research complete. Confidence: {confidence:.2f}. Sources: {len(research_data.get('sources', []))}",
            metadata={"confidence": confidence, "source_count": len(research_data.get("sources", []))},
        )

        result["stages"]["research"] = {"status": "complete", "confidence": confidence}

    except Exception as e:
        error_decision = handle_error(e, resort_name, "research", None)
        result["status"] = "failed"
        result["error"] = f"Research failed: {e}"
        result["stages"]["research"] = {"status": "failed", "error": str(e)}

        if error_decision.get("action") == "retry":
            time.sleep(error_decision.get("retry_delay_seconds", 60))
            return run_resort_pipeline(resort_name, country, None, auto_publish)

        return result

    # =========================================================================
    # STAGE 2.5: Trail Map Data (OpenStreetMap)
    # =========================================================================
    trail_map_data = None
    try:
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_trail_map",
            reasoning=f"Fetching trail map data from OpenStreetMap for {resort_name}",
        )

        # Get coordinates from research data if available
        latitude = research_data.get("latitude")
        longitude = research_data.get("longitude")

        # Fetch trail map data
        trail_map_result = asyncio.run(get_trail_map(
            resort_name=resort_name,
            country=country,
            latitude=latitude,
            longitude=longitude,
            radius_km=8.0,  # Larger radius for big resorts
        ))

        # Get difficulty breakdown
        difficulty_breakdown = asyncio.run(get_difficulty_breakdown(trail_map_result.pistes))

        # Convert to dict for storage (without full geometry for smaller payload)
        trail_map_data = {
            "quality": trail_map_result.quality.value,
            "piste_count": len(trail_map_result.pistes),
            "lift_count": len(trail_map_result.lifts),
            "center_coords": trail_map_result.center_coords,
            "bbox": trail_map_result.bbox,
            "official_map_url": trail_map_result.official_map_url,
            "osm_attribution": trail_map_result.osm_attribution,
            "confidence": trail_map_result.confidence,
            "difficulty_breakdown": difficulty_breakdown,
            "fetched_at": datetime.utcnow().isoformat(),
        }

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="trail_map_complete",
            reasoning=f"Trail map: {trail_map_result.quality.value} quality, {len(trail_map_result.pistes)} pistes, {len(trail_map_result.lifts)} lifts",
            metadata=trail_map_data,
        )

        result["stages"]["trail_map"] = {
            "status": "complete",
            "quality": trail_map_result.quality.value,
            "piste_count": len(trail_map_result.pistes),
            "lift_count": len(trail_map_result.lifts),
        }

    except Exception as e:
        # Trail map is non-critical - continue without it
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="trail_map_failed",
            reasoning=f"Trail map fetch failed (non-critical): {e}",
        )
        result["stages"]["trail_map"] = {"status": "skipped", "error": str(e)}

    # =========================================================================
    # STAGE 3: Content Generation
    # =========================================================================
    try:
        log_reasoning(
            task_id=None,
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

        # Add resort_name, country, and defaults for template formatting
        # Extract family_score from research if available, otherwise use placeholder
        family_metrics = research_data.get("family_metrics", {})
        family_score = family_metrics.get("family_overall_score", "N/A")

        content_context = {
            "resort_name": resort_name,
            "country": country,
            "family_score": family_score,
            # Trail map data for content generation
            "trail_map": trail_map_data,
            # Memory insights from past runs
            "memory_insights": memory_insights,
            # Flatten research data for template access
            **research_data,
        }

        for section in sections:
            content[section] = asyncio.run(write_section(
                section_name=section,
                context=content_context,
                voice_profile="snowthere_guide",
            ))

        # Generate FAQs
        content["faqs"] = asyncio.run(generate_faq(
            resort_name=resort_name,
            country=country,
            context=content_context,
            num_questions=6,
            voice_profile="snowthere_guide",
        ))

        # Generate SEO meta
        content["seo_meta"] = asyncio.run(generate_seo_meta(
            resort_name=resort_name,
            country=country,
            quick_take=content["quick_take"],
        ))

        # Log content generation cost (~$0.80 for Claude API)
        log_cost("anthropic", 0.80, None, {"run_id": run_id, "stage": "content_generation"})

        result["stages"]["content"] = {"status": "complete", "sections": len(sections)}

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="content_complete",
            reasoning=f"Generated {len(sections)} content sections + FAQs + SEO meta",
        )

    except Exception as e:
        error_decision = handle_error(e, resort_name, "content_generation", None)
        result["status"] = "failed"
        result["error"] = f"Content generation failed: {e}"
        result["stages"]["content"] = {"status": "failed", "error": str(e)}
        return result

    # =========================================================================
    # STAGE 4: Database Storage
    # =========================================================================
    import sys  # For stderr logging

    try:
        log_reasoning(
            task_id=None,
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
                task_id=None,
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
            # CRITICAL: Verify resort was created
            if not resort or "id" not in resort:
                raise ValueError(f"Failed to create resort record for {resort_name} - no ID returned")
            resort_id = resort["id"]
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="created_new",
                reasoning=f"Created new resort entry (ID: {resort_id})",
            )

        # Update content - verify write succeeded
        content_result = update_resort_content(resort_id, content)
        if not content_result:
            raise ValueError(f"Failed to save content for resort {resort_id}")

        # Update costs if available - verify write succeeded
        if research_data.get("costs"):
            costs_result = update_resort_costs(resort_id, research_data["costs"])
            if not costs_result:
                print(f"⚠️  Warning: Failed to save costs for {resort_name}", file=sys.stderr)

        # Update family metrics if available - verify write succeeded
        if research_data.get("family_metrics"):
            metrics_result = update_resort_family_metrics(resort_id, research_data["family_metrics"])
            if not metrics_result:
                print(f"⚠️  Warning: Failed to save family metrics for {resort_name}", file=sys.stderr)

        # Update calendar if available
        if research_data.get("calendar"):
            for month_data in research_data["calendar"]:
                calendar_result = update_resort_calendar(resort_id, month_data["month"], month_data)
                if not calendar_result:
                    print(f"⚠️  Warning: Failed to save calendar month {month_data.get('month')} for {resort_name}", file=sys.stderr)

        # Update trail map data if available
        # NOTE: Disabled until migration 004_trail_map_data.sql is applied to production
        # if trail_map_data:
        #     trail_map_result = update_resort(resort_id, {"trail_map_data": trail_map_data})
        #     if not trail_map_result:
        #         print(f"⚠️  Warning: Failed to save trail map data for {resort_name}", file=sys.stderr)

        result["resort_id"] = resort_id
        result["stages"]["storage"] = {"status": "complete", "resort_id": resort_id}

        print(f"✓ Storage complete for {resort_name} (ID: {resort_id})")

    except Exception as e:
        # CRITICAL: Mark as failed and log clearly to stderr for Railway visibility
        result["status"] = "failed"
        result["error"] = f"Storage failed: {e}"
        result["stages"]["storage"] = {"status": "failed", "error": str(e)}

        # Log to stderr so Railway logs show clear failure
        print(f"❌ STORAGE FAILED for {resort_name}: {e}", file=sys.stderr)

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="storage_failed",
            reasoning=f"Storage failed for {resort_name}: {e}",
            metadata={"error": str(e), "run_id": run_id},
        )

        return result

    # =========================================================================
    # STAGE 4.5: Image Generation (3-tier fallback)
    # =========================================================================
    try:
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_image_generation",
            reasoning=f"Generating hero and atmosphere images for {resort_name}",
        )

        # Generate images with 3-tier fallback (Gemini → Glif → Replicate)
        image_results = asyncio.run(generate_resort_image_set(
            resort_id=resort_id,
            resort_name=resort_name,
            country=country,
            task_id=None,
        ))

        hero_result = image_results.get("hero")
        atmosphere_result = image_results.get("atmosphere")

        # Track results
        images_generated = sum(1 for r in [hero_result, atmosphere_result] if r and r.success)
        total_image_cost = sum(r.cost for r in [hero_result, atmosphere_result] if r and r.success)

        if images_generated > 0:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="image_generation_complete",
                reasoning=f"Generated {images_generated} images for {resort_name}. Cost: ${total_image_cost:.3f}",
                metadata={
                    "hero_success": hero_result.success if hero_result else False,
                    "hero_url": hero_result.url if hero_result and hero_result.success else None,
                    "hero_source": hero_result.source.value if hero_result and hero_result.success else None,
                    "atmosphere_success": atmosphere_result.success if atmosphere_result else False,
                    "atmosphere_url": atmosphere_result.url if atmosphere_result and atmosphere_result.success else None,
                    "total_cost": total_image_cost,
                },
            )

        result["stages"]["images"] = {
            "status": "complete" if images_generated > 0 else "partial",
            "hero_generated": hero_result.success if hero_result else False,
            "atmosphere_generated": atmosphere_result.success if atmosphere_result else False,
            "images_count": images_generated,
            "cost": total_image_cost,
        }

        print(f"✓ Images: {images_generated}/2 generated for {resort_name}")

    except Exception as e:
        # Image generation is non-critical - continue without it
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="image_generation_failed",
            reasoning=f"Image generation failed (non-critical): {e}",
        )
        result["stages"]["images"] = {"status": "skipped", "error": str(e)}
        print(f"⚠️  Images skipped for {resort_name}: {e}", file=sys.stderr)

    # =========================================================================
    # STAGE 4.6: UGC Photos (Google Places)
    # =========================================================================
    try:
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_ugc_photos",
            reasoning=f"Fetching user-generated photos from Google Places for {resort_name}",
        )

        # Get coordinates from research data if available
        latitude = research_data.get("latitude")
        longitude = research_data.get("longitude")

        # Fetch and store UGC photos
        ugc_result = asyncio.run(fetch_and_store_ugc_photos(
            resort_id=resort_id,
            resort_name=resort_name,
            country=country,
            latitude=latitude,
            longitude=longitude,
            max_photos=8,
            filter_with_vision=True,  # Use Gemini to filter family-relevant photos
        ))

        if ugc_result.success and ugc_result.photos:
            # Log cost
            log_cost("google_places", ugc_result.cost, None, {"run_id": run_id, "stage": "ugc_photos"})

            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="ugc_photos_complete",
                reasoning=f"Fetched {len(ugc_result.photos)} UGC photos for {resort_name}. Cost: ${ugc_result.cost:.3f}",
                metadata={
                    "photos_found": ugc_result.total_found,
                    "photos_kept": len(ugc_result.photos),
                    "place_id": ugc_result.place_id,
                    "cost": ugc_result.cost,
                },
            )

            result["stages"]["ugc_photos"] = {
                "status": "complete",
                "photos_count": len(ugc_result.photos),
                "total_found": ugc_result.total_found,
                "cost": ugc_result.cost,
            }
            print(f"✓ UGC Photos: {len(ugc_result.photos)} family-relevant photos for {resort_name}")

        else:
            result["stages"]["ugc_photos"] = {
                "status": "no_photos",
                "error": ugc_result.error,
                "cost": ugc_result.cost,
            }
            print(f"⚠️  No UGC photos found for {resort_name}: {ugc_result.error}")

    except Exception as e:
        # UGC photos are non-critical - continue without them
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="ugc_photos_failed",
            reasoning=f"UGC photo fetch failed (non-critical): {e}",
        )
        result["stages"]["ugc_photos"] = {"status": "skipped", "error": str(e)}
        print(f"⚠️  UGC photos skipped for {resort_name}: {e}", file=sys.stderr)

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
                task_id=None,
            )

            if decision.get("should_publish"):
                publish_resort(resort_id, None)  # run_id tracked in result metadata
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
        task_id=None,
        agent_name="pipeline_runner",
        action="pipeline_complete",
        reasoning=f"Pipeline complete. Status: {result['status']}. Confidence: {result.get('confidence', 'N/A')}",
        metadata=result,
    )

    # =========================================================================
    # MEMORY: Store episode for future learning
    # =========================================================================
    try:
        # Build plan summary (what stages were attempted)
        plan = {
            "stages_attempted": list(result.get("stages", {}).keys()),
            "auto_publish": auto_publish,
        }

        # Build observation (what we learned)
        observation = {
            "success": result["status"] in ("published", "draft"),
            "confidence": result.get("confidence", 0),
            "published": result["status"] == "published",
            "stages_completed": [
                stage for stage, data in result.get("stages", {}).items()
                if isinstance(data, dict) and data.get("status") in ("complete", "published")
            ],
            "stages_failed": [
                stage for stage, data in result.get("stages", {}).items()
                if isinstance(data, dict) and data.get("status") == "failed"
            ],
            "lessons": [],
        }

        # Extract lessons based on what happened
        if result.get("confidence", 0) < 0.5:
            observation["lessons"].append(f"Low confidence ({result.get('confidence', 0):.2f}) for {country} resort - may need better research sources")

        if result["status"] == "published" and result.get("confidence", 0) > 0.8:
            observation["lessons"].append(f"High-confidence publish for {country} - research strategy effective")

        if "images" in result.get("stages", {}) and result["stages"]["images"].get("status") == "complete":
            observation["lessons"].append(f"Image generation successful for {resort_name}")

        # Store the episode
        asyncio.run(memory.store_episode(
            run_id=run_id,
            objective=objective,
            plan=plan,
            result=result,
            observation=observation,
        ))

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="memory_stored",
            reasoning=f"Stored episode in memory for future learning. Lessons: {len(observation['lessons'])}",
        )

    except Exception as e:
        # Memory storage is non-critical - don't fail the pipeline
        print(f"⚠️  Memory storage failed (non-critical): {e}", file=sys.stderr)

    return result
