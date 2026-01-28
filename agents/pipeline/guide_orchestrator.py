"""Guide generation orchestrator for autonomous guide production.

This orchestrator handles the complete guide generation pipeline:
1. Topic discovery and selection
2. Research and planning
3. Content generation
4. Expert panel review (5 experts, up to 3 improvement iterations)
5. Publication or draft

Usage:
    from pipeline.guide_orchestrator import run_guide_pipeline

    result = await run_guide_pipeline(max_guides=2)

Design:
    - Runs 2x/week as part of cron job
    - Target: 2 guides/week (8/month)
    - Uses expert_panel.py for content-agnostic quality review
    - 5 expert reviewers with iterative improvement (vs old 3-reviewer single-shot)
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from zoneinfo import ZoneInfo

from shared.primitives.guides import (
    GuideCandidate,
    GuideOutline,
    discover_topics,
    plan_guide_structure,
    generate_guide_content,
    create_guide,
    publish_guide,
    link_resorts_to_guide,
    check_guide_exists,
)
from shared.primitives.expert_panel import expert_approval_loop, ExpertApprovalLoopResult
from shared.primitives.images import generate_image_with_fallback, AspectRatio
from shared.primitives.publishing import revalidate_page
from shared.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
PT_TIMEZONE = ZoneInfo("America/Los_Angeles")


# =============================================================================
# RESULT CLASSES
# =============================================================================


@dataclass
class GuideResult:
    """Result of processing a single guide."""

    success: bool
    guide_id: str | None = None
    slug: str | None = None
    title: str | None = None
    status: str = "unknown"  # draft, published, failed
    confidence: float = 0.0
    approval_result: ExpertApprovalLoopResult | None = None
    error: str | None = None


@dataclass
class GuidePipelineResult:
    """Result of the full guide pipeline run."""

    success: bool
    guides_processed: list[GuideResult]
    published_count: int = 0
    draft_count: int = 0
    failed_count: int = 0
    duration_seconds: float = 0.0


# =============================================================================
# GUIDE GENERATION PIPELINE
# =============================================================================


async def generate_single_guide(
    topic: GuideCandidate,
    dry_run: bool = False,
) -> GuideResult:
    """
    Generate a single guide from discovery through publication.

    Stages:
    1. Check for duplicates
    2. Plan structure
    3. Research (if needed)
    4. Generate content
    5. Run approval panel
    6. Create guide in database
    7. Publish or save as draft
    """
    logger.info(f"Generating guide: {topic.title}")

    try:
        # Stage 1: Check for duplicates
        if check_guide_exists(topic.title):
            return GuideResult(
                success=False,
                title=topic.title,
                status="skipped",
                error="Guide with similar title already exists",
            )

        if dry_run:
            return GuideResult(
                success=True,
                title=topic.title,
                status="dry_run",
            )

        # Stage 2: Plan structure
        logger.info(f"  Planning structure...")
        outline = await plan_guide_structure(topic)

        # Stage 3: Research (for comparison guides, gather resort data)
        research_data = None
        if topic.guide_type == "comparison" and topic.suggested_resorts:
            logger.info(f"  Researching {len(topic.suggested_resorts)} resorts...")
            research_data = {}
            for resort_id in topic.suggested_resorts[:5]:
                # Could enhance this with actual research
                research_data[resort_id] = {"status": "referenced"}

        # Stage 4: Generate content
        logger.info(f"  Generating content ({len(outline.sections)} sections)...")
        content = await generate_guide_content(outline, research_data)

        # Stage 5: Run expert approval loop (5 experts, up to 3 iterations)
        logger.info(f"  Running expert approval panel...")
        approval = await expert_approval_loop(
            content=content,
            content_type="guide",
            voice_profile="snowthere_guide",
            context=f"Guide: {topic.title} ({topic.guide_type})",
            max_iterations=3,
        )

        logger.info(
            f"  Approval: {'approved' if approval.approved else 'not approved'} "
            f"after {approval.iterations} iteration(s)"
        )

        # Use improved content if iterations were applied
        if approval.approved and approval.final_content is not None:
            content = approval.final_content

        # Stage 6: Create guide in database
        logger.info(f"  Creating guide in database...")
        guide = create_guide(
            title=outline.title,
            guide_type=outline.guide_type,
            content=content,
            category=outline.category,
            excerpt=outline.excerpt,
            seo_meta=outline.seo_meta,
            featured_resort_ids=outline.featured_resort_ids,
            status="draft",
        )

        guide_id = guide["id"]
        slug = guide["slug"]

        # Link resorts if applicable
        if outline.featured_resort_ids:
            link_resorts_to_guide(
                guide_id,
                [{"resort_id": rid} for rid in outline.featured_resort_ids],
            )

        # Stage 6.5: Generate featured image
        logger.info(f"  Generating featured image...")
        try:
            image_prompt = (
                f"Editorial travel photography for a family ski guide about: {outline.title}. "
                f"Warm golden hour lighting, professional magazine quality, "
                f"mountain landscape or ski atmosphere, no close-up faces, "
                f"distant silhouettes only, 16:9 landscape format"
            )
            image_result = await generate_image_with_fallback(
                prompt=image_prompt,
                aspect_ratio=AspectRatio.LANDSCAPE,
            )
            if image_result.success and image_result.url:
                client = get_supabase_client()
                client.table("guides").update(
                    {"featured_image_url": image_result.url}
                ).eq("id", guide_id).execute()
                logger.info(f"  Featured image set: {image_result.url[:60]}...")
            else:
                logger.warning(f"  Image generation failed: {image_result.error}")
        except Exception as e:
            logger.warning(f"  Image generation error (non-fatal): {e}")

        # Stage 7: Publish or draft based on approval
        final_status = "draft"
        if approval.approved:
            logger.info(f"  Publishing guide...")
            publish_guide(guide_id)
            final_status = "published"

            # Revalidate the guides listing and individual page
            try:
                revalidate_page("/guides")
                revalidate_page(f"/guides/{slug}")
            except Exception as e:
                logger.warning(f"Revalidation failed: {e}")
        else:
            logger.info(f"  Saving as draft (not approved)")

        # Extract confidence from the last panel result
        confidence = 0.0
        if approval.panel_history:
            last_panel = approval.panel_history[-1]
            if hasattr(last_panel, "evaluations") and last_panel.evaluations:
                confidence = sum(
                    e.confidence for e in last_panel.evaluations
                ) / len(last_panel.evaluations)

        return GuideResult(
            success=True,
            guide_id=guide_id,
            slug=slug,
            title=topic.title,
            status=final_status,
            confidence=confidence,
            approval_result=approval,
        )

    except Exception as e:
        logger.error(f"Guide generation failed for '{topic.title}': {e}")
        return GuideResult(
            success=False,
            title=topic.title,
            status="failed",
            error=str(e),
        )


async def run_guide_pipeline(
    max_guides: int = 2,
    dry_run: bool = False,
) -> GuidePipelineResult:
    """
    Run the full guide generation pipeline.

    Args:
        max_guides: Maximum guides to generate this run
        dry_run: If True, don't actually create guides

    Returns:
        GuidePipelineResult with all guide results
    """
    start_time = datetime.now(PT_TIMEZONE)
    logger.info(f"Starting guide pipeline (max: {max_guides}, dry_run: {dry_run})")

    results = []
    published = 0
    drafts = 0
    failed = 0

    try:
        # Discover topics
        logger.info("Discovering guide topics...")
        topics = await discover_topics(max_topics=max_guides * 2)

        logger.info(f"Found {len(topics)} candidate topics:")
        for t in topics[:max_guides]:
            logger.info(f"  - {t.title} ({t.guide_type}, {t.priority_score:.2f})")

        # Generate guides
        for topic in topics[:max_guides]:
            result = await generate_single_guide(topic, dry_run=dry_run)
            results.append(result)

            if result.status == "published":
                published += 1
            elif result.status == "draft":
                drafts += 1
            elif result.status == "failed":
                failed += 1

    except Exception as e:
        logger.error(f"Guide pipeline failed: {e}")

    duration = (datetime.now(PT_TIMEZONE) - start_time).total_seconds()

    logger.info(f"Guide pipeline complete: {published} published, {drafts} drafts, {failed} failed ({duration:.1f}s)")

    return GuidePipelineResult(
        success=failed < len(results),
        guides_processed=results,
        published_count=published,
        draft_count=drafts,
        failed_count=failed,
        duration_seconds=duration,
    )


# =============================================================================
# SCHEDULE CHECKING
# =============================================================================


def should_run_guide_pipeline() -> bool:
    """
    Check if the guide pipeline should run.

    Runs twice per week (Monday and Thursday) to produce ~8 guides/month.
    Only runs if we haven't already produced a guide today.
    """
    now = datetime.now(PT_TIMEZONE)

    # Run on Monday (0) and Thursday (3)
    if now.weekday() not in [0, 3]:
        return False

    # Check if we've already created a guide today
    supabase = get_supabase_client()
    today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)

    existing = supabase.table("guides").select("id").gte(
        "created_at", today_start.isoformat()
    ).execute()

    if existing.data:
        logger.info(f"Already created {len(existing.data)} guide(s) today")
        return False

    return True


# =============================================================================
# CRON ENTRY POINT
# =============================================================================


async def run_guide_generation() -> dict[str, Any]:
    """
    Entry point for cron job.

    Returns dict suitable for logging/reporting.
    """
    if not should_run_guide_pipeline():
        return {
            "success": True,
            "status": "not_scheduled",
            "message": "Guide generation not scheduled for today",
        }

    result = await run_guide_pipeline(max_guides=2)

    return {
        "success": result.success,
        "status": "completed",
        "published": result.published_count,
        "drafts": result.draft_count,
        "failed": result.failed_count,
        "duration_seconds": result.duration_seconds,
        "guides": [
            {
                "title": g.title,
                "status": g.status,
                "slug": g.slug,
                "confidence": g.confidence,
            }
            for g in result.guides_processed
        ],
    }
