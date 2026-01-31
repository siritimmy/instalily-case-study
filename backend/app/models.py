from pydantic import BaseModel, Field
from typing import Literal, Optional


class PartResult(BaseModel):
    part_number: str
    name: str
    price: float
    image_url: str
    manufacturer: str
    in_stock: bool
    part_select_url: str


class SearchPartsInput(BaseModel):
    query: str = Field(description="Search query (e.g., 'ice maker', 'PS11752778')")
    appliance_type: Literal["refrigerator", "dishwasher"] = Field(
        description="Type of appliance"
    )


class SearchPartsOutput(BaseModel):
    parts: list[PartResult]
    total_results: int


class PartDetails(BaseModel):
    part_number: str
    full_name: str
    description: str
    price: float
    image_urls: list[str]
    manufacturer: str
    in_stock: bool
    avg_rating: Optional[float] = None
    num_reviews: int = 0
    compatible_models: list[str]
    installation_difficulty: Literal["easy", "moderate", "difficult"]
    warranty_info: str
    part_select_url: str


class CompatibilityCheck(BaseModel):
    part_number: str
    model_number: str
    is_compatible: bool
    confidence: Literal["confirmed", "likely", "unlikely"]
    explanation: str
    alternative_parts: list[str] = []


class InstallationStep(BaseModel):
    step_number: int
    instruction: str
    image_url: Optional[str] = None
    warning: Optional[str] = None


class InstallationGuide(BaseModel):
    part_number: str
    difficulty: Literal["easy", "moderate", "difficult"]
    estimated_time_minutes: int
    tools_required: list[str]
    steps: list[InstallationStep]
    video_url: Optional[str] = None
    pdf_url: Optional[str] = None


class DiagnosisInput(BaseModel):
    appliance_type: Literal["refrigerator", "dishwasher"]
    brand: str = Field(description="e.g., Whirlpool, GE, Samsung")
    symptom: str = Field(description="What's wrong? e.g., 'ice maker not working'")


class DiagnosisResult(BaseModel):
    likely_causes: list[str]
    recommended_parts: list[PartResult]
    diy_difficulty: Literal["easy", "moderate", "difficult", "call_professional"]
    troubleshooting_steps: list[str]


class ModelPartsResult(BaseModel):
    model_number: str
    appliance_info: str
    common_parts: list[PartResult]
    all_parts_count: int
    parts_by_category: dict[str, list[PartResult]]


class ChatRequest(BaseModel):
    message: str
    conversation_history: list[dict] = []


class ChatResponse(BaseModel):
    message: str
    parts: list[PartResult] = []
