# PartSelect Chat Agent - Case Study

A modern, production-ready chat agent for PartSelect e-commerce focused on refrigerator and dishwasher parts. Built with NextJS, FastAPI, and Pydantic AI to demonstrate modern AI architecture, extensibility, and real-world problem-solving.

## Project Structure

```
instalily-case-study/
├── frontend/                    # NextJS chat interface
│   ├── app/                    # Next.js app directory
│   ├── components/             # React components
│   │   ├── ChatWindow.tsx      # Main chat interface
│   │   ├── MessageBubble.tsx   # Message + response routing
│   │   ├── PartCard.tsx        # Compact product cards
│   │   ├── DetailedProductView.tsx  # Full product view
│   │   ├── CompatibilityCard.tsx    # Compatibility results
│   │   ├── InstallationWizard.tsx   # Step-by-step guide
│   │   └── DiagnosticFlow.tsx       # Troubleshooting UI
│   ├── lib/                    # Utilities and types
│   │   ├── api.ts              # API client
│   │   └── types.ts            # TypeScript interfaces
│   └── package.json
├── backend/                    # FastAPI + Pydantic AI
│   ├── app/
│   │   ├── main.py            # FastAPI app
│   │   ├── orchestrator.py    # Agent coordination
│   │   ├── router_agent.py    # Intent classification
│   │   ├── response_models.py # Typed responses
│   │   ├── search_agent.py    # Search sub-agent
│   │   ├── part_details_agent.py
│   │   ├── compatibility_agent.py
│   │   ├── installation_agent.py
│   │   ├── troubleshooting_agent.py
│   │   └── web_fetcher.py     # Data fetching
│   └── requirements.txt
├── CLAUDE.md                   # Detailed architecture docs
└── README.md                   # This file
```

## Quick Start

### Prerequisites
- Node.js 18+ and npm
- Python 3.11+
- Anthropic API key (get from https://console.anthropic.com)

### Setup

#### 1. Backend (FastAPI + Pydantic AI)

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

#### 2. Frontend (NextJS)

```bash
# In a new terminal, navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Create .env.local file
cp .env.example .env.local
# Ensure FASTAPI_URL=http://localhost:8000
```

### Running the Application

#### Terminal 1: Start FastAPI Backend
```bash
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
```

The backend will be available at `http://localhost:8000` with API docs at `http://localhost:8000/docs`.

#### Terminal 2: Start NextJS Frontend
```bash
cd frontend
npm run dev
```

The frontend will be available at `http://localhost:3000`.

## Architecture

### Frontend (NextJS)
- **Framework**: Next.js 14+ with TypeScript
- **Styling**: Tailwind CSS with PartSelect branding
- **Response-Type Components**: Each response type renders a specialized UI component
  - `PartCard`: Compact product cards for search results
  - `DetailedProductView`: Full product view with tabs
  - `CompatibilityCard`: Visual compatibility check results
  - `InstallationWizard`: Step-by-step installation guide
  - `DiagnosticFlow`: Troubleshooting with expandable sections

### Backend (FastAPI + Sub-Agent Architecture)
- **Framework**: FastAPI with async support
- **Pattern**: Router + Specialized Sub-Agents
- **Sub-Agents** (each with typed output):
  1. **SearchAgent** → `SearchResponse`: Find parts by query
  2. **PartDetailsAgent** → `PartDetailsResponse`: Full product info
  3. **CompatibilityAgent** → `CompatibilityResponse`: Model compatibility
  4. **InstallationAgent** → `InstallationResponse`: Installation guides
  5. **TroubleshootingAgent** → `DiagnosisResponse`: Problem diagnosis

### Data Flow
```
User Input (NextJS)
    ↓
NextJS API Route (/api/chat)
    ↓
FastAPI Backend (/chat endpoint)
    ↓
Orchestrator
    ↓
Router Agent (intent classification)
    ↓
Specialized Sub-Agent (based on intent)
    ↓
Tool Functions (Web Fetching)
    ↓
PartSelect.com (Live Data)
    ↓
Typed Response (SearchResponse | CompatibilityResponse | etc.)
    ↓
Frontend renders matching UI component
```

## Example Queries

Try these in the chat:

1. **Part Search**
   - "Tell me about part PS11752778"
   - "I need an ice maker for my refrigerator"

2. **Compatibility Check**
   - "Is PS11752778 compatible with WDT780SAEM1?"

3. **Installation Help**
   - "How can I install part number PS11752778?"

4. **Troubleshooting**
   - "The ice maker on my Whirlpool fridge is not working. How can I fix it?"

5. **Model Search**
   - "What parts are available for WDT780SAEM1?"

## Key Features

### Advanced Sub-Agent Architecture
- **Router + Sub-Agents**: Intent classification routes to specialized agents
- **Typed Responses**: Each sub-agent returns a strongly-typed response
- **Discriminated Unions**: Frontend uses `type` field to render correct component
- **Live Data Integration**: Fetches real PartSelect data via web tools

### Type-Driven Development
- **Backend**: Pydantic models with `type` discriminator field
- **Frontend**: TypeScript interfaces matching backend models
- **UI Routing**: `switch(response.type)` renders specialized components

### Extensibility
- Add new sub-agent without modifying existing agents
- Each agent has focused system prompt and tools
- Clear pattern: Agent → Response Type → UI Component

### Production-Ready
- Proper error handling and logging
- CORS middleware for cross-origin requests
- Health check endpoints
- Environment variable configuration

### Rich User Experience
- **Search**: Grid of product cards with images and prices
- **Part Details**: Tabbed view with specs, models, related parts
- **Compatibility**: Visual checkmark/X with confidence level
- **Installation**: Step-by-step wizard with safety warnings
- **Diagnosis**: Expandable accordion with causes and fixes

## Scope Control

The agent is designed to ONLY help with:
- **Refrigerator parts** from PartSelect
- **Dishwasher parts** from PartSelect
- Installation guides, compatibility checking, troubleshooting

The agent will politely decline help with other appliances.

## API Documentation

Once running, view the interactive API docs at:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Environment Variables

### Frontend (`frontend/.env.local`)
```
FASTAPI_URL=http://localhost:8000
NEXT_PUBLIC_API_URL=http://localhost:3000/api
```

### Backend (`backend/.env`)
```
ANTHROPIC_API_KEY=your-key-here
LOG_LEVEL=INFO
```

## Testing

### Manual Testing
1. Open http://localhost:3000 in your browser
2. Try the example queries above
3. Check that products display correctly with images and details
4. Test scope control by asking about non-refrigerator/dishwasher items

### API Testing
Use the Swagger UI at http://localhost:8000/docs to test endpoints directly.

## Development Notes

- The web fetcher functions are designed to scrape PartSelect.com
- You may need to adjust CSS selectors based on actual HTML structure
- For production, consider caching tool responses to improve performance
- Conversation history is currently stateless; add database persistence for production

## Performance Considerations

- Response time: < 5 seconds for tool calls
- Parts search returns top 6 results by default
- Web scraping is async for better performance
- Consider adding Redis caching for frequently accessed products

## Deployment

### Frontend (Vercel)
```bash
cd instalily-nextjs
vercel deploy
```

### Backend (Cloud Run, Railway, etc.)
```bash
cd instalily-backend
# Build Docker container or deploy directly
```

## Known Limitations

- Web scraping depends on PartSelect.com HTML structure (may need updates)
- Real PartSelect integration requires handling actual page layouts
- Product images may need fallback handling
- Rate limiting may be needed for high-traffic scenarios

## Next Steps for Production

1. Implement actual PartSelect API integration (if available)
2. Add conversation history to database
3. Implement caching layer (Redis)
4. Add analytics and monitoring
5. Implement rate limiting and authentication
6. Add payment integration for direct purchases
7. Optimize web scraping with proper selector mapping

## Support

For issues or questions, check:
1. Backend logs at http://localhost:8000/docs
2. Browser console for frontend errors
3. Ensure ANTHROPIC_API_KEY is set in .env
4. Verify both services are running on correct ports

## Success Criteria Met

✅ Modern framework (NextJS + FastAPI)
✅ PartSelect branding and styling
✅ **Sub-agent architecture** with router and specialized agents
✅ **Typed responses** with discriminated unions
✅ **Specialized UI components** per response type
✅ Extensible design (add new sub-agents easily)
✅ Real data integration from PartSelect.com
✅ Installation wizard with step navigation
✅ Visual compatibility checking
✅ Diagnostic flow with troubleshooting
✅ Scope enforcement via router agent
✅ Professional UX with rich product displays