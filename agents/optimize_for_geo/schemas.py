"""Pydantic schemas for optimize_for_geo agent."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..generate_guide.schemas import FAQItem, GenerateOutput, SEOMetadata
from ..research_resort.schemas import BasicInfo, CostEstimates, FamilyMetrics


class ObjectiveStatus(str, Enum):
    """Status of an objective/task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class OptimizeInput(BaseModel):
    """Input for GEO optimization."""

    resort_id: str | None = Field(None, description="Resort ID for database update")
    resort_name: str = Field(..., description="Resort name")
    country: str = Field(..., description="Country")
    region: str | None = Field(None, description="Region")

    # Content from generate_guide
    generated_content: GenerateOutput = Field(..., description="Generated content to optimize")

    # Structured data from research
    basic_info: BasicInfo = Field(default_factory=BasicInfo)
    family_metrics: FamilyMetrics = Field(default_factory=FamilyMetrics)
    costs: CostEstimates = Field(default_factory=CostEstimates)


class SchemaMarkup(BaseModel):
    """Schema.org markup for structured data."""

    type: str = Field(..., description="Schema type (FAQPage, SkiResort, etc.)")
    json_ld: dict[str, Any] = Field(..., description="JSON-LD structured data")


class OptimizedTable(BaseModel):
    """An optimized data table for GEO."""

    name: str = Field(..., description="Table name/purpose")
    markdown: str = Field(..., description="Markdown table format")
    html: str = Field(..., description="HTML table with proper structure")


class GEOScore(BaseModel):
    """GEO optimization score breakdown."""

    tables_score: float = Field(default=0.0, ge=0, le=1)
    faqs_score: float = Field(default=0.0, ge=0, le=1)
    structured_data_score: float = Field(default=0.0, ge=0, le=1)
    bluf_score: float = Field(default=0.0, ge=0, le=1)
    llms_txt_score: float = Field(default=0.0, ge=0, le=1)
    overall_score: float = Field(default=0.0, ge=0, le=1)


class OptimizeOutput(BaseModel):
    """Complete GEO-optimized content."""

    resort_name: str
    country: str
    region: str | None = None

    # Optimized content sections
    sections: dict[str, str] = Field(default_factory=dict)

    # Tables for AI parsing
    tables: list[OptimizedTable] = Field(default_factory=list)

    # FAQs with Schema.org markup
    faqs: list[FAQItem] = Field(default_factory=list)
    faq_schema: SchemaMarkup | None = None

    # Other structured data
    ski_resort_schema: SchemaMarkup | None = None

    # SEO metadata
    seo_meta: SEOMetadata | None = None

    # llms.txt for AI crawlers
    llms_txt: str | None = None

    # GEO optimization score
    geo_score: GEOScore = Field(default_factory=GEOScore)

    # Metadata
    optimized_at: datetime = Field(default_factory=datetime.utcnow)
    errors: list[str] = Field(default_factory=list)


class ObjectiveRequest(BaseModel):
    """Request to create a new objective."""

    input: OptimizeInput


class ObjectiveResponse(BaseModel):
    """Response for objective status."""

    id: str
    status: ObjectiveStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: OptimizeOutput | None = None
    error: str | None = None


class AgentIdentity(BaseModel):
    """Agent identity response."""

    name: str = "optimize_for_geo"
    version: str = "0.1.0"
    description: str = "Enhances resort content for AI citation and search engine optimization"


class ToolManifest(BaseModel):
    """Tool manifest for IACP."""

    name: str = "optimize_for_geo"
    description: str = "Optimize content for GEO (Generative Engine Optimization)"
    input_schema: dict = Field(default_factory=lambda: OptimizeInput.model_json_schema())
    output_schema: dict = Field(default_factory=lambda: OptimizeOutput.model_json_schema())
