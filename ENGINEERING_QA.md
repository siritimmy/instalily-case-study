# Engineering Q&A: PartSelect Chat Agent

Technical questions and answers addressing the evaluation criteria for this case study.

---

## Agentic Architecture

### Q: Performance concerns with multiple LLM calls?

**A:** Actually just 2 calls (router + sub-agent). Alternative of iterative clarification would be 3-5 calls. Can optimize router with fine-tuned classifier later.

### Q: Why not use LangChain?

**A:** Pydantic AI gives better type safety, simpler codebase, less abstraction overhead. For this use case, don't need LangChain's ecosystem complexity.

### Q: Why a router + sub-agent pattern instead of a single multi-tool agent?

**A:** Separation of concerns. Each sub-agent has a focused system prompt optimized for its task. A monolithic agent would have prompt bloat and confused tool selection. The router pattern also enables:
- Independent testing of each agent
- Easy addition of new capabilities (just add a new agent)
- Different models per task if needed (e.g., faster model for router)
- Clear debugging (know exactly which agent handled a query)

### Q: How does the orchestrator decide which agent to call?

**A:** The router agent returns a `RoutingDecision` with `category` (one of 6 types) and `confidence` level. The orchestrator maps this to the appropriate sub-agent. Low-confidence classifications could trigger clarification prompts in the future.

### Q: Why use discriminated unions for response types?

**A:** The `type` field discriminator enables:
- Type-safe frontend rendering (TypeScript knows exactly which fields exist)
- Clean switch statement routing to specialized UI components
- Self-documenting API contracts via Pydantic schemas
- Each query type gets purpose-built UI (not generic text)

---

## Handling the Example Queries

### Q: How does "How can I install part PS11752778?" work?

**A:** Flow:
1. Router classifies as `installation` intent, extracts part number via regex
2. InstallationAgent receives the request
3. Agent calls `get_installation_guide_tool(part_number)` which scrapes PartSelect
4. Returns structured `InstallationResponse` with steps, tools needed, difficulty, video links
5. Frontend renders **InstallationWizard** component with step-by-step progress tracker

Key UX decisions:
- Safety warnings displayed prominently before steps
- Difficulty rating helps users decide DIY vs professional
- Video links provide visual guidance
- Estimated time sets expectations

### Q: How does "Ice maker not working" troubleshooting work?

**A:** Flow:
1. Router classifies as `troubleshooting`, extracts appliance type + symptom
2. TroubleshootingAgent calls `diagnose_issue_tool(appliance, brand, symptom)`
3. Tool returns likely causes ranked by probability + recommended parts
4. Agent provides troubleshooting steps to verify diagnosis before buying
5. Frontend renders **DiagnosticFlow** with expandable cause/fix sections

Key UX decisions:
- Lists multiple possible causes (not just one guess)
- DIY difficulty rating prevents users from attempting risky repairs
- Troubleshooting steps help users verify the issue before purchasing
- Recommended parts are actionable (can click to see details/buy)

---

## Scope Control

### Q: How do you handle scope control?

**A:** Router agent has explicit instructions to only classify refrigerator/dishwasher intents. Returns "out_of_scope" type which triggers polite decline message.

### Q: What happens if someone asks about ovens or washing machines?

**A:** The router system prompt explicitly restricts to refrigerators and dishwashers:
```
IMPORTANT: Only classify questions about REFRIGERATORS and DISHWASHERS.
Any questions about other appliances should be classified as "off_topic".
```

User receives a polite response explaining the scope and what the agent CAN help with, rather than a generic "I can't help."

### Q: How does the system infer appliance type when not specified?

**A:** Keyword-based heuristics in the router:
- **Refrigerator signals**: ice, freezer, cooling, cold, fridge, water dispenser
- **Dishwasher signals**: dish, drain, spray arm, rack, detergent, rinse

If ambiguous, the agent asks for clarification rather than guessing wrong.

---

## User Experience

### Q: Why different UI components for different response types?

**A:** Generic chat bubbles work poorly for structured product data. Each response type has specific UX needs:

| Response Type | Why Specialized UI? |
|--------------|---------------------|
| Search results | Grid layout lets users scan/compare multiple parts quickly |
| Part details | Tabbed interface organizes specs, compatibility, related parts |
| Compatibility | Visual checkmark/X provides instant answer |
| Installation | Step-by-step wizard with progress tracking |
| Troubleshooting | Expandable sections for causes/fixes reduce overwhelm |

### Q: How does conversation context work for follow-ups?

**A:** Users shouldn't have to repeat themselves. The system:
1. Maintains last 3 messages as context
2. Router resolves pronouns ("it", "that part", "this model")
3. Entity extraction runs on history, not just current message
4. Example: "Tell me about PS11752778" → "Is it compatible with my fridge?" works seamlessly

### Q: Why show safety warnings prominently for installation?

**A:** Liability and user safety. Installation guides always lead with:
- "Disconnect power before starting"
- "Turn off water supply" (for water-connected parts)
- Difficult installations recommend professional help
- Gas/electrical work explicitly requires licensed professionals

### Q: How are products displayed in search results?

**A:** ProductGrid component shows:
- Part image (visual recognition)
- Part name and number (identification)
- Price (decision factor)
- Stock status (availability)
- Manufacturer (brand trust)
- One-click to view details or check compatibility

Limited to 3-8 results to avoid overwhelming users while providing choice.

---

## Extensibility

### Q: How would you add a new agent (e.g., order tracking)?

**A:** The architecture makes this straightforward:

1. **Create agent** (`order_tracking_agent.py`):
   ```python
   agent = Agent(model=model, output_type=OrderTrackingResponse)
   @agent.tool
   def get_order_status(order_id: str) -> OrderStatus: ...
   ```

2. **Define response type**:
   ```python
   class OrderTrackingResponse(BaseModel):
       type: Literal["order_tracking"]
       order_id: str
       status: str
       estimated_delivery: Optional[date]
   ```

3. **Update router** to recognize "order tracking" intent

4. **Add orchestrator case**:
   ```python
   elif category == "order_tracking":
       return await self.order_tracking_agent.run(...)
   ```

5. **Create frontend component** (`OrderTrackingCard.tsx`)

6. **Add switch case** in MessageBubble

Each step is isolated—no changes to existing agents required.

### Q: How would you add support for more appliance types?

**A:** Gradual expansion:
1. Update router system prompt to accept new types (e.g., "washing machines")
2. Add appliance-specific inference keywords
3. Web fetcher may need new URL patterns if PartSelect organizes differently
4. Update off-topic message to reflect new scope
5. Existing agents (search, compatibility, etc.) work without modification

### Q: Could this architecture support a different e-commerce domain?

**A:** Yes, the pattern is domain-agnostic:
- Swap web fetcher for domain-specific data source (or API)
- Update Pydantic models for domain entities (e.g., `AutoPart` vs `AppliancePart`)
- Modify system prompts for domain expertise
- Frontend components adapt to new response structures
- Router categories stay similar (search, details, compatibility are universal)

### Q: How would you add proactive features (e.g., "You might also need...")?

**A:** The `related_parts` field already supports this. Could extend by:
- Adding "frequently bought together" data to part details
- Installation agent suggesting required tools/supplies
- Troubleshooting agent recommending diagnostic tools
- These are response model changes, not architecture changes

---

## Scalability

### Q: What's the typical response latency?

**A:** 2-4 seconds total:
- Router classification: ~500ms-1s
- Sub-agent reasoning: ~1-2s
- Web scraping (if needed): ~1-2s

Web scraping is the bottleneck—would improve with caching or API access.

### Q: How would this scale for high traffic?

**A:** The architecture supports horizontal scaling:

1. **Caching** (Redis): Part details, compatibility checks, search results
2. **Async throughout**: Already using async/await for concurrent requests
3. **Stateless design**: Any server instance can handle any request
4. **Model optimization**: Could use faster model for router, full model for agents

### Q: Why is the conversation stateless?

**A:** Simpler for MVP, but production would add persistence:
- Store conversations in database with session ID
- Enables cross-device continuity
- Supports conversation history for customer service
- Architecture doesn't change—just add storage layer

---

## Data & Accuracy

### Q: How reliable is the product data?

**A:** Data comes directly from PartSelect.com via web scraping:
- Prices, stock status, specs are real-time
- Multiple CSS selector fallbacks for reliability
- Graceful degradation if scraping fails (helpful error vs crash)
- **Ideal**: Official PartSelect API would be more reliable

### Q: How do you prevent hallucinated product information?

**A:** Agents don't make up data—they use tools:
- Part details come from `get_part_details_tool()` (scraped data)
- Compatibility comes from `check_compatibility_tool()` (database match)
- Prices, specs, availability are never generated by LLM
- If data unavailable, agent says "I couldn't find that" vs inventing

### Q: How accurate is the compatibility checking?

**A:** Multiple verification strategies:
1. **Exact match**: Model number in part's compatible models list
2. **Fuzzy match**: Handles model number variations (WDT780SAEM1 vs WDT780SAEM)
3. **Confidence levels**: "confirmed" vs "likely" vs "unlikely"
4. **Alternatives**: If not compatible, suggests parts that ARE compatible

---

## Technical Decisions

### Q: Why Pydantic AI over other frameworks?

**A:** Best fit for this use case:
- **Type safety**: Response schemas enforced at runtime
- **Simplicity**: Less abstraction than LangChain
- **Tool integration**: Clean `@agent.tool` decorator pattern
- **Structured outputs**: Native support for Pydantic models
- **Debugging**: Clear error messages when schemas don't match

### Q: Why Claude (Sonnet) as the LLM?

**A:** Strong balance of capabilities:
- Excellent instruction following for structured outputs
- Good reasoning for troubleshooting/diagnosis
- Cost-effective for production workloads
- Fast enough for real-time chat (< 2s responses)
- Could swap models via config if needed