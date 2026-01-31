"""
Specialized Response Types for Sub-Agent Architecture

Each sub-agent returns a unique response type with a `type` discriminator field
that the frontend uses to render the appropriate UI component.

Response Type → UI Component Mapping:
- SearchResponse → ProductGrid
- PartDetailsResponse → DetailedProductView
- CompatibilityResponse → CompatibilityCard
- InstallationResponse → InstallationWizard
- DiagnosisResponse → DiagnosticFlow
"""

from pydantic import BaseModel, Field
from typing import Literal, Optional, Union

from .models import PartResult, PartDetails, InstallationStep


class SearchResponse(BaseModel):
    """Response for product search queries.

    UI Component: ProductGrid
    Triggered by: "Find ice makers", "Show me water filters", etc.
    """
    type: Literal["search"] = "search"
    message: str = Field(description="Natural language context about the search results")
    parts: list[PartResult] = Field(default=[], description="3-8 relevant parts")
    total_results: int = Field(default=0, description="Total number of parts found")
    search_query: str = Field(default="", description="The search query used")
    appliance_type: Optional[Literal["refrigerator", "dishwasher"]] = Field(
        default=None, description="Type of appliance filtered for"
    )


class PartDetailsResponse(BaseModel):
    """Response for detailed part information queries.

    UI Component: DetailedProductView
    Triggered by: "Tell me about PS11752778", "What's the price of...?", etc.
    """
    type: Literal["part_details"] = "part_details"
    message: str = Field(description="Natural language description of the part")
    part: Optional[PartDetails] = Field(
        default=None, description="Full part info with specs, reviews, warranty"
    )
    compatible_models: list[str] = Field(
        default=[], description="Top 10-20 compatible appliance models"
    )
    related_parts: list[PartResult] = Field(
        default=[], description="Commonly bought together or alternative parts"
    )


class CompatibilityResponse(BaseModel):
    """Response for compatibility check queries.

    UI Component: CompatibilityCard (with visual ✓/✗ indicator)
    Triggered by: "Is PS11752778 compatible with WDT780SAEM1?", etc.
    """
    type: Literal["compatibility"] = "compatibility"
    message: str = Field(description="Explanation of compatibility result")
    part_number: str = Field(default="", description="The part being checked")
    model_number: str = Field(default="", description="The appliance model being checked")
    is_compatible: bool = Field(default=False, description="Whether the part fits the model")
    confidence: Literal["confirmed", "likely", "unlikely"] = Field(
        default="unlikely", description="Confidence level of the compatibility check"
    )
    explanation: str = Field(
        default="", description="Detailed explanation of compatibility determination"
    )
    alternative_parts: list[PartResult] = Field(
        default=[], description="Alternative parts if incompatible"
    )


class InstallationResponse(BaseModel):
    """Response for installation guide queries.

    UI Component: InstallationWizard (step-by-step with progress tracker)
    Triggered by: "How do I install PS11752778?", "What tools do I need?", etc.
    """
    type: Literal["installation"] = "installation"
    message: str = Field(description="Overview of the installation process")
    part_number: str = Field(default="", description="The part to install")
    difficulty: Literal["easy", "moderate", "difficult"] = Field(
        default="moderate", description="Installation difficulty level"
    )
    estimated_time_minutes: int = Field(
        default=30, description="Estimated installation time"
    )
    tools_required: list[str] = Field(
        default=[], description="Tools needed for installation"
    )
    steps: list[InstallationStep] = Field(
        default=[], description="Step-by-step installation instructions"
    )
    video_url: Optional[str] = Field(
        default=None, description="YouTube or other video tutorial URL"
    )
    pdf_url: Optional[str] = Field(
        default=None, description="PDF installation manual URL"
    )
    safety_warnings: list[str] = Field(
        default=[], description="Important safety warnings"
    )


class DiagnosisResponse(BaseModel):
    """Response for troubleshooting/diagnosis queries.

    UI Component: DiagnosticFlow (symptom → cause → solution flow)
    Triggered by: "My ice maker isn't working", "Dishwasher won't drain", etc.
    """
    type: Literal["diagnosis"] = "diagnosis"
    message: str = Field(description="Overview of the diagnosis")
    symptom: str = Field(default="", description="The symptom being diagnosed")
    appliance_type: Optional[Literal["refrigerator", "dishwasher"]] = Field(
        default=None, description="Type of appliance"
    )
    likely_causes: list[str] = Field(
        default=[], description="Ranked list of likely causes"
    )
    recommended_parts: list[PartResult] = Field(
        default=[], description="Parts to fix the issue"
    )
    diy_difficulty: Literal["easy", "moderate", "difficult", "call_professional"] = Field(
        default="moderate", description="DIY difficulty assessment"
    )
    troubleshooting_steps: list[str] = Field(
        default=[], description="Steps to verify diagnosis before purchasing parts"
    )


class OffTopicResponse(BaseModel):
    """Response for off-topic queries (not refrigerator/dishwasher related).

    UI Component: Simple message display
    Triggered by: Questions about other appliances, general queries, etc.
    """
    type: Literal["off_topic"] = "off_topic"
    message: str = Field(
        description="Polite message explaining scope and redirecting user"
    )


# Union type for API response - frontend uses the `type` field to render appropriate component
AgentResponse = Union[
    SearchResponse,
    PartDetailsResponse,
    CompatibilityResponse,
    InstallationResponse,
    DiagnosisResponse,
    OffTopicResponse,
]
