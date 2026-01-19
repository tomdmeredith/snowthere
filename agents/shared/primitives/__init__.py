"""Atomic primitives for agent operations.

Following Agent Native principles, these primitives are the atomic building
blocks that enable agents to achieve any outcome a human editor can.

Organized into six categories:
- Research: Information gathering from external sources
- Content: AI-powered content generation
- Database: CRUD operations for resorts, passes, metrics
- Publishing: Publication lifecycle and page revalidation
- System: Queue management, cost tracking, audit logging
- Intelligence: LLM-based reasoning and decision-making
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

# Intelligence primitives (Agent Native reasoning)
from .intelligence import (
    # Data quality
    assess_data_quality,
    QualityAssessment,
    # Schema extraction
    synthesize_to_schema,
    # Decision making
    make_decision,
    Decision,
    # Prioritization
    prioritize_items,
    PrioritizedItem,
    # Error handling
    handle_error_intelligently,
    ErrorHandling,
    # Learning
    learn_from_outcome,
    LearningOutcome,
)

# Quality audit primitives
from .quality import (
    # Enums and data classes
    IssueSeverity,
    IssueType,
    QualityIssue,
    AuditResult,
    # Formula-based checks
    check_staleness,
    check_low_confidence,
    check_completeness,
    get_resorts_needing_audit,
    get_stale_resorts_count,
    # Audit logging
    log_quality_issue,
    log_audit_run,
    get_recent_quality_issues,
    # Helpers
    calculate_fix_priority,
    batch_issues_for_fix,
    # Constants
    REQUIRED_CONTENT_SECTIONS,
    OPTIONAL_CONTENT_SECTIONS,
)

# Trail map primitives
from .trail_map import (
    # Data classes
    PisteData,
    LiftData,
    TrailMapResult,
    TrailMapQuality,
    TrailDifficulty,
    # Main functions
    get_trail_map,
    search_resort_location,
    get_difficulty_breakdown,
    search_official_trail_map,
    has_trail_map_data,
    # Helpers
    calculate_bbox,
)

# Image generation primitives (3-tier fallback)
from .images import (
    # Enums and data classes
    ImageType,
    ImageProvider,
    AspectRatio,
    ImageResult,
    # Prompt helpers
    get_resort_prompt,
    VIBE_PROMPTS,
    # Provider functions
    generate_with_gemini,
    generate_with_glif,
    generate_with_replicate,
    # Main fallback function
    generate_image_with_fallback,
    provider_configured,
    # Resort-specific generation
    generate_resort_hero_image,
    generate_resort_atmosphere_image,
    generate_resort_image_set,
    # Database operations
    save_resort_image,
    get_resort_images,
    get_resort_hero_image,
    delete_resort_images,
    # Storage
    upload_image_to_storage,
)

# UGC Photos primitives (Google Places API)
from .ugc_photos import (
    # Data classes
    PhotoCategory,
    UGCPhoto,
    UGCPhotoResult,
    # Google Places functions
    find_place_id,
    get_place_details,
    fetch_place_photo,
    # Main functions
    fetch_ugc_photos,
    fetch_and_store_ugc_photos,
    get_ugc_photos_for_resort,
    # Vision classification
    classify_photo_with_vision,
)

# Linking primitives (Similar resorts, internal links)
from .linking import (
    # Constants
    SIMILARITY_WEIGHTS,
    PRICE_TIERS,
    REGION_GROUPS,
    LinkType,
    # Data classes
    SimilarityResult,
    SimilarResort,
    InternalLink,
    # Similarity calculation
    calculate_similarity,
    store_similarity,
    get_similar_resorts,
    get_similarity_score,
    # Internal links
    create_internal_link,
    get_internal_links,
    generate_anchor_text,
    # Batch operations
    calculate_similarities_for_resort,
    generate_links_for_resort,
    refresh_all_similarities,
    # Utilities
    get_shared_features,
    delete_stale_similarities,
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
    # Intelligence - Data quality
    "assess_data_quality",
    "QualityAssessment",
    # Intelligence - Schema extraction
    "synthesize_to_schema",
    # Intelligence - Decision making
    "make_decision",
    "Decision",
    # Intelligence - Prioritization
    "prioritize_items",
    "PrioritizedItem",
    # Intelligence - Error handling
    "handle_error_intelligently",
    "ErrorHandling",
    # Intelligence - Learning
    "learn_from_outcome",
    "LearningOutcome",
    # Quality - Enums and data classes
    "IssueSeverity",
    "IssueType",
    "QualityIssue",
    "AuditResult",
    # Quality - Formula-based checks
    "check_staleness",
    "check_low_confidence",
    "check_completeness",
    "get_resorts_needing_audit",
    "get_stale_resorts_count",
    # Quality - Audit logging
    "log_quality_issue",
    "log_audit_run",
    "get_recent_quality_issues",
    # Quality - Helpers
    "calculate_fix_priority",
    "batch_issues_for_fix",
    # Quality - Constants
    "REQUIRED_CONTENT_SECTIONS",
    "OPTIONAL_CONTENT_SECTIONS",
    # Trail map - Data classes
    "PisteData",
    "LiftData",
    "TrailMapResult",
    "TrailMapQuality",
    "TrailDifficulty",
    # Trail map - Main functions
    "get_trail_map",
    "search_resort_location",
    "get_difficulty_breakdown",
    "search_official_trail_map",
    "has_trail_map_data",
    # Trail map - Helpers
    "calculate_bbox",
    # Image generation - Enums and data classes
    "ImageType",
    "ImageProvider",
    "AspectRatio",
    "ImageResult",
    # Image generation - Prompt helpers
    "get_resort_prompt",
    "VIBE_PROMPTS",
    # Image generation - Provider functions
    "generate_with_gemini",
    "generate_with_glif",
    "generate_with_replicate",
    # Image generation - Main fallback function
    "generate_image_with_fallback",
    "provider_configured",
    # Image generation - Resort-specific
    "generate_resort_hero_image",
    "generate_resort_atmosphere_image",
    "generate_resort_image_set",
    # Image generation - Database operations
    "save_resort_image",
    "get_resort_images",
    "get_resort_hero_image",
    "delete_resort_images",
    # Image generation - Storage
    "upload_image_to_storage",
    # UGC Photos - Data classes
    "PhotoCategory",
    "UGCPhoto",
    "UGCPhotoResult",
    # UGC Photos - Google Places functions
    "find_place_id",
    "get_place_details",
    "fetch_place_photo",
    # UGC Photos - Main functions
    "fetch_ugc_photos",
    "fetch_and_store_ugc_photos",
    "get_ugc_photos_for_resort",
    # UGC Photos - Vision classification
    "classify_photo_with_vision",
    # Linking - Constants
    "SIMILARITY_WEIGHTS",
    "PRICE_TIERS",
    "REGION_GROUPS",
    "LinkType",
    # Linking - Data classes
    "SimilarityResult",
    "SimilarResort",
    "InternalLink",
    # Linking - Similarity calculation
    "calculate_similarity",
    "store_similarity",
    "get_similar_resorts",
    "get_similarity_score",
    # Linking - Internal links
    "create_internal_link",
    "get_internal_links",
    "generate_anchor_text",
    # Linking - Batch operations
    "calculate_similarities_for_resort",
    "generate_links_for_resort",
    "refresh_all_similarities",
    # Linking - Utilities
    "get_shared_features",
    "delete_stale_similarities",
]
