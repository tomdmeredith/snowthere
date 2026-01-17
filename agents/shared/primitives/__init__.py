"""Atomic primitives for agent operations.

Following Agent Native principles, these primitives are the atomic building
blocks that enable agents to achieve any outcome a human editor can.

Organized into four categories:
- Research: Information gathering from external sources
- Content: AI-powered content generation
- Database: CRUD operations for resorts, passes, metrics
- Publishing: Publication lifecycle and page revalidation
- System: Queue management, cost tracking, audit logging
"""

# Research primitives
from .research import (
    exa_search,
    serp_search,
    tavily_search,
    search_resort_info,
    scrape_url,
)

# Content primitives
from .content import (
    write_section,
    generate_faq,
    apply_voice,
    generate_seo_meta,
)

# Database primitives
from .database import (
    # Resort CRUD
    list_resorts,
    get_resort,
    get_resort_by_slug,
    create_resort,
    update_resort,
    delete_resort,
    search_resorts,
    get_resort_full,
    # Resort content
    get_resort_content,
    update_resort_content,
    # Resort costs
    get_resort_costs,
    update_resort_costs,
    # Resort family metrics
    get_resort_family_metrics,
    update_resort_family_metrics,
    # Ski passes
    list_ski_passes,
    get_ski_pass,
    get_resort_passes,
    add_resort_pass,
    remove_resort_pass,
    # Ski calendar
    get_resort_calendar,
    update_resort_calendar,
)

# Publishing primitives
from .publishing import (
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
)

# System primitives
from .system import (
    # Cost tracking
    log_cost,
    get_daily_spend,
    check_budget,
    get_cost_breakdown,
    # Reasoning/audit
    log_reasoning,
    read_audit_log,
    get_task_audit_trail,
    get_recent_activity,
    # Queue management
    queue_task,
    get_next_task,
    update_task_status,
    list_queue,
    get_queue_stats,
    clear_completed_tasks,
)

__all__ = [
    # Research
    "exa_search",
    "serp_search",
    "tavily_search",
    "search_resort_info",
    "scrape_url",
    # Content
    "write_section",
    "generate_faq",
    "apply_voice",
    "generate_seo_meta",
    # Database - Resort CRUD
    "list_resorts",
    "get_resort",
    "get_resort_by_slug",
    "create_resort",
    "update_resort",
    "delete_resort",
    "search_resorts",
    "get_resort_full",
    # Database - Resort content
    "get_resort_content",
    "update_resort_content",
    # Database - Resort costs
    "get_resort_costs",
    "update_resort_costs",
    # Database - Resort family metrics
    "get_resort_family_metrics",
    "update_resort_family_metrics",
    # Database - Ski passes
    "list_ski_passes",
    "get_ski_pass",
    "get_resort_passes",
    "add_resort_pass",
    "remove_resort_pass",
    # Database - Ski calendar
    "get_resort_calendar",
    "update_resort_calendar",
    # Publishing
    "publish_resort",
    "unpublish_resort",
    "archive_resort",
    "restore_resort",
    "revalidate_resort_page",
    "revalidate_page",
    "revalidate_multiple_pages",
    "publish_multiple_resorts",
    "get_publish_candidates",
    "get_stale_resorts",
    "mark_resort_refreshed",
    # System - Cost tracking
    "log_cost",
    "get_daily_spend",
    "check_budget",
    "get_cost_breakdown",
    # System - Reasoning/audit
    "log_reasoning",
    "read_audit_log",
    "get_task_audit_trail",
    "get_recent_activity",
    # System - Queue management
    "queue_task",
    "get_next_task",
    "update_task_status",
    "list_queue",
    "get_queue_stats",
    "clear_completed_tasks",
]
