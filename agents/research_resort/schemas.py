"""Pydantic schemas for research_resort agent."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class ObjectiveStatus(str, Enum):
    """Status of an objective/task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ResearchInput(BaseModel):
    """Input for research task."""

    resort_name: str = Field(..., description="Name of the ski resort")
    country: str = Field(..., description="Country where resort is located")
    region: str | None = Field(None, description="Region/state (optional)")
    focus_areas: list[str] = Field(
        default=["family", "costs", "logistics"],
        description="Areas to focus research on",
    )


class BasicInfo(BaseModel):
    """Basic resort information."""

    elevation_base: int | None = Field(None, description="Base elevation in meters")
    elevation_top: int | None = Field(None, description="Summit elevation in meters")
    vertical_drop: int | None = Field(None, description="Vertical drop in meters")
    terrain_beginner_pct: int | None = Field(None, description="Percent beginner terrain")
    terrain_intermediate_pct: int | None = Field(None, description="Percent intermediate terrain")
    terrain_advanced_pct: int | None = Field(None, description="Percent advanced terrain")
    num_lifts: int | None = Field(None, description="Number of lifts")
    skiable_acres: int | None = Field(None, description="Skiable acres/hectares")


class FamilyMetrics(BaseModel):
    """Family-specific metrics."""

    family_overall_score: int | None = Field(None, ge=1, le=10, description="Overall family score 1-10")
    best_age_min: int | None = Field(None, description="Minimum recommended kid age")
    best_age_max: int | None = Field(None, description="Maximum recommended kid age")
    kid_friendly_terrain_pct: int | None = Field(None, description="Percent kid-friendly terrain")
    has_childcare: bool | None = Field(None, description="Has childcare facilities")
    childcare_min_age_months: int | None = Field(None, description="Minimum age for childcare in months")
    ski_school_min_age: int | None = Field(None, description="Minimum age for ski school in years")
    kids_ski_free_age: int | None = Field(None, description="Age under which kids ski free")
    has_magic_carpet: bool | None = Field(None, description="Has magic carpet/beginner lift")
    has_kids_terrain_park: bool | None = Field(None, description="Has kids terrain park")
    perfect_if: list[str] = Field(default_factory=list, description="Perfect for these families")
    skip_if: list[str] = Field(default_factory=list, description="Skip if these apply")


class CostEstimates(BaseModel):
    """Cost estimates for the resort."""

    currency: str = Field(default="USD", description="Currency code")
    lift_adult_daily: float | None = Field(None, description="Adult daily lift ticket")
    lift_child_daily: float | None = Field(None, description="Child daily lift ticket")
    lift_family_daily: float | None = Field(None, description="Family of 4 daily lift cost")
    lodging_budget_nightly: float | None = Field(None, description="Budget lodging per night")
    lodging_mid_nightly: float | None = Field(None, description="Mid-range lodging per night")
    lodging_luxury_nightly: float | None = Field(None, description="Luxury lodging per night")
    meal_family_avg: float | None = Field(None, description="Average family meal cost")
    estimated_family_daily: float | None = Field(None, description="Estimated total daily cost family of 4")


class ReviewSnippet(BaseModel):
    """A snippet from a parent review."""

    text: str = Field(..., description="Review text snippet")
    source: str | None = Field(None, description="Source (tripadvisor, google, etc)")
    sentiment: str | None = Field(None, description="positive, negative, neutral")


class SourceReference(BaseModel):
    """Reference to a source used in research."""

    url: str = Field(..., description="Source URL")
    title: str | None = Field(None, description="Page title")
    type: str = Field(default="web", description="Source type: official, review, blog, news")
    reliability: str = Field(default="medium", description="high, medium, low")


class ResearchOutput(BaseModel):
    """Complete research output for a resort."""

    resort_name: str
    country: str
    region: str | None = None

    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    family_metrics: FamilyMetrics = Field(default_factory=FamilyMetrics)
    costs: CostEstimates = Field(default_factory=CostEstimates)

    review_snippets: list[ReviewSnippet] = Field(default_factory=list)
    sources: list[SourceReference] = Field(default_factory=list)

    # Raw research data for content generation
    raw_research: dict[str, Any] = Field(default_factory=dict)

    # Metadata
    confidence_score: float = Field(default=0.5, ge=0, le=1, description="Overall data confidence")
    researched_at: datetime = Field(default_factory=datetime.utcnow)
    errors: list[str] = Field(default_factory=list, description="Any errors during research")


class ObjectiveRequest(BaseModel):
    """Request to create a new objective."""

    input: ResearchInput


class ObjectiveResponse(BaseModel):
    """Response for objective status."""

    id: str
    status: ObjectiveStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: ResearchOutput | None = None
    error: str | None = None


class AgentIdentity(BaseModel):
    """Agent identity response."""

    name: str = "research_resort"
    version: str = "0.1.0"
    description: str = "Gathers comprehensive ski resort data from multiple sources"


class ToolManifest(BaseModel):
    """Tool manifest for IACP."""

    name: str = "research_resort"
    description: str = "Research ski resort information for family guides"
    input_schema: dict = Field(
        default_factory=lambda: ResearchInput.model_json_schema()
    )
    output_schema: dict = Field(
        default_factory=lambda: ResearchOutput.model_json_schema()
    )
