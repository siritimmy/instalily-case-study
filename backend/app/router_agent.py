"""
Router Agent - LLM-Based Question Classification

Classifies user questions into 5 categories and extracts relevant entities.
Uses Claude Haiku for fast, cost-effective classification.

Categories:
1. search - Product search queries ("Find ice makers", "Show me filters")
2. part_details - Specific part information ("Tell me about PS11752778")
3. compatibility - Part/model fit checks ("Is PS11752778 compatible with WDT780SAEM1?")
4. installation - Installation guidance ("How do I install this?")
5. troubleshooting - Problem diagnosis ("My ice maker isn't working")
6. off_topic - Non-refrigerator/dishwasher queries
"""

import os
import re
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from pydantic_ai import Agent
from typing import Literal, Optional

# Load environment variables
load_dotenv()

# Get API key from environment
api_key = os.getenv("ANTHROPIC_API_KEY")
use_test_mode = not api_key or api_key.startswith("sk-test")

# Use Haiku for fast classification (or Sonnet if accuracy issues)
# Using Haiku for cost/speed optimization in routing
model = "test" if use_test_mode else "claude-sonnet-4-5-20250929"


class ExtractedEntities(BaseModel):
    """Entities extracted from the user's question."""
    part_numbers: list[str] = Field(
        default=[],
        description="PartSelect part numbers (e.g., 'PS11752778', 'PS12345678')"
    )
    model_numbers: list[str] = Field(
        default=[],
        description="Appliance model numbers (e.g., 'WDT780SAEM1', 'RF28R7351SR')"
    )
    appliance_type: Optional[Literal["refrigerator", "dishwasher"]] = Field(
        default=None,
        description="Type of appliance mentioned or implied"
    )
    brand: Optional[str] = Field(
        default=None,
        description="Appliance brand (e.g., 'Whirlpool', 'GE', 'Samsung', 'LG')"
    )
    symptom: Optional[str] = Field(
        default=None,
        description="Problem symptom for troubleshooting (e.g., 'not cooling', 'won't drain')"
    )
    search_query: Optional[str] = Field(
        default=None,
        description="Search terms for product search (e.g., 'ice maker', 'water filter')"
    )


class RoutingDecision(BaseModel):
    """Output from the router agent with classification and extracted entities."""
    category: Literal[
        "search",
        "part_details",
        "compatibility",
        "installation",
        "troubleshooting",
        "off_topic"
    ] = Field(description="The category of the user's question")
    confidence: Literal["high", "medium", "low"] = Field(
        description="Confidence level in the classification"
    )
    entities: ExtractedEntities = Field(
        default_factory=ExtractedEntities,
        description="Entities extracted from the question"
    )
    reasoning: str = Field(
        description="Brief explanation of why this category was chosen (for debugging)"
    )


# Router classification prompt
ROUTER_SYSTEM_PROMPT = """You are a question classifier for a PartSelect customer service agent.
Your job is to categorize customer questions and extract relevant entities.

IMPORTANT: Only classify questions about REFRIGERATORS and DISHWASHERS.
Any questions about other appliances (ovens, washers, dryers, microwaves, etc.) should be classified as "off_topic".

CATEGORIES:

1. **search** - Customer wants to find/browse parts
   - "I need an ice maker"
   - "Show me water filters for dishwashers"
   - "Find door gaskets"
   - "What parts do you have for refrigerators?"

2. **part_details** - Customer asks about a SPECIFIC part (has part number or wants details)
   - "Tell me about PS11752778"
   - "What's the price of the ice maker assembly?"
   - "Is PS11752778 in stock?"
   - "Show me details for part number PS12345678"

3. **compatibility** - Customer asks if a part fits their model
   - "Is PS11752778 compatible with WDT780SAEM1?"
   - "Will this work with my Whirlpool fridge?"
   - "Does part PS12345678 fit model RF28R7351SR?"
   - "Can I use this on my Samsung dishwasher?"

4. **installation** - Customer asks about installing a part
   - "How do I install PS11752778?"
   - "What tools do I need to replace the ice maker?"
   - "Is this hard to install?"
   - "Show me installation instructions"

5. **troubleshooting** - Customer describes a PROBLEM/SYMPTOM
   - "My ice maker isn't working"
   - "The dishwasher won't drain"
   - "Fridge is making a loud noise"
   - "Water is leaking from my refrigerator"

6. **off_topic** - NOT about refrigerators or dishwashers
   - "Tell me about oven parts"
   - "I need a washing machine belt"
   - "What's the weather like?"
   - "Help me with my dryer"

ENTITY EXTRACTION:

Extract these entities when present:
- part_numbers: PartSelect numbers like "PS11752778" (starts with PS followed by digits)
- model_numbers: Appliance models like "WDT780SAEM1", "RF28R7351SR"
- appliance_type: "refrigerator" or "dishwasher" (infer from context if possible)
- brand: Whirlpool, GE, Samsung, LG, Frigidaire, Maytag, KitchenAid, Bosch, etc.
- symptom: The problem described (for troubleshooting)
- search_query: What they're looking for (for search)

CONTEXT CLUES for appliance_type:
- Ice maker, water filter, compressor, door gasket, freezer → refrigerator
- Spray arm, drain pump, detergent dispenser, dish rack → dishwasher

IMPORTANT - CONVERSATION CONTEXT:
When recent conversation history is provided, you MUST extract entities from it.
If the user says "this part", "that part", "it", or similar references, look at the conversation
history to find the actual part number or model number being referenced.

Example:
- History: "user: tell me about PS11752778" / "assistant: [details about PS11752778]"
- Current: "Is this part compatible with my WDT780SAEM1?"
- You MUST extract PS11752778 from the history as the part_number

OUTPUT your classification with high confidence when the intent is clear.
Use medium confidence when there's some ambiguity.
Use low confidence when the question is very unclear."""


# Create the router agent
router_agent = Agent(
    model=model,
    output_type=RoutingDecision,
    system_prompt=ROUTER_SYSTEM_PROMPT,
)


class RouterAgent:
    """Router agent that classifies questions and extracts entities."""

    def __init__(self):
        self.agent = router_agent

    async def classify(
        self,
        message: str,
        conversation_history: list[dict] | None = None
    ) -> RoutingDecision:
        """
        Classify a user message into one of 6 categories.

        Args:
            message: The user's question
            conversation_history: Optional list of previous messages for context

        Returns:
            RoutingDecision with category, confidence, and extracted entities
        """
        # Build context from conversation history if provided
        context = ""
        if conversation_history:
            # Get last 3 messages for context (to resolve "it", "that part", etc.)
            recent_history = conversation_history[-3:]
            context_parts = []
            for msg in recent_history:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context_parts.append(f"{role}: {content}")
            if context_parts:
                context = "Recent conversation:\n" + "\n".join(context_parts) + "\n\n"

        # Combine context with current message
        full_prompt = f"{context}Current question: {message}"

        # Run the router agent
        result = await self.agent.run(full_prompt)
        routing_decision = result.output

        # Post-process: ensure entities are properly extracted
        # Pass conversation_history to also extract entities from context
        routing_decision = self._enhance_entities(message, routing_decision, conversation_history)

        return routing_decision

    def _enhance_entities(
        self,
        message: str,
        decision: RoutingDecision,
        conversation_history: list[dict] | None = None
    ) -> RoutingDecision:
        """
        Enhance entity extraction with regex patterns for part/model numbers.
        This catches any entities the LLM might have missed, including from
        conversation history to resolve references like "this part".
        """
        # Pattern for PartSelect part numbers (PS followed by digits)
        part_pattern = r'\bPS\d{6,10}\b'
        # Pattern for model numbers (alphanumeric, usually with letters and numbers)
        # Common patterns: WDT780SAEM1, RF28R7351SR, KDTE334GPS0
        model_pattern = r'\b[A-Z]{2,4}\d{2,4}[A-Z0-9]{3,10}\b'

        # Collect all text to search: current message + conversation history
        texts_to_search = [message]
        if conversation_history:
            for msg in conversation_history:
                content = msg.get("content", "")
                if content:
                    texts_to_search.append(content)

        # Extract from all texts
        found_parts = []
        found_models = []
        for text in texts_to_search:
            found_parts.extend(re.findall(part_pattern, text, re.IGNORECASE))
            found_models.extend(re.findall(model_pattern, text, re.IGNORECASE))

        # Merge with existing entities (avoid duplicates)
        existing_parts = set(p.upper() for p in decision.entities.part_numbers)
        existing_models = set(m.upper() for m in decision.entities.model_numbers)

        for part in found_parts:
            if part.upper() not in existing_parts:
                decision.entities.part_numbers.append(part.upper())
                existing_parts.add(part.upper())

        for model in found_models:
            # Don't add if it looks like a part number
            if not model.upper().startswith("PS") and model.upper() not in existing_models:
                decision.entities.model_numbers.append(model.upper())
                existing_models.add(model.upper())

        return decision


# Convenience function for direct use
async def classify_question(
    message: str,
    conversation_history: list[dict] | None = None
) -> RoutingDecision:
    """
    Classify a user question into a category.

    Args:
        message: The user's question
        conversation_history: Optional conversation history for context

    Returns:
        RoutingDecision with category, confidence, and extracted entities
    """
    router = RouterAgent()
    return await router.classify(message, conversation_history)
