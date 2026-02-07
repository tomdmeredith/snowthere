"""DiscoveryAgent - Find new resort opportunities through intelligent discovery.

This agent identifies high-value content opportunities through:
1. Keyword Research: Analyze search demand for ski resorts
2. Gap Discovery: Find coverage gaps in pass networks and regions
3. Trending: Identify trending topics and resorts
4. Exploration: Random discovery to avoid echo chambers

Design Principles:
- Multi-signal approach: Combines search data, coverage gaps, and trends
- Anti-echo-chamber: Built-in exploration and diversity mechanisms
- Cost-conscious: DataForSEO calls are tracked and budgeted
- Actionable output: Candidates are scored and ready for the pipeline
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import uuid4
import random

from ..base import BaseAgent, AgentPlan, Observation
from .schemas.discovery import (
    DiscoveryObjective,
    DiscoveryPlan,
    DiscoveryPlanStep,
    DiscoveryObservation,
    KeywordResearchConfig,
    GapDiscoveryConfig,
    TrendingConfig,
    ExplorationConfig,
    FullDiscoveryConfig,
    OPPORTUNITY_WEIGHTS,
    DISCOVERY_SOURCE_PRIORITY,
    DIVERSITY_RULES,
    PASS_NETWORKS,
    REGION_DEFINITIONS,
)
from shared.primitives.discovery import (
    DiscoveryCandidate,
    DiscoveryResult,
    DiscoverySource,
    CompetitiveGap,
    CandidateStatus,
    get_keyword_data,
    get_keyword_suggestions,
    search_trending_ski_topics,
    extract_resort_mentions,
    find_pass_coverage_gaps,
    find_region_coverage_gaps,
    calculate_opportunity_score,
    save_discovery_candidate,
    get_covered_resorts,
    run_keyword_discovery,
    run_gap_discovery,
    run_trending_discovery,
    run_exploration_discovery,
    run_full_discovery,
)
from shared.primitives import (
    log_reasoning,
    log_cost,
    get_daily_spend,
    queue_task,
)
from shared.config import settings
from shared.supabase_client import get_supabase_client


@dataclass
class DiscoveryRunResult:
    """Result of a discovery run."""

    run_id: str
    mode: str
    started_at: datetime
    completed_at: datetime | None = None

    # Counts
    candidates_found: int = 0
    candidates_new: int = 0
    candidates_updated: int = 0
    candidates_rejected: int = 0

    # Top results
    top_candidates: list[DiscoveryCandidate] = field(default_factory=list)

    # Patterns
    patterns_discovered: list[str] = field(default_factory=list)

    # Costs
    api_cost: float = 0.0
    tokens_used: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "run_id": self.run_id,
            "mode": self.mode,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "candidates_found": self.candidates_found,
            "candidates_new": self.candidates_new,
            "candidates_updated": self.candidates_updated,
            "candidates_rejected": self.candidates_rejected,
            "top_candidates": [c.to_dict() if hasattr(c, 'to_dict') else c for c in self.top_candidates],
            "patterns_discovered": self.patterns_discovered,
            "api_cost": self.api_cost,
        }


class DiscoveryAgent(BaseAgent):
    """Agent that discovers new resort opportunities for content creation.

    Usage:
        # Weekly keyword research
        agent = DiscoveryAgent()
        objective = DiscoveryObjective.keyword_research(seed_keywords=["family ski"])
        result = await agent.run(objective.__dict__)

        # Coverage gap analysis
        objective = DiscoveryObjective.gap_discovery(pass_networks=["Epic", "Ikon"])
        result = await agent.run(objective.__dict__)

        # Trending topics
        objective = DiscoveryObjective.trending(lookback_days=7)
        result = await agent.run(objective.__dict__)

        # Random exploration
        objective = DiscoveryObjective.exploration(sample_size=10)
        result = await agent.run(objective.__dict__)

        # Full discovery (all modes)
        objective = DiscoveryObjective.full(max_candidates=50)
        result = await agent.run(objective.__dict__)
    """

    def __init__(self):
        """Initialize DiscoveryAgent."""
        super().__init__(name="discovery")

    # =========================================================================
    # THINK PHASE: Analyze what discovery approach to use
    # =========================================================================

    async def _think(self, objective: dict[str, Any]) -> AgentPlan:
        """Analyze the discovery objective and create an execution plan."""
        mode = objective.get("mode", "keyword_research")
        config = objective.get("config", {})
        triggered_by = objective.get("triggered_by", "cron")

        log_reasoning(
            task_id=None,
            agent_name=self.name,
            action="think_mode_analysis",
            reasoning=f"Planning {mode} discovery triggered by {triggered_by}",
            metadata={"mode": mode, "config": config},
        )

        if mode == "keyword_research":
            return await self._plan_keyword_research(config)
        elif mode == "gap_discovery":
            return await self._plan_gap_discovery(config)
        elif mode == "trending":
            return await self._plan_trending(config)
        elif mode == "exploration":
            return await self._plan_exploration(config)
        elif mode == "full":
            return await self._plan_full_discovery(config)
        else:
            raise ValueError(f"Unknown discovery mode: {mode}")

    async def _plan_keyword_research(self, config: dict) -> AgentPlan:
        """Plan keyword research discovery."""
        seed_keywords = config.get("seed_keywords", [
            "family ski resort",
            "ski with kids",
            "beginner ski resort",
        ])
        max_keywords = config.get("max_keywords", 50)
        min_search_volume = config.get("min_search_volume", 100)

        # Check budget
        remaining = settings.daily_budget_limit - get_daily_spend()
        estimated_cost = len(seed_keywords) * 0.10  # ~$0.10 per keyword batch

        if remaining < estimated_cost:
            return AgentPlan(
                steps=["Skip keyword research - insufficient budget"],
                reasoning=f"Budget ${remaining:.2f} < estimated ${estimated_cost:.2f}",
                estimated_cost=0.0,
                confidence=1.0,
                primitives_needed=[],
                dependencies=[],
            )

        steps = [
            f"Expand {len(seed_keywords)} seed keywords via DataForSEO",
            f"Filter to keywords with volume > {min_search_volume}",
            "Extract resort names from keywords",
            "Score candidates by search demand",
            "Filter existing resorts",
            "Save new candidates",
        ]

        reasoning = f"""Keyword Research Plan:
Starting with {len(seed_keywords)} seed keywords.
Will expand via DataForSEO and filter to volume > {min_search_volume}.
Estimated cost: ~${estimated_cost:.2f}
Focus: Finding resorts with proven search demand."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            confidence=0.8,
            primitives_needed=[
                "get_keyword_data",
                "get_keyword_suggestions",
                "extract_resort_mentions",
                "save_discovery_candidate",
            ],
            dependencies=[],
        )

    async def _plan_gap_discovery(self, config: dict) -> AgentPlan:
        """Plan coverage gap discovery."""
        check_pass_networks = config.get("check_pass_networks", True)
        check_regions = config.get("check_regions", True)
        pass_networks = config.get("pass_networks", ["Epic", "Ikon", "Mountain Collective"])
        min_gap_score = config.get("min_gap_score", 0.5)

        steps = []
        if check_pass_networks:
            steps.append(f"Analyze {len(pass_networks)} pass networks for coverage gaps")
        if check_regions:
            steps.append("Analyze regional coverage for underserved areas")
        steps.extend([
            "Score gaps by strategic importance",
            "Filter by minimum gap score",
            "Save candidates with coverage_gap source",
        ])

        reasoning = f"""Gap Discovery Plan:
Analyzing coverage gaps in pass networks and regions.
Pass networks: {pass_networks}
Will identify resorts we're missing that competitors cover.
This is database-analysis plus light research, minimal API cost."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=0.5,  # Light research
            confidence=0.85,
            primitives_needed=[
                "find_pass_coverage_gaps",
                "find_region_coverage_gaps",
                "save_discovery_candidate",
            ],
            dependencies=[],
        )

    async def _plan_trending(self, config: dict) -> AgentPlan:
        """Plan trending topic discovery."""
        lookback_days = config.get("lookback_days", 7)
        min_trending_score = config.get("min_trending_score", 0.6)
        include_news = config.get("include_news", True)

        steps = [
            f"Search Exa for trending ski topics (last {lookback_days} days)",
            "Extract resort mentions from trending content",
            "Score by trending velocity and relevance",
            "Filter existing resorts",
            "Save trending candidates",
        ]

        reasoning = f"""Trending Discovery Plan:
Looking for resorts getting buzz in the last {lookback_days} days.
Using Exa semantic search for trending ski/family content.
These are timely opportunities - seasonal, news-driven, or viral.
Estimated cost: ~$0.50 for trending search."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=0.5,
            confidence=0.7,  # Trending is less predictable
            primitives_needed=[
                "search_trending_ski_topics",
                "extract_resort_mentions",
                "save_discovery_candidate",
            ],
            dependencies=[],
        )

    async def _plan_exploration(self, config: dict) -> AgentPlan:
        """Plan exploration discovery (random sampling for diversity)."""
        sample_size = config.get("sample_size", 10)
        diversity_weight = config.get("diversity_weight", 0.5)
        region_spread = config.get("region_spread", True)

        steps = [
            f"Generate {sample_size} exploration candidates",
            "Ensure geographic diversity across regions",
            "Apply exploration scoring bonus",
            "Save candidates with exploration source",
        ]

        reasoning = f"""Exploration Discovery Plan:
Anti-echo-chamber mechanism: discovering {sample_size} random resorts.
This ensures we don't only chase high-volume keywords.
Region spread: {region_spread}
Minimal cost - mostly random selection + light verification."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=0.2,
            confidence=0.6,  # Exploration is inherently uncertain
            primitives_needed=[
                "save_discovery_candidate",
            ],
            dependencies=[],
        )

    async def _plan_full_discovery(self, config: dict) -> AgentPlan:
        """Plan full discovery (all modes)."""
        max_total_candidates = config.get("max_total_candidates", 50)
        max_api_cost = config.get("max_api_cost", 5.0)

        # Check budget
        remaining = settings.daily_budget_limit - get_daily_spend()
        if remaining < max_api_cost:
            return AgentPlan(
                steps=["Skip full discovery - insufficient budget"],
                reasoning=f"Budget ${remaining:.2f} < max_cost ${max_api_cost:.2f}",
                estimated_cost=0.0,
                confidence=1.0,
                primitives_needed=[],
                dependencies=[],
            )

        steps = [
            "Run keyword research discovery",
            "Run coverage gap discovery",
            "Run trending topic discovery",
            "Run exploration discovery",
            "Merge and deduplicate candidates",
            f"Rank and select top {max_total_candidates} candidates",
            "Save all candidates with appropriate sources",
        ]

        reasoning = f"""Full Discovery Plan:
Running all four discovery modes for comprehensive coverage.
Max candidates: {max_total_candidates}
Budget cap: ${max_api_cost:.2f}
This is the weekly comprehensive discovery run."""

        return AgentPlan(
            steps=steps,
            reasoning=reasoning,
            estimated_cost=max_api_cost,
            confidence=0.75,
            primitives_needed=[
                "get_keyword_data",
                "get_keyword_suggestions",
                "search_trending_ski_topics",
                "extract_resort_mentions",
                "find_pass_coverage_gaps",
                "find_region_coverage_gaps",
                "save_discovery_candidate",
            ],
            dependencies=[],
        )

    # =========================================================================
    # ACT PHASE: Execute the discovery plan
    # =========================================================================

    async def _act(self, plan: AgentPlan) -> DiscoveryRunResult:
        """Execute the discovery plan."""
        run_id = str(uuid4())
        started_at = datetime.utcnow()

        result = DiscoveryRunResult(
            run_id=run_id,
            mode="unknown",
            started_at=started_at,
        )

        # Determine mode from plan reasoning
        if "Keyword Research" in plan.reasoning:
            result.mode = "keyword_research"
            await self._execute_keyword_research(result, plan)
        elif "Gap Discovery" in plan.reasoning:
            result.mode = "gap_discovery"
            await self._execute_gap_discovery(result, plan)
        elif "Trending Discovery" in plan.reasoning:
            result.mode = "trending"
            await self._execute_trending(result, plan)
        elif "Exploration Discovery" in plan.reasoning:
            result.mode = "exploration"
            await self._execute_exploration(result, plan)
        elif "Full Discovery" in plan.reasoning:
            result.mode = "full"
            await self._execute_full_discovery(result, plan)
        elif "Skip" in plan.reasoning:
            # Budget skip case
            result.mode = "skipped"
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="discovery_skipped",
                reasoning=plan.reasoning,
                metadata={"run_id": run_id},
            )
        else:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="act_error",
                reasoning=f"Could not determine discovery mode from plan: {plan.reasoning[:100]}",
                metadata={"run_id": run_id},
            )

        result.completed_at = datetime.utcnow()
        return result

    async def _execute_keyword_research(
        self, result: DiscoveryRunResult, plan: AgentPlan
    ) -> None:
        """Execute keyword research discovery."""
        try:
            discovery_result = await run_keyword_discovery(
                seed_keywords=[
                    "family ski resort",
                    "ski with kids",
                    "beginner ski resort",
                    "kids ski free",
                    "ski school for children",
                ],
                min_search_volume=100,
                max_keywords=50,
            )

            result.candidates_found = discovery_result.candidates_found
            result.candidates_new = discovery_result.candidates_new
            result.candidates_updated = discovery_result.candidates_updated
            result.top_candidates = discovery_result.top_candidates[:10]
            result.api_cost = discovery_result.api_cost
            result.patterns_discovered.extend(discovery_result.patterns)

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="keyword_research_error",
                reasoning=f"Keyword research failed: {e}",
                metadata={"error": str(e)},
            )

    async def _execute_gap_discovery(
        self, result: DiscoveryRunResult, plan: AgentPlan
    ) -> None:
        """Execute coverage gap discovery."""
        try:
            discovery_result = await run_gap_discovery(
                check_pass_networks=True,
                check_regions=True,
                pass_networks=["Epic", "Ikon", "Mountain Collective"],
            )

            result.candidates_found = discovery_result.candidates_found
            result.candidates_new = discovery_result.candidates_new
            result.candidates_updated = discovery_result.candidates_updated
            result.top_candidates = discovery_result.top_candidates[:10]
            result.api_cost = discovery_result.api_cost
            result.patterns_discovered.extend(discovery_result.patterns)

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="gap_discovery_error",
                reasoning=f"Gap discovery failed: {e}",
                metadata={"error": str(e)},
            )

    async def _execute_trending(
        self, result: DiscoveryRunResult, plan: AgentPlan
    ) -> None:
        """Execute trending discovery."""
        try:
            discovery_result = await run_trending_discovery(
                lookback_days=7,
                min_trending_score=0.6,
            )

            result.candidates_found = discovery_result.candidates_found
            result.candidates_new = discovery_result.candidates_new
            result.candidates_updated = discovery_result.candidates_updated
            result.top_candidates = discovery_result.top_candidates[:10]
            result.api_cost = discovery_result.api_cost
            result.patterns_discovered.extend(discovery_result.patterns)

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="trending_error",
                reasoning=f"Trending discovery failed: {e}",
                metadata={"error": str(e)},
            )

    async def _execute_exploration(
        self, result: DiscoveryRunResult, plan: AgentPlan
    ) -> None:
        """Execute exploration discovery (random sampling)."""
        try:
            discovery_result = await run_exploration_discovery(
                sample_size=10,
                ensure_region_spread=True,
            )

            result.candidates_found = discovery_result.candidates_found
            result.candidates_new = discovery_result.candidates_new
            result.candidates_updated = discovery_result.candidates_updated
            result.top_candidates = discovery_result.top_candidates[:10]
            result.api_cost = discovery_result.api_cost
            result.patterns_discovered.extend(discovery_result.patterns)

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="exploration_error",
                reasoning=f"Exploration discovery failed: {e}",
                metadata={"error": str(e)},
            )

    async def _execute_full_discovery(
        self, result: DiscoveryRunResult, plan: AgentPlan
    ) -> None:
        """Execute full discovery (all modes)."""
        try:
            discovery_result = await run_full_discovery(
                max_total_candidates=50,
                max_api_cost=5.0,
            )

            result.candidates_found = discovery_result.candidates_found
            result.candidates_new = discovery_result.candidates_new
            result.candidates_updated = discovery_result.candidates_updated
            result.top_candidates = discovery_result.top_candidates[:20]
            result.api_cost = discovery_result.api_cost
            result.patterns_discovered.extend(discovery_result.patterns)

        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="full_discovery_error",
                reasoning=f"Full discovery failed: {e}",
                metadata={"error": str(e)},
            )

    # =========================================================================
    # OBSERVE PHASE: Evaluate results and extract lessons
    # =========================================================================

    async def _observe(
        self, result: DiscoveryRunResult, objective: dict[str, Any]
    ) -> Observation:
        """Evaluate discovery results and extract patterns."""
        mode = objective.get("mode", "keyword_research")

        # Determine success criteria
        if result.mode == "skipped":
            success = True  # Budget skip is intentional
            outcome = "Discovery skipped due to budget constraints"
        elif result.candidates_new > 0:
            success = True
            outcome = f"Found {result.candidates_new} new candidates (total {result.candidates_found})"
        elif result.candidates_found > 0:
            success = True
            outcome = f"Found {result.candidates_found} candidates ({result.candidates_updated} updated)"
        else:
            success = False
            outcome = "No candidates found"

        # Extract lessons
        lessons = []

        if result.candidates_new > 10:
            lessons.append(f"High discovery rate: {result.candidates_new} new candidates")

        if result.api_cost > 3.0:
            lessons.append(f"High API cost (${result.api_cost:.2f}) - consider optimization")

        # Analyze top candidates for patterns
        if result.top_candidates:
            # Country distribution
            countries = [c.country if hasattr(c, 'country') else c.get('country', '') for c in result.top_candidates]
            country_counts = {}
            for c in countries:
                country_counts[c] = country_counts.get(c, 0) + 1

            top_country = max(country_counts.items(), key=lambda x: x[1])[0] if country_counts else None
            if top_country:
                lessons.append(f"Top discovery country: {top_country}")

        # Add discovered patterns
        lessons.extend(result.patterns_discovered[:3])

        # Metrics
        metrics = {
            "candidates_found": result.candidates_found,
            "candidates_new": result.candidates_new,
            "candidates_updated": result.candidates_updated,
            "candidates_rejected": result.candidates_rejected,
            "api_cost": result.api_cost,
            "mode": result.mode,
            "duration_seconds": (
                (result.completed_at - result.started_at).total_seconds()
                if result.completed_at else 0
            ),
        }

        # Log the discovery run
        await self._log_discovery_run(result)

        # Determine if follow-up is needed
        follow_up_needed = result.candidates_new >= 20  # Lots of new candidates
        follow_up_context = None

        if follow_up_needed:
            follow_up_context = {
                "reason": "high_discovery_rate",
                "candidates_to_queue": [
                    c.resort_name if hasattr(c, 'resort_name') else c.get('resort_name')
                    for c in result.top_candidates[:5]
                ],
            }

        return Observation(
            success=success,
            outcome_summary=outcome,
            metrics=metrics,
            lessons=lessons,
            follow_up_needed=follow_up_needed,
            follow_up_context=follow_up_context,
        )

    async def _log_discovery_run(self, result: DiscoveryRunResult) -> None:
        """Log the discovery run to the database."""
        try:
            client = get_supabase_client()
            client.table("discovery_runs").insert({
                "id": result.run_id,
                "mode": result.mode,
                "config": {},  # Could store config here
                "candidates_found": result.candidates_found,
                "candidates_new": result.candidates_new,
                "candidates_updated": result.candidates_updated,
                "started_at": result.started_at.isoformat(),
                "completed_at": result.completed_at.isoformat() if result.completed_at else None,
                "status": "completed",
                "api_cost": result.api_cost,
                "patterns_discovered": result.patterns_discovered,
            }).execute()
        except Exception as e:
            log_reasoning(
                task_id=None,
                agent_name=self.name,
                action="log_discovery_run_error",
                reasoning=f"Failed to log discovery run: {e}",
                metadata={"run_id": result.run_id, "error": str(e)},
            )


# =============================================================================
# ENTRY POINTS
# =============================================================================


async def run_keyword_research_discovery(**config_kwargs) -> dict:
    """Convenience function to run keyword research discovery.

    Args:
        seed_keywords: List of seed keywords (default: family ski terms)
        max_keywords: Maximum keywords to analyze (default: 50)
        min_search_volume: Minimum search volume (default: 100)

    Returns:
        Dict with discovery results
    """
    agent = DiscoveryAgent()
    objective = DiscoveryObjective.keyword_research(**config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_gap_discovery_agent(**config_kwargs) -> dict:
    """Convenience function to run gap discovery.

    Args:
        check_pass_networks: Whether to check pass networks (default: True)
        check_regions: Whether to check regions (default: True)
        pass_networks: List of pass networks to check (default: Epic, Ikon, Mountain Collective)

    Returns:
        Dict with discovery results
    """
    agent = DiscoveryAgent()
    objective = DiscoveryObjective.gap_discovery(**config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_trending_discovery_agent(lookback_days: int = 7, **config_kwargs) -> dict:
    """Convenience function to run trending discovery.

    Args:
        lookback_days: How many days to look back (default: 7)
        min_trending_score: Minimum trending score (default: 0.6)

    Returns:
        Dict with discovery results
    """
    agent = DiscoveryAgent()
    objective = DiscoveryObjective.trending(lookback_days=lookback_days, **config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_exploration_discovery_agent(sample_size: int = 10, **config_kwargs) -> dict:
    """Convenience function to run exploration discovery.

    Args:
        sample_size: Number of random candidates to discover (default: 10)
        diversity_weight: Balance between score and diversity (default: 0.5)

    Returns:
        Dict with discovery results
    """
    agent = DiscoveryAgent()
    objective = DiscoveryObjective.exploration(sample_size=sample_size, **config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }


async def run_full_discovery_agent(max_candidates: int = 50, **config_kwargs) -> dict:
    """Convenience function to run full discovery (all modes).

    Args:
        max_candidates: Maximum total candidates (default: 50)
        max_api_cost: Budget cap for this run (default: 5.0)

    Returns:
        Dict with discovery results
    """
    agent = DiscoveryAgent()
    objective = DiscoveryObjective.full(max_candidates=max_candidates, **config_kwargs)
    result = await agent.run({
        "mode": objective.mode,
        "config": objective.config.__dict__,
        "triggered_by": objective.triggered_by,
    })
    return {
        "success": result.success,
        "output": result.output.to_dict() if result.output else None,
        "reasoning": result.reasoning,
    }
