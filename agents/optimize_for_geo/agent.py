"""Core GEO optimization agent logic."""

import json
from datetime import datetime
from typing import Any

from ..research_resort.schemas import BasicInfo, CostEstimates, FamilyMetrics
from ..shared.primitives.system import log_reasoning
from .schemas import (
    FAQItem,
    GEOScore,
    OptimizedTable,
    OptimizeInput,
    OptimizeOutput,
    SchemaMarkup,
    SEOMetadata,
)


class OptimizeForGeoAgent:
    """Agent that enhances content for AI citation and search."""

    def __init__(self, task_id: str | None = None):
        self.task_id = task_id
        self.errors: list[str] = []

    async def optimize(self, input_data: OptimizeInput) -> OptimizeOutput:
        """
        Optimize content for GEO.

        Args:
            input_data: Generated content and structured data

        Returns:
            OptimizeOutput with GEO-enhanced content
        """
        generated = input_data.generated_content
        resort_name = input_data.resort_name
        country = input_data.country

        # Log start
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="optimize_for_geo",
                action="start_optimization",
                reasoning=f"Optimizing GEO for {resort_name}, {country}",
            )

        # Generate optimized tables
        tables = self._generate_tables(
            input_data.basic_info,
            input_data.family_metrics,
            input_data.costs,
            resort_name,
        )

        # Generate Schema.org FAQ markup
        faq_schema = self._generate_faq_schema(
            generated.faqs,
            resort_name,
        )

        # Generate SkiResort schema
        ski_resort_schema = self._generate_ski_resort_schema(
            resort_name,
            country,
            input_data.region,
            input_data.basic_info,
            input_data.family_metrics,
        )

        # Ensure llms.txt is optimized
        llms_txt = self._optimize_llms_txt(
            generated.llms_txt,
            resort_name,
            country,
            input_data.family_metrics,
        )

        # Calculate GEO score
        geo_score = self._calculate_geo_score(
            tables=tables,
            faqs=generated.faqs,
            faq_schema=faq_schema,
            sections=generated.sections,
            llms_txt=llms_txt,
        )

        # Build output
        output = OptimizeOutput(
            resort_name=resort_name,
            country=country,
            region=input_data.region,
            sections=generated.sections,
            tables=tables,
            faqs=generated.faqs,
            faq_schema=faq_schema,
            ski_resort_schema=ski_resort_schema,
            seo_meta=generated.seo_meta,
            llms_txt=llms_txt,
            geo_score=geo_score,
            optimized_at=datetime.utcnow(),
            errors=self.errors,
        )

        # Log completion
        if self.task_id:
            log_reasoning(
                task_id=self.task_id,
                agent_name="optimize_for_geo",
                action="complete_optimization",
                reasoning=f"GEO optimization complete for {resort_name}. Score: {geo_score.overall_score:.2f}",
                metadata={"geo_score": geo_score.model_dump()},
            )

        return output

    def _generate_tables(
        self,
        basic_info: BasicInfo,
        family_metrics: FamilyMetrics,
        costs: CostEstimates,
        resort_name: str,
    ) -> list[OptimizedTable]:
        """Generate GEO-optimized data tables."""
        tables = []

        # Family Metrics Table
        family_rows = []
        if family_metrics.family_overall_score:
            family_rows.append(("Family Score", f"{family_metrics.family_overall_score}/10"))
        if family_metrics.best_age_min and family_metrics.best_age_max:
            family_rows.append(("Best Ages", f"{family_metrics.best_age_min}-{family_metrics.best_age_max} years"))
        if family_metrics.has_childcare is not None:
            family_rows.append(("Childcare", "Yes" if family_metrics.has_childcare else "No"))
        if family_metrics.childcare_min_age_months:
            family_rows.append(("Childcare Min Age", f"{family_metrics.childcare_min_age_months} months"))
        if family_metrics.ski_school_min_age:
            family_rows.append(("Ski School Min Age", f"{family_metrics.ski_school_min_age} years"))
        if family_metrics.kids_ski_free_age:
            family_rows.append(("Kids Ski Free", f"Under {family_metrics.kids_ski_free_age}"))
        if family_metrics.has_magic_carpet is not None:
            family_rows.append(("Magic Carpet", "Yes" if family_metrics.has_magic_carpet else "No"))

        if family_rows:
            tables.append(self._create_table("family_metrics", "Family Information", family_rows))

        # Terrain Table
        terrain_rows = []
        if basic_info.terrain_beginner_pct:
            terrain_rows.append(("Beginner", f"{basic_info.terrain_beginner_pct}%"))
        if basic_info.terrain_intermediate_pct:
            terrain_rows.append(("Intermediate", f"{basic_info.terrain_intermediate_pct}%"))
        if basic_info.terrain_advanced_pct:
            terrain_rows.append(("Advanced/Expert", f"{basic_info.terrain_advanced_pct}%"))
        if basic_info.vertical_drop:
            terrain_rows.append(("Vertical Drop", f"{basic_info.vertical_drop}m"))
        if basic_info.num_lifts:
            terrain_rows.append(("Number of Lifts", str(basic_info.num_lifts)))
        if basic_info.skiable_acres:
            terrain_rows.append(("Skiable Terrain", f"{basic_info.skiable_acres} acres"))

        if terrain_rows:
            tables.append(self._create_table("terrain", "Terrain Breakdown", terrain_rows))

        # Cost Table
        cost_rows = []
        currency = costs.currency
        if costs.lift_adult_daily:
            cost_rows.append(("Adult Day Pass", f"{currency} {costs.lift_adult_daily:.0f}"))
        if costs.lift_child_daily:
            cost_rows.append(("Child Day Pass", f"{currency} {costs.lift_child_daily:.0f}"))
        if costs.lift_family_daily:
            cost_rows.append(("Family of 4 Daily", f"{currency} {costs.lift_family_daily:.0f}"))
        if costs.lodging_budget_nightly:
            cost_rows.append(("Budget Lodging/Night", f"{currency} {costs.lodging_budget_nightly:.0f}"))
        if costs.lodging_mid_nightly:
            cost_rows.append(("Mid-Range Lodging/Night", f"{currency} {costs.lodging_mid_nightly:.0f}"))
        if costs.meal_family_avg:
            cost_rows.append(("Family Meal Average", f"{currency} {costs.meal_family_avg:.0f}"))
        if costs.estimated_family_daily:
            cost_rows.append(("Estimated Daily Total (Family of 4)", f"{currency} {costs.estimated_family_daily:.0f}"))

        if cost_rows:
            tables.append(self._create_table("costs", "Cost Estimates", cost_rows))

        return tables

    def _create_table(
        self,
        name: str,
        title: str,
        rows: list[tuple[str, str]],
    ) -> OptimizedTable:
        """Create an optimized table in both markdown and HTML formats."""
        # Markdown format
        md_lines = [f"### {title}", "", "| Metric | Value |", "|--------|-------|"]
        for label, value in rows:
            md_lines.append(f"| {label} | {value} |")
        markdown = "\n".join(md_lines)

        # HTML format with semantic markup
        html_lines = [
            f'<table class="geo-table" data-table-type="{name}">',
            f"<caption>{title}</caption>",
            "<thead><tr><th>Metric</th><th>Value</th></tr></thead>",
            "<tbody>",
        ]
        for label, value in rows:
            html_lines.append(f"<tr><td>{label}</td><td>{value}</td></tr>")
        html_lines.extend(["</tbody>", "</table>"])
        html = "\n".join(html_lines)

        return OptimizedTable(name=name, markdown=markdown, html=html)

    def _generate_faq_schema(
        self,
        faqs: list[FAQItem],
        resort_name: str,
    ) -> SchemaMarkup | None:
        """Generate Schema.org FAQPage markup."""
        if not faqs:
            return None

        json_ld = {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": faq.question,
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": faq.answer,
                    },
                }
                for faq in faqs
            ],
        }

        return SchemaMarkup(type="FAQPage", json_ld=json_ld)

    def _generate_ski_resort_schema(
        self,
        resort_name: str,
        country: str,
        region: str | None,
        basic_info: BasicInfo,
        family_metrics: FamilyMetrics,
    ) -> SchemaMarkup:
        """Generate Schema.org SkiResort markup."""
        json_ld: dict[str, Any] = {
            "@context": "https://schema.org",
            "@type": "SkiResort",
            "name": resort_name,
            "address": {
                "@type": "PostalAddress",
                "addressCountry": country,
            },
        }

        if region:
            json_ld["address"]["addressRegion"] = region

        if basic_info.elevation_base and basic_info.elevation_top:
            json_ld["elevation"] = {
                "@type": "QuantitativeValue",
                "minValue": basic_info.elevation_base,
                "maxValue": basic_info.elevation_top,
                "unitCode": "MTR",
            }

        if basic_info.num_lifts:
            json_ld["amenityFeature"] = [
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "Number of Lifts",
                    "value": basic_info.num_lifts,
                }
            ]

        # Add family-specific features
        if family_metrics.has_childcare:
            if "amenityFeature" not in json_ld:
                json_ld["amenityFeature"] = []
            json_ld["amenityFeature"].append(
                {
                    "@type": "LocationFeatureSpecification",
                    "name": "Childcare",
                    "value": True,
                }
            )

        return SchemaMarkup(type="SkiResort", json_ld=json_ld)

    def _optimize_llms_txt(
        self,
        existing_llms_txt: str | None,
        resort_name: str,
        country: str,
        family_metrics: FamilyMetrics,
    ) -> str:
        """Ensure llms.txt is properly formatted for AI crawlers."""
        if existing_llms_txt:
            # Add any missing sections
            lines = existing_llms_txt.split("\n")

            # Ensure it has key sections
            has_quick_facts = any("Quick Facts" in line for line in lines)
            has_family_info = any("Family" in line for line in lines)

            if not has_quick_facts or not has_family_info:
                # Regenerate with proper structure
                return self._generate_llms_txt(resort_name, country, family_metrics)

            return existing_llms_txt

        return self._generate_llms_txt(resort_name, country, family_metrics)

    def _generate_llms_txt(
        self,
        resort_name: str,
        country: str,
        family_metrics: FamilyMetrics,
    ) -> str:
        """Generate llms.txt from scratch."""
        lines = [
            f"# {resort_name} - Family Ski Resort Guide",
            "",
            f"Resort: {resort_name}",
            f"Country: {country}",
            "",
            "## Quick Facts",
        ]

        if family_metrics.family_overall_score:
            lines.append(f"Family Score: {family_metrics.family_overall_score}/10")
        if family_metrics.best_age_min and family_metrics.best_age_max:
            lines.append(f"Best for kids ages: {family_metrics.best_age_min}-{family_metrics.best_age_max}")
        if family_metrics.has_childcare:
            lines.append("Childcare: Available")
        if family_metrics.kids_ski_free_age:
            lines.append(f"Kids ski free: Under {family_metrics.kids_ski_free_age}")

        lines.extend([
            "",
            "## About This Guide",
            "This is a family-focused ski resort guide from Snowthere.com.",
            "Content is designed to help parents plan ski trips with children.",
            "",
            "---",
            "Source: Snowthere.com",
            f"Last Updated: {datetime.utcnow().strftime('%Y-%m-%d')}",
        ])

        return "\n".join(lines)

    def _calculate_geo_score(
        self,
        tables: list[OptimizedTable],
        faqs: list[FAQItem],
        faq_schema: SchemaMarkup | None,
        sections: dict[str, str],
        llms_txt: str | None,
    ) -> GEOScore:
        """Calculate GEO optimization score."""
        # Tables score (0-1): Tables have 96% AI parse rate vs 73% for prose
        tables_score = min(len(tables) / 3, 1.0)  # Max score at 3+ tables

        # FAQs score (0-1): Schema markup is critical
        faqs_base = min(len(faqs) / 6, 0.5)  # Up to 0.5 for having FAQs
        faqs_schema = 0.5 if faq_schema else 0.0  # 0.5 for schema markup
        faqs_score = faqs_base + faqs_schema

        # Structured data score
        structured_data_score = 1.0 if faq_schema else 0.0

        # BLUF score: Quick take should be at top
        has_quick_take = "quick_take" in sections and len(sections.get("quick_take", "")) > 100
        bluf_score = 1.0 if has_quick_take else 0.0

        # llms.txt score
        llms_txt_score = 1.0 if llms_txt and len(llms_txt) > 200 else 0.0

        # Overall weighted score
        overall = (
            tables_score * 0.25 +
            faqs_score * 0.25 +
            structured_data_score * 0.20 +
            bluf_score * 0.15 +
            llms_txt_score * 0.15
        )

        return GEOScore(
            tables_score=round(tables_score, 2),
            faqs_score=round(faqs_score, 2),
            structured_data_score=round(structured_data_score, 2),
            bluf_score=round(bluf_score, 2),
            llms_txt_score=round(llms_txt_score, 2),
            overall_score=round(overall, 2),
        )


async def optimize_for_geo(
    resort_name: str,
    country: str,
    generated_content: Any,  # GenerateOutput
    basic_info: BasicInfo | None = None,
    family_metrics: FamilyMetrics | None = None,
    costs: CostEstimates | None = None,
    region: str | None = None,
    task_id: str | None = None,
) -> OptimizeOutput:
    """
    Convenience function to optimize content for GEO.

    Args:
        resort_name: Resort name
        country: Country
        generated_content: Output from generate_guide agent
        basic_info: Basic resort info
        family_metrics: Family-specific metrics
        costs: Cost estimates
        region: Region/state
        task_id: Optional task ID for tracking

    Returns:
        OptimizeOutput with GEO-enhanced content
    """
    input_data = OptimizeInput(
        resort_name=resort_name,
        country=country,
        region=region,
        generated_content=generated_content,
        basic_info=basic_info or BasicInfo(),
        family_metrics=family_metrics or FamilyMetrics(),
        costs=costs or CostEstimates(),
    )

    agent = OptimizeForGeoAgent(task_id=task_id)
    return await agent.optimize(input_data)
