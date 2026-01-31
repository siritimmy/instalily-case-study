"""
End-to-End Test for Agent Orchestrator

Tests the full flow from user message → router → sub-agent → typed response.

Run with: python test_orchestrator.py
"""

import asyncio
from app.orchestrator import AgentOrchestrator


async def test_orchestrator():
    """Test the orchestrator with various query types."""
    print("=" * 70)
    print("Agent Orchestrator End-to-End Tests")
    print("=" * 70)

    orchestrator = AgentOrchestrator()

    # Test cases for each category
    test_cases = [
        # (query, expected_type, description)
        ("I need an ice maker for my refrigerator", "search", "Product search"),
        ("Tell me about PS11752778", "part_details", "Part details"),
        ("Is PS11752778 compatible with WDT780SAEM1?", "compatibility", "Compatibility check"),
        ("How do I install PS11752778?", "installation", "Installation guide"),
        ("My ice maker isn't working", "diagnosis", "Troubleshooting"),
        ("Tell me about oven parts", "off_topic", "Off-topic query"),
    ]

    passed = 0
    failed = 0

    for query, expected_type, description in test_cases:
        print(f"\n{'─' * 70}")
        print(f"Test: {description}")
        print(f"Query: {query}")
        print(f"Expected type: {expected_type}")

        try:
            result = await orchestrator.process_message(query)

            print(f"Actual type: {result.type}")
            print(f"Message preview: {result.message[:100]}..." if len(result.message) > 100 else f"Message: {result.message}")

            if result.type == expected_type:
                print("✓ PASSED")
                passed += 1
            else:
                print("✗ FAILED - Wrong response type")
                failed += 1

            # Print additional details based on type
            if result.type == "search" and hasattr(result, 'parts'):
                print(f"  Parts found: {len(result.parts)}")
            elif result.type == "compatibility" and hasattr(result, 'is_compatible'):
                print(f"  Compatible: {result.is_compatible}")
            elif result.type == "installation" and hasattr(result, 'difficulty'):
                print(f"  Difficulty: {result.difficulty}")
            elif result.type == "diagnosis" and hasattr(result, 'likely_causes'):
                print(f"  Causes found: {len(result.likely_causes)}")

        except Exception as e:
            print(f"✗ FAILED - Error: {e}")
            failed += 1

    print(f"\n{'=' * 70}")
    print(f"Results: {passed}/{len(test_cases)} passed")
    print("=" * 70)

    return passed, failed


async def test_conversation_context():
    """Test that conversation history is passed through correctly."""
    print("\n" + "=" * 70)
    print("Conversation Context Test")
    print("=" * 70)

    orchestrator = AgentOrchestrator()

    # First message establishes context
    history = [
        {"role": "user", "content": "Tell me about PS11752778"},
        {"role": "assistant", "content": "PS11752778 is an ice maker assembly..."},
    ]

    # Follow-up uses "it"
    result = await orchestrator.process_message(
        "Is it compatible with WDT780SAEM1?",
        history
    )

    print(f"Query: 'Is it compatible with WDT780SAEM1?'")
    print(f"With history referencing PS11752778")
    print(f"Response type: {result.type}")
    print(f"Message: {result.message[:150]}...")

    if result.type == "compatibility":
        print("✓ Correctly identified as compatibility query")
    else:
        print(f"✗ Expected 'compatibility', got '{result.type}'")


if __name__ == "__main__":
    asyncio.run(test_orchestrator())
    asyncio.run(test_conversation_context())
