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
NextJS Frontend (Chat UI + Product Cards)
    ↓ HTTP/JSON
NextJS API Routes (/api/chat)
    ↓ HTTP/JSON
FastAPI Backend (Agent Orchestration)
    ↓ Function Calls
Pydantic AI Agent (6 Tools)
    ↓ Web Fetch/Scrape
PartSelect.com (Live Data)
```

### Key Design Decisions

1. **Tool-Based Architecture**: Each capability (search, compatibility, installation) is a separate Pydantic AI tool. This makes the system highly extensible - adding new appliances or features just means adding new tools.

2. **Live Data Integration**: No static database or cached data. All product information comes from live PartSelect.com scraping, ensuring accuracy.

3. **Structured Outputs**: All tools use Pydantic models for validation and type safety throughout the stack.

4. **Scope Control**: Enforced at multiple levels:
   - System prompt restricts to refrigerator/dishwasher only
   - Tool inputs use `Literal["refrigerator", "dishwasher"]` type constraints
   - Pre-processing filters catch off-topic requests

## Project Structure

### Frontend (Next.js)
```
instalily-nextjs/
├── app/
│   ├── page.tsx              # Main chat page
│   ├── layout.tsx            # Root layout with branding
│   ├── api/chat/route.ts     # Proxy to FastAPI backend
│   └── globals.css           # Tailwind base styles
├── components/
│   ├── ChatWindow.tsx        # Main chat interface
│   ├── MessageBubble.tsx     # Message display with markdown
│   ├── PartCard.tsx          # Product display cards
│   ├── LoadingIndicator.tsx  # Loading states
│   └── ErrorBoundary.tsx     # Error handling
└── lib/
    ├── api.ts                # API client for FastAPI
    └── types.ts              # TypeScript interfaces
```

### Backend (FastAPI)
```
backend/
├── main.py                   # FastAPI app + /chat endpoint
├── agent.py                  # Pydantic AI agent configuration
├── tools/
│   ├── search_parts.py       # Tool 1: Search parts by query
│   ├── part_details.py       # Tool 2: Get full part details
│   ├── compatibility.py      # Tool 3: Check model compatibility
│   ├── installation.py       # Tool 4: Installation guides
│   ├── diagnosis.py          # Tool 5: Troubleshoot issues
│   └── model_search.py       # Tool 6: Search by model number
├── models.py                 # Shared Pydantic models
├── web_fetcher.py            # Web scraping utilities
└── config.py                 # Environment config
```

## The 6 Pydantic AI Tools

### 1. search_parts
- **Purpose**: Find parts matching user query or symptoms
- **Input**: `query: str`, `appliance_type: Literal["refrigerator", "dishwasher"]`
- **Output**: List of `PartResult` objects with images, prices, stock status
- **Example**: "I need an ice maker for my fridge" → Returns ice maker parts

### 2. get_part_details
- **Purpose**: Get comprehensive information about a specific part
- **Input**: `part_number: str`
- **Output**: Full specs, images, compatible models, reviews, difficulty
- **Example**: "Tell me about PS11752778" → Returns complete part details

### 3. check_compatibility
- **Purpose**: Verify if a part fits a specific appliance model
- **Input**: `part_number: str`, `model_number: str`
- **Output**: Compatibility status, confidence level, explanation, alternatives
- **Example**: "Is PS11752778 compatible with WDT780SAEM1?" → Yes/No + details

### 4. get_installation_guide
- **Purpose**: Provide step-by-step installation instructions
- **Input**: `part_number: str`
- **Output**: Steps, tools required, difficulty, time estimate, video links
- **Example**: "How do I install PS11752778?" → Step-by-step guide

### 5. diagnose_issue
- **Purpose**: Troubleshoot problems and recommend parts
- **Input**: `appliance_type`, `brand`, `symptom`
- **Output**: Likely causes, recommended parts, troubleshooting steps
- **Example**: "Ice maker not working on Whirlpool fridge" → Diagnosis + parts

### 6. search_by_model
- **Purpose**: Find all parts compatible with a specific model
- **Input**: `model_number: str`
- **Output**: All parts categorized by type, common replacements highlighted
- **Example**: "What parts fit WDT780SAEM1?" → Categorized parts list

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
1. **New Appliance Type**: Add tools with updated `appliance_type` Literal
2. **New Capability**: Create new tool in `/backend/tools/` with Pydantic models
3. **UI Enhancement**: Add components in `/components/`, import in ChatWindow
4. **Branding Update**: Modify `tailwind.config.ts` for color changes

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

### Message Structure
```typescript
interface Message {
  role: 'user' | 'assistant'
  content: string              // Markdown-formatted text
  parts?: Part[]              // Rich product data from tools
}
```

### API Contract (NextJS ↔ FastAPI)
```typescript
// Request
{
  message: string
  conversation_history: Array<{role: string, content: string}>
}

// Response
{
  message: string              // Agent's text response
  parts: Array<PartResult>    // Products to display
}
```

### Tool Return Pattern
All tools return Pydantic models that serialize to JSON for frontend consumption:
```python
class PartResult(BaseModel):
    part_number: str
    name: str
    price: float
    image_url: str
    manufacturer: str
    in_stock: bool
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

### What Was Added
- Server-side rendering with Next.js App Router
- API routes for backend proxy
- Pydantic AI agent with 6 tools
- Rich product card components
- PartSelect branding and styling
- Error handling and loading states
- Live data integration with PartSelect.com

## Case Study Alignment

This implementation demonstrates:
1. **Modern Framework Expertise**: Next.js 14+ with App Router
2. **AI Engineering Best Practices**: Pydantic AI tool-based architecture
3. **Full-Stack Capability**: Frontend + Backend + AI integration
4. **Real-World E-commerce**: Live data, product display, compatibility logic
5. **Production-Ready Code**: Type safety, error handling, scalability
6. **UX Excellence**: Rich product cards, smooth chat experience
7. **Extensibility**: Clear patterns for adding features/appliances

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

**Last Updated**: Based on implementation plan v1
**Primary Contact**: Case study implementation
**Status**: Ready for development