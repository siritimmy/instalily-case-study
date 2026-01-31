"""
Test Router Agent - Question Classification

Tests the router agent's ability to classify questions into 5 categories
and extract relevant entities.

Run with: python -m pytest test_router.py -v
Or for async: python test_router.py
"""

import asyncio
import sys
from app.router_agent import RouterAgent, classify_question, RoutingDecision

# Test cases mapping expected categories
TEST_CASES = [
    # Search queries
    ("I need an ice maker", "search"),
    ("Find water filters for dishwashers", "search"),
    ("Show me door gaskets", "search"),
    ("What refrigerator parts do you have?", "search"),

    # Part details queries
    ("Tell me about PS11752778", "part_details"),
    ("What's the price of PS11752778?", "part_details"),
    ("Is PS12345678 in stock?", "part_details"),
    ("Show me details for part PS11752778", "part_details"),

    # Compatibility queries
    ("Is PS11752778 compatible with WDT780SAEM1?", "compatibility"),
    ("Will PS11752778 work with my Whirlpool fridge?", "compatibility"),
    ("Does this part fit model RF28R7351SR?", "compatibility"),
    ("Can I use PS11752778 on my Samsung dishwasher?", "compatibility"),

    # Installation queries
    ("How do I install PS11752778?", "installation"),
    ("What tools do I need to replace the ice maker?", "installation"),
    ("Is this hard to install?", "installation"),
    ("Show me installation instructions for PS11752778", "installation"),

    # Troubleshooting queries
    ("My ice maker isn't working", "troubleshooting"),
    ("The dishwasher won't drain", "troubleshooting"),
    ("Fridge is making a loud noise", "troubleshooting"),
    ("Water is leaking from my refrigerator", "troubleshooting"),

    # Off-topic queries
    ("Tell me about oven parts", "off_topic"),
    ("I need a washing machine belt", "off_topic"),
    ("Help me with my dryer", "off_topic"),
    ("What's the weather like?", "off_topic"),
]


async def test_single_classification(message: str, expected_category: str) -> tuple[bool, RoutingDecision]:
    """Test a single classification."""
    result = await classify_question(message)
    passed = result.category == expected_category
    return passed, result


async def run_all_tests():
    """Run all classification tests."""
    print("=" * 70)
    print("Router Agent Classification Tests")
    print("=" * 70)

    router = RouterAgent()
    passed = 0
    failed = 0

    for message, expected in TEST_CASES:
        result = await router.classify(message)

        if result.category == expected:
            status = "PASS"
            passed += 1
        else:
            status = "FAIL"
            failed += 1

        print(f"\n{status}: '{message[:50]}...' " if len(message) > 50 else f"\n{status}: '{message}'")
        print(f"  Expected: {expected}")
        print(f"  Got: {result.category} (confidence: {result.confidence})")
        print(f"  Entities: {result.entities.model_dump_json()}")
        print(f"  Reasoning: {result.reasoning}")

    print("\n" + "=" * 70)
    print(f"Results: {passed}/{len(TEST_CASES)} passed ({100*passed/len(TEST_CASES):.1f}%)")
    print("=" * 70)

    return passed, failed


async def test_entity_extraction():
    """Test entity extraction specifically."""
    print("\n" + "=" * 70)
    print("Entity Extraction Tests")
    print("=" * 70)

    router = RouterAgent()

    test_cases = [
        # (message, expected_parts, expected_models, expected_appliance)
        (
            "Is PS11752778 compatible with WDT780SAEM1?",
            ["PS11752778"],
            ["WDT780SAEM1"],
            None  # Could be either
        ),
        (
            "Tell me about PS12345678 for my Samsung refrigerator",
            ["PS12345678"],
            [],
            "refrigerator"
        ),
        (
            "My Whirlpool dishwasher won't drain",
            [],
            [],
            "dishwasher"
        ),
        (
            "Find ice makers",
            [],
            [],
            "refrigerator"
        ),
    ]

    for message, expected_parts, expected_models, expected_appliance in test_cases:
        result = await router.classify(message)

        print(f"\nMessage: '{message}'")
        print(f"  Part numbers: {result.entities.part_numbers} (expected: {expected_parts})")
        print(f"  Model numbers: {result.entities.model_numbers} (expected: {expected_models})")
        print(f"  Appliance type: {result.entities.appliance_type} (expected: {expected_appliance})")

        # Check part numbers
        parts_match = set(p.upper() for p in result.entities.part_numbers) == set(p.upper() for p in expected_parts)
        print(f"  Parts match: {'YES' if parts_match else 'NO'}")


async def test_conversation_context():
    """Test that router uses conversation history for context."""
    print("\n" + "=" * 70)
    print("Conversation Context Tests")
    print("=" * 70)

    router = RouterAgent()

    # First message mentions a part
    history = [
        {"role": "user", "content": "Tell me about PS11752778"},
        {"role": "assistant", "content": "PS11752778 is an ice maker assembly..."},
    ]

    # Follow-up message uses "it"
    follow_up = "Is it compatible with WDT780SAEM1?"

    result = await router.classify(follow_up, history)

    print(f"\nHistory: {history}")
    print(f"Follow-up: '{follow_up}'")
    print(f"Category: {result.category}")
    print(f"Entities: {result.entities.model_dump_json()}")
    print(f"Reasoning: {result.reasoning}")


if __name__ == "__main__":
    print("\nRunning Router Agent Tests...\n")

    asyncio.run(run_all_tests())
    asyncio.run(test_entity_extraction())
    asyncio.run(test_conversation_context())
