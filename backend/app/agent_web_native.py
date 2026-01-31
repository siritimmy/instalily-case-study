"""
PartSelect Agent - Web-Native Version (Simplified)

This version completely removes custom tools and lets the agent
use WebFetch and WebSearch naturally to answer questions.

This is the most "Pydantic AI native" approach but requires changes
to how the frontend handles responses (less structured data).
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, WebFetchTool, WebSearchTool
from pydantic import BaseModel, Field

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Determine model to use
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"

class Part(BaseModel):
    """Part information extracted from PartSelect.com"""
    part_number: str = Field(description="PartSelect part number, e.g., 'PS11752778'")
    name: str = Field(description="Full product name")
    price: float | None = Field(description="Price of the part")
    image_url: str | None = Field(description="URL of the product image")
    manufacturer: str | None = Field(description="Brand name, e.g., Whirlpool, GE")
    in_stock: bool | None = Field(description="Whether the part is currently in stock")
    url: str | None = Field(description="Full PartSelect.com URL to the product")


# Define result model for structured output
class PartSelectResponse(BaseModel):
    """Structured response from the PartSelect agent"""
    message: str = Field(description="Natural language response to the user")
    parts: list[Part] = Field(
        default=[],
        description="List of parts found"
    )
    source_urls: list[str] = Field(
        default=[],
        description="PartSelect.com URLs used to generate this response"
    )


# Initialize agent with web tools ONLY
agent = Agent(
    model=model,
    output_type=PartSelectResponse,
    system_prompt="""You are a specialized PartSelect assistant for refrigerator and dishwasher parts ONLY.

You help customers:
- Find the right replacement parts for refrigerators and dishwashers
- Check if specific parts are compatible with their appliance models
- Get detailed installation instructions for parts
- Troubleshoot common appliance problems and recommend parts to fix them
- Find all compatible parts for a specific appliance model

CRITICAL: You have WebFetch and WebSearch tools available. Use them to access PartSelect.com!

HOW TO USE YOUR WEB TOOLS:

1. **Searching for parts**:
   - Use WebSearch: "site:partselect.com ice maker refrigerator"
   - Or WebFetch: "https://www.partselect.com/api/search/?searchterm=ice+maker"

2. **Getting part details**:
   - Use WebFetch: "https://www.partselect.com/PS{part_number}-*.html"
   - Or search for the part number and fetch the result page

3. **Checking compatibility**:
   - Fetch the part detail page
   - Look for "Fits Models" or "Compatible Models" section
   - Check if user's model is listed

4. **Installation guides**:
   - Fetch the part detail page
   - Extract difficulty, tools needed, steps, and video links
   - Look for YouTube embeds or PDF manuals

5. **Finding parts by model**:
   - Use WebFetch: "https://www.partselect.com/Models/{model_number}/"
   - Extract all compatible parts

IMPORTANT RULES:
1. ONLY help with refrigerator and dishwasher parts
2. Do NOT help with other appliances (ovens, washers, dryers, etc.)
3. ALWAYS use your web tools to get real-time data from PartSelect.com
4. Extract and return structured data in the `parts` field
5. When asked about other appliances, politely decline

EXTRACTING STRUCTURED DATA:
For each part you find, extract:
- part_number: The PartSelect part number (e.g., "PS11752778")
- name: Full product name
- price: Price as a number (e.g., 89.99)
- image_url: Product image URL
- manufacturer: Brand name (Whirlpool, GE, etc.)
- in_stock: Boolean - whether part is in stock
- url: Full PartSelect.com URL to the product

Store all PartSelect.com URLs you fetched in the `source_urls` field.

OUTPUT FORMAT:
You MUST return a JSON object with this exact structure:
{
  "message": "Your natural language response here",
  "parts": [array of part objects],
  "source_urls": [array of URLs you fetched]
}

Be helpful, friendly, and focus on finding the right solutions for customers.
Present information clearly in the `message` field and structured data in the `parts` field.""",
    builtin_tools=[
        # WebFetchTool for fetching specific PartSelect pages
        WebFetchTool(
            allowed_domains=['partselect.com', 'www.partselect.com'],
            max_uses=20,
            enable_citations=True,
            max_content_tokens=50000,
        ),
        # WebSearchTool for searching PartSelect catalog
        WebSearchTool(
            allowed_domains=['partselect.com', 'www.partselect.com'],
            max_uses=10,
        ),
    ],
)


# Simple run function
async def run_agent(user_message: str, conversation_history: list = None) -> PartSelectResponse:
    """
    Run the agent with a user message.

    Returns:
        PartSelectResponse: Structured response containing:
            - message: Natural language response
            - parts: List of Part objects
            - source_urls: URLs used
    """
    result = await agent.run(user_message)
    return result.output
