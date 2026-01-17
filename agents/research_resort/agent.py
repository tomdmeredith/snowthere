"""Core research agent logic for gathering ski resort data."""

import asyncio
from datetime import datetime
from typing import Any

from ..shared.config import settings
from ..shared.primitives.research import (
    exa_search,
    scrape_url,
    search_resort_info,
    serp_search,
    tavily_search,
)
from ..shared.primitives.system import log_cost, log_reasoning
from .schemas import (
    BasicInfo,
    CostEstimates,
    FamilyMetrics,
    ResearchInput,
    ResearchOutput,
    ReviewSnippet,
    SourceReference,
)


class ResearchResortAgent:
    """Agent that gathers comprehensive ski resort data from multiple sources."""

    def __init__(self, task_id: str | None = None):
        self.task_id = task_id
        self.errors: list[str] = []
        self.sources: list[SourceReference] = []

    async def research(self, input_data: ResearchInput) -> ResearchOutput:
        """
        Execute full research pipeline for a resort.

        Args:
            input_data: Resort name, country, and focus areas

        Returns:
            ResearchOutput with all gathered data
        """
        resort_name = input_data.resort_name
        country = input_data.country
        region = input_data.region

        # Log start of research
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="research_resort",
                action="start_research",
                reasoning=f"Starting research for {resort_name}, {country}",
                metadata={"input": input_data.model_dump()},
            )

        # Run parallel research queries
        raw_research = await self._gather_research(resort_name, country, region)

        # Extract structured data
        basic_info = self._extract_basic_info(raw_research)
        family_metrics = self._extract_family_metrics(raw_research)
        costs = self._extract_costs(raw_research, country)
        review_snippets = self._extract_reviews(raw_research)

        # Calculate confidence score
        confidence = self._calculate_confidence(basic_info, family_metrics, costs)

        # Build output
        output = ResearchOutput(
            resort_name=resort_name,
            country=country,
            region=region,
            basic_info=basic_info,
            family_metrics=family_metrics,
            costs=costs,
            review_snippets=review_snippets,
            sources=self.sources,
            raw_research=raw_research,
            confidence_score=confidence,
            researched_at=datetime.utcnow(),
            errors=self.errors,
        )

        # Log completion
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="research_resort",
                action="complete_research",
                reasoning=f"Completed research for {resort_name} with confidence {confidence:.2f}",
                metadata={
                    "sources_count": len(self.sources),
                    "errors_count": len(self.errors),
                },
            )

        return output

    async def _gather_research(
        self,
        resort_name: str,
        country: str,
        region: str | None,
    ) -> dict[str, Any]:
        """Gather research from multiple sources in parallel."""
        location = f"{resort_name}, {region}, {country}" if region else f"{resort_name}, {country}"

        # Define search queries
        queries = {
            "official": f"{resort_name} ski resort official site",
            "family_reviews": f"{resort_name} ski resort family review kids children",
            "ski_school": f"{resort_name} ski school children lessons daycare",
            "costs": f"{resort_name} lift ticket prices {datetime.now().year}",
            "lodging": f"{resort_name} ski in ski out family lodging hotel",
            "getting_there": f"{resort_name} ski resort airport transfer how to get there",
        }

        results = {}

        # Run Exa searches in parallel for semantic results
        exa_tasks = []
        for key, query in queries.items():
            if key in ["family_reviews", "ski_school"]:
                exa_tasks.append(self._safe_exa_search(key, query))

        # Run SerpAPI for factual/official info
        serp_tasks = []
        for key, query in queries.items():
            if key in ["official", "costs", "lodging"]:
                serp_tasks.append(self._safe_serp_search(key, query))

        # Run Tavily for comprehensive web research
        tavily_task = self._safe_tavily_search(
            "comprehensive",
            f"{resort_name} {country} ski resort family guide kids terrain childcare prices",
        )

        # Execute all in parallel
        all_results = await asyncio.gather(
            *exa_tasks,
            *serp_tasks,
            tavily_task,
            return_exceptions=True,
        )

        # Process results
        for result in all_results:
            if isinstance(result, Exception):
                self.errors.append(str(result))
            elif isinstance(result, tuple):
                key, data = result
                results[key] = data

        return results

    async def _safe_exa_search(self, key: str, query: str) -> tuple[str, list]:
        """Safely execute Exa search with error handling."""
        try:
            results = await exa_search(query, num_results=5)
            # Track sources
            for r in results:
                self.sources.append(
                    SourceReference(
                        url=r.url,
                        title=r.title,
                        type="review" if "review" in key else "web",
                        reliability="medium",
                    )
                )
            # Log cost (Exa ~$0.01 per search)
            if self.task_id:
                log_cost("exa", 0.01, self.task_id, {"query": query})
            return (key, [r.__dict__ for r in results])
        except Exception as e:
            self.errors.append(f"Exa search failed for {key}: {e}")
            return (key, [])

    async def _safe_serp_search(self, key: str, query: str) -> tuple[str, list]:
        """Safely execute SerpAPI search with error handling."""
        try:
            results = await serp_search(query, num_results=5)
            # Track sources
            for r in results:
                reliability = "high" if "official" in key else "medium"
                self.sources.append(
                    SourceReference(
                        url=r.url,
                        title=r.title,
                        type="official" if "official" in key else "web",
                        reliability=reliability,
                    )
                )
            # Log cost (SerpAPI ~$0.005 per search)
            if self.task_id:
                log_cost("serp", 0.005, self.task_id, {"query": query})
            return (key, [r.__dict__ for r in results])
        except Exception as e:
            self.errors.append(f"SerpAPI search failed for {key}: {e}")
            return (key, [])

    async def _safe_tavily_search(self, key: str, query: str) -> tuple[str, dict]:
        """Safely execute Tavily search with error handling."""
        try:
            result = await tavily_search(query)
            # Track sources from Tavily results
            for source in result.get("results", []):
                self.sources.append(
                    SourceReference(
                        url=source.get("url", ""),
                        title=source.get("title"),
                        type="web",
                        reliability="medium",
                    )
                )
            # Log cost (Tavily ~$0.01 per search)
            if self.task_id:
                log_cost("tavily", 0.01, self.task_id, {"query": query})
            return (key, result)
        except Exception as e:
            self.errors.append(f"Tavily search failed for {key}: {e}")
            return (key, {})

    def _extract_basic_info(self, raw: dict[str, Any]) -> BasicInfo:
        """Extract basic resort metrics from raw research."""
        # This is a simplified extraction - in production, we'd use
        # more sophisticated NLP or structured data extraction
        info = BasicInfo()

        # Look for terrain breakdown in comprehensive results
        comprehensive = raw.get("comprehensive", {})
        if comprehensive:
            answer = comprehensive.get("answer", "")
            # Extract percentages if mentioned
            # In production, use regex or Claude for extraction

        return info

    def _extract_family_metrics(self, raw: dict[str, Any]) -> FamilyMetrics:
        """Extract family-specific metrics from raw research."""
        metrics = FamilyMetrics()

        # Look through family reviews and ski school info
        family_reviews = raw.get("family_reviews", [])
        ski_school = raw.get("ski_school", [])

        # Extract mentions of childcare, ski school ages, etc.
        # In production, use Claude to extract structured data

        # Set defaults for now - will be enhanced with Claude extraction
        metrics.perfect_if = []
        metrics.skip_if = []

        return metrics

    def _extract_costs(self, raw: dict[str, Any], country: str) -> CostEstimates:
        """Extract cost estimates from raw research."""
        costs = CostEstimates()

        # Set currency based on country
        currency_map = {
            "USA": "USD",
            "United States": "USD",
            "Canada": "CAD",
            "Austria": "EUR",
            "Switzerland": "CHF",
            "France": "EUR",
            "Italy": "EUR",
            "Germany": "EUR",
            "Japan": "JPY",
            "Australia": "AUD",
            "New Zealand": "NZD",
        }
        costs.currency = currency_map.get(country, "USD")

        # Look through costs search results
        cost_results = raw.get("costs", [])
        # In production, extract actual prices using Claude

        return costs

    def _extract_reviews(self, raw: dict[str, Any]) -> list[ReviewSnippet]:
        """Extract review snippets from raw research."""
        snippets = []

        # Look through family reviews
        family_reviews = raw.get("family_reviews", [])
        for review in family_reviews[:3]:  # Limit to 3 snippets
            snippet_text = review.get("snippet", "")
            if snippet_text and len(snippet_text) > 50:
                snippets.append(
                    ReviewSnippet(
                        text=snippet_text[:500],  # Limit length
                        source="exa",
                        sentiment="neutral",  # Would use sentiment analysis
                    )
                )

        # Also check Tavily answer
        comprehensive = raw.get("comprehensive", {})
        if comprehensive.get("answer"):
            snippets.append(
                ReviewSnippet(
                    text=comprehensive["answer"][:500],
                    source="tavily",
                    sentiment="neutral",
                )
            )

        return snippets

    def _calculate_confidence(
        self,
        basic_info: BasicInfo,
        family_metrics: FamilyMetrics,
        costs: CostEstimates,
    ) -> float:
        """Calculate overall confidence score based on data completeness."""
        score = 0.0
        max_score = 0.0

        # Basic info completeness
        basic_fields = [
            basic_info.elevation_base,
            basic_info.elevation_top,
            basic_info.terrain_beginner_pct,
            basic_info.num_lifts,
        ]
        max_score += len(basic_fields)
        score += sum(1 for f in basic_fields if f is not None)

        # Family metrics completeness
        family_fields = [
            family_metrics.family_overall_score,
            family_metrics.has_childcare,
            family_metrics.ski_school_min_age,
            family_metrics.kids_ski_free_age,
        ]
        max_score += len(family_fields)
        score += sum(1 for f in family_fields if f is not None)

        # Cost completeness
        cost_fields = [
            costs.lift_adult_daily,
            costs.lift_child_daily,
            costs.lodging_mid_nightly,
        ]
        max_score += len(cost_fields)
        score += sum(1 for f in cost_fields if f is not None)

        # Source count bonus
        source_bonus = min(len(self.sources) / 10, 0.2)  # Up to 0.2 bonus

        # Error penalty
        error_penalty = min(len(self.errors) * 0.05, 0.3)  # Up to 0.3 penalty

        base_confidence = score / max_score if max_score > 0 else 0.0
        final_confidence = min(1.0, max(0.0, base_confidence + source_bonus - error_penalty))

        return round(final_confidence, 2)


async def research_resort(
    resort_name: str,
    country: str,
    region: str | None = None,
    focus_areas: list[str] | None = None,
    task_id: str | None = None,
) -> ResearchOutput:
    """
    Convenience function to research a resort.

    Args:
        resort_name: Name of the ski resort
        country: Country where resort is located
        region: Optional region/state
        focus_areas: Areas to focus on (default: family, costs, logistics)
        task_id: Optional task ID for tracking

    Returns:
        ResearchOutput with all gathered data
    """
    input_data = ResearchInput(
        resort_name=resort_name,
        country=country,
        region=region,
        focus_areas=focus_areas or ["family", "costs", "logistics"],
    )

    agent = ResearchResortAgent(task_id=task_id)
    return await agent.research(input_data)
