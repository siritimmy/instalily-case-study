"""
Part Details Agent - Product Information Specialist

Handles queries about specific parts and returns PartDetailsResponse.
Uses get_part_details tool from web_fetcher.

UI Component: DetailedProductView
Example queries: "Tell me about PS11752778", "What's the price of...?"
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from .response_models import PartDetailsResponse
from .router_agent import ExtractedEntities
from .models import PartDetails, PartResult
from .web_fetcher import get_part_details, search_parts

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Model configuration
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


# System prompt for part details specialist
PART_DETAILS_SYSTEM_PROMPT = """You are a PartSelect product information specialist for refrigerator and dishwasher parts.

Your job is to provide comprehensive, accurate information about specific parts.

AVAILABLE TOOLS:
1. get_part_details_tool - Get full specifications for a part number
2. get_related_parts_tool - Find related or alternative parts

INFORMATION TO PROVIDE:
- Full product name and description
- Price and availability
- Specifications and features
- Compatible appliance models (top 10-20)
- Installation difficulty
- Warranty information
- Related/alternative parts

GUIDELINES:
- If part not found, provide helpful error message with suggestions
- Highlight key features that matter to customers
- Mention if part is in stock or backordered
- Include installation difficulty assessment

OUTPUT:
Provide a detailed, helpful response about the part with all relevant information.
Focus on helping the customer understand if this is the right part for them."""


# Create the part details agent
part_details_agent = Agent(
    model=model,
    output_type=PartDetailsResponse,
    system_prompt=PART_DETAILS_SYSTEM_PROMPT,
)


@part_details_agent.tool
async def get_part_details_tool(ctx: RunContext, part_number: str) -> PartDetails:
    """Get detailed information about a specific part.

    Returns: full specs, price, compatibility list, installation difficulty, warranty info.

    Args:
        part_number: The PartSelect part number (e.g., 'PS11752778')
    """
    details = await get_part_details(part_number)
    if not details:
        return PartDetails(
            part_number=part_number,
            full_name="Part not found",
            description=f"Part number '{part_number}' was not found in the PartSelect catalog. Please verify the part number is correct.",
            price=0.0,
            image_urls=[],
            manufacturer="Unknown",
            in_stock=False,
            compatible_models=[],
            installation_difficulty="moderate",
            warranty_info="Unknown",
            part_select_url=f"https://www.partselect.com/Search.aspx?SearchTerm={part_number}",
        )

    return PartDetails(**details)


@part_details_agent.tool
async def get_related_parts_tool(ctx: RunContext, query: str) -> list[PartResult]:
    """Find related or alternative parts.

    Use this to find parts that are commonly bought together or alternatives.

    Args:
        query: Search query for related parts
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


class PartDetailsAgent:
    """Part details agent that provides comprehensive part information."""

    def __init__(self):
        self.agent = part_details_agent

    async def run(
        self,
        message: str,
        entities: ExtractedEntities
    ) -> PartDetailsResponse:
        """
        Run the part details agent with extracted entities.

        Args:
            message: The user's original message
            entities: Extracted entities from the router

        Returns:
            PartDetailsResponse with full part information
        """
        # Get the part number from entities
        part_number = entities.part_numbers[0] if entities.part_numbers else None

        if not part_number:
            # No part number found - return error response
            return PartDetailsResponse(
                type="part_details",
                message="I need a part number to look up details. Could you please provide the PartSelect part number (e.g., PS11752778)?",
                part=None,
                compatible_models=[],
                related_parts=[],
            )

        # Build the prompt
        prompt = f"""User request: {message}

Part number to look up: {part_number}

Get the full details for this part and return a PartDetailsResponse with:
- A helpful message describing the part
- The complete part information
- Compatible models (top 10-20)
- Related parts that might be useful"""

        # Run the agent
        result = await self.agent.run(prompt)
        return result.output
