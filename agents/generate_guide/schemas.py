"""Pydantic schemas for generate_guide agent."""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field

from ..research_resort.schemas import ResearchOutput


class ObjectiveStatus(str, Enum):
    """Status of an objective/task."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class GenerateInput(BaseModel):
    """Input for content generation."""

    resort_id: str | None = Field(None, description="Resort ID if updating existing")
    research_data: ResearchOutput = Field(..., description="Research data from research_resort agent")
    voice_profile: str = Field(default="instagram_mom", description="Voice profile to use")
    sections: list[str] = Field(
        default=[
            "quick_take",
            "getting_there",
            "where_to_stay",
            "lift_tickets",
            "on_mountain",
            "off_mountain",
            "parent_reviews_summary",
        ],
        description="Content sections to generate",
    )


class GeneratedSection(BaseModel):
    """A generated content section."""

    name: str = Field(..., description="Section name")
    content: str = Field(..., description="Generated HTML content")
    tokens_used: int = Field(default=0, description="Tokens used to generate")


class FAQItem(BaseModel):
    """A single FAQ item."""

    question: str
    answer: str


class SEOMetadata(BaseModel):
    """SEO metadata for the page."""

    title: str = Field(..., description="Page title (50-60 chars)")
    description: str = Field(..., description="Meta description (150-160 chars)")


class GenerateOutput(BaseModel):
    """Complete generated content for a resort."""

    resort_name: str
    country: str
    region: str | None = None

    # Generated content sections
    sections: dict[str, str] = Field(default_factory=dict, description="Section name -> HTML content")

    # FAQ and SEO
    faqs: list[FAQItem] = Field(default_factory=list)
    seo_meta: SEOMetadata | None = None

    # llms.txt content for AI crawlers
    llms_txt: str | None = None

    # Metadata
    voice_profile: str = "instagram_mom"
    total_tokens_used: int = 0
    generated_at: datetime = Field(default_factory=datetime.utcnow)
    errors: list[str] = Field(default_factory=list)


class ObjectiveRequest(BaseModel):
    """Request to create a new objective."""

    input: GenerateInput


class ObjectiveResponse(BaseModel):
    """Response for objective status."""

    id: str
    status: ObjectiveStatus
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    result: GenerateOutput | None = None
    error: str | None = None


class AgentIdentity(BaseModel):
    """Agent identity response."""

    name: str = "generate_guide"
    version: str = "0.1.0"
    description: str = "Creates family-focused ski resort guide content in instagram mom voice"


class ToolManifest(BaseModel):
    """Tool manifest for IACP."""

    name: str = "generate_guide"
    description: str = "Generate family-friendly ski resort guide content"
    input_schema: dict = Field(default_factory=lambda: GenerateInput.model_json_schema())
    output_schema: dict = Field(default_factory=lambda: GenerateOutput.model_json_schema())
