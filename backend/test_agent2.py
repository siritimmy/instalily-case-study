#!/usr/bin/env python3
"""Test agent response structure"""

import asyncio
import os
import json
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    from app.agent import agent

    print("Testing agent...")
    result = await agent.run("I need help finding an ice maker for my Whirlpool refrigerator model WRS325SDHZ00")

    print("\n=== Agent Result Structure ===")
    print(f"Type: {type(result)}")
    print(f"\nOutput type: {type(result.output)}")
    print(f"\nOutput value:\n{result.output}")

    print(f"\n\nHas _state? {hasattr(result, '_state')}")
    if hasattr(result, '_state'):
        print(f"State type: {type(result._state)}")
        print(f"State dict keys: {result._state.__dict__.keys() if hasattr(result._state, '__dict__') else 'N/A'}")

if __name__ == "__main__":
    asyncio.run(test_agent())
