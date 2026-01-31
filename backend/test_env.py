#!/usr/bin/env python3
import os
from dotenv import load_dotenv

# Load .env file
load_dotenv()

api_key = os.getenv("ANTHROPIC_API_KEY")
print(f"API Key loaded: {api_key[:20] if api_key else 'None'}...")
print(f"Starts with sk-ant: {api_key.startswith('sk-ant') if api_key else False}")
print(f"Is test key: {api_key.startswith('sk-test') if api_key else False}")
