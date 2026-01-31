"""
Test script for conversation context resolution.

Tests that the router correctly extracts part numbers from conversation
history when the user uses references like "this part", "that part", etc.
"""

import asyncio
import sys
sys.path.insert(0, 'app')

from app.router_agent import RouterAgent


async def test_context_resolution():
    """Test the exact scenario from the user's example."""
    router = RouterAgent()

    # Simulate the conversation history
    conversation_history = [
        {
            "role": "user",
            "content": "tell me about part PS11752778"
        },
        {
            "role": "assistant",
            "content": "The Whirlpool WPW10321304 (Part PS11752778) is a genuine OEM refrigerator door shelf bin designed for side-by-side refrigerators. Priced at $44.95, this clear door bin with white trim provides convenient storage for jars and bottles on your refrigerator door. It's compatible with multiple brands including Whirlpool, KitchenAid, Maytag, and Amana. Installation is straightforward and tool-free—simply align and snap into place, making it an easy DIY replacement. This high-quality replacement part is currently in stock and ready to help restore your refrigerator's storage capacity and organization."
        }
    ]

    # Current message uses "this part" reference
    current_message = "Is this part compatible with my WDT780SAEM1 model?"

    print("=" * 60)
    print("Testing Conversation Context Resolution")
    print("=" * 60)
    print(f"\nConversation history:")
    for msg in conversation_history:
        print(f"  {msg['role']}: {msg['content'][:80]}...")
    print(f"\nCurrent message: {current_message}")
    print("-" * 60)

    # Classify the question
    result = await router.classify(current_message, conversation_history)

    print(f"\nRouting Decision:")
    print(f"  Category: {result.category}")
    print(f"  Confidence: {result.confidence}")
    print(f"  Reasoning: {result.reasoning}")
    print(f"\nExtracted Entities:")
    print(f"  Part numbers: {result.entities.part_numbers}")
    print(f"  Model numbers: {result.entities.model_numbers}")
    print(f"  Appliance type: {result.entities.appliance_type}")
    print(f"  Brand: {result.entities.brand}")

    # Verify the fix worked
    print("\n" + "=" * 60)
    print("VERIFICATION:")

    success = True

    if "PS11752778" in result.entities.part_numbers:
        print("  ✓ Part number PS11752778 extracted from context")
    else:
        print("  ✗ FAILED: Part number PS11752778 NOT extracted")
        success = False

    if "WDT780SAEM1" in result.entities.model_numbers:
        print("  ✓ Model number WDT780SAEM1 extracted from message")
    else:
        print("  ✗ FAILED: Model number WDT780SAEM1 NOT extracted")
        success = False

    if result.category == "compatibility":
        print("  ✓ Correctly classified as 'compatibility'")
    else:
        print(f"  ✗ FAILED: Expected 'compatibility', got '{result.category}'")
        success = False

    print("=" * 60)
    if success:
        print("ALL TESTS PASSED!")
    else:
        print("SOME TESTS FAILED!")
    print("=" * 60)

    return success


if __name__ == "__main__":
    success = asyncio.run(test_context_resolution())
    sys.exit(0 if success else 1)
