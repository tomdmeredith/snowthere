"""MCP Server for Snowthere - Exposes all primitives as tools.

This server enables Claude Code to orchestrate content creation autonomously
by providing access to all 50+ atomic primitives following Agent Native principles.

Run with: python -m mcp_server.server
Or: uv run mcp_server/server.py
"""

from typing import Any
from mcp.server.fastmcp import FastMCP

# Import all primitives
from shared.primitives import (
    # Research
    exa_search,
    serp_search,
    tavily_search,
    search_resort_info,
    scrape_url,
    # Content
    write_section,
    generate_faq,
    apply_voice,
    generate_seo_meta,
    # Database - Resort CRUD
    list_resorts,
    get_resort,
    get_resort_by_slug,
    create_resort,
    update_resort,
    delete_resort,
    search_resorts,
    get_resort_full,
    # Database - Content
    get_resort_content,
    update_resort_content,
    # Database - Costs
    get_resort_costs,
    update_resort_costs,
    # Database - Family Metrics
    get_resort_family_metrics,
    update_resort_family_metrics,
    # Database - Ski Passes
    list_ski_passes,
    get_ski_pass,
    get_resort_passes,
    add_resort_pass,
    remove_resort_pass,
    # Database - Calendar
    get_resort_calendar,
    update_resort_calendar,
    # Publishing
    publish_resort,
    unpublish_resort,
    archive_resort,
    restore_resort,
    revalidate_resort_page,
    revalidate_page,
    revalidate_multiple_pages,
    publish_multiple_resorts,
    get_publish_candidates,
    get_stale_resorts,
    mark_resort_refreshed,
    # System - Cost
    log_cost,
    get_daily_spend,
    check_budget,
    get_cost_breakdown,
    # System - Audit
    log_reasoning,
    read_audit_log,
    get_task_audit_trail,
    get_recent_activity,
    # System - Queue
    queue_task,
    get_next_task,
    update_task_status,
    list_queue,
    get_queue_stats,
    clear_completed_tasks,
)

# Create MCP server
mcp = FastMCP(
    name="snowthere",
    version="1.0.0",
    instructions="""Snowthere MCP Server - Family Ski Resort Directory

This server provides tools for researching ski resorts, generating family-focused
content in 'instagram mom' voice, and managing publication lifecycle.

WORKFLOW:
1. Research: Use research tools to gather data about a resort
2. Generate: Use content tools to create sections in the right voice
3. Store: Use database tools to save content
4. Publish: Use publishing tools to make content live

VOICE: All content should be in 'instagram_mom' voice - encouraging, practical,
relatable. Like a helpful friend who's done all the research.

AUTONOMY: This server enables fully autonomous content generation. Use
confidence scoring to decide whether to auto-publish or flag for review.
""",
)


# =============================================================================
# RESEARCH TOOLS
# =============================================================================


@mcp.tool()
async def tool_exa_search(
    query: str,
    num_results: int = 10,
    use_autoprompt: bool = True,
) -> dict[str, Any]:
    """Search using Exa's semantic search API.

    Best for: Finding family ski reviews, trip reports, detailed articles.
    Returns rich results with content snippets.
    """
    return await exa_search(query, num_results, use_autoprompt)


@mcp.tool()
async def tool_serp_search(
    query: str,
    num_results: int = 10,
) -> dict[str, Any]:
    """Search Google via SerpAPI.

    Best for: Official resort sites, pricing pages, Google reviews.
    """
    return await serp_search(query, num_results)


@mcp.tool()
async def tool_tavily_search(
    query: str,
    search_depth: str = "basic",
    include_answer: bool = True,
) -> dict[str, Any]:
    """Search using Tavily's AI-powered research API.

    Best for: General web research, news, updates.
    Set search_depth='advanced' for deeper research.
    """
    return await tavily_search(query, search_depth, include_answer)


@mcp.tool()
async def tool_search_resort_info(
    resort_name: str,
    country: str,
) -> dict[str, Any]:
    """Comprehensive resort research using all search APIs in parallel.

    This is the primary research tool - it queries Exa, SerpAPI, and Tavily
    simultaneously to gather comprehensive information about a resort.
    Returns combined results from all sources.
    """
    return await search_resort_info(resort_name, country)


@mcp.tool()
async def tool_scrape_url(url: str) -> dict[str, Any]:
    """Fetch and parse a specific URL.

    Use for: Official resort pages, pricing pages, specific articles.
    Returns cleaned text content.
    """
    return await scrape_url(url)


# =============================================================================
# CONTENT GENERATION TOOLS
# =============================================================================


@mcp.tool()
async def tool_write_section(
    section_name: str,
    resort_name: str,
    context: dict[str, Any],
    voice_profile: str = "instagram_mom",
) -> str:
    """Generate a content section for a resort page.

    Section names: quick_take, getting_there, where_to_stay, lift_tickets,
    on_mountain, off_mountain, parent_reviews_summary

    Voice profiles: instagram_mom (default), practical_mom, excited_mom, budget_mom
    """
    return await write_section(section_name, resort_name, context, voice_profile)


@mcp.tool()
async def tool_generate_faq(
    resort_name: str,
    context: dict[str, Any],
    num_questions: int = 6,
) -> list[dict[str, str]]:
    """Generate FAQ section for a resort.

    Creates family-focused questions with Schema.org-ready answers.
    """
    return await generate_faq(resort_name, context, num_questions)


@mcp.tool()
async def tool_apply_voice(
    content: str,
    voice_profile: str = "instagram_mom",
) -> str:
    """Transform content to match a voice profile.

    Use to adjust tone of existing content.
    """
    return await apply_voice(content, voice_profile)


@mcp.tool()
async def tool_generate_seo_meta(
    resort_name: str,
    country: str,
    quick_take: str,
) -> dict[str, str]:
    """Generate SEO metadata for a resort page.

    Returns: title (50-60 chars), description (150-160 chars), keywords
    """
    return await generate_seo_meta(resort_name, country, quick_take)


# =============================================================================
# DATABASE TOOLS - RESORT CRUD
# =============================================================================


@mcp.tool()
def tool_list_resorts(
    country: str | None = None,
    region: str | None = None,
    status: str | None = None,
    limit: int = 100,
    offset: int = 0,
) -> list[dict]:
    """List all resorts, optionally filtered.

    Status options: draft, published, archived
    """
    return list_resorts(country, region, status, limit, offset)


@mcp.tool()
def tool_get_resort(resort_id: str) -> dict | None:
    """Get a resort by its UUID."""
    return get_resort(resort_id)


@mcp.tool()
def tool_get_resort_by_slug(slug: str, country: str) -> dict | None:
    """Get a resort by its URL slug and country."""
    return get_resort_by_slug(slug, country)


@mcp.tool()
def tool_create_resort(
    name: str,
    country: str,
    region: str,
    slug: str | None = None,
    latitude: float | None = None,
    longitude: float | None = None,
) -> dict:
    """Create a new resort entry.

    Slug is auto-generated from name if not provided.
    Returns the created resort record.
    """
    return create_resort(name, country, region, slug, latitude, longitude)


@mcp.tool()
def tool_update_resort(resort_id: str, updates: dict[str, Any]) -> dict:
    """Update resort basic info (name, region, coordinates)."""
    return update_resort(resort_id, updates)


@mcp.tool()
def tool_delete_resort(resort_id: str, hard_delete: bool = False) -> bool:
    """Delete a resort.

    Default is soft delete (archive). Set hard_delete=True to permanently remove.
    """
    return delete_resort(resort_id, hard_delete)


@mcp.tool()
def tool_search_resorts(
    query: str,
    filters: dict[str, Any] | None = None,
    limit: int = 20,
) -> list[dict]:
    """Search resorts by name, country, or region."""
    return search_resorts(query, filters, limit)


@mcp.tool()
def tool_get_resort_full(resort_id: str) -> dict | None:
    """Get complete resort data including all related tables.

    Returns: resort + content + costs + family_metrics + passes + calendar
    """
    return get_resort_full(resort_id)


# =============================================================================
# DATABASE TOOLS - CONTENT
# =============================================================================


@mcp.tool()
def tool_get_resort_content(resort_id: str) -> dict | None:
    """Get all content sections for a resort."""
    return get_resort_content(resort_id)


@mcp.tool()
def tool_update_resort_content(
    resort_id: str,
    content: dict[str, Any],
) -> dict:
    """Update content sections for a resort.

    Content fields: quick_take, getting_there, where_to_stay, lift_tickets,
    on_mountain, off_mountain, parent_reviews_summary, faqs, seo_meta, llms_txt
    """
    return update_resort_content(resort_id, content)


# =============================================================================
# DATABASE TOOLS - COSTS
# =============================================================================


@mcp.tool()
def tool_get_resort_costs(resort_id: str) -> dict | None:
    """Get pricing information for a resort."""
    return get_resort_costs(resort_id)


@mcp.tool()
def tool_update_resort_costs(
    resort_id: str,
    costs: dict[str, Any],
) -> dict:
    """Update pricing information.

    Fields: currency, lift_adult_daily, lift_child_daily, lift_family_daily,
    lodging_budget_nightly, lodging_mid_nightly, lodging_luxury_nightly,
    meal_family_avg, estimated_family_daily
    """
    return update_resort_costs(resort_id, costs)


# =============================================================================
# DATABASE TOOLS - FAMILY METRICS
# =============================================================================


@mcp.tool()
def tool_get_resort_family_metrics(resort_id: str) -> dict | None:
    """Get family-specific metrics for a resort."""
    return get_resort_family_metrics(resort_id)


@mcp.tool()
def tool_update_resort_family_metrics(
    resort_id: str,
    metrics: dict[str, Any],
) -> dict:
    """Update family metrics.

    Fields: family_overall_score (1-10), best_age_min, best_age_max,
    kid_friendly_terrain_pct, has_childcare, childcare_min_age (months),
    ski_school_min_age (years), kids_ski_free_age, has_magic_carpet,
    has_terrain_park_kids, perfect_if (list), skip_if (list)
    """
    return update_resort_family_metrics(resort_id, metrics)


# =============================================================================
# DATABASE TOOLS - SKI PASSES
# =============================================================================


@mcp.tool()
def tool_list_ski_passes(pass_type: str | None = None) -> list[dict]:
    """List all ski passes.

    Types: mega (Epic, Ikon), regional, single
    """
    return list_ski_passes(pass_type)


@mcp.tool()
def tool_get_ski_pass(pass_id: str) -> dict | None:
    """Get details about a specific ski pass."""
    return get_ski_pass(pass_id)


@mcp.tool()
def tool_get_resort_passes(resort_id: str) -> list[dict]:
    """Get all ski passes that include a resort."""
    return get_resort_passes(resort_id)


@mcp.tool()
def tool_add_resort_pass(
    resort_id: str,
    pass_id: str,
    access_type: str = "full",
) -> dict:
    """Add a ski pass to a resort.

    Access types: full, limited, blackout
    """
    return add_resort_pass(resort_id, pass_id, access_type)


@mcp.tool()
def tool_remove_resort_pass(resort_id: str, pass_id: str) -> bool:
    """Remove a ski pass from a resort."""
    return remove_resort_pass(resort_id, pass_id)


# =============================================================================
# DATABASE TOOLS - CALENDAR
# =============================================================================


@mcp.tool()
def tool_get_resort_calendar(resort_id: str) -> list[dict]:
    """Get ski quality calendar for all 12 months."""
    return get_resort_calendar(resort_id)


@mcp.tool()
def tool_update_resort_calendar(
    resort_id: str,
    month: int,
    data: dict[str, Any],
) -> dict:
    """Update calendar data for a specific month.

    Month: 1-12
    Data: snow_quality_score (1-5), crowd_level (low/medium/high),
    family_recommendation (1-10), notes
    """
    return update_resort_calendar(resort_id, month, data)


# =============================================================================
# PUBLISHING TOOLS
# =============================================================================


@mcp.tool()
def tool_publish_resort(
    resort_id: str,
    task_id: str | None = None,
    trigger_revalidation: bool = True,
) -> dict:
    """Publish a resort (draft → published).

    Optionally triggers Vercel ISR page revalidation.
    """
    return publish_resort(resort_id, task_id, trigger_revalidation)


@mcp.tool()
def tool_unpublish_resort(
    resort_id: str,
    task_id: str | None = None,
    trigger_revalidation: bool = True,
) -> dict:
    """Unpublish a resort (published → draft)."""
    return unpublish_resort(resort_id, task_id, trigger_revalidation)


@mcp.tool()
def tool_archive_resort(
    resort_id: str,
    task_id: str | None = None,
    reason: str | None = None,
) -> dict:
    """Archive a resort (soft delete).

    Preserves all data but hides from public site.
    """
    return archive_resort(resort_id, task_id, reason)


@mcp.tool()
def tool_restore_resort(
    resort_id: str,
    to_status: str = "draft",
    task_id: str | None = None,
) -> dict:
    """Restore an archived resort."""
    return restore_resort(resort_id, to_status, task_id)


@mcp.tool()
def tool_revalidate_resort_page(slug: str, country: str) -> dict[str, Any]:
    """Trigger Vercel ISR revalidation for a resort page."""
    return revalidate_resort_page(slug, country)


@mcp.tool()
def tool_revalidate_page(path: str) -> dict[str, Any]:
    """Trigger Vercel ISR revalidation for any page path."""
    return revalidate_page(path)


@mcp.tool()
def tool_revalidate_multiple_pages(paths: list[str]) -> list[dict[str, Any]]:
    """Batch revalidate multiple pages."""
    return revalidate_multiple_pages(paths)


@mcp.tool()
def tool_publish_multiple_resorts(
    resort_ids: list[str],
    task_id: str | None = None,
) -> dict[str, Any]:
    """Batch publish multiple resorts."""
    return publish_multiple_resorts(resort_ids, task_id)


@mcp.tool()
def tool_get_publish_candidates(
    min_confidence: float = 0.7,
    limit: int = 10,
) -> list[dict]:
    """Get draft resorts ready for publishing.

    Filters by content completeness and optional confidence score.
    """
    return get_publish_candidates(min_confidence, limit)


@mcp.tool()
def tool_get_stale_resorts(
    days_threshold: int = 30,
    limit: int = 20,
) -> list[dict]:
    """Get published resorts needing refresh.

    Returns resorts not updated in days_threshold days.
    """
    return get_stale_resorts(days_threshold, limit)


@mcp.tool()
def tool_mark_resort_refreshed(resort_id: str) -> dict:
    """Update last_refreshed timestamp after content refresh."""
    return mark_resort_refreshed(resort_id)


# =============================================================================
# SYSTEM TOOLS - COST TRACKING
# =============================================================================


@mcp.tool()
def tool_log_cost(
    api_name: str,
    amount_usd: float,
    task_id: str | None = None,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Log API cost for budget tracking.

    API names: exa, serp, tavily, anthropic
    """
    return log_cost(api_name, amount_usd, task_id, metadata)


@mcp.tool()
def tool_get_daily_spend() -> float:
    """Get total API spend for today (UTC)."""
    return get_daily_spend()


@mcp.tool()
def tool_check_budget(
    required_usd: float,
    daily_limit: float = 5.0,
) -> bool:
    """Check if budget allows an operation.

    Returns True if (current_spend + required) <= daily_limit.
    """
    return check_budget(required_usd, daily_limit)


@mcp.tool()
def tool_get_cost_breakdown(days: int = 7) -> dict[str, Any]:
    """Get cost breakdown by API and day for the last N days."""
    return get_cost_breakdown(days)


# =============================================================================
# SYSTEM TOOLS - AUDIT LOG
# =============================================================================


@mcp.tool()
def tool_log_reasoning(
    task_id: str,
    agent_name: str,
    action: str,
    reasoning: str,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Log agent reasoning for observability.

    Creates audit trail of why decisions were made.
    """
    return log_reasoning(task_id, agent_name, action, reasoning, metadata)


@mcp.tool()
def tool_read_audit_log(
    task_id: str | None = None,
    agent_name: str | None = None,
    action: str | None = None,
    limit: int = 100,
) -> list[dict]:
    """Read entries from the audit log."""
    return read_audit_log(task_id, agent_name, action, limit)


@mcp.tool()
def tool_get_task_audit_trail(task_id: str) -> list[dict]:
    """Get complete audit trail for a specific task."""
    return get_task_audit_trail(task_id)


@mcp.tool()
def tool_get_recent_activity(
    hours: int = 24,
    limit: int = 50,
) -> list[dict]:
    """Get recent agent activity."""
    return get_recent_activity(hours, limit)


# =============================================================================
# SYSTEM TOOLS - QUEUE MANAGEMENT
# =============================================================================


@mcp.tool()
def tool_queue_task(
    task_type: str,
    resort_id: str | None = None,
    priority: int = 5,
    metadata: dict[str, Any] | None = None,
) -> dict:
    """Add a task to the content queue.

    Task types: discover, research, generate, geo_optimize, validate, publish
    Priority: 1-10 (higher = more urgent)
    """
    return queue_task(task_type, resort_id, priority, metadata)


@mcp.tool()
def tool_get_next_task(
    task_types: list[str] | None = None,
) -> dict | None:
    """Get the next pending task from the queue.

    Returns highest priority pending task.
    """
    return get_next_task(task_types)


@mcp.tool()
def tool_update_task_status(
    task_id: str,
    status: str,
    error: str | None = None,
) -> dict:
    """Update task status in the queue.

    Statuses: pending, processing, completed, failed
    """
    return update_task_status(task_id, status, error)


@mcp.tool()
def tool_list_queue(
    status: str | None = None,
    task_type: str | None = None,
    limit: int = 50,
) -> list[dict]:
    """List tasks in the content queue."""
    return list_queue(status, task_type, limit)


@mcp.tool()
def tool_get_queue_stats() -> dict[str, Any]:
    """Get queue statistics (counts by status and type)."""
    return get_queue_stats()


@mcp.tool()
def tool_clear_completed_tasks(older_than_days: int = 7) -> int:
    """Remove completed tasks older than N days.

    Returns count of deleted tasks.
    """
    return clear_completed_tasks(older_than_days)


# =============================================================================
# RUN SERVER
# =============================================================================

if __name__ == "__main__":
    # Run in stdio mode for Claude Code integration
    mcp.run(transport="stdio")
