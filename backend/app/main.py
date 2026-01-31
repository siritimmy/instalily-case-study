from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from .models import ChatRequest, ChatResponse, PartResult
from .agent import agent

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="PartSelect Agent API",
    description="Chat agent for PartSelect refrigerator and dishwasher parts",
    version="1.0.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PartSelect Agent API"}


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Handle chat requests from the frontend

    Takes a user message and optional conversation history,
    processes it through the Pydantic AI agent with PartSelect tools,
    and returns the response with any relevant parts found.
    """
    try:
        logger.info(f"Processing chat request: {request.message[:50]}...")

        # Run the agent with the user's message
        # Note: In a real production app, you might want to maintain conversation
        # history server-side or use a more sophisticated state management
        result = await agent.run(request.message)

        # Extract message and parts from result
        message = result.output if hasattr(result, "output") else str(result)

        # Extract parts if any tools returned them
        # This is a simplified version - actual implementation would need to
        # track which tools returned part data
        parts = []

        # Try to extract parts from the result if available
        if hasattr(result, "tool_results"):
            for tool_result in result.tool_results.values():
                if isinstance(tool_result, dict) and "parts" in tool_result:
                    for part_data in tool_result["parts"]:
                        if isinstance(part_data, dict):
                            parts.append(
                                PartResult(
                                    part_number=part_data.get("part_number", ""),
                                    name=part_data.get("name", ""),
                                    price=part_data.get("price", 0.0),
                                    image_url=part_data.get("image_url", ""),
                                    manufacturer=part_data.get("manufacturer", ""),
                                    in_stock=part_data.get("in_stock", False),
                                    part_select_url=part_data.get("part_select_url", ""),
                                )
                            )

        logger.info(f"Returning response with {len(parts)} parts")
        return ChatResponse(message=message, parts=parts)

    except Exception as e:
        logger.error(f"Error processing chat: {e}")
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@app.get("/")
async def root():
    """Root endpoint with API info"""
    return {
        "name": "PartSelect Assistant API",
        "version": "1.0.0",
        "endpoints": {"/health": "Health check", "/chat": "Chat endpoint"},
        "docs": "/docs",
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
