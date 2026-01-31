# Migration Guide: Custom Web Scraping → Pydantic AI Web Tools

## Overview

This guide explains the reimplementation of the PartSelect agent from custom web scraping (httpx + BeautifulSoup) to Pydantic AI's built-in WebFetchTool and WebSearchTool.

## Current Architecture (Original)

```
User Question
    ↓
Agent (agent.py)
    ↓
Custom Tools (@agent.tool decorators)
    ↓
Web Fetcher Functions (web_fetcher.py)
    ↓
httpx + BeautifulSoup (Manual HTML Parsing)
    ↓
CSS Selectors (.part-number, .price, etc.)
    ↓
Extracted Data → Pydantic Models
    ↓
Structured Response to Frontend
```

**Files**:
- `agent.py` (265 lines) - Agent config + 6 custom tools
- `web_fetcher.py` (752 lines) - All scraping logic
- `models.py` (85+ lines) - Pydantic models

**Pros**:
✅ Full control over data extraction
✅ Highly structured output (PartResult, PartDetails, etc.)
✅ Predictable tool usage

**Cons**:
❌ Brittle - breaks when PartSelect HTML changes
❌ ~750 lines of scraping code to maintain
❌ Multiple CSS selector fallback strategies needed
❌ Manual parsing of prices, images, compatibility lists
❌ Error-prone (missing elements, timeouts, format changes)

---

## New Architecture: Option 1 - Hybrid Approach

**File**: `agent_v2.py`

This keeps the custom tool structure but removes HTML parsing. Tools return "instructions" for the agent to use its web tools.

```
User Question
    ↓
Agent (agent_v2.py)
    ↓
Custom Tool with Instructions
    ↓
Agent Uses WebFetchTool or WebSearchTool
    ↓
Anthropic Infrastructure Fetches Page
    ↓
Claude Analyzes Content (AI-powered extraction)
    ↓
Structured Response (Pydantic Models)
```

**Changes**:
- ✅ Keeps same tool structure (`search_parts_tool`, `get_part_details_tool`, etc.)
- ✅ Maintains structured output (frontend compatibility)
- ✅ Removes all HTML parsing code
- ⚠️ Tools now return instructions + empty data
- ⚠️ Agent interprets instructions and uses web tools
- ⚠️ Less deterministic (AI decides how to extract data)

**Pros**:
✅ No HTML parsing maintenance
✅ Robust to website changes (AI adapts)
✅ Same frontend API
✅ Structured output preserved

**Cons**:
⚠️ Less predictable tool usage
⚠️ Depends on AI's extraction quality
⚠️ May require prompt tuning

---

## New Architecture: Option 2 - Web-Native Approach

**File**: `agent_web_native.py`

Completely removes custom tools. Agent uses web tools naturally and returns structured output via `result_type`.

```
User Question
    ↓
Agent (agent_web_native.py)
    ↓
Agent Decides: Use WebFetch or WebSearch?
    ↓
Anthropic Infrastructure Fetches Pages
    ↓
Claude Analyzes Content
    ↓
PartSelectResponse (message + parts + source_urls)
```

**Changes**:
- ✅ Simplest implementation (~100 lines vs 1000+)
- ✅ No custom tools, just web tools
- ✅ Agent autonomously decides how to answer
- ✅ Returns `PartSelectResponse` with `message` and `parts` fields
- ⚠️ Frontend needs minor changes to handle new response format

**Pros**:
✅ Minimal code (~90% reduction)
✅ No HTML parsing
✅ Most flexible and adaptable
✅ Agent optimizes its own workflow
✅ Still returns structured data via `result_type`

**Cons**:
⚠️ Requires frontend updates (different response shape)
⚠️ Less explicit control over tool usage
⚠️ May need prompt refinement

---

## Comparison Table

| Feature | Current (Scraping) | Option 1 (Hybrid) | Option 2 (Web-Native) |
|---------|-------------------|-------------------|----------------------|
| **Lines of Code** | ~1000 | ~300 | ~100 |
| **HTML Parsing** | Manual (BeautifulSoup) | None | None |
| **Maintenance** | High | Low | Minimal |
| **Robustness** | Breaks on HTML changes | AI adapts | AI adapts |
| **Tool Structure** | 6 custom tools | 6 custom tools | 0 custom tools |
| **Structured Output** | ✅ Full | ✅ Full | ✅ Via result_type |
| **Frontend Compatibility** | ✅ Current | ✅ Compatible | ⚠️ Needs updates |
| **Predictability** | ✅ High | ⚠️ Medium | ⚠️ Lower |
| **Extensibility** | ❌ New scraping logic | ✅ Add instructions | ✅ Just prompt |
| **Dependencies** | httpx, beautifulsoup4 | None (built-in) | None (built-in) |

---

## Recommendation

**For this project, I recommend Option 2 (Web-Native)**:

1. **Massive Code Reduction**: From ~1000 lines to ~100 lines
2. **Zero Maintenance**: No scraping code to maintain when PartSelect changes their site
3. **AI-Powered Extraction**: Claude is excellent at extracting structured data from web pages
4. **Future-Proof**: More adaptable to website changes
5. **Frontend Changes**: Minor - just handle new response format

The frontend update is minimal:
```typescript
// Current
{ message: string, parts: Part[] }

// New
{ message: string, parts: Array<{part_number, name, price, ...}>, source_urls: string[] }
```

---

## Implementation Steps

### Step 1: Test the Web-Native Agent

```bash
cd backend
python test_agent_web_native.py
```

### Step 2: Update Frontend API Client

```typescript
// lib/api.ts - Update response interface
interface AgentResponse {
  message: string;
  parts: Array<{
    part_number: string;
    name: string;
    price: number;
    image_url: string;
    manufacturer: string;
    in_stock: boolean;
    url: string;
  }>;
  source_urls: string[];
}
```

### Step 3: Update FastAPI Endpoint

```python
# main.py - Switch to new agent
from app.agent_web_native import agent, run_agent

@app.post("/chat")
async def chat(request: ChatRequest):
    result = await run_agent(request.message)
    return {
        "message": result["message"],
        "parts": result["parts"]
    }
```

### Step 4: Remove Old Dependencies

```bash
# requirements.txt - Remove these
# httpx
# beautifulsoup4
```

### Step 5: Archive Old Code

```bash
mv backend/app/web_fetcher.py backend/app/web_fetcher_old.py
mv backend/app/agent.py backend/app/agent_old.py
```

---

## Testing Strategy

### Test Cases

1. **Part Search**: "I need an ice maker for my Whirlpool fridge"
   - Verify: Returns list of ice maker parts with prices, images, URLs

2. **Part Details**: "Tell me about PS11752778"
   - Verify: Returns full part details, compatibility, installation info

3. **Compatibility**: "Is PS11752778 compatible with WDT780SAEM1?"
   - Verify: Returns yes/no + explanation + alternative parts if no

4. **Installation**: "How do I install PS11752778?"
   - Verify: Returns difficulty, tools, steps, video links

5. **Diagnosis**: "My ice maker isn't working"
   - Verify: Returns likely causes + recommended parts

6. **Model Search**: "What parts fit WDT780SAEM1?"
   - Verify: Returns categorized parts list

### Expected Improvements

- ✅ More robust to PartSelect HTML changes
- ✅ Better at understanding natural language queries
- ✅ Can handle edge cases (unavailable parts, redirects)
- ✅ Provides better explanations (AI-generated)
- ⚠️ May be slower (web fetches vs local parsing)
- ⚠️ Depends on AI model quality

---

## Rollback Plan

If the new approach doesn't work:

1. Keep `agent_old.py` and `web_fetcher_old.py` as backups
2. FastAPI can easily switch between implementations:
   ```python
   # main.py
   USE_NEW_AGENT = os.getenv("USE_NEW_AGENT", "true") == "true"

   if USE_NEW_AGENT:
       from app.agent_web_native import agent
   else:
       from app.agent_old import agent
   ```
3. Frontend doesn't need changes if response format stays the same

---

## Next Steps

1. **Test web-native agent** with real PartSelect queries
2. **Compare extraction quality** vs current scraping
3. **Measure response times** (web fetch latency)
4. **Update frontend** if adopting Option 2
5. **Deploy and monitor** for accuracy

---

## Key Takeaway

**From 750 lines of brittle HTML parsing → ~100 lines of AI-powered web analysis**

The Pydantic AI built-in tools handle the complexity of web fetching and let Claude do what it does best: understanding and extracting information from unstructured web content.
