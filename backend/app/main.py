from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import logging
from .models import ChatRequest
from .orchestrator import AgentOrchestrator
from .response_models import AgentResponse

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

# Initialize orchestrator (singleton pattern)
orchestrator = AgentOrchestrator()


@app.get("/health")
async def health():
    """Health check endpoint"""
    return {"status": "healthy", "service": "PartSelect Agent API"}


@app.post("/chat")
async def chat(request: ChatRequest):
    """Handle chat requests from the frontend.

    Takes a user message and optional conversation history,
    routes it through the agent orchestrator to the appropriate sub-agent,
    and returns a typed response based on the question category.

    Response types (frontend uses `type` field to render UI component):
    - SearchResponse → ProductGrid
    - PartDetailsResponse → DetailedProductView
    - CompatibilityResponse → CompatibilityCard
    - InstallationResponse → InstallationWizard
    - DiagnosisResponse → DiagnosticFlow
    - OffTopicResponse → Simple message
    """
    try:
        logger.info(f"Processing chat request: {request.message[:50]}...")

        # Use orchestrator to route to appropriate sub-agent
        # Returns typed response based on question category
        result: AgentResponse = await orchestrator.process_message(
            request.message,
            request.conversation_history
        )

        logger.info(f"Returning response type: {result.type}")
        return result

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
