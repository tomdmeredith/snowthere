"""Core content generation agent logic."""

import asyncio
from datetime import datetime
from typing import Any

from ..research_resort.schemas import ResearchOutput
from ..shared.config import settings
from ..shared.primitives.content import (
    apply_voice,
    generate_faq,
    generate_seo_meta,
    write_section,
)
from ..shared.primitives.system import log_cost, log_reasoning
from ..shared.voice_profiles import get_voice_profile
from .schemas import FAQItem, GenerateInput, GenerateOutput, SEOMetadata


class GenerateGuideAgent:
    """Agent that generates family-focused ski resort guide content."""

    def __init__(self, task_id: str | None = None):
        self.task_id = task_id
        self.errors: list[str] = []
        self.total_tokens = 0

    async def generate(self, input_data: GenerateInput) -> GenerateOutput:
        """
        Generate complete guide content for a resort.

        Args:
            input_data: Research data and configuration

        Returns:
            GenerateOutput with all generated content
        """
        research = input_data.research_data
        voice_profile = input_data.voice_profile
        sections_to_generate = input_data.sections

        # Log start
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="generate_guide",
                action="start_generation",
                reasoning=f"Generating content for {research.resort_name} using {voice_profile} voice",
                metadata={"sections": sections_to_generate},
            )

        # Build context from research
        context = self._build_context(research)

        # Generate sections in parallel (where possible)
        sections = await self._generate_sections(
            sections_to_generate,
            context,
            voice_profile,
        )

        # Generate FAQs
        faqs = await self._generate_faqs(
            research.resort_name,
            research.country,
            context,
            voice_profile,
        )

        # Generate SEO metadata
        seo_meta = await self._generate_seo(
            research.resort_name,
            research.country,
            sections.get("quick_take", ""),
        )

        # Generate llms.txt
        llms_txt = self._generate_llms_txt(research, sections, faqs)

        # Estimate token cost (~$0.50-1.00 per resort for Opus)
        estimated_cost = self.total_tokens * 0.000015  # Opus pricing
        if self.task_id:
            log_cost("anthropic", estimated_cost, self.task_id, {
                "tokens": self.total_tokens,
                "resort": research.resort_name,
            })

        # Build output
        output = GenerateOutput(
            resort_name=research.resort_name,
            country=research.country,
            region=research.region,
            sections=sections,
            faqs=[FAQItem(**f) for f in faqs],
            seo_meta=seo_meta,
            llms_txt=llms_txt,
            voice_profile=voice_profile,
            total_tokens_used=self.total_tokens,
            generated_at=datetime.utcnow(),
            errors=self.errors,
        )

        # Log completion
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="generate_guide",
                action="complete_generation",
                reasoning=f"Generated {len(sections)} sections + {len(faqs)} FAQs for {research.resort_name}",
                metadata={
                    "tokens_used": self.total_tokens,
                    "errors_count": len(self.errors),
                },
            )

        return output

    def _build_context(self, research: ResearchOutput) -> dict[str, Any]:
        """Build context dict for content generation prompts."""
        return {
            "resort_name": research.resort_name,
            "country": research.country,
            "region": research.region or "",
            "family_score": research.family_metrics.family_overall_score or 7,
            "basic_info": research.basic_info.model_dump(),
            "family_metrics": research.family_metrics.model_dump(),
            "costs": research.costs.model_dump(),
            "reviews": [r.model_dump() for r in research.review_snippets],
            "raw_research": research.raw_research,
        }

    async def _generate_sections(
        self,
        section_names: list[str],
        context: dict[str, Any],
        voice_profile: str,
    ) -> dict[str, str]:
        """Generate multiple content sections."""
        sections = {}

        # Generate sections - could parallelize but be mindful of rate limits
        for section_name in section_names:
            try:
                content = await write_section(
                    section_name=section_name,
                    context=context,
                    voice_profile=voice_profile,
                )
                sections[section_name] = content
                # Rough token estimate (content length / 4)
                self.total_tokens += len(content) // 4 + 500  # Plus prompt tokens
            except Exception as e:
                self.errors.append(f"Failed to generate {section_name}: {e}")
                sections[section_name] = f"<p>Content generation failed for this section.</p>"

        return sections

    async def _generate_faqs(
        self,
        resort_name: str,
        country: str,
        context: dict[str, Any],
        voice_profile: str,
    ) -> list[dict[str, str]]:
        """Generate FAQ section."""
        try:
            faqs = await generate_faq(
                resort_name=resort_name,
                country=country,
                context=context,
                num_questions=6,
                voice_profile=voice_profile,
            )
            self.total_tokens += 1000  # Estimate
            return faqs
        except Exception as e:
            self.errors.append(f"Failed to generate FAQs: {e}")
            return []

    async def _generate_seo(
        self,
        resort_name: str,
        country: str,
        quick_take: str,
    ) -> SEOMetadata | None:
        """Generate SEO metadata."""
        try:
            meta = await generate_seo_meta(
                resort_name=resort_name,
                country=country,
                quick_take=quick_take,
            )
            self.total_tokens += 200  # Estimate
            return SEOMetadata(**meta)
        except Exception as e:
            self.errors.append(f"Failed to generate SEO meta: {e}")
            return SEOMetadata(
                title=f"{resort_name} Family Ski Guide | Snowthere",
                description=f"Complete family guide to skiing at {resort_name}, {country}. Kid-friendly terrain, costs, and honest parent reviews.",
            )

    def _generate_llms_txt(
        self,
        research: ResearchOutput,
        sections: dict[str, str],
        faqs: list[dict[str, str]],
    ) -> str:
        """Generate llms.txt content for AI crawlers."""
        lines = [
            f"# {research.resort_name} Family Ski Guide",
            "",
            f"Location: {research.resort_name}, {research.region or ''}, {research.country}".strip(", "),
            "",
            "## Quick Facts",
        ]

        # Add basic info
        if research.basic_info.terrain_beginner_pct:
            lines.append(f"- Beginner Terrain: {research.basic_info.terrain_beginner_pct}%")
        if research.basic_info.num_lifts:
            lines.append(f"- Number of Lifts: {research.basic_info.num_lifts}")

        # Add family metrics
        lines.append("")
        lines.append("## Family Information")
        if research.family_metrics.family_overall_score:
            lines.append(f"- Family Score: {research.family_metrics.family_overall_score}/10")
        if research.family_metrics.has_childcare is not None:
            lines.append(f"- Childcare Available: {'Yes' if research.family_metrics.has_childcare else 'No'}")
        if research.family_metrics.ski_school_min_age:
            lines.append(f"- Ski School Minimum Age: {research.family_metrics.ski_school_min_age} years")
        if research.family_metrics.kids_ski_free_age:
            lines.append(f"- Kids Ski Free Under Age: {research.family_metrics.kids_ski_free_age}")

        # Add costs
        lines.append("")
        lines.append("## Costs")
        if research.costs.lift_adult_daily:
            lines.append(f"- Adult Day Pass: {research.costs.currency} {research.costs.lift_adult_daily}")
        if research.costs.lift_child_daily:
            lines.append(f"- Child Day Pass: {research.costs.currency} {research.costs.lift_child_daily}")

        # Add FAQ summary
        if faqs:
            lines.append("")
            lines.append("## Frequently Asked Questions")
            for faq in faqs[:5]:
                lines.append(f"- Q: {faq.get('question', '')}")
                lines.append(f"  A: {faq.get('answer', '')[:200]}...")

        lines.append("")
        lines.append("---")
        lines.append("Source: Snowthere.com - Family Ski Resort Guide")
        lines.append(f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d')}")

        return "\n".join(lines)


async def generate_guide(
    research_data: ResearchOutput,
    voice_profile: str = "instagram_mom",
    sections: list[str] | None = None,
    task_id: str | None = None,
) -> GenerateOutput:
    """
    Convenience function to generate a resort guide.

    Args:
        research_data: Output from research_resort agent
        voice_profile: Voice to use for content
        sections: Sections to generate (default: all)
        task_id: Optional task ID for tracking

    Returns:
        GenerateOutput with all content
    """
    input_data = GenerateInput(
        research_data=research_data,
        voice_profile=voice_profile,
        sections=sections or [
            "quick_take",
            "getting_there",
            "where_to_stay",
            "lift_tickets",
            "on_mountain",
            "off_mountain",
            "parent_reviews_summary",
        ],
    )

    agent = GenerateGuideAgent(task_id=task_id)
    return await agent.generate(input_data)
