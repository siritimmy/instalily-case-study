"""
Search Agent - Product Search Specialist

Handles product search queries and returns SearchResponse.
Uses search_parts and search_by_model tools from web_fetcher.

UI Component: ProductGrid
Example queries: "Find ice makers", "Show me water filters", "WDT780SAEM1 parts"
"""

import os
from dotenv import load_dotenv
from pydantic_ai import Agent, RunContext
from pydantic import BaseModel, Field
from typing import Optional, Literal

from .response_models import SearchResponse
from .router_agent import ExtractedEntities
from .models import PartResult, SearchPartsInput, SearchPartsOutput, ModelPartsResult
from .web_fetcher import search_parts, search_by_model

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Model configuration
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


# System prompt for search specialist
SEARCH_SYSTEM_PROMPT = """You are a PartSelect product search specialist for refrigerator and dishwasher parts.

Your job is to help customers find the right replacement parts.

AVAILABLE TOOLS:
1. search_parts_tool - Search by query (e.g., "ice maker", "water filter")
2. search_by_model_tool - Find all parts for a specific appliance model number

SEARCH STRATEGIES:
1. General queries ("ice maker", "door gasket") → Use search_parts_tool
2. Model number queries ("WDT780SAEM1") → Use search_by_model_tool
3. Combined queries ("ice maker for Whirlpool") → Use search_parts_tool with refined query

GUIDELINES:
- Return 3-8 most relevant parts
- Highlight key differentiators (price, features, ratings, stock status)
- If no results found, suggest alternative search terms
- Always specify whether parts are in stock

OUTPUT:
Provide a helpful message summarizing the search results along with the structured parts data.
Focus on helping the customer find the right part for their needs."""


# Create the search agent
search_agent = Agent(
    model=model,
    output_type=SearchResponse,
    system_prompt=SEARCH_SYSTEM_PROMPT,
)


@search_agent.tool
async def search_parts_tool(
    ctx: RunContext,
    query: str,
    appliance_type: Literal["refrigerator", "dishwasher"] | None = None
) -> SearchPartsOutput:
    """Search PartSelect catalog for parts matching a query.

    Use this to find parts by:
    - Part name (e.g., 'ice maker', 'water filter', 'door gasket')
    - Symptom or problem (e.g., 'dishwasher not cleaning')

    Args:
        query: Search terms
        appliance_type: Optional filter for 'refrigerator' or 'dishwasher'
    """
    # Add appliance type to query if specified
    search_query = query
    if appliance_type:
        search_query = f"{query} {appliance_type}"

    parts = await search_parts(search_query, limit=8)
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


@search_agent.tool
async def search_by_model_tool(ctx: RunContext, model_number: str) -> ModelPartsResult:
    """Find all compatible parts for a specific appliance model.

    Use this when customers have a model number and want to see available parts.
    Returns common replacement parts and parts grouped by category.

    Args:
        model_number: The appliance model number (e.g., 'WDT780SAEM1')
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


class SearchAgent:
    """Search agent that handles product search queries."""

    def __init__(self):
        self.agent = search_agent

    async def run(
        self,
        message: str,
        entities: ExtractedEntities
    ) -> SearchResponse:
        """
        Run the search agent with extracted entities.

        Args:
            message: The user's original message
            entities: Extracted entities from the router

        Returns:
            SearchResponse with parts and search metadata
        """
        # Build context from entities
        context_parts = []

        if entities.search_query:
            context_parts.append(f"Search query: {entities.search_query}")
        if entities.appliance_type:
            context_parts.append(f"Appliance type: {entities.appliance_type}")
        if entities.model_numbers:
            context_parts.append(f"Model numbers: {', '.join(entities.model_numbers)}")
        if entities.brand:
            context_parts.append(f"Brand: {entities.brand}")

        context = "\n".join(context_parts) if context_parts else ""

        # Build the prompt
        prompt = f"""User request: {message}

{f"Extracted context:{chr(10)}{context}" if context else ""}

Search for relevant parts and return a SearchResponse with:
- A helpful message summarizing the results
- The list of parts found
- The search query used
- The appliance type if applicable"""

        # Run the agent
        result = await self.agent.run(prompt)
        return result.output
