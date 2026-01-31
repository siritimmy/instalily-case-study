"""
PartSelect Agent - Reimplemented with Pydantic AI Built-in Web Tools

This version uses WebFetchTool and WebSearchTool instead of custom web scraping.
The AI analyzes web pages directly rather than manual HTML parsing.
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext, WebFetchTool, WebSearchTool
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

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Determine model to use
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"

# Initialize agent with built-in web tools
agent = Agent(
    model=model,
    system_prompt="""You are a specialized PartSelect assistant for refrigerator and dishwasher parts ONLY.

You help customers:
- Find the right replacement parts for refrigerators and dishwashers
- Check if specific parts are compatible with their appliance models
- Get detailed installation instructions for parts
- Troubleshoot common appliance problems and recommend parts to fix them
- Find all compatible parts for a specific appliance model

You have access to web search and web fetch tools that let you:
- Search the web for part information
- Fetch and analyze PartSelect.com pages directly
- Extract product details, pricing, compatibility, and installation info

IMPORTANT RULES:
1. ONLY help with refrigerator and dishwasher parts
2. Do NOT help with other appliances (ovens, washers, dryers, etc.)
3. Always use web tools to get accurate, up-to-date information from PartSelect.com
4. Present products clearly with part numbers, prices, and availability
5. When asked about other appliances, politely decline and say:
   "I specialize in refrigerator and dishwasher parts from PartSelect. For other appliances,
   please contact PartSelect customer service."

USING WEB TOOLS EFFECTIVELY:
- Use WebFetch to analyze PartSelect.com URLs directly
- Extract structured data (part numbers, prices, specs, compatibility lists)
- When searching, use WebSearch to find relevant PartSelect pages
- Always verify information from official PartSelect.com sources

HANDLING DATA EXTRACTION:
- Extract: part_number, name, price, manufacturer, in_stock status, image_url
- For compatibility: look for "Fits Models" sections or compatibility lists
- For installation: find difficulty ratings, tools needed, video links
- If data is missing or page not found, clearly communicate this to the user

Be helpful, friendly, and focus on finding the right solutions for customers.""",
    builtin_tools=[
        # WebFetchTool allows fetching and analyzing specific URLs
        WebFetchTool(
            allowed_domains=['partselect.com', 'www.partselect.com'],
            max_uses=20,  # Allow multiple fetches per conversation
            enable_citations=True,  # Include source citations
            max_content_tokens=50000,  # Large pages with product details
        ),
        # WebSearchTool allows searching for parts
        WebSearchTool(
            allowed_domains=['partselect.com', 'www.partselect.com'],
            max_uses=10,  # Limit searches to avoid excessive API usage
        ),
    ],
)


# Define custom tools that use the web tools internally

@agent.tool
async def search_parts_tool(ctx: RunContext, input: SearchPartsInput) -> SearchPartsOutput:
    """Search PartSelect catalog for parts matching a query.

    Use this to find parts by:
    - Part number (e.g., 'PS11752778')
    - Product name (e.g., 'ice maker', 'water filter')
    - Symptom or problem (e.g., 'dishwasher not cleaning')

    This tool instructs you to use WebSearch or WebFetch to find parts on PartSelect.com.

    Steps:
    1. Use WebSearch to search "site:partselect.com {query} {appliance_type}"
    2. Analyze the search results to find relevant part pages
    3. Extract part information from the results
    4. Return structured data as PartResult objects

    Return up to 6 parts with: part_number, name, price, image_url, manufacturer, in_stock, part_select_url
    """
    # The agent will handle the actual web search/fetch using its builtin tools
    # This tool just provides instructions for what data to extract
    return SearchPartsOutput(
        parts=[],
        total_results=0,
        _instructions=f"Search PartSelect.com for '{input.query}' parts for {input.appliance_type}. "
        f"Extract part_number, name, price, image_url, manufacturer, in_stock status, and URL for up to 6 results."
    )


@agent.tool
async def get_part_details_tool(ctx: RunContext, part_number: str) -> PartDetails:
    """Get detailed information about a specific part.

    This tool instructs you to fetch the PartSelect page for this part and extract:
    - Full product name and description
    - Price and availability
    - Images
    - Manufacturer
    - Compatible models list
    - Installation difficulty
    - Warranty information

    Steps:
    1. Use WebFetch to load https://www.partselect.com/PS{part_number}-*.html
       or search for the part number on PartSelect.com
    2. Extract all relevant product details
    3. If page shows "not found" or redirects to search, return "Part not found"

    Return structured PartDetails with all available information.
    """
    return PartDetails(
        part_number=part_number,
        full_name="",
        description="",
        price=0.0,
        image_urls=[],
        manufacturer="",
        in_stock=False,
        compatible_models=[],
        installation_difficulty="moderate",
        warranty_info="",
        part_select_url=f"https://www.partselect.com",
        _instructions=f"Fetch PartSelect.com page for part number '{part_number}' and extract: "
        f"full_name, description, price, image_urls, manufacturer, in_stock, compatible_models, "
        f"installation_difficulty, warranty_info. If part not found, set full_name='Part not found'."
    )


@agent.tool
async def check_compatibility_tool(
    ctx: RunContext, part_number: str, model_number: str
) -> CompatibilityCheck:
    """Check if a specific part is compatible with an appliance model.

    This tool instructs you to:
    1. Fetch the part details page for {part_number}
    2. Look for "Fits Models" or "Compatible Models" section
    3. Check if {model_number} is in the list (exact match or fuzzy match)
    4. If not compatible, search for alternative parts for the model

    Return:
    - is_compatible: True/False
    - confidence: "confirmed", "likely", or "unlikely"
    - explanation: Clear explanation of compatibility
    - alternative_parts: List of part numbers if not compatible
    """
    return CompatibilityCheck(
        part_number=part_number,
        model_number=model_number,
        is_compatible=False,
        confidence="unlikely",
        explanation="",
        alternative_parts=[],
        _instructions=f"Check if part {part_number} is compatible with model {model_number}. "
        f"Fetch the part page, find the compatible models list, and check for exact or fuzzy matches. "
        f"If not compatible, search for alternative parts that fit {model_number}."
    )


@agent.tool
async def get_installation_guide_tool(
    ctx: RunContext, part_number: str
) -> InstallationGuide:
    """Get step-by-step installation instructions for a part.

    This tool instructs you to:
    1. Fetch the PartSelect page for {part_number}
    2. Extract installation information:
       - Difficulty level (easy/moderate/difficult)
       - Estimated time in minutes
       - Tools required
       - Step-by-step instructions
       - YouTube video links (if available)
       - PDF manual links (if available)
    3. Look for repair difficulty indicators, installation videos, and guides

    If the part page has installation videos, extract YouTube URLs.
    If detailed steps aren't available, provide generic safety steps.
    """
    return InstallationGuide(
        part_number=part_number,
        difficulty="moderate",
        estimated_time_minutes=30,
        tools_required=[],
        steps=[],
        video_url=None,
        pdf_url=None,
        _instructions=f"Fetch installation guide for part {part_number}. "
        f"Extract: difficulty, estimated_time_minutes, tools_required, installation steps, "
        f"video_url (YouTube), pdf_url (manual). If part not found, return empty steps list."
    )


@agent.tool
async def diagnose_issue_tool(
    ctx: RunContext, input: DiagnosisInput
) -> DiagnosisResult:
    """Diagnose appliance problems and recommend parts to fix them.

    This tool instructs you to:
    1. Use your knowledge of common {appliance_type} issues for symptom: "{symptom}"
    2. Identify likely causes
    3. Search PartSelect.com for recommended replacement parts for {brand} {appliance_type}
    4. Provide troubleshooting steps

    Common symptom mappings:
    - "ice maker not working": water line, ice maker assembly, water filter
    - "not cooling": compressor, condenser fan, start relay
    - "water leak": drain line, water line, water pump
    - "not draining": drain pump, drain hose, filter
    - "not cleaning": spray arm, detergent dispenser, filter

    Return likely causes, recommended parts (with full details), and troubleshooting steps.
    """
    return DiagnosisResult(
        likely_causes=[],
        recommended_parts=[],
        diy_difficulty="moderate",
        troubleshooting_steps=[],
        _instructions=f"Diagnose {input.appliance_type} issue: '{input.symptom}' for brand {input.brand}. "
        f"Identify likely causes, search PartSelect for recommended parts, and provide troubleshooting steps."
    )


@agent.tool
async def search_by_model_tool(
    ctx: RunContext, model_number: str
) -> ModelPartsResult:
    """Find all compatible parts for a specific appliance model.

    This tool instructs you to:
    1. Fetch https://www.partselect.com/Models/{model_number}/
    2. Extract all parts listed for this model
    3. Group parts by category (if available)
    4. Identify common replacement parts

    Return:
    - Appliance information
    - List of common parts (top 5-10)
    - Total parts count
    - Parts organized by category (if available)
    """
    return ModelPartsResult(
        model_number=model_number,
        appliance_info="",
        common_parts=[],
        all_parts_count=0,
        parts_by_category={},
        _instructions=f"Fetch PartSelect.com page for model number '{model_number}'. "
        f"Extract all compatible parts, group by category, identify common replacements."
    )