# PartSelect Chat Agent - Project Context

## Project Overview
This is a modern chat agent implementation for PartSelect e-commerce, focusing specifically on **refrigerator and dishwasher parts**. The agent helps customers find parts, check compatibility, get installation guides, and troubleshoot issues.

**Important**: This is a case study/demo project to showcase modern AI engineering practices with real e-commerce use cases.

## Architecture

### Tech Stack
- **Frontend**: Next.js 14+ (App Router) with TypeScript and Tailwind CSS
- **Backend**: FastAPI (Python) with async support
- **AI Framework**: Pydantic AI with Claude (Anthropic)
- **Data Source**: Live data from PartSelect.com via web scraping
- **Web Scraping**: httpx + BeautifulSoup4

### Architecture Pattern
```
NextJS Frontend (Chat UI + Specialized Components)
    ↓ HTTP/JSON (Typed Responses)
NextJS API Routes (/api/chat)
    ↓ HTTP/JSON
FastAPI Backend (/chat endpoint)
    ↓
Orchestrator (agent coordination)
    ↓
Router Agent (intent classification)
    ↓ Routes to appropriate sub-agent
┌─────────────────────────────────────────────────────────┐
│  Sub-Agents (each with specialized tools & prompts)     │
│  ├── SearchAgent → SearchResponse                       │
│  ├── PartDetailsAgent → PartDetailsResponse             │
│  ├── CompatibilityAgent → CompatibilityResponse         │
│  ├── InstallationAgent → InstallationResponse           │
│  └── TroubleshootingAgent → DiagnosisResponse           │
└─────────────────────────────────────────────────────────┘
    ↓ Web Fetch/Scrape
PartSelect.com (Live Data)
```

### Key Design Decisions

1. **Sub-Agent Architecture**: Each capability has a dedicated Pydantic AI agent with its own system prompt, tools, and typed output. This enables:
   - **Specialized expertise**: Each agent focuses on one task
   - **Typed responses**: Discriminated union types for frontend rendering
   - **Extensibility**: Add new agents without modifying existing ones
   - **Maintainability**: Clear separation of concerns

2. **Router-Based Intent Classification**: A lightweight router agent classifies user intent and delegates to the appropriate sub-agent, ensuring optimal handling for each request type.

3. **Live Data Integration**: No static database or cached data. All product information comes from live PartSelect.com scraping, ensuring accuracy.

4. **Typed Response System**: All sub-agents return strongly-typed responses using Pydantic models with a `type` discriminator field, enabling the frontend to render specialized UI components.

5. **Scope Control**: Enforced at multiple levels:
   - Router agent filters off-topic requests (returns `OffTopicResponse`)
   - System prompts restrict to refrigerator/dishwasher only
   - Tool inputs use `Literal["refrigerator", "dishwasher"]` type constraints

## Project Structure

### Frontend (Next.js)
```
frontend/
├── app/
│   ├── page.tsx              # Main chat page
│   ├── layout.tsx            # Root layout with branding
│   ├── api/chat/route.ts     # Proxy to FastAPI backend
│   └── globals.css           # Tailwind base styles
├── components/
│   ├── ChatWindow.tsx        # Main chat interface
│   ├── MessageBubble.tsx     # Message display + response routing
│   ├── PartCard.tsx          # Compact product cards (search results)
│   ├── DetailedProductView.tsx # Full product view with tabs
│   ├── CompatibilityCard.tsx # Compatibility check results
│   ├── InstallationWizard.tsx # Step-by-step installation guide
│   ├── DiagnosticFlow.tsx    # Troubleshooting accordion UI
│   └── LoadingIndicator.tsx  # Loading states
└── lib/
    ├── api.ts                # API client (returns AgentResponse)
    └── types.ts              # TypeScript interfaces (6 response types)
```

### Backend (FastAPI)
```
backend/app/
├── main.py                   # FastAPI app + /chat endpoint
├── orchestrator.py           # Coordinates router + sub-agents
├── router_agent.py           # Intent classification agent
├── response_models.py        # Typed response Pydantic models
│
│  # Sub-Agents (each has tools + typed output)
├── search_agent.py           # SearchAgent → SearchResponse
├── part_details_agent.py     # PartDetailsAgent → PartDetailsResponse
├── compatibility_agent.py    # CompatibilityAgent → CompatibilityResponse
├── installation_agent.py     # InstallationAgent → InstallationResponse
├── troubleshooting_agent.py  # TroubleshootingAgent → DiagnosisResponse
│
├── models.py                 # Shared Pydantic models (Part, etc.)
├── web_fetcher.py            # Web scraping utilities
└── agent.py                  # (Legacy) Single-agent implementation
```

## Sub-Agent System

### Router Agent
- **Purpose**: Classify user intent and route to appropriate sub-agent
- **Input**: User message + conversation history
- **Output**: `RouterDecision` with `intent` field
- **Intents**: `search`, `part_details`, `compatibility`, `installation`, `troubleshooting`, `off_topic`

### Sub-Agents

#### 1. SearchAgent
- **Purpose**: Find parts matching user query or symptoms
- **Tools**: `search_parts(query, appliance_type)`
- **Output**: `SearchResponse`
  ```typescript
  { type: "search", message, parts[], total_results, search_query, appliance_type? }
  ```
- **UI Component**: Grid of `PartCard` components
- **Example**: "I need an ice maker for my fridge"

#### 2. PartDetailsAgent
- **Purpose**: Get comprehensive information about a specific part
- **Tools**: `get_part_details(part_number)`
- **Output**: `PartDetailsResponse`
  ```typescript
  { type: "part_details", message, part?, compatible_models[], related_parts[] }
  ```
- **UI Component**: `DetailedProductView` with tabs
- **Example**: "Tell me about PS11752778"

#### 3. CompatibilityAgent
- **Purpose**: Verify if a part fits a specific appliance model
- **Tools**: `check_compatibility(part_number, model_number)`
- **Output**: `CompatibilityResponse`
  ```typescript
  { type: "compatibility", message, is_compatible, confidence, explanation, alternative_parts[] }
  ```
- **UI Component**: `CompatibilityCard` with visual status
- **Example**: "Is PS11752778 compatible with WDT780SAEM1?"

#### 4. InstallationAgent
- **Purpose**: Provide step-by-step installation instructions
- **Tools**: `get_installation_guide(part_number)`
- **Output**: `InstallationResponse`
  ```typescript
  { type: "installation", message, difficulty, steps[], tools_required[], safety_warnings[] }
  ```
- **UI Component**: `InstallationWizard` with step navigation
- **Example**: "How do I install PS11752778?"

#### 5. TroubleshootingAgent
- **Purpose**: Troubleshoot problems and recommend parts
- **Tools**: `diagnose_issue(appliance_type, brand, symptom)`
- **Output**: `DiagnosisResponse`
  ```typescript
  { type: "diagnosis", message, likely_causes[], recommended_parts[], troubleshooting_steps[] }
  ```
- **UI Component**: `DiagnosticFlow` with expandable sections
- **Example**: "Ice maker not working on Whirlpool fridge"

### Off-Topic Handling
When the router detects off-topic requests, it returns `OffTopicResponse` directly without invoking any sub-agent:
```typescript
{ type: "off_topic", message: "I specialize in refrigerator and dishwasher parts..." }
```

## Branding & UX Guidelines

### PartSelect Color Theme
```javascript
// tailwind.config.ts
colors: {
  'partselect-blue': '#003366',    // Primary brand color
  'partselect-orange': '#FF6600',  // CTA buttons
  'partselect-gray': '#F5F5F5',    // Backgrounds
}
```

### UX Patterns
- **Product Display**: Rich product cards in chat with images, prices, stock status
- **Message Flow**: User messages (right, blue) / Assistant messages (left, gray)
- **Loading States**: Typing indicators while agent processes requests
- **Error Handling**: Graceful error messages, retry options
- **Auto-scroll**: Always scroll to latest message

## Scope & Constraints

### ✅ What the Agent Does
- Find replacement parts for refrigerators and dishwashers
- Check part compatibility with specific models
- Provide installation instructions with videos
- Troubleshoot common appliance issues
- Recommend parts based on symptoms

### ❌ What the Agent Does NOT Do
- Other appliances (ovens, washers, dryers, microwaves, etc.)
- Non-PartSelect products or competitors
- General appliance advice unrelated to parts
- Process transactions or orders (information only)
- Repairs requiring professional service (gas, electrical)

### Off-Topic Handling
If users ask about out-of-scope topics, the agent politely redirects:
> "I specialize in refrigerator and dishwasher parts from PartSelect. For other appliances, please contact PartSelect customer service."

## Development Guidelines

### When Adding New Features

#### Adding a New Sub-Agent
1. Create response model in `response_models.py` with `type` discriminator
2. Create sub-agent file (e.g., `pricing_agent.py`) with:
   - System prompt focused on the task
   - Tools for data fetching
   - Typed output model
3. Add intent to `RouterDecision.intent` Literal type
4. Update `orchestrator.py` to route to new agent
5. Add TypeScript interface in `frontend/lib/types.ts`
6. Create UI component in `frontend/components/`
7. Add case to `renderAgentResponse()` in `MessageBubble.tsx`

#### Adding a New Appliance Type
1. Update `appliance_type` Literal in relevant agents
2. Update router agent's system prompt
3. Add appliance-specific tools if needed

#### UI Enhancement
1. Add components in `/components/`, import in MessageBubble
2. Ensure component handles the typed response interface
3. Add to `renderAgentResponse()` switch statement

### Testing Checklist
- [ ] Part search returns relevant results
- [ ] Compatibility checks are accurate
- [ ] Installation guides are complete
- [ ] Off-topic queries are gracefully declined
- [ ] Product cards display properly with images
- [ ] Response times < 5 seconds
- [ ] Error states are handled gracefully

### Environment Variables
```bash
# Backend (.env)
ANTHROPIC_API_KEY=your_api_key_here

# Frontend (.env.local)
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Key Technical Patterns

### Typed Response System (Discriminated Union)
All sub-agents return responses with a `type` discriminator field, enabling the frontend to render the appropriate UI component:

```typescript
// Union of all response types
type AgentResponse =
  | SearchResponse        // type: "search"
  | PartDetailsResponse   // type: "part_details"
  | CompatibilityResponse // type: "compatibility"
  | InstallationResponse  // type: "installation"
  | DiagnosisResponse     // type: "diagnosis"
  | OffTopicResponse      // type: "off_topic"
```

### Response Type → UI Component Mapping
```typescript
function renderAgentResponse(response: AgentResponse) {
  switch (response.type) {
    case "search":        return <PartCard[] />
    case "part_details":  return <DetailedProductView />
    case "compatibility": return <CompatibilityCard />
    case "installation":  return <InstallationWizard />
    case "diagnosis":     return <DiagnosticFlow />
    case "off_topic":     return null  // Message only
  }
}
```

### Message Structure
```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string              // Markdown-formatted text
  parts?: Part[]               // Legacy: product data for search results
  responseData?: AgentResponse // Typed response for specialized UI
}
```

### API Contract (NextJS ↔ FastAPI)
```typescript
// Request
{
  message: string
  conversationHistory: Array<{role: string, content: string}>
}

// Response: AgentResponse (one of 6 typed responses)
{
  type: "search" | "part_details" | "compatibility" | "installation" | "diagnosis" | "off_topic"
  message: string
  // ... type-specific fields
}
```

### Backend Response Models (Pydantic)
```python
# Base response with discriminator
class SearchResponse(BaseModel):
    type: Literal["search"] = "search"
    message: str
    parts: list[PartResult]
    total_results: int
    search_query: str
    appliance_type: Optional[Literal["refrigerator", "dishwasher"]] = None

class PartDetailsResponse(BaseModel):
    type: Literal["part_details"] = "part_details"
    message: str
    part: Optional[PartDetails] = None
    compatible_models: list[str] = []
    related_parts: list[PartResult] = []

# ... similar pattern for other response types
```

### Part Models
```python
# Compact part for search results
class PartResult(BaseModel):
    part_number: str
    name: str
    price: float
    image_url: str
    manufacturer: str
    in_stock: bool
    part_select_url: str

# Detailed part for product view
class PartDetails(BaseModel):
    part_number: str
    full_name: str
    description: str
    price: float
    image_urls: list[str]
    manufacturer: str
    in_stock: bool
    avg_rating: Optional[float] = None
    num_reviews: int = 0
    compatible_models: list[str]
    installation_difficulty: Literal["easy", "moderate", "difficult"]
    warranty_info: str
    part_select_url: str
```

## Migration Notes

### From React to Next.js
The original React app provided the foundation:
- ✅ Message bubble UI patterns (reused)
- ✅ Auto-scroll behavior (kept)
- ✅ Input handling (enhanced with loading states)
- ❌ Placeholder API (replaced with real FastAPI backend)
- ❌ Static responses (replaced with Pydantic AI agent)

### From Single Agent to Sub-Agent Architecture
The original single-agent implementation (`agent.py`) was refactored:
- ❌ Single agent with 6 tools → ✅ Router + 5 specialized sub-agents
- ❌ Generic `ChatResponse` → ✅ 6 typed response models
- ❌ Parts-only UI cards → ✅ Specialized UI components per response type
- ❌ Simple text responses → ✅ Rich structured data with typed fields

**Why Sub-Agents?**
1. **Better prompts**: Each agent has a focused system prompt optimized for its task
2. **Type safety**: Strongly-typed outputs enable compile-time checks
3. **UI flexibility**: Different response types render different components
4. **Maintainability**: Changes to one agent don't affect others
5. **Extensibility**: Add new capabilities by adding new sub-agents

### What Was Added (Sub-Agent Migration)
- Router agent for intent classification
- 5 specialized sub-agents with typed outputs
- Orchestrator for agent coordination
- Response models with discriminator field
- 4 new UI components (CompatibilityCard, InstallationWizard, DiagnosticFlow, DetailedProductView)
- Dynamic component rendering in MessageBubble

## Case Study Alignment

This implementation demonstrates:
1. **Modern Framework Expertise**: Next.js 14+ with App Router, TypeScript
2. **Advanced AI Architecture**: Sub-agent pattern with router, orchestrator, and specialized agents
3. **Full-Stack Capability**: Frontend + Backend + AI integration with type safety throughout
4. **Real-World E-commerce**: Live data, product display, compatibility logic
5. **Production-Ready Code**: Discriminated unions, Pydantic models, error handling
6. **UX Excellence**: Specialized UI components per response type (wizard, accordion, cards)
7. **Extensibility**: Clear patterns for adding new sub-agents and capabilities
8. **Type-Driven Development**: Typed responses enable compile-time safety and IDE support

## Running the Project

### Backend
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend
```bash
cd instalily-nextjs
npm install
npm run dev  # Runs on http://localhost:3000
```

### Test the Agent
Visit http://localhost:3000 and try:
- "I need an ice maker for my Whirlpool fridge"
- "Is PS11752778 compatible with WDT780SAEM1?"
- "How do I install a water filter?"
- "My dishwasher isn't draining"

---

**Last Updated**: Sub-agent architecture implementation complete
**Architecture Version**: v2 (Router + Sub-Agents)
**Status**: Frontend integration complete, ready for testing