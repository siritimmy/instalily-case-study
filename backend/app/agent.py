import os
import json
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from .models import (
    SearchPartsInput,
    SearchPartsOutput,
    PartDetails,
    CompatibilityCheck,
    InstallationGuide,
    DiagnosisInput,
    DiagnosisResult,
    ModelPartsResult,
    PartResult,
)
from .web_fetcher import (
    search_parts,
    get_part_details,
    check_compatibility,
    get_installation_guide,
    diagnose_issue,
    search_by_model,
)

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Determine model to use
# Using latest Sonnet 4.5 model
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"

# Initialize agent
agent = Agent(
    model=model,
    system_prompt="""You are a specialized PartSelect assistant for refrigerator and dishwasher parts ONLY.

You help customers:
- Find the right replacement parts for refrigerators and dishwashers
- Check if specific parts are compatible with their appliance models
- Get detailed installation instructions for parts
- Troubleshoot common appliance problems and recommend parts to fix them
- Find all compatible parts for a specific appliance model

You have access to tools that fetch live data from PartSelect.com.

IMPORTANT RULES:
1. ONLY help with refrigerator and dishwasher parts
2. Do NOT help with other appliances (ovens, washers, dryers, etc.)
3. Always use tools to get accurate, up-to-date information
4. Present products clearly with part numbers, prices, and availability
5. When asked about other appliances, politely decline and say:
   "I specialize in refrigerator and dishwasher parts from PartSelect. For other appliances,
   please contact PartSelect customer service."

HANDLING INVALID PART NUMBERS:
- If get_part_details_tool returns full_name="Part not found", tell the user:
  "I couldn't find part number [XXX] in the PartSelect catalog. Please double-check the part number."
- If get_installation_guide_tool returns empty steps, tell the user:
  "I couldn't find that part number. Please verify the part number is correct."
- Do NOT show technical details, empty arrays, or JSON output to users
- Be friendly and helpful when parts aren't found

Be helpful, friendly, and focus on finding the right solutions for customers.""",
)


# Define tools for the agent


@agent.tool
async def search_parts_tool(ctx: RunContext, input: SearchPartsInput) -> SearchPartsOutput:
    """Search PartSelect catalog for parts matching a query.

    Use this to find parts by:
    - Part number (e.g., 'PS11752778')
    - Product name (e.g., 'ice maker', 'water filter')
    - Symptom or problem (e.g., 'dishwasher not cleaning')

    Specify the appliance type as either 'refrigerator' or 'dishwasher'.
    """
    parts = await search_parts(input.query, limit=6)
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
        for p in parts
    ]
    return SearchPartsOutput(parts=part_results, total_results=len(part_results))


@agent.tool
async def get_part_details_tool(
    ctx: RunContext, part_number: str
) -> PartDetails:
    """Get detailed information about a specific part.

    Returns: full specs, price, compatibility list, installation difficulty, warranty info.
    Use this when a customer wants to know everything about a particular part.

    IMPORTANT: If the full_name is "Part not found", it means the part number is invalid
    and you should tell the user that part number doesn't exist in the PartSelect catalog.
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


@agent.tool
async def check_compatibility_tool(
    ctx: RunContext, part_number: str, model_number: str
) -> CompatibilityCheck:
    """Check if a specific part is compatible with an appliance model.

    Args:
    - part_number: The part number (e.g., 'PS11752778')
    - model_number: The appliance model number (e.g., 'WDT780SAEM1')

    Returns: whether the part is compatible and alternative options if not.
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


@agent.tool
async def get_installation_guide_tool(
    ctx: RunContext, part_number: str
) -> InstallationGuide:
    """Get step-by-step installation instructions for a part.

    Returns: difficulty level, estimated time, tools needed, and detailed steps.
    Use this when customers ask 'How do I install...' a specific part.

    IMPORTANT: If steps is an empty list, it means the part was not found
    and you should tell the user that part number doesn't exist.
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


@agent.tool
async def diagnose_issue_tool(
    ctx: RunContext, input: DiagnosisInput
) -> DiagnosisResult:
    """Diagnose appliance problems and recommend parts to fix them.

    Use this when customers describe a problem with their refrigerator or dishwasher:
    - appliance_type: 'refrigerator' or 'dishwasher'
    - brand: The appliance brand (e.g., 'Whirlpool', 'GE', 'Samsung')
    - symptom: What's wrong (e.g., 'ice maker not working', 'not cooling')

    Returns: likely causes, recommended parts, difficulty level, and troubleshooting steps.
    """
    result = await diagnose_issue(input.appliance_type, input.brand, input.symptom)

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


@agent.tool
async def search_by_model_tool(
    ctx: RunContext, model_number: str
) -> ModelPartsResult:
    """Find all compatible parts for a specific appliance model.

    Use this when customers have a model number and want to see all available parts.
    Returns: common replacement parts and parts grouped by category.
    """
    result = await search_by_model(model_number)

    # Convert parts dicts to PartResult objects
    common_parts = [
        PartResult(
            part_number=p["part_number"],
            name=p["name"],
            price=p["price"],
            image_url=p.get("image_url", ""),
            manufacturer=p.get("manufacturer", ""),
            in_stock=p.get("in_stock", True),
            part_select_url=p["part_select_url"],
        )
        for p in result.get("common_parts", [])
    ]

    parts_by_category = {}
    for category, parts in result.get("parts_by_category", {}).items():
        parts_by_category[category] = [
            PartResult(
                part_number=p["part_number"],
                name=p["name"],
                price=p["price"],
                image_url=p.get("image_url", ""),
                manufacturer=p.get("manufacturer", ""),
                in_stock=p.get("in_stock", True),
                part_select_url=p["part_select_url"],
            )
            for p in parts
        ]

    return ModelPartsResult(
        model_number=model_number,
        appliance_info=result.get("appliance_info", ""),
        common_parts=common_parts,
        all_parts_count=result.get("all_parts_count", 0),
        parts_by_category=parts_by_category,
    )
