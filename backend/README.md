# PartSelect Agent Backend

FastAPI backend for the PartSelect chat assistant, powered by Pydantic AI and Claude.

## Setup

### Prerequisites
- Python 3.11+
- pip

### Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file from the example:
```bash
cp .env.example .env
```

3. Add your Anthropic API key to `.env`:
```
ANTHROPIC_API_KEY=sk-your-key-here
```

### Running the Server

Development mode:
```bash
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Production mode:
```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at `http://localhost:8000` with docs at `http://localhost:8000/docs`.

## API Endpoints

### POST /chat
Handle chat messages with the PartSelect agent.

**Request:**
```json
{
  "message": "Tell me about part PS11752778",
  "conversation_history": []
}
```

**Response:**
```json
{
  "message": "This is an ice maker assembly...",
  "parts": [
    {
      "partNumber": "PS11752778",
      "name": "Ice Maker Assembly",
      "price": 249.99,
      "imageUrl": "...",
      "manufacturer": "Whirlpool",
      "inStock": true,
      "partSelectUrl": "https://www.partselect.com/PS11752778"
    }
  ]
}
```

### GET /health
Health check endpoint.

### GET /
Root endpoint with API information.

## Architecture

The backend uses:
- **Pydantic AI**: Agent framework with Claude integration
- **FastAPI**: Web framework
- **Web Fetchers**: Functions to scrape live PartSelect data
- **Tools**: Specialized functions for product search, compatibility checking, installation guides, troubleshooting

## Available Agent Tools

1. **search_parts**: Find parts by query, part number, or symptom
2. **get_part_details**: Get full product information
3. **check_compatibility**: Verify part fits a model
4. **get_installation_guide**: Get installation instructions
5. **diagnose_issue**: Troubleshoot appliance problems
6. **search_by_model**: Find all parts for an appliance model

## Development Notes

- The agent is configured to only help with refrigerator and dishwasher parts
- Web scraping functions fetch live data from PartSelect.com
- Tool responses are structured using Pydantic models for type safety
- All errors are logged and returned with appropriate HTTP status codes

## Next Steps

- Implement actual web scraping selectors for PartSelect.com HTML structure
- Add conversation history management (currently stateless)
- Add rate limiting and caching for performance
- Implement analytics and logging improvements
