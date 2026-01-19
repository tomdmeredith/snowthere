"""Schemas for the Discovery Agent.

Defines the configuration, objectives, plans, and observations
used by DiscoveryAgent in its think→act→observe loops.

Discovery modes:
- keyword_research: Analyze search demand for ski resorts
- gap_discovery: Find coverage gaps in pass networks and regions
- trending: Identify trending topics and resorts
- exploration: Random exploration to avoid echo chambers
- full: Run all discovery modes
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Literal


# =============================================================================
# Configuration Types (one per discovery mode)
# =============================================================================


@dataclass
class KeywordResearchConfig:
    """Configuration for keyword research mode."""

    seed_keywords: list[str] = field(default_factory=lambda: [
        "family ski resort",
        "ski with kids",
        "beginner ski resort",
        "kids ski free",
        "ski school",
    ])
    max_keywords: int = 50
    min_search_volume: int = 100
    include_long_tail: bool = True
    countries_focus: list[str] = field(default_factory=list)  # Empty = all


@dataclass
class GapDiscoveryConfig:
    """Configuration for coverage gap discovery mode."""

    check_pass_networks: bool = True
    check_regions: bool = True
    pass_networks: list[str] = field(default_factory=lambda: [
        "Epic",
        "Ikon",
        "Mountain Collective",
    ])
    regions_focus: list[str] = field(default_factory=list)  # Empty = all
    min_gap_score: float = 0.5  # Minimum gap score to consider


@dataclass
class TrendingConfig:
    """Configuration for trending discovery mode."""

    lookback_days: int = 7
    min_trending_score: float = 0.6
    include_news: bool = True
    include_social: bool = True
    exclude_already_covered: bool = True


@dataclass
class ExplorationConfig:
    """Configuration for exploration mode (random discovery)."""

    sample_size: int = 10  # How many random resorts to discover
    diversity_weight: float = 0.5  # Balance between score and diversity
    region_spread: bool = True  # Ensure geographic diversity
    exclude_top_countries: list[str] = field(default_factory=list)  # Avoid oversaturation


@dataclass
class FullDiscoveryConfig:
    """Configuration for full discovery (all modes)."""

    keyword_config: KeywordResearchConfig = field(default_factory=KeywordResearchConfig)
    gap_config: GapDiscoveryConfig = field(default_factory=GapDiscoveryConfig)
    trending_config: TrendingConfig = field(default_factory=TrendingConfig)
    exploration_config: ExplorationConfig = field(default_factory=ExplorationConfig)

    # Resource limits
    max_total_candidates: int = 50
    max_api_cost: float = 5.0  # Budget cap for this run


# =============================================================================
# Discovery Objective
# =============================================================================


DiscoveryMode = Literal["keyword_research", "gap_discovery", "trending", "exploration", "full"]
DiscoveryConfig = (
    KeywordResearchConfig
    | GapDiscoveryConfig
    | TrendingConfig
    | ExplorationConfig
    | FullDiscoveryConfig
)


@dataclass
class DiscoveryObjective:
    """Objective passed to DiscoveryAgent.run()."""

    mode: DiscoveryMode
    config: DiscoveryConfig
    triggered_by: str = "cron"  # cron, manual, orchestrator
    context: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def keyword_research(cls, **config_kwargs) -> "DiscoveryObjective":
        """Create a keyword research objective."""
        return cls(
            mode="keyword_research",
            config=KeywordResearchConfig(**config_kwargs),
        )

    @classmethod
    def gap_discovery(cls, **config_kwargs) -> "DiscoveryObjective":
        """Create a coverage gap discovery objective."""
        return cls(
            mode="gap_discovery",
            config=GapDiscoveryConfig(**config_kwargs),
        )

    @classmethod
    def trending(cls, lookback_days: int = 7, **config_kwargs) -> "DiscoveryObjective":
        """Create a trending discovery objective."""
        return cls(
            mode="trending",
            config=TrendingConfig(lookback_days=lookback_days, **config_kwargs),
        )

    @classmethod
    def exploration(cls, sample_size: int = 10, **config_kwargs) -> "DiscoveryObjective":
        """Create an exploration objective."""
        return cls(
            mode="exploration",
            config=ExplorationConfig(sample_size=sample_size, **config_kwargs),
        )

    @classmethod
    def full(cls, max_candidates: int = 50, **config_kwargs) -> "DiscoveryObjective":
        """Create a full discovery objective (all modes)."""
        return cls(
            mode="full",
            config=FullDiscoveryConfig(max_total_candidates=max_candidates, **config_kwargs),
        )


# =============================================================================
# Discovery Plan
# =============================================================================


@dataclass
class DiscoveryPlanStep:
    """A single step in the discovery plan."""

    step_id: int
    action: str  # search_keywords, check_gaps, fetch_trending, explore_random, score_candidates
    params: dict[str, Any] = field(default_factory=dict)
    estimated_cost: float = 0.0
    estimated_duration_seconds: float = 0.0
    depends_on: list[int] = field(default_factory=list)


@dataclass
class DiscoveryPlan:
    """Plan generated by DiscoveryAgent._think()."""

    mode: DiscoveryMode
    steps: list[DiscoveryPlanStep]
    reasoning: str

    # Resource estimates
    estimated_total_cost: float = 0.0
    estimated_total_duration_seconds: float = 0.0

    # Scope
    keywords_to_search: list[str] = field(default_factory=list)
    passes_to_check: list[str] = field(default_factory=list)
    regions_to_check: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "mode": self.mode,
            "steps": [
                {
                    "step_id": s.step_id,
                    "action": s.action,
                    "params": s.params,
                    "estimated_cost": s.estimated_cost,
                    "depends_on": s.depends_on,
                }
                for s in self.steps
            ],
            "reasoning": self.reasoning,
            "estimated_total_cost": self.estimated_total_cost,
            "keywords_to_search": self.keywords_to_search,
            "passes_to_check": self.passes_to_check,
            "regions_to_check": self.regions_to_check,
        }


# =============================================================================
# Discovery Observation
# =============================================================================


@dataclass
class DiscoveryObservation:
    """Observation generated by DiscoveryAgent._observe()."""

    success: bool

    # Candidate counts
    candidates_found: int = 0
    candidates_new: int = 0
    candidates_updated: int = 0
    candidates_rejected: int = 0  # Filtered out by criteria

    # Top opportunities
    top_candidates: list[dict[str, Any]] = field(default_factory=list)

    # Patterns learned
    patterns_discovered: list[str] = field(default_factory=list)

    # Lessons for future discovery
    lessons: list[str] = field(default_factory=list)

    # Coverage analysis
    coverage_gaps_remaining: list[str] = field(default_factory=list)

    # Meta-observations
    process_notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "success": self.success,
            "candidates_found": self.candidates_found,
            "candidates_new": self.candidates_new,
            "candidates_updated": self.candidates_updated,
            "candidates_rejected": self.candidates_rejected,
            "top_candidates": self.top_candidates,
            "patterns_discovered": self.patterns_discovered,
            "lessons": self.lessons,
            "coverage_gaps_remaining": self.coverage_gaps_remaining,
            "process_notes": self.process_notes,
        }


# =============================================================================
# Opportunity Scoring Weights
# =============================================================================


OPPORTUNITY_WEIGHTS = {
    "search_demand": 0.25,      # Search volume exists
    "competitive_gap": 0.30,    # Others don't cover well
    "value_potential": 0.20,    # Fits "value skiing" angle
    "coverage_completeness": 0.15,  # Fills gap in our DB
    "exploration_bonus": 0.10,  # Random discovery factor
}


# =============================================================================
# Discovery Source Priorities
# =============================================================================


DISCOVERY_SOURCE_PRIORITY = {
    "keyword_research": 1,  # Highest - proven demand
    "gap_discovery": 2,     # High - strategic coverage
    "trending": 3,          # Medium - timely relevance
    "exploration": 4,       # Lower - discovery for diversity
}


# =============================================================================
# Anti-Echo-Chamber Rules
# =============================================================================


DIVERSITY_RULES = {
    "max_per_country_per_run": 5,   # Max candidates from same country
    "exploration_quota": 0.2,        # 20% of discoveries from exploration
    "region_rotation_enabled": True,  # Rotate focus regions
    "random_seed_injection": 0.1,    # 10% random seed keywords
}


# =============================================================================
# Pass Network Definitions
# =============================================================================


PASS_NETWORKS = {
    "Epic": {
        "owner": "Vail Resorts",
        "key_resorts": ["Vail", "Park City", "Whistler Blackcomb", "Verbier"],
        "regions": ["North America", "Europe", "Australia", "Japan"],
    },
    "Ikon": {
        "owner": "Alterra Mountain Company",
        "key_resorts": ["Aspen", "Jackson Hole", "Chamonix", "Zermatt"],
        "regions": ["North America", "Europe", "Australia", "New Zealand"],
    },
    "Mountain Collective": {
        "owner": "Independent Coalition",
        "key_resorts": ["Alta", "Snowbird", "Revelstoke", "Taos"],
        "regions": ["North America", "Japan"],
    },
    "Indy Pass": {
        "owner": "Independent",
        "key_resorts": ["Various independent resorts"],
        "regions": ["North America"],
    },
}


# =============================================================================
# Region Definitions
# =============================================================================


REGION_DEFINITIONS = {
    "Alps": {
        "countries": ["Switzerland", "Austria", "France", "Italy", "Germany"],
        "priority": "high",
        "value_angle": True,
    },
    "Rocky Mountains": {
        "countries": ["USA", "Canada"],
        "priority": "high",
        "value_angle": False,  # Generally expensive
    },
    "Pyrenees": {
        "countries": ["Spain", "Andorra", "France"],
        "priority": "medium",
        "value_angle": True,
    },
    "Scandinavia": {
        "countries": ["Norway", "Sweden", "Finland"],
        "priority": "medium",
        "value_angle": True,
    },
    "Japan": {
        "countries": ["Japan"],
        "priority": "high",
        "value_angle": True,
    },
    "Eastern Europe": {
        "countries": ["Bulgaria", "Romania", "Slovenia", "Slovakia", "Czech Republic"],
        "priority": "medium",
        "value_angle": True,
    },
}
