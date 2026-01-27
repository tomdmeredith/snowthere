"""Pipeline runner - executes the full content generation pipeline for a resort.

This is the core execution logic that:
1. Researches a resort using multiple APIs
2. Generates content in snowthere_guide voice
3. Optimizes for GEO (tables, FAQs, schema)
4. Stores in database
5. Runs three-agent approval panel (TrustGuard, FamilyValue, VoiceCoach)
6. Publishes if 2/3 majority approval, iterates up to 3 times

Design Decisions:
- Uses existing primitives directly (no MCP overhead)
- Three-agent approval panel replaces simple confidence thresholds
- Diverse perspectives: accuracy (TrustGuard), completeness (FamilyValue), voice (VoiceCoach)
- 2/3 majority vote for publication approval
- Iterative improvement loop (max 3 iterations) before final decision
- Logs all reasoning for observability
- Handles errors gracefully with retry logic
"""

import asyncio
import logging
import sys
import time
from datetime import datetime
from typing import Any
from uuid import uuid4

# Agent Layer - Memory for learning from past runs
from agent_layer.memory import AgentMemory

# Supabase client for direct DB operations
from shared.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)

from shared.primitives import (
    # Research
    search_resort_info,
    # Content
    write_section,
    generate_faq,
    generate_seo_meta,
    generate_tagline,
    # Quick Take (Round 8 - Editorial Verdict Model)
    generate_quick_take,
    QuickTakeContext,
    QuickTakeResult,
    extract_quick_take_context,
    # Quality
    score_resort_page,
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
    # Scoring (R9 - deterministic family score calculation)
    calculate_family_score,
    # Official images (real photos from resort websites)
    fetch_resort_images_with_fallback,
    # UGC Photos (Google Places) - kept as fallback
    fetch_and_store_ugc_photos,
    # Approval Panel (Three-agent quality evaluation)
    approval_loop,
    format_loop_summary,
)

from .decision_maker import handle_error


def slugify(name: str) -> str:
    """Convert resort name to URL-safe ASCII slug.

    Uses unidecode to transliterate Unicode to ASCII (e.g., Kitzbühel → kitzbuhel).
    This prevents duplicate resorts from different slug encodings.
    """
    try:
        from unidecode import unidecode
        ascii_name = unidecode(name)
    except ImportError:
        ascii_name = name
    return ascii_name.lower().replace(" ", "-").replace("'", "").replace(".", "")


def calculate_confidence(research_data: dict[str, Any]) -> float:
    """Calculate confidence score from research quality.

    Factors:
    - Number of sources found
    - Presence of official resort data
    - Price data completeness (CRITICAL - weighted 0.4)
    - Family metrics completeness
    - Review data quality

    Returns: 0.0 - 1.0
    """
    score = 0.0

    # Source count (max 0.2)
    sources = research_data.get("sources", [])
    source_score = min(len(sources) / 10, 0.2)
    score += source_score

    # Official data present (0.15)
    if research_data.get("official_site_data"):
        score += 0.15

    # Price data completeness (max 0.4) - CRITICAL for family value
    # Without pricing, families can't plan trips
    costs = research_data.get("costs", {})
    price_fields = ["lift_adult_daily", "lift_child_daily", "lodging_mid_nightly"]
    price_completeness = sum(1 for f in price_fields if costs.get(f)) / len(price_fields)
    score += price_completeness * 0.4

    # Family metrics completeness (max 0.15)
    metrics = research_data.get("family_metrics", {})
    metric_fields = ["family_overall_score", "best_age_min", "best_age_max"]
    metric_completeness = sum(1 for f in metric_fields if metrics.get(f)) / len(metric_fields)
    score += metric_completeness * 0.15

    # Review data (max 0.1)
    reviews = research_data.get("reviews", [])
    if len(reviews) >= 5:
        score += 0.1
    elif len(reviews) >= 2:
        score += 0.05

    return min(score, 1.0)


def has_minimum_data(research_data: dict[str, Any]) -> tuple[bool, list[str]]:
    """Check if research data meets minimum requirements for publication.

    Families need at least SOME pricing data to plan trips. Without it,
    the content is incomplete regardless of how well-written it is.

    Returns:
        Tuple of (has_minimum, missing_fields)
    """
    REQUIRED_COST_FIELDS = ["lift_adult_daily", "lodging_mid_nightly"]
    REQUIRED_METRIC_FIELDS = ["family_overall_score", "best_age_min"]

    costs = research_data.get("costs", {})
    metrics = research_data.get("family_metrics", {})

    missing = []

    # Check costs - need at least ONE cost field
    cost_present = any(costs.get(f) for f in REQUIRED_COST_FIELDS)
    if not cost_present:
        missing.extend([f"costs.{f}" for f in REQUIRED_COST_FIELDS])

    # Check metrics - need at least ONE metric field
    metric_present = any(metrics.get(f) for f in REQUIRED_METRIC_FIELDS)
    if not metric_present:
        missing.extend([f"metrics.{f}" for f in REQUIRED_METRIC_FIELDS])

    # Must have at least one cost OR one metric to publish
    # This is a soft gate - we want SOME data, not necessarily all
    has_minimum = cost_present or metric_present

    return has_minimum, missing


async def run_resort_pipeline(
    resort_name: str,
    country: str,
    task_id: str | None = None,
    auto_publish: bool = True,
) -> dict[str, Any]:
    """Run the full pipeline for a single resort.

    Steps:
    1. Check budget
    2. Research resort (Exa + SerpAPI + Tavily)
    3. Fetch trail map data (OpenStreetMap)
    4. Generate content (Claude in snowthere_guide voice)
    5. Store in database
    6. Generate images (Gemini → Glif → Replicate fallback)
    7. Fetch UGC photos (Google Places)
    8. Run three-agent approval panel (TrustGuard, FamilyValue, VoiceCoach)
       - Requires 2/3 majority to approve
       - Iterates up to 3 times, improving content based on feedback
       - Publishes if approved, saves as draft otherwise

    Args:
        resort_name: Name of the resort
        country: Country the resort is in
        task_id: Optional task ID for audit logging
        auto_publish: Whether to run approval panel and publish if approved

    Returns:
        Pipeline result with status, approval panel history, and any errors
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
    memory_context = await memory.get_context_for_objective(objective)
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
    if not check_budget(10.0):  # ~$10 per resort (Opus content + research APIs)
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

        research_data = await search_resort_info(resort_name, country)

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

        # Extract coordinates for better Google Places and trail map lookups
        from shared.primitives.research import extract_coordinates
        coords = await extract_coordinates(resort_name, country)
        if coords:
            research_data["latitude"], research_data["longitude"] = coords
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="coordinates_extracted",
                reasoning=f"Extracted coordinates: {coords[0]:.4f}, {coords[1]:.4f}",
                metadata={"lat": coords[0], "lon": coords[1]},
            )

        # Extract region for location display ("Region, Country" instead of just "Country")
        from shared.primitives.intelligence import extract_region
        region = await extract_region(resort_name, country)
        if region:
            research_data["region"] = region
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="region_extracted",
                reasoning=f"Extracted region: {region}",
                metadata={"region": region},
            )
            # Log cost (~$0.002 for Haiku)
            log_cost("anthropic", 0.002, None, {"run_id": run_id, "stage": "region_extraction"})

        # =====================================================================
        # EXTRACTION: Transform raw research into structured costs/family_metrics
        # This is the critical layer between research and storage
        # =====================================================================
        from shared.primitives.intelligence import extract_resort_data

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_extraction",
            reasoning=f"Extracting structured costs and family metrics from raw research for {resort_name}",
        )

        extracted = await extract_resort_data(
            raw_research=research_data,
            resort_name=resort_name,
            country=country,
        )

        # Merge extracted data into research_data for downstream use
        research_data["costs"] = extracted.costs
        research_data["family_metrics"] = extracted.family_metrics

        # Log extraction cost (~$0.01 for Sonnet)
        log_cost("anthropic", 0.01, None, {"run_id": run_id, "stage": "extraction"})

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="extraction_complete",
            reasoning=f"Extracted data with confidence {extracted.confidence:.2f}: {extracted.reasoning}",
            metadata={
                "extraction_confidence": extracted.confidence,
                "missing_fields": extracted.missing_fields,
                "costs_fields": list(extracted.costs.keys()) if extracted.costs else [],
                "metrics_fields": list(extracted.family_metrics.keys()) if extracted.family_metrics else [],
            },
        )

        # Update confidence with extraction quality
        if extracted.confidence < 0.5 and extracted.missing_fields:
            # Reduce overall confidence if extraction was poor
            confidence = confidence * 0.8
            result["confidence"] = confidence
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="confidence_adjusted",
                reasoning=f"Adjusted confidence to {confidence:.2f} due to poor extraction (missing: {len(extracted.missing_fields)} fields)",
            )

        # =====================================================================
        # STAGE 2.2: Multi-Strategy Cost Acquisition
        # If extraction didn't find good cost data, try additional strategies
        # =====================================================================
        costs = research_data.get("costs", {})
        needs_cost_acquisition = (
            not costs.get("lift_adult_daily")
            or not costs.get("lodging_mid_nightly")
        )

        if needs_cost_acquisition:
            from shared.primitives.costs import acquire_resort_costs

            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="start_cost_acquisition",
                reasoning=f"Extraction missing cost data. Starting multi-strategy cost acquisition for {resort_name}",
            )

            # Collect research snippets for Claude extraction fallback
            research_snippets = []
            for source in research_data.get("sources", []):
                if source.get("snippet"):
                    research_snippets.append(source["snippet"])
                elif source.get("content"):
                    research_snippets.append(source["content"][:500])

            cost_result = await acquire_resort_costs(
                resort_name=resort_name,
                country=country,
                official_website=research_data.get("official_website"),
                research_snippets=research_snippets,
            )

            if cost_result.success:
                # Merge acquired costs with existing (acquired takes precedence for missing fields)
                for key, value in cost_result.costs.items():
                    if value is not None and not costs.get(key):
                        costs[key] = value

                # Update currency if we acquired it
                if cost_result.currency and not costs.get("currency"):
                    costs["currency"] = cost_result.currency

                research_data["costs"] = costs

                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="cost_acquisition_complete",
                    reasoning=f"Acquired costs from {cost_result.source} with confidence {cost_result.confidence:.2f}",
                    metadata={
                        "source": cost_result.source,
                        "confidence": cost_result.confidence,
                        "costs_acquired": list(cost_result.costs.keys()),
                    },
                )

                result["stages"]["cost_acquisition"] = {
                    "status": "complete",
                    "source": cost_result.source,
                    "confidence": cost_result.confidence,
                }
                print(f"✓ Cost Acquisition: {cost_result.source} (confidence: {cost_result.confidence:.2f})")

                # Recalculate overall confidence with updated cost data
                confidence = calculate_confidence(research_data)
                result["confidence"] = confidence
                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="confidence_recalculated",
                    reasoning=f"Recalculated confidence after cost acquisition: {confidence:.2f}",
                    metadata={"confidence": confidence, "trigger": "cost_acquisition_complete"},
                )
            else:
                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="cost_acquisition_failed",
                    reasoning=f"Cost acquisition failed: {cost_result.error}",
                )
                result["stages"]["cost_acquisition"] = {
                    "status": "failed",
                    "error": cost_result.error,
                }
                print(f"⚠️  Cost Acquisition: Failed - {cost_result.error}")
        else:
            result["stages"]["cost_acquisition"] = {
                "status": "skipped",
                "reason": "Extraction already found cost data",
            }

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
        trail_map_result = await get_trail_map(
            resort_name=resort_name,
            country=country,
            latitude=latitude,
            longitude=longitude,
            radius_km=8.0,  # Larger radius for big resorts
        )

        # Get difficulty breakdown
        difficulty_breakdown = await get_difficulty_breakdown(trail_map_result.pistes)

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
            reasoning="Generating content sections in snowthere_guide voice",
        )

        content = {}

        # =====================================================================
        # STAGE 3.1: Extract Quick Take Context (Round 8)
        # =====================================================================
        # Extract editorial inputs for the new Quick Take model
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_quick_take_context",
            reasoning=f"Extracting editorial context for Quick Take: {resort_name}",
        )

        qt_context_result = await extract_quick_take_context(
            resort_name=resort_name,
            country=country,
            research_data=research_data,
        )

        # Log cost (~$0.01 for Sonnet)
        log_cost("anthropic", 0.01, None, {"run_id": run_id, "stage": "quick_take_context"})

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="quick_take_context_complete",
            reasoning=f"Extracted Quick Take context (confidence: {qt_context_result.extraction_confidence:.2f})",
            metadata={
                "unique_angle": qt_context_result.unique_angle,
                "primary_weakness": qt_context_result.primary_weakness,
                "extraction_confidence": qt_context_result.extraction_confidence,
            },
        )

        # =====================================================================
        # STAGE 3.2: Generate Quick Take (Round 8 - Editorial Verdict Model)
        # =====================================================================
        family_metrics = research_data.get("family_metrics", {})
        family_score = family_metrics.get("family_overall_score")

        # Build Quick Take context from research + extracted editorial inputs
        qt_context = QuickTakeContext(
            resort_name=resort_name,
            country=country,
            region=research_data.get("region"),
            family_score=family_score,
            best_age_min=family_metrics.get("best_age_min"),
            best_age_max=family_metrics.get("best_age_max"),
            # Editorial inputs from extraction
            unique_angle=qt_context_result.unique_angle,
            signature_experience=qt_context_result.signature_experience,
            primary_strength=qt_context_result.primary_strength,
            primary_weakness=qt_context_result.primary_weakness,
            who_should_skip=qt_context_result.who_should_skip,
            memorable_detail=qt_context_result.memorable_detail,
            price_context=qt_context_result.price_context,
            # Additional context
            terrain_pct_beginner=family_metrics.get("kid_friendly_terrain_pct"),
            has_ski_school=True,  # Most resorts have ski schools
            ski_school_min_age=family_metrics.get("ski_school_min_age"),
            has_childcare=family_metrics.get("has_childcare", False),
            kids_ski_free_age=family_metrics.get("kids_ski_free_age"),
        )

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_quick_take_generation",
            reasoning=f"Generating Quick Take with Editorial Verdict Model for {resort_name}",
        )

        quick_take_result = await generate_quick_take(
            context=qt_context,
            voice_profile="snowthere_guide",
        )

        # Log cost (~$0.10 for Opus)
        log_cost("anthropic", 0.10, None, {"run_id": run_id, "stage": "quick_take_generation"})

        # Store Quick Take in content (but NOT perfect_if/skip_if - those go to family_metrics)
        content["quick_take"] = quick_take_result.quick_take_html

        # Route perfect_if/skip_if to family_metrics for proper storage
        # (resort_content table doesn't have these columns)
        if "family_metrics" not in research_data:
            research_data["family_metrics"] = {}
        if quick_take_result.perfect_if:
            research_data["family_metrics"]["perfect_if"] = quick_take_result.perfect_if
        if quick_take_result.skip_if:
            research_data["family_metrics"]["skip_if"] = quick_take_result.skip_if

        # Log quality metrics
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="quick_take_complete",
            reasoning=f"Quick Take generated: {quick_take_result.word_count} words, specificity {quick_take_result.specificity_score:.2f}, valid: {quick_take_result.is_valid}",
            metadata={
                "word_count": quick_take_result.word_count,
                "specificity_score": quick_take_result.specificity_score,
                "forbidden_phrases": quick_take_result.forbidden_phrases_found,
                "is_valid": quick_take_result.is_valid,
                "validation_errors": quick_take_result.validation_errors,
                "perfect_if_count": len(quick_take_result.perfect_if),
                "skip_if_count": len(quick_take_result.skip_if),
            },
        )

        result["stages"]["quick_take"] = {
            "status": "complete" if quick_take_result.is_valid else "quality_issues",
            "word_count": quick_take_result.word_count,
            "specificity_score": quick_take_result.specificity_score,
            "is_valid": quick_take_result.is_valid,
            "validation_errors": quick_take_result.validation_errors,
        }

        if quick_take_result.is_valid:
            print(f"✓ Quick Take: {quick_take_result.word_count} words, specificity {quick_take_result.specificity_score:.2f}")
        else:
            print(f"⚠️  Quick Take quality issues: {', '.join(quick_take_result.validation_errors[:2])}")

        # =====================================================================
        # STAGE 3.3: Generate Other Content Sections
        # =====================================================================
        # Note: quick_take is now generated separately above
        sections = [
            "getting_there",
            "where_to_stay",
            "lift_tickets",
            "on_mountain",
            "off_mountain",
            "parent_reviews_summary",
        ]

        # Add resort_name, country, and defaults for template formatting
        content_context = {
            "resort_name": resort_name,
            "country": country,
            "family_score": family_score if family_score else "N/A",
            # Trail map data for content generation
            "trail_map": trail_map_data,
            # Memory insights from past runs
            "memory_insights": memory_insights,
            # Flatten research data for template access
            **research_data,
        }

        for section in sections:
            content[section] = await write_section(
                section_name=section,
                context=content_context,
                voice_profile="snowthere_guide",
            )

        # Generate FAQs
        content["faqs"] = await generate_faq(
            resort_name=resort_name,
            country=country,
            context=content_context,
            num_questions=6,
            voice_profile="snowthere_guide",
        )

        # Generate SEO meta
        content["seo_meta"] = await generate_seo_meta(
            resort_name=resort_name,
            country=country,
            quick_take=content["quick_take"],
        )

        # Generate unique tagline (8-12 words capturing resort personality)
        content["tagline"] = await generate_tagline(
            resort_name=resort_name,
            country=country,
            context=content_context,
            voice_profile="snowthere_guide",
        )

        # Log content generation cost (~$0.70 for Claude API, Quick Take logged separately)
        log_cost("anthropic", 0.70, None, {"run_id": run_id, "stage": "content_generation"})

        # Total sections = 6 regular + 1 quick_take (generated earlier)
        result["stages"]["content"] = {"status": "complete", "sections": len(sections) + 1}

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="content_complete",
            reasoning=f"Generated {len(sections)} content sections + FAQs + SEO meta",
        )

    except Exception as e:
        # Explicitly log the content generation error before calling handle_error
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="content_generation_failed",
            reasoning=f"Content generation failed for {resort_name}: {type(e).__name__}: {e}",
            metadata={"error_type": type(e).__name__, "error_message": str(e)},
        )
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
            # R9.2 FIX: Recalculate score with deterministic formula
            # Replaces LLM-extracted integer (8, 9) with precise decimal (6.8, 7.3)
            old_score = research_data["family_metrics"].get("family_overall_score")
            calculated_score = calculate_family_score(research_data["family_metrics"])
            research_data["family_metrics"]["family_overall_score"] = calculated_score
            if old_score != calculated_score:
                print(f"  Score recalculated: {old_score} → {calculated_score}")

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
        if trail_map_data:
            trail_map_result = update_resort(resort_id, {"trail_map_data": trail_map_data})
            if not trail_map_result:
                print(f"⚠️  Warning: Failed to save trail map data for {resort_name}", file=sys.stderr)

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
    # STAGE 4.5: Official Images (Real photos from resort websites)
    # =========================================================================
    # Philosophy: Families deserve REAL images, not AI-generated approximations.
    # Priority: Official website > Google Places UGC > No image (NO AI generation)
    try:
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_official_images",
            reasoning=f"Fetching real images from official website for {resort_name}",
        )

        # Get coordinates from research data if available
        latitude = research_data.get("latitude")
        longitude = research_data.get("longitude")

        # Fetch real images (official website → UGC fallback, NO AI)
        image_result = await fetch_resort_images_with_fallback(
            resort_id=resort_id,
            resort_name=resort_name,
            country=country,
            official_website=None,  # Will be discovered via search
            latitude=latitude,
            longitude=longitude,
            task_id=None,
        )

        if image_result.success:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="official_image_complete",
                reasoning=f"Fetched real image for {resort_name} from {image_result.source}",
                metadata={
                    "hero_url": image_result.url,
                    "source": image_result.source,
                    "attribution": image_result.attribution,
                },
            )

            result["stages"]["images"] = {
                "status": "complete",
                "hero_generated": True,
                "source": image_result.source,
                "images_count": 1,
                "cost": 0,  # Scraping is free
            }

            print(f"✓ Image: Real photo from {image_result.source} for {resort_name}")
        else:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="official_image_failed",
                reasoning=f"Could not fetch real images for {resort_name}: {image_result.error}",
            )

            result["stages"]["images"] = {
                "status": "skipped",
                "hero_generated": False,
                "reason": "No real images available (AI images disabled)",
                "images_count": 0,
                "cost": 0,
            }

            print(f"⚠️  No real images found for {resort_name} (AI disabled)")

    except Exception as e:
        # Image fetching is non-critical - continue without it
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="official_image_error",
            reasoning=f"Image fetching failed (non-critical): {e}",
        )
        result["stages"]["images"] = {"status": "skipped", "error": str(e)}
        print(f"⚠️  Images skipped for {resort_name}: {e}", file=sys.stderr)

    # =========================================================================
    # STAGE 4.6: Additional UGC Photos (Google Places)
    # =========================================================================
    # Note: Hero image already fetched in 4.5 (may include UGC fallback).
    # This stage fetches ADDITIONAL gallery photos if we don't already have them.
    hero_source = result.get("stages", {}).get("images", {}).get("source", "")
    if hero_source == "google_places":
        # We already got UGC photos via the fallback, skip duplicate fetch
        result["stages"]["ugc_photos"] = {
            "status": "skipped",
            "reason": "UGC photos already fetched as hero fallback",
        }
        print(f"✓ UGC Photos: Already fetched as hero fallback for {resort_name}")
    else:
        try:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="start_ugc_photos",
                reasoning=f"Fetching additional UGC photos from Google Places for {resort_name}",
            )

            # Get coordinates from research data if available
            latitude = research_data.get("latitude")
            longitude = research_data.get("longitude")

            # Fetch and store UGC photos for gallery
            ugc_result = await fetch_and_store_ugc_photos(
                resort_id=resort_id,
                resort_name=resort_name,
                country=country,
                latitude=latitude,
                longitude=longitude,
                max_photos=8,
                filter_with_vision=True,  # Use Gemini to filter family-relevant photos
            )

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
    # STAGE 4.8: Link Curation (Extract family-relevant links from sources)
    # =========================================================================
    try:
        from shared.primitives.intelligence import curate_resort_links
        from shared.primitives.links import get_resort_links

        # Check if we already have links for this resort
        existing_links = await get_resort_links(resort_id) if resort_id else []

        if not existing_links:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="start_link_curation",
                reasoning=f"Curating family-relevant links for {resort_name}",
            )

            # Get research sources for link curation
            research_sources = research_data.get("sources", [])

            link_result = await curate_resort_links(
                resort_name=resort_name,
                country=country,
                research_sources=research_sources,
            )

            if link_result.success and link_result.links:
                # Store curated links in database
                client = get_supabase_client()

                for link in link_result.links:
                    try:
                        client.table("resort_links").upsert({
                            "resort_id": resort_id,
                            "title": link.title,
                            "url": link.url,
                            "category": link.category,
                            "description": link.description,
                        }, on_conflict="resort_id,url").execute()
                    except Exception as link_err:
                        logger.warning(f"Failed to store link {link.url}: {link_err}")

                # Log cost (~$0.01 for Sonnet)
                log_cost("anthropic", 0.01, None, {"run_id": run_id, "stage": "link_curation"})

                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="link_curation_complete",
                    reasoning=f"Curated {len(link_result.links)} links (official: {link_result.has_official})",
                    metadata={
                        "links_count": len(link_result.links),
                        "has_official": link_result.has_official,
                        "categories": list(set(l.category for l in link_result.links)),
                    },
                )

                result["stages"]["link_curation"] = {
                    "status": "complete",
                    "links_count": len(link_result.links),
                    "has_official": link_result.has_official,
                }
                print(f"✓ Link Curation: {len(link_result.links)} links (official: {'✓' if link_result.has_official else '✗'})")
            else:
                result["stages"]["link_curation"] = {
                    "status": "no_links",
                    "error": link_result.error,
                }
                print(f"⚠️  Link Curation: No links found - {link_result.error}")
        else:
            result["stages"]["link_curation"] = {
                "status": "skipped",
                "reason": f"Already has {len(existing_links)} links",
            }

    except Exception as e:
        # Link curation is non-critical - continue without them
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="link_curation_failed",
            reasoning=f"Link curation failed (non-critical): {e}",
        )
        result["stages"]["link_curation"] = {"status": "skipped", "error": str(e)}
        print(f"⚠️  Link curation skipped for {resort_name}: {e}", file=sys.stderr)

    # =========================================================================
    # STAGE 4.9: External Link Injection (Hotels, Restaurants, etc.)
    # =========================================================================
    # Part of Round 7.3: Inject links to hotels, restaurants, ski schools, etc.
    # Uses Google Places API for entity resolution and affiliate URL transformation.
    try:
        from shared.primitives.external_links import inject_links_in_content_sections

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="start_external_link_injection",
            reasoning=f"Injecting external links (hotels, restaurants, etc.) for {resort_name}",
        )

        modified_content, injected_links = await inject_links_in_content_sections(
            content=content,
            resort_name=resort_name,
            country=country,
        )

        if injected_links:
            # Update content with injected links
            content = modified_content
            # Re-save content to database with new links
            update_resort_content(resort_id, content)

            # Count affiliate links for logging
            affiliate_count = sum(1 for link in injected_links if link.is_affiliate)

            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="external_link_injection_complete",
                reasoning=f"Injected {len(injected_links)} external links ({affiliate_count} affiliate) for {resort_name}",
                metadata={
                    "total_links": len(injected_links),
                    "affiliate_links": affiliate_count,
                    "by_type": {
                        link.entity_type: sum(1 for l in injected_links if l.entity_type == link.entity_type)
                        for link in injected_links
                    },
                    "entities_linked": [link.entity_name for link in injected_links],
                },
            )

            result["stages"]["external_link_injection"] = {
                "status": "complete",
                "links_injected": len(injected_links),
                "affiliate_links": affiliate_count,
                "entities": [link.entity_name for link in injected_links[:5]],  # Top 5 for brevity
            }
            print(f"✓ External Links: {len(injected_links)} links ({affiliate_count} affiliate)")

        else:
            result["stages"]["external_link_injection"] = {
                "status": "no_entities",
                "reason": "No linkable entities found in content",
            }
            print(f"⚠️  External Links: No entities found for {resort_name}")

    except Exception as e:
        # External link injection is non-critical - continue without it
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="external_link_injection_failed",
            reasoning=f"External link injection failed (non-critical): {e}",
        )
        result["stages"]["external_link_injection"] = {"status": "skipped", "error": str(e)}
        print(f"⚠️  External links skipped for {resort_name}: {e}", file=sys.stderr)

    # =========================================================================
    # STAGE 4.7: Perfect Page Quality Gate
    # =========================================================================
    # Philosophy: Quality checklist ensures every page meets the "gold standard"
    # before publishing. This prevents data gaps like missing cost data or
    # family metrics from reaching production.
    quality_score_result = score_resort_page(resort_id)
    if quality_score_result:
        result["stages"]["quality_check"] = {
            "status": "complete",
            "score_pct": quality_score_result.score_pct,
            "passed": quality_score_result.passed_checks,
            "total": quality_score_result.total_checks,
            "failing": [r.check_id for r in quality_score_result.failing_checks],
        }

        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="quality_check",
            reasoning=f"Quality score: {quality_score_result.score_pct:.0f}% ({quality_score_result.passed_checks}/{quality_score_result.total_checks})",
            metadata=quality_score_result.to_dict(),
        )

        print(f"✓ Quality Check: {quality_score_result.score_pct:.0f}% ({quality_score_result.passed_checks}/{quality_score_result.total_checks} checks)")

        # Block publishing if below 70%
        QUALITY_GATE_THRESHOLD = 70
        if quality_score_result.score_pct < QUALITY_GATE_THRESHOLD:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="quality_gate_failed",
                reasoning=f"Blocked: Quality {quality_score_result.score_pct:.0f}% < {QUALITY_GATE_THRESHOLD}%. Failing: {[r.check_id for r in quality_score_result.failing_checks]}",
            )
            result["status"] = "draft"
            result["publish_blocked"] = True
            result["publish_blocked_reason"] = f"Quality score {quality_score_result.score_pct:.0f}% below {QUALITY_GATE_THRESHOLD}%"
            auto_publish = False
            print(f"🚫 Quality Gate: BLOCKED publishing (score {quality_score_result.score_pct:.0f}% < {QUALITY_GATE_THRESHOLD}%)")
            print(f"   Failing checks: {[r.check_id for r in quality_score_result.failing_checks]}")

    # =========================================================================
    # STAGE 5: Three-Agent Approval Panel (Publish-First Model)
    # =========================================================================
    # Philosophy: Publish early, improve continuously (agent-native approach)
    # The approval panel provides quality signals but doesn't gate publication.
    # PUBLISH-FIRST PHILOSOPHY: Always publish, queue low-quality for improvement.
    # The quality score determines enhancement priority, NOT whether to publish.
    # A thin page is better than no page - it can be discovered and improved.
    # =========================================================================

    # Check data completeness (for improvement queue priority, not gating)
    has_data, missing_fields = has_minimum_data(research_data)
    confidence = result.get("confidence", 0)
    QUALITY_THRESHOLD = 0.60  # Below this = high priority for improvement

    # Track quality issues for improvement queue
    quality_issues = []
    improvement_priority = 5  # Default medium priority

    if not has_data:
        quality_issues.append(f"Missing data: {', '.join(missing_fields[:4])}")
        improvement_priority = max(improvement_priority, 8)  # High priority
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="data_quality_note",
            reasoning=f"Low data completeness for {resort_name}: missing {missing_fields}. Will publish and queue for improvement.",
            metadata={"missing_fields": missing_fields},
        )
        print(f"📝 Low data completeness - will publish and queue for improvement: {resort_name}")

    if confidence < QUALITY_THRESHOLD:
        quality_issues.append(f"Low confidence: {confidence:.2f}")
        improvement_priority = max(improvement_priority, 7)  # High priority
        log_reasoning(
            task_id=None,
            agent_name="pipeline_runner",
            action="confidence_quality_note",
            reasoning=f"Low research confidence {confidence:.2f} for {resort_name}. Will publish and queue for improvement.",
            metadata={"confidence": confidence, "threshold": QUALITY_THRESHOLD},
        )
        print(f"📝 Low confidence ({confidence:.2f}) - will publish and queue for improvement: {resort_name}")

    if auto_publish:
        try:
            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="start_approval_panel",
                reasoning=f"Running three-agent approval panel for {resort_name} (publish-first model)",
            )

            # Build resort data for approval panel evaluation
            resort_data = {
                "name": resort_name,
                "country": country,
                "region": research_data.get("region", ""),
                "family_score": research_data.get("family_metrics", {}).get("family_overall_score"),
                "costs": research_data.get("costs", {}),
                "family_metrics": research_data.get("family_metrics", {}),
            }

            # Run approval panel (TrustGuard + FamilyValue + VoiceCoach)
            # This iterates up to 3 times, improving content based on feedback
            approval_result = await approval_loop(
                content=content,
                sources=research_data.get("sources", []),
                resort_data=resort_data,
                voice_profile="snowthere_guide",
                max_iterations=3,
            )

            # Log approval panel cost (~$0.45-0.60 for 3 agents × up to 3 iterations)
            panel_cost = 0.15 * approval_result.iterations  # ~$0.15 per panel run
            log_cost("anthropic", panel_cost, None, {
                "run_id": run_id,
                "stage": "approval_panel",
                "iterations": approval_result.iterations,
            })

            # Update content with improved version
            if approval_result.final_content:
                content = approval_result.final_content
                # Re-save improved content to database
                update_resort_content(resort_id, content)

            # PUBLISH-FIRST: Always publish - approval panel informs, doesn't gate
            publish_resort(resort_id, None)
            result["status"] = "published"

            if approval_result.approved:
                result["stages"]["approval_panel"] = {
                    "status": "approved",
                    "iterations": approval_result.iterations,
                    "summary": format_loop_summary(approval_result),
                }

                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="approval_panel_approved",
                    reasoning=f"Content approved after {approval_result.iterations} iteration(s). Published.",
                    metadata={
                        "iterations": approval_result.iterations,
                        "panel_history": [
                            {
                                "approve_count": p.approve_count,
                                "improve_count": p.improve_count,
                                "reject_count": p.reject_count,
                            }
                            for p in approval_result.panel_history
                        ],
                    },
                )

                print(f"✓ Approval Panel: APPROVED after {approval_result.iterations} iteration(s)")
            else:
                # PUBLISH-FIRST: Still publish, but queue for continuous improvement
                result["stages"]["approval_panel"] = {
                    "status": "published_with_issues",
                    "iterations": approval_result.iterations,
                    "final_issues": approval_result.final_issues,
                    "summary": format_loop_summary(approval_result),
                }

                # Queue for quality improvement (continuous improvement model)
                try:
                    queue_task(
                        task_type="quality_improvement",
                        resort_id=resort_id,
                        priority=8 if approval_result.iterations == 3 else 6,  # high: 8, medium: 6
                        metadata={
                            "resort_name": resort_name,
                            "country": country,
                            "issues": approval_result.final_issues,
                            "sources": research_data.get("sources", [])[:10],  # Include top sources for re-evaluation
                        },
                    )

                    log_reasoning(
                        task_id=None,
                        agent_name="pipeline_runner",
                        action="queued_for_improvement",
                        reasoning=f"Published but queued for improvement: {len(approval_result.final_issues)} issues",
                        metadata={
                            "resort_id": resort_id,
                            "issues_count": len(approval_result.final_issues),
                            "priority": 8 if approval_result.iterations == 3 else 6,
                        },
                    )
                except Exception as queue_error:
                    # Non-critical if queue fails - still published
                    print(f"⚠️  Failed to queue for improvement: {queue_error}", file=sys.stderr)

                log_reasoning(
                    task_id=None,
                    agent_name="pipeline_runner",
                    action="published_with_issues",
                    reasoning=f"Content published with issues after {approval_result.iterations} iterations. Queued for improvement.",
                    metadata={
                        "iterations": approval_result.iterations,
                        "final_issues": approval_result.final_issues,
                    },
                )

                print(f"✓ Published with issues after {approval_result.iterations} iteration(s)")
                print(f"   Queued for improvement: {', '.join(approval_result.final_issues[:3])}")

        except Exception as e:
            # On approval panel error, still try to publish (content is valid, panel failed)
            try:
                publish_resort(resort_id, None)
                result["status"] = "published"
                result["stages"]["approval_panel"] = {"status": "error_but_published", "error": str(e)}
                print(f"⚠️  Approval Panel failed but content published for {resort_name}: {e}", file=sys.stderr)
            except Exception as pub_error:
                result["status"] = "draft"
                result["stages"]["approval_panel"] = {"status": "error", "error": str(e), "publish_error": str(pub_error)}
                print(f"❌ Approval Panel and publish both failed for {resort_name}: {e}", file=sys.stderr)

            log_reasoning(
                task_id=None,
                agent_name="pipeline_runner",
                action="approval_panel_error",
                reasoning=f"Approval panel failed: {e}. Attempted publish: {result['status']}.",
            )
    else:
        result["status"] = "draft"
        result["stages"]["approval_panel"] = {"status": "skipped", "reason": "auto_publish=False"}

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
        await memory.store_episode(
            run_id=run_id,
            objective=objective,
            plan=plan,
            result=result,
            observation=observation,
        )

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
