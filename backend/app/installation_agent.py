"""
Installation Agent - Installation Guide Specialist

Handles installation queries and returns InstallationResponse.
Uses get_installation_guide tool from web_fetcher.

UI Component: InstallationWizard (step-by-step with progress tracker)
Example queries: "How do I install PS11752778?", "What tools do I need?"
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext

from .response_models import InstallationResponse
from .router_agent import ExtractedEntities
from .models import InstallationGuide, InstallationStep
from .web_fetcher import get_installation_guide

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Model configuration
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


# System prompt for installation specialist
INSTALLATION_SYSTEM_PROMPT = """You are a PartSelect installation specialist for refrigerator and dishwasher parts.

Your job is to provide safe, clear installation guidance.

AVAILABLE TOOLS:
1. get_installation_guide_tool - Get step-by-step installation instructions

INFORMATION TO PROVIDE:
- Difficulty level (easy/moderate/difficult)
- Estimated time
- Required tools
- Step-by-step instructions
- Video tutorials (if available)
- PDF manuals (if available)
- Safety warnings

SAFETY RULES (CRITICAL):
1. ALWAYS include safety warnings at the beginning
2. For "difficult" installations → Recommend professional installation
3. Gas appliances → REQUIRE licensed professional
4. Electrical work beyond unplugging → REQUIRE licensed electrician
5. Water line work → Emphasize shutoff procedures

STANDARD SAFETY WARNINGS:
- "Disconnect power before starting any repair"
- "Turn off water supply for water-related parts"
- "Wear safety glasses when working with glass or metal"
- "Keep children and pets away from work area"

OUTPUT:
Provide clear, safe installation guidance with emphasis on user safety.
If installation is too complex, recommend professional help."""


# Create the installation agent
installation_agent = Agent(
    model=model,
    output_type=InstallationResponse,
    system_prompt=INSTALLATION_SYSTEM_PROMPT,
)


@installation_agent.tool
async def get_installation_guide_tool(ctx: RunContext, part_number: str) -> InstallationGuide:
    """Get step-by-step installation instructions for a part.

    Returns: difficulty level, estimated time, tools needed, and detailed steps.

    Args:
        part_number: The PartSelect part number (e.g., 'PS11752778')
    """
    guide = await get_installation_guide(part_number)
    if not guide:
        return InstallationGuide(
            part_number=part_number,
            difficulty="moderate",
            estimated_time_minutes=0,
            tools_required=[],
            steps=[],
            video_url=None,
            pdf_url=None,
        )

    return InstallationGuide(**guide)


class InstallationAgent:
    """Installation agent that provides installation guidance."""

    def __init__(self):
        self.agent = installation_agent

    async def run(
        self,
        message: str,
        entities: ExtractedEntities
    ) -> InstallationResponse:
        """
        Run the installation agent with extracted entities.

        Args:
            message: The user's original message
            entities: Extracted entities from the router

        Returns:
            InstallationResponse with installation guide and safety warnings
        """
        # Get the part number from entities
        part_number = entities.part_numbers[0] if entities.part_numbers else None

        if not part_number:
            # No part number found - return helpful error
            return InstallationResponse(
                type="installation",
                message="I need a part number to provide installation instructions. Could you please provide the PartSelect part number (e.g., PS11752778)?",
                part_number="",
                difficulty="moderate",
                estimated_time_minutes=0,
                tools_required=[],
                steps=[],
                video_url=None,
                pdf_url=None,
                safety_warnings=[
                    "Always disconnect power before starting any repair",
                    "Turn off water supply for water-related parts",
                ],
            )

        # Build the prompt
        prompt = f"""User request: {message}

Part number for installation: {part_number}
{f"Appliance type: {entities.appliance_type}" if entities.appliance_type else ""}
{f"Brand: {entities.brand}" if entities.brand else ""}

Get the installation guide for this part and return an InstallationResponse with:
- A helpful overview message
- Difficulty level
- Estimated time
- Required tools
- Step-by-step instructions
- Video URL if available
- PDF URL if available
- Safety warnings (ALWAYS include these)

IMPORTANT: Always include safety warnings, especially:
- Disconnect power before starting
- Turn off water for water-related parts
- Recommend professional help for difficult installations"""

        # Run the agent
        result = await self.agent.run(prompt)

        # Ensure safety warnings are always present
        response = result.output
        if not response.safety_warnings:
            response.safety_warnings = [
                "Always disconnect power before starting any repair",
                "Turn off water supply for water-related parts",
            ]

        return response
