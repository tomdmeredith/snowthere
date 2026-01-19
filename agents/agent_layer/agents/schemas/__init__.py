"""Agent-specific data schemas.

These schemas define the data structures used by concrete agent implementations.
Schemas are separate from primitives to maintain clean separation of concerns.
"""

from .quality import (
    QuickScanConfig,
    DeepAuditConfig,
    TriggeredAuditConfig,
    AuditObjective,
    AuditPlanStep,
    QualityAuditPlan,
    QualityObservation,
)

from .discovery import (
    # Config types
    KeywordResearchConfig,
    GapDiscoveryConfig,
    TrendingConfig,
    ExplorationConfig,
    FullDiscoveryConfig,
    # Objective and plan
    DiscoveryObjective,
    DiscoveryPlanStep,
    DiscoveryPlan,
    DiscoveryObservation,
    # Constants
    OPPORTUNITY_WEIGHTS,
    DISCOVERY_SOURCE_PRIORITY,
    DIVERSITY_RULES,
    PASS_NETWORKS,
    REGION_DEFINITIONS,
)

__all__ = [
    # Quality Agent
    "QuickScanConfig",
    "DeepAuditConfig",
    "TriggeredAuditConfig",
    "AuditObjective",
    "AuditPlanStep",
    "QualityAuditPlan",
    "QualityObservation",
    # Discovery Agent
    "KeywordResearchConfig",
    "GapDiscoveryConfig",
    "TrendingConfig",
    "ExplorationConfig",
    "FullDiscoveryConfig",
    "DiscoveryObjective",
    "DiscoveryPlanStep",
    "DiscoveryPlan",
    "DiscoveryObservation",
    "OPPORTUNITY_WEIGHTS",
    "DISCOVERY_SOURCE_PRIORITY",
    "DIVERSITY_RULES",
    "PASS_NETWORKS",
    "REGION_DEFINITIONS",
]
