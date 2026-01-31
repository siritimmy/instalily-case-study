"""
Compatibility Agent - Part/Model Compatibility Specialist

Handles compatibility check queries and returns CompatibilityResponse.
Uses check_compatibility tool from web_fetcher.

UI Component: CompatibilityCard (with visual checkmark/X indicator)
Example queries: "Is PS11752778 compatible with WDT780SAEM1?"
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from .response_models import CompatibilityResponse
from .router_agent import ExtractedEntities
from .models import CompatibilityCheck, PartResult
from .web_fetcher import check_compatibility, search_parts

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Model configuration
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


# System prompt for compatibility specialist
COMPATIBILITY_SYSTEM_PROMPT = """You are a PartSelect compatibility verification specialist for refrigerator and dishwasher parts.

Your job is to verify if specific parts are compatible with customer appliance models.

AVAILABLE TOOLS:
1. check_compatibility_tool - Verify if a part fits a specific model
2. find_alternative_parts_tool - Find compatible alternatives if part doesn't fit

CONFIDENCE LEVELS:
- "confirmed" = 100% match found in compatibility database
- "likely" = Strong match based on similar models, recommend verification
- "unlikely" = No match found, part probably won't fit

GUIDELINES:
- Be explicit about confidence levels
- If incompatible, always suggest alternatives
- Explain WHY a part is or isn't compatible when possible
- Mention if model number format looks incorrect

OUTPUT:
Provide a clear yes/no answer with explanation and confidence level.
If incompatible, include alternative parts that would work."""


# Create the compatibility agent
compatibility_agent = Agent(
    model=model,
    output_type=CompatibilityResponse,
    system_prompt=COMPATIBILITY_SYSTEM_PROMPT,
)


@compatibility_agent.tool
async def check_compatibility_tool(
    ctx: RunContext,
    part_number: str,
    model_number: str
) -> CompatibilityCheck:
    """Check if a specific part is compatible with an appliance model.

    Args:
        part_number: The PartSelect part number (e.g., 'PS11752778')
        model_number: The appliance model number (e.g., 'WDT780SAEM1')

    Returns:
        Compatibility status with confidence level and explanation
    """
    result = await check_compatibility(part_number, model_number)
    return CompatibilityCheck(
        part_number=part_number,
        model_number=model_number,
        is_compatible=result["is_compatible"],
        confidence=result["confidence"],
        explanation=result["explanation"],
        alternative_parts=result.get("alternative_parts", []),
    )


@compatibility_agent.tool
async def find_alternative_parts_tool(ctx: RunContext, query: str) -> list[PartResult]:
    """Find alternative parts that might be compatible.

    Use this when the requested part is not compatible to suggest alternatives.

    Args:
        query: Search query for alternative parts
    """
    parts = await search_parts(query, limit=5)
    return [
        PartResult(
            part_number=p["part_number"],
            name=p["name"],
            price=p["price"],
            image_url=p["image_url"],
            manufacturer=p["manufacturer"],
            in_stock=p["in_stock"],
            part_select_url=p["part_select_url"],
        )
        for p in parts
    ]


class CompatibilityAgent:
    """Compatibility agent that verifies part/model compatibility."""

    def __init__(self):
        self.agent = compatibility_agent

    async def run(
        self,
        message: str,
        entities: ExtractedEntities
    ) -> CompatibilityResponse:
        """
        Run the compatibility agent with extracted entities.

        Args:
            message: The user's original message
            entities: Extracted entities from the router

        Returns:
            CompatibilityResponse with compatibility status and alternatives
        """
        # Get part and model numbers from entities
        part_number = entities.part_numbers[0] if entities.part_numbers else None
        model_number = entities.model_numbers[0] if entities.model_numbers else None

        # Check if we have both required pieces
        missing = []
        if not part_number:
            missing.append("part number")
        if not model_number:
            missing.append("model number")

        if missing:
            return CompatibilityResponse(
                type="compatibility",
                message=f"To check compatibility, I need both a part number and a model number. Could you please provide the {' and '.join(missing)}?",
                part_number=part_number or "",
                model_number=model_number or "",
                is_compatible=False,
                confidence="unlikely",
                explanation="Missing required information for compatibility check.",
                alternative_parts=[],
            )

        # Build the prompt
        prompt = f"""User request: {message}

Check compatibility:
- Part number: {part_number}
- Model number: {model_number}
{f"- Brand: {entities.brand}" if entities.brand else ""}
{f"- Appliance type: {entities.appliance_type}" if entities.appliance_type else ""}

Verify if this part is compatible with this model and return a CompatibilityResponse with:
- A clear message explaining the compatibility result
- The compatibility status (is_compatible)
- Confidence level (confirmed/likely/unlikely)
- Detailed explanation
- Alternative parts if not compatible"""

        # Run the agent
        result = await self.agent.run(prompt)
        return result.output
