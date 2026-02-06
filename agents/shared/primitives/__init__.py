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
    flatten_sources,
    extract_coordinates,
)

# Research cache primitives
from .research_cache import (
    get_cached_results,
    cache_results,
    store_resort_sources,
    mark_sources_cited,
    get_cache_stats,
    clear_expired_cache,
)

# Content primitives
from .content import (
    write_section,
    generate_faq,
    apply_voice,
    generate_seo_meta,
    generate_country_intro,
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
    # Existence checking (agent-native duplicate detection)
    check_resort_exists,
    find_similar_resorts,
    count_resorts,
    get_country_coverage_summary,
    # Portfolio diversity (Agent-Native tagline - Round 12)
    get_recent_portfolio_taglines,
)

# Discovery primitives
from .discovery import (
    check_discovery_candidate_exists,
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
    request_indexing,
    get_uncrawled_urls,
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

# Alerts primitives
from .alerts import (
    send_slack_alert,
    alert_pipeline_error,
    alert_pipeline_summary,
    alert_budget_warning,
    alert_startup_failure,
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
    # Resort validation (agent-native duplicate detection)
    validate_resort_selection,
    ResortValidationResult,
    # Content generation (legacy)
    generate_tagline,
    # Tagline generation (Agent-Native - Round 12)
    extract_tagline_atoms,
    generate_diverse_tagline,
    evaluate_tagline_quality,
    TaglineAtoms,
    TaglineQualityScore,
    # Resort data extraction
    extract_resort_data,
    ExtractedResortData,
    # Link curation
    curate_resort_links,
    CuratedLink,
    LinkCurationResult,
)

# Cost acquisition primitives (Multi-strategy pricing)
from .costs import (
    # Data classes
    CostResult,
    # Core acquisition
    acquire_resort_costs,
    get_cached_pricing,
    cache_pricing_result,
    # Individual strategies
    get_pass_network_pricing,
    search_targeted_pricing,
    scrape_resort_pricing_page,
    find_pricing_page,
    extract_pricing_with_claude,
    # Utilities
    get_currency_for_country,
    convert_to_usd,
    update_usd_columns,
    parse_prices_from_text,
    extract_pricing_from_html,
    # Constants
    COUNTRY_CURRENCIES,
    USD_RATES,
)

# Quality audit primitives
from .quality import (
    # Enums and data classes
    IssueSeverity,
    IssueType,
    QualityIssue,
    AuditResult,
    CheckResult,
    PageQualityScore,
    # Formula-based checks
    check_staleness,
    check_low_confidence,
    check_completeness,
    get_resorts_needing_audit,
    get_stale_resorts_count,
    # Perfect Page Checklist
    PERFECT_PAGE_CHECKLIST,
    score_resort_page,
    get_resorts_below_quality_threshold,
    queue_quality_improvements,
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

# Official Images primitives (Real photos from resort websites)
from .official_images import (
    OfficialImageResult,
    fetch_official_resort_image,
    fetch_resort_images_with_fallback,
    find_resort_website,
    extract_images_from_page,
    download_and_store_image,
    delete_ai_generated_images,
    count_ai_generated_images,
)

# Approval Panel primitives (Three-agent quality evaluation)
from .approval import (
    # Data classes
    EvaluationResult,
    PanelResult,
    ApprovalLoopResult,
    # Atomic evaluation primitives
    evaluate_trust,
    evaluate_completeness,
    evaluate_voice,
    # Orchestration
    run_approval_panel,
    # Content improvement
    improve_content,
    # Full loop
    approval_loop,
    # Utilities
    format_panel_summary,
    format_loop_summary,
    # Constants
    REQUIRED_SECTIONS,
)

# External linking primitives (Google Places, affiliates)
from .external_links import (
    # Data classes
    ResolvedEntity,
    AffiliateConfig,
    InjectedLink,
    LinkInjectionResult,
    # Cache operations
    clear_expired_cache as clear_entity_cache,
    # Google Places
    resolve_google_place,
    # Affiliate URLs
    lookup_affiliate_url,
    # Main resolution
    resolve_entity_link,
    # Link injection (Round 7.3)
    inject_external_links,
    inject_links_in_content_sections,
    # Utilities
    get_rel_attribute,
)

# Entity extraction from intelligence
from .intelligence import (
    extract_linkable_entities,
    ExtractedEntity,
    EntityExtractionResult,
    # Quick Take context extraction (Round 8)
    extract_quick_take_context,
    QuickTakeContextResult,
)

# Quick Take generation primitives (Round 8)
from .quick_take import (
    # Data classes
    QuickTakeContext,
    QuickTakeResult,
    # Main generation
    generate_quick_take,
    regenerate_quick_take_if_invalid,
    # Quality metrics
    calculate_specificity_score,
    check_forbidden_phrases,
    validate_quick_take,
    # Constants
    FORBIDDEN_PHRASES,
)

# Expert Panel primitives (Content-agnostic quality evaluation)
from .expert_panel import (
    # Data classes
    ExpertRole,
    ExpertPanelResult,
    ExpertApprovalLoopResult,
    # Expert definitions
    ACCURACY_EXPERT,
    FAMILY_USEFULNESS_EXPERT,
    VOICE_EXPERT,
    SEO_GEO_EXPERT,
    SKEPTIC_EXPERT,
    BUSY_PARENT_EXPERT,
    # Registry
    EXPERT_PANELS,
    get_experts_for_content_type,
    # Evaluation
    evaluate_with_expert,
    run_expert_panel as run_content_expert_panel,
    # Review
    review_and_summarize,
    # Approval loop
    expert_approval_loop,
    improve_content_from_panel,
    log_panel_result,
    # Voice cleanup
    apply_voice_cleanup,
)

# Scoring primitives (Deterministic family score calculation)
from .scoring import (
    # Data classes
    ScoreBreakdown,
    # Core calculation
    calculate_family_score,
    calculate_family_score_with_breakdown,
    calculate_data_completeness,
    KEY_COMPLETENESS_FIELDS,
    # Formatting
    format_score_explanation,
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
    "flatten_sources",
    "extract_coordinates",
    # Content
    "write_section",
    "generate_faq",
    "apply_voice",
    "generate_seo_meta",
    # Content - Country pages
    "generate_country_intro",
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
    # Database - Existence checking (agent-native)
    "check_resort_exists",
    "find_similar_resorts",
    "count_resorts",
    "get_country_coverage_summary",
    # Discovery
    "check_discovery_candidate_exists",
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
    # Publishing - Indexing
    "request_indexing",
    "get_uncrawled_urls",
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
    # Alerts
    "send_slack_alert",
    "alert_pipeline_error",
    "alert_pipeline_summary",
    "alert_budget_warning",
    "alert_startup_failure",
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
    # Intelligence - Resort validation (agent-native)
    "validate_resort_selection",
    "ResortValidationResult",
    # Intelligence - Content generation
    "generate_tagline",
    # Intelligence - Resort data extraction
    "extract_resort_data",
    "ExtractedResortData",
    # Intelligence - Link curation
    "curate_resort_links",
    "CuratedLink",
    "LinkCurationResult",
    # Cost acquisition - Data classes
    "CostResult",
    # Cost acquisition - Core
    "acquire_resort_costs",
    "get_cached_pricing",
    "cache_pricing_result",
    # Cost acquisition - Strategies
    "get_pass_network_pricing",
    "search_targeted_pricing",
    "scrape_resort_pricing_page",
    "find_pricing_page",
    "extract_pricing_with_claude",
    # Cost acquisition - Utilities
    "get_currency_for_country",
    "convert_to_usd",
    "update_usd_columns",
    "parse_prices_from_text",
    "extract_pricing_from_html",
    # Cost acquisition - Constants
    "COUNTRY_CURRENCIES",
    "USD_RATES",
    # Quality - Enums and data classes
    "IssueSeverity",
    "IssueType",
    "QualityIssue",
    "AuditResult",
    "CheckResult",
    "PageQualityScore",
    # Quality - Formula-based checks
    "check_staleness",
    "check_low_confidence",
    "check_completeness",
    "get_resorts_needing_audit",
    "get_stale_resorts_count",
    # Quality - Perfect Page Checklist
    "PERFECT_PAGE_CHECKLIST",
    "score_resort_page",
    "get_resorts_below_quality_threshold",
    "queue_quality_improvements",
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
    # Approval Panel - Data classes
    "EvaluationResult",
    "PanelResult",
    "ApprovalLoopResult",
    # Approval Panel - Atomic evaluation primitives
    "evaluate_trust",
    "evaluate_completeness",
    "evaluate_voice",
    # Approval Panel - Orchestration
    "run_approval_panel",
    # Approval Panel - Content improvement
    "improve_content",
    # Approval Panel - Full loop
    "approval_loop",
    # Approval Panel - Utilities
    "format_panel_summary",
    "format_loop_summary",
    # Approval Panel - Constants
    "REQUIRED_SECTIONS",
    # Official Images - Data classes
    "OfficialImageResult",
    # Official Images - Main functions
    "fetch_official_resort_image",
    "fetch_resort_images_with_fallback",
    "find_resort_website",
    "extract_images_from_page",
    "download_and_store_image",
    # Official Images - Cleanup
    "delete_ai_generated_images",
    "count_ai_generated_images",
    # External Links - Data classes
    "ResolvedEntity",
    "AffiliateConfig",
    # External Links - Cache operations
    "clear_entity_cache",
    # External Links - Google Places
    "resolve_google_place",
    # External Links - Affiliate URLs
    "lookup_affiliate_url",
    # External Links - Main resolution
    "resolve_entity_link",
    # External Links - Utilities
    "get_rel_attribute",
    # Entity Extraction
    "extract_linkable_entities",
    "ExtractedEntity",
    "EntityExtractionResult",
    # Quick Take Context Extraction (Round 8)
    "extract_quick_take_context",
    "QuickTakeContextResult",
    # Quick Take Generation (Round 8)
    "QuickTakeContext",
    "QuickTakeResult",
    "generate_quick_take",
    "regenerate_quick_take_if_invalid",
    "calculate_specificity_score",
    "check_forbidden_phrases",
    "validate_quick_take",
    "FORBIDDEN_PHRASES",
    # Scoring (Round 9 - Deterministic formula)
    "ScoreBreakdown",
    "calculate_family_score",
    "calculate_family_score_with_breakdown",
    "calculate_data_completeness",
    "KEY_COMPLETENESS_FIELDS",
    "format_score_explanation",
    # Expert Panel - Data classes
    "ExpertRole",
    "ExpertPanelResult",
    "ExpertApprovalLoopResult",
    # Expert Panel - Expert definitions
    "ACCURACY_EXPERT",
    "FAMILY_USEFULNESS_EXPERT",
    "VOICE_EXPERT",
    "SEO_GEO_EXPERT",
    "SKEPTIC_EXPERT",
    "BUSY_PARENT_EXPERT",
    # Expert Panel - Registry
    "EXPERT_PANELS",
    "get_experts_for_content_type",
    # Expert Panel - Evaluation
    "evaluate_with_expert",
    "run_content_expert_panel",
    # Expert Panel - Review
    "review_and_summarize",
    # Expert Panel - Approval loop
    "expert_approval_loop",
    "improve_content_from_panel",
    "log_panel_result",
    # Expert Panel - Voice cleanup
    "apply_voice_cleanup",
]
