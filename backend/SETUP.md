# Setup Guide for Web-Native Agent

## Quick Start

### 1. Set Up Your API Key

You need an Anthropic API key to use the web-native agent.

**Option A: Add to .env file (Recommended)**

```bash
cd /Users/timmy/Documents/2025-26/instalily-case-study/backend
echo "ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here" > .env
```

**Option B: Export as environment variable**

```bash
export ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key-here
```

Get your API key from: https://console.anthropic.com/settings/keys

### 2. Install Dependencies

Make sure you have Pydantic AI installed:

```bash
pip install pydantic-ai
```

Or install from requirements:

```bash
pip install -r requirements.txt
```

### 3. Test the Agent

**Run automated tests:**

```bash
python test_web_native.py
```

**Run interactive mode:**

```bash
python test_web_native.py --interactive
```

---

## What the Web-Native Agent Does

The web-native agent uses Pydantic AI's built-in `WebFetchTool` and `WebSearchTool` to:

1. **Search PartSelect.com** for parts matching your query
2. **Fetch product pages** to get detailed information
3. **Extract structured data** using AI (no manual HTML parsing!)
4. **Return results** in a consistent format

### Example Queries

Try these in interactive mode:

- "I need an ice maker for my Whirlpool refrigerator"
- "Tell me about part PS11752778"
- "Is part PS11752778 compatible with model WDT780SAEM1?"
- "How do I install a water filter?"
- "My dishwasher isn't draining properly"

---

## Troubleshooting

### "ANTHROPIC_API_KEY not found"

Make sure you've set the API key in your .env file:

```bash
cat .env
# Should show: ANTHROPIC_API_KEY=sk-ant-api03-...
```

If the file is empty, add your key:

```bash
echo "ANTHROPIC_API_KEY=your-key-here" > .env
```

### "Module not found: pydantic_ai"

Install Pydantic AI:

```bash
pip install pydantic-ai
```

### "Unknown keyword arguments: builtin_tools"

Your Pydantic AI version might be outdated. Update it:

```bash
pip install --upgrade pydantic-ai
```

### Import errors from app module

Make sure you're running from the backend directory:

```bash
cd /Users/timmy/Documents/2025-26/instalily-case-study/backend
python test_web_native.py
```

---

## Comparing with Current Implementation

### Current (Custom Scraping)

```bash
# Test the current implementation
python test_agent.py
```

This uses httpx + BeautifulSoup to manually parse HTML.

### New (Web-Native)

```bash
# Test the web-native implementation
python test_web_native.py
```

This uses Pydantic AI's built-in web tools - no HTML parsing!

---

## Next Steps

1. ✅ Set up your API key (above)
2. ✅ Test the web-native agent
3. ✅ Compare results with current implementation
4. ✅ Read [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for full migration details
5. ✅ Update FastAPI endpoint to use new agent (if satisfied with results)

---

## Cost Considerations

The web-native agent uses Claude API calls which have costs:

- **Web fetches**: Charged based on tokens in/out
- **Web searches**: Additional API calls

Typical cost per query: $0.01 - $0.05 depending on:
- Number of pages fetched
- Length of pages
- Complexity of extraction

Monitor costs in the test output:
```
💰 Cost: $0.0234
```

You can limit costs by:
- Setting `max_uses` in WebFetchTool/WebSearchTool
- Using cheaper models (haiku vs sonnet)
- Caching results when appropriate

---

## Questions?

- Read [REIMPLEMENTATION_SUMMARY.md](REIMPLEMENTATION_SUMMARY.md) for full details
- Check [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md) for migration steps
- Review [agent_web_native.py](app/agent_web_native.py) for implementation
