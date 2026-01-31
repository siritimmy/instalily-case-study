"""
Troubleshooting Agent - Diagnosis Specialist

Handles troubleshooting queries and returns DiagnosisResponse.
Uses diagnose_issue tool from web_fetcher.

UI Component: DiagnosticFlow (symptom → cause → solution flow)
Example queries: "My ice maker isn't working", "Dishwasher won't drain"
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from typing import Literal

from .response_models import DiagnosisResponse
from .router_agent import ExtractedEntities
from .models import DiagnosisResult, DiagnosisInput, PartResult
from .web_fetcher import diagnose_issue, search_parts

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Model configuration
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


# System prompt for troubleshooting specialist
TROUBLESHOOTING_SYSTEM_PROMPT = """You are a PartSelect troubleshooting specialist for refrigerator and dishwasher problems.

Your job is to diagnose appliance issues and recommend parts to fix them.

AVAILABLE TOOLS:
1. diagnose_issue_tool - Diagnose problems based on symptoms
2. search_parts_tool - Find parts to fix the issue

DIAGNOSIS PROCESS:
1. Identify the symptom from user description
2. Determine appliance type (refrigerator or dishwasher)
3. Get brand if mentioned (helps with diagnosis accuracy)
4. Use diagnose_issue_tool to get likely causes
5. Recommend specific parts to fix each cause

DIY DIFFICULTY LEVELS:
- "easy" - Simple replacement, no special tools
- "moderate" - Some disassembly required, basic tools
- "difficult" - Complex repair, may need specialized tools
- "call_professional" - Requires licensed technician (gas, electrical, sealed systems)

PROFESSIONAL REQUIRED FOR:
- Gas leak or gas line issues
- Refrigerant/sealed system problems
- Complex electrical issues
- Structural damage

TROUBLESHOOTING STEPS:
Always provide steps to help verify the diagnosis before purchasing parts.
This helps customers avoid buying the wrong parts.

OUTPUT:
Provide a helpful diagnosis with:
- Likely causes ranked by probability
- Recommended parts for each cause
- DIY difficulty assessment
- Troubleshooting steps to verify the issue"""


# Create the troubleshooting agent
troubleshooting_agent = Agent(
    model=model,
    output_type=DiagnosisResponse,
    system_prompt=TROUBLESHOOTING_SYSTEM_PROMPT,
)


@troubleshooting_agent.tool
async def diagnose_issue_tool(
    ctx: RunContext,
    appliance_type: Literal["refrigerator", "dishwasher"],
    brand: str,
    symptom: str
) -> DiagnosisResult:
    """Diagnose appliance problems and recommend parts to fix them.

    Args:
        appliance_type: 'refrigerator' or 'dishwasher'
        brand: The appliance brand (e.g., 'Whirlpool', 'GE', 'Samsung')
        symptom: What's wrong (e.g., 'ice maker not working', 'won't drain')

    Returns:
        Diagnosis with likely causes, recommended parts, and troubleshooting steps
    """
    result = await diagnose_issue(appliance_type, brand, symptom)

    part_results = [
        PartResult(
            part_number=p["part_number"],
            name=p["name"],
            price=p["price"],
            image_url=p["image_url"],
            manufacturer=p["manufacturer"],
            in_stock=p["in_stock"],
            part_select_url=p["part_select_url"],
        )
        for p in result.get("recommended_parts", [])
    ]

    return DiagnosisResult(
        likely_causes=result.get("likely_causes", []),
        recommended_parts=part_results,
        diy_difficulty=result.get("diy_difficulty", "moderate"),
        troubleshooting_steps=result.get("troubleshooting_steps", []),
    )


@troubleshooting_agent.tool
async def search_parts_tool(ctx: RunContext, query: str) -> list[PartResult]:
    """Search for parts related to the diagnosed issue.

    Use this to find additional parts that might be needed.

    Args:
        query: Search query for parts
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


class TroubleshootingAgent:
    """Troubleshooting agent that diagnoses appliance problems."""

    def __init__(self):
        self.agent = troubleshooting_agent

    async def run(
        self,
        message: str,
        entities: ExtractedEntities
    ) -> DiagnosisResponse:
        """
        Run the troubleshooting agent with extracted entities.

        Args:
            message: The user's original message
            entities: Extracted entities from the router

        Returns:
            DiagnosisResponse with diagnosis and recommended parts
        """
        # Extract symptom and appliance info from entities
        symptom = entities.symptom or message
        appliance_type = entities.appliance_type
        brand = entities.brand or "Unknown"

        # If appliance type is not specified, try to infer from symptom
        if not appliance_type:
            symptom_lower = symptom.lower()
            if any(word in symptom_lower for word in ["ice", "freezer", "cooling", "cold", "fridge", "refrigerator"]):
                appliance_type = "refrigerator"
            elif any(word in symptom_lower for word in ["dish", "drain", "spray", "rack", "detergent"]):
                appliance_type = "dishwasher"

        # If still no appliance type, ask for clarification
        if not appliance_type:
            return DiagnosisResponse(
                type="diagnosis",
                message="I'd be happy to help diagnose the issue. Is this problem with your refrigerator or dishwasher?",
                symptom=symptom,
                appliance_type=None,
                likely_causes=[],
                recommended_parts=[],
                diy_difficulty="moderate",
                troubleshooting_steps=[],
            )

        # Build the prompt
        prompt = f"""User describes a problem: {message}

Diagnosis context:
- Symptom: {symptom}
- Appliance type: {appliance_type}
- Brand: {brand}

Diagnose this issue and return a DiagnosisResponse with:
- A helpful message summarizing the diagnosis
- The symptom being diagnosed
- Likely causes ranked by probability
- Recommended parts to fix each cause
- DIY difficulty level
- Troubleshooting steps to verify the diagnosis before purchasing"""

        # Run the agent
        result = await self.agent.run(prompt)
        return result.output
