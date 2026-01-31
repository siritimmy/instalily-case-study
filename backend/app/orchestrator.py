"""
Agent Orchestrator - Main Coordination Layer

Routes questions to appropriate sub-agents and returns typed responses.
This is the main entry point called by main.py instead of run_agent().

Architecture:
    User Question → Router Agent → Sub-Agent → Typed Response

The orchestrator:
1. Uses RouterAgent to classify the question into 1 of 6 categories
2. Routes to the appropriate sub-agent based on classification
3. Returns a specialized response type (SearchResponse, CompatibilityResponse, etc.)
4. Frontend uses the `type` field to render the appropriate UI component
"""

import logging
from typing import Union

from .router_agent import RouterAgent, RoutingDecision
from .search_agent import SearchAgent
from .part_details_agent import PartDetailsAgent
from .compatibility_agent import CompatibilityAgent
from .installation_agent import InstallationAgent
from .troubleshooting_agent import TroubleshootingAgent
from .response_models import (
    AgentResponse,
    SearchResponse,
    PartDetailsResponse,
    CompatibilityResponse,
    InstallationResponse,
    DiagnosisResponse,
    OffTopicResponse,
)

# Setup logging
logger = logging.getLogger(__name__)


class AgentOrchestrator:
    """
    Coordinates the router and 5 sub-agents to handle user questions.

    Usage:
        orchestrator = AgentOrchestrator()
        response = await orchestrator.process_message("Find ice makers")
        # response.type == "search" → render ProductGrid
    """

    def __init__(self):
        """Initialize the orchestrator with router and all sub-agents."""
        self.router = RouterAgent()
        self.search_agent = SearchAgent()
        self.part_details_agent = PartDetailsAgent()
        self.compatibility_agent = CompatibilityAgent()
        self.installation_agent = InstallationAgent()
        self.troubleshooting_agent = TroubleshootingAgent()

    async def process_message(
        self,
        message: str,
        conversation_history: list[dict] | None = None
    ) -> AgentResponse:
        """
        Process a user message and return a typed response.

        Args:
            message: The user's question
            conversation_history: Optional list of previous messages for context

        Returns:
            AgentResponse (Union of 6 response types) with a `type` discriminator
            that the frontend uses to render the appropriate UI component.

        Flow:
            1. Router classifies question → category + entities
            2. Route to appropriate sub-agent
            3. Sub-agent processes with tools
            4. Return typed response
        """
        try:
            # Step 1: Classify the question
            logger.info(f"Routing question: {message[:50]}...")
            routing: RoutingDecision = await self.router.classify(
                message,
                conversation_history
            )
            logger.info(
                f"Classified as: {routing.category} "
                f"(confidence: {routing.confidence})"
            )

            # Step 2: Route to appropriate sub-agent
            response = await self._route_to_agent(message, routing)

            logger.info(f"Response type: {response.type}")
            return response

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            # Return a graceful error response
            return OffTopicResponse(
                type="off_topic",
                message=f"I encountered an error processing your request. Please try again or rephrase your question. Error: {str(e)}"
            )

    async def _route_to_agent(
        self,
        message: str,
        routing: RoutingDecision
    ) -> AgentResponse:
        """
        Route the message to the appropriate sub-agent.

        Args:
            message: The user's original message
            routing: The routing decision from the router

        Returns:
            The appropriate response type from the sub-agent
        """
        category = routing.category
        entities = routing.entities

        if category == "search":
            return await self.search_agent.run(message, entities)

        elif category == "part_details":
            return await self.part_details_agent.run(message, entities)

        elif category == "compatibility":
            return await self.compatibility_agent.run(message, entities)

        elif category == "installation":
            return await self.installation_agent.run(message, entities)

        elif category == "troubleshooting":
            return await self.troubleshooting_agent.run(message, entities)

        elif category == "off_topic":
            return self._handle_off_topic(routing)

        else:
            # Fallback for unknown categories
            logger.warning(f"Unknown category: {category}")
            return self._handle_off_topic(routing)

    def _handle_off_topic(self, routing: RoutingDecision) -> OffTopicResponse:
        """
        Handle off-topic queries with a polite redirect.

        Args:
            routing: The routing decision (for logging/debugging)

        Returns:
            OffTopicResponse with helpful message
        """
        return OffTopicResponse(
            type="off_topic",
            message=(
                "I specialize in refrigerator and dishwasher parts from PartSelect. "
                "I can help you:\n\n"
                "• **Find parts** - Search for replacement parts\n"
                "• **Check compatibility** - Verify if a part fits your model\n"
                "• **Installation guides** - Get step-by-step instructions\n"
                "• **Troubleshoot issues** - Diagnose problems and find fixes\n\n"
                "For other appliances like ovens, washers, or dryers, please contact "
                "PartSelect customer service."
            )
        )


# Convenience function for direct use
async def process_message(
    message: str,
    conversation_history: list[dict] | None = None
) -> AgentResponse:
    """
    Process a user message through the orchestrator.

    This is a convenience function that creates an orchestrator instance
    and processes the message. For production use, prefer creating a
    single AgentOrchestrator instance and reusing it.

    Args:
        message: The user's question
        conversation_history: Optional conversation history

    Returns:
        AgentResponse with typed response
    """
    orchestrator = AgentOrchestrator()
    return await orchestrator.process_message(message, conversation_history)
