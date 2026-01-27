"""Guide generation orchestrator for autonomous guide production.

This orchestrator handles the complete guide generation pipeline:
1. Topic discovery and selection
2. Research and planning
3. Content generation
4. Approval panel (3 reviewers)
5. Publication or draft

Usage:
    from pipeline.guide_orchestrator import run_guide_pipeline

    result = await run_guide_pipeline(max_guides=2)

Design:
    - Runs 2x/week as part of cron job
    - Target: 2 guides/week (8/month)
    - Uses same approval pattern as resort content
"""

import asyncio
import json
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
    list_guides,
)
from shared.primitives.research import search_resort_info
from shared.primitives.publishing import revalidate_page
from shared.supabase_client import get_supabase_client

logger = logging.getLogger(__name__)
PT_TIMEZONE = ZoneInfo("America/Los_Angeles")


# =============================================================================
# RESULT CLASSES
# =============================================================================


@dataclass
class GuideApprovalVote:
    """A single reviewer's vote on guide content."""

    reviewer: str  # TrustGuard, FamilyValue, VoiceCoach
    approved: bool
    confidence: float
    reasoning: str
    suggestions: list[str] = field(default_factory=list)


@dataclass
class GuideApprovalResult:
    """Result of the 3-agent approval panel."""

    approved: bool
    votes: list[GuideApprovalVote]
    unanimous: bool
    majority_confidence: float
    summary: str


@dataclass
class GuideResult:
    """Result of processing a single guide."""

    success: bool
    guide_id: str | None = None
    slug: str | None = None
    title: str | None = None
    status: str = "unknown"  # draft, published, failed
    confidence: float = 0.0
    approval_result: GuideApprovalResult | None = None
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
# APPROVAL PANEL
# =============================================================================


async def run_approval_panel(
    guide_title: str,
    guide_type: str,
    content: dict[str, Any],
    outline: GuideOutline,
) -> GuideApprovalResult:
    """
    Run the 3-agent approval panel on guide content.

    Reviewers:
    - TrustGuard: Fact accuracy, source reliability
    - FamilyValue: Usefulness for families
    - VoiceCoach: Tone and brand consistency

    Approval requires 2/3 majority.
    """
    import anthropic
    from shared.config import settings

    client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    votes = []

    content_summary = json.dumps(content, indent=2, default=str)[:4000]

    # Reviewer 1: TrustGuard - Fact accuracy
    trust_prompt = f"""You are TrustGuard, a fact-checking reviewer for ski guides.

GUIDE: {guide_title} ({guide_type})

CONTENT:
{content_summary}

Review for:
1. Factual accuracy - Are claims verifiable?
2. Source reliability - Could this be verified against resort websites?
3. Currency - Is information likely current?
4. Completeness - Are important caveats included?

Return JSON:
{{
    "approved": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence assessment",
    "suggestions": ["improvement1", "improvement2"]
}}

Be strict. Reject if you find factual errors or unsupported claims."""

    # Reviewer 2: FamilyValue - Usefulness for families
    family_prompt = f"""You are FamilyValue, reviewing guides for family usefulness.

GUIDE: {guide_title} ({guide_type})

CONTENT:
{content_summary}

Review for:
1. Actionability - Can families use this to make decisions?
2. Relevance - Does this address real family concerns?
3. Age-appropriate - Does it consider different child ages?
4. Practicality - Are tips actually doable?

Return JSON:
{{
    "approved": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence assessment",
    "suggestions": ["improvement1", "improvement2"]
}}

Be helpful. Approve if families will find this useful."""

    # Reviewer 3: VoiceCoach - Tone and brand
    voice_prompt = f"""You are VoiceCoach, reviewing content for brand voice consistency.

GUIDE: {guide_title} ({guide_type})

CONTENT:
{content_summary}

BRAND VOICE: Snowthere - warm, practical, encouraging. Like a helpful ski mom friend.
- Uses "you" and "your family"
- Specific and actionable, not generic
- Encouraging without being overwhelming
- Honest about challenges

Review for:
1. Voice consistency - Does it sound like Snowthere?
2. Engagement - Is it readable and compelling?
3. Tone - Is it appropriate for the content type?
4. Clarity - Is it easy to understand?

Return JSON:
{{
    "approved": true/false,
    "confidence": 0.0-1.0,
    "reasoning": "2-3 sentence assessment",
    "suggestions": ["improvement1", "improvement2"]
}}

Be generous. Approve if voice is generally on-brand."""

    # Run all three reviews
    reviewers = [
        ("TrustGuard", trust_prompt),
        ("FamilyValue", family_prompt),
        ("VoiceCoach", voice_prompt),
    ]

    for reviewer_name, prompt in reviewers:
        try:
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
                system="You are a content reviewer. Return valid JSON only.",
            )

            text = response.content[0].text
            # Parse JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            parsed = json.loads(text.strip())

            votes.append(GuideApprovalVote(
                reviewer=reviewer_name,
                approved=parsed.get("approved", False),
                confidence=float(parsed.get("confidence", 0.5)),
                reasoning=parsed.get("reasoning", ""),
                suggestions=parsed.get("suggestions", []),
            ))

        except Exception as e:
            logger.error(f"{reviewer_name} review failed: {e}")
            # Conservative: count as rejection if review fails
            votes.append(GuideApprovalVote(
                reviewer=reviewer_name,
                approved=False,
                confidence=0.3,
                reasoning=f"Review failed: {e}",
            ))

    # Calculate approval (2/3 majority)
    approval_count = sum(1 for v in votes if v.approved)
    approved = approval_count >= 2
    unanimous = approval_count == 3

    avg_confidence = sum(v.confidence for v in votes) / len(votes) if votes else 0

    summary_parts = []
    for v in votes:
        status = "approved" if v.approved else "rejected"
        summary_parts.append(f"{v.reviewer}: {status} ({v.confidence:.2f})")

    return GuideApprovalResult(
        approved=approved,
        votes=votes,
        unanimous=unanimous,
        majority_confidence=avg_confidence,
        summary="; ".join(summary_parts),
    )


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

        # Stage 5: Run approval panel
        logger.info(f"  Running approval panel...")
        approval = await run_approval_panel(
            topic.title,
            topic.guide_type,
            content,
            outline,
        )

        logger.info(f"  Approval: {approval.summary}")

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

        return GuideResult(
            success=True,
            guide_id=guide_id,
            slug=slug,
            title=topic.title,
            status=final_status,
            confidence=approval.majority_confidence,
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
