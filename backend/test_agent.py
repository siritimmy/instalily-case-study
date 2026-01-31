#!/usr/bin/env python3
"""Quick test to see what the agent returns"""

import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

async def test_agent():
    from app.agent import agent

    print("Testing agent with simple message...")
    result = await agent.run("Can you help me find an ice maker?")

    print("\n=== Agent Result ===")
    print(f"Type: {type(result)}")
    print(f"Result: {result}")

    if hasattr(result, "data"):
        print(f"\nresult.data: {result.data}")

    if hasattr(result, "output"):
        print(f"\nresult.output: {result.output}")

    if hasattr(result, "__dict__"):
        print(f"\nresult attributes: {result.__dict__.keys()}")

if __name__ == "__main__":
    asyncio.run(test_agent())
