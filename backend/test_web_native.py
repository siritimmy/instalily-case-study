"""
Test script for the web-native PartSelect agent

This demonstrates how the new agent uses WebFetch and WebSearch
instead of custom web scraping.
"""

import asyncio
import os
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Import the web-native agent
from app.agent_web_native import agent


async def test_agent():
    """Test the web-native agent with various queries"""

    test_queries = [
        # Test 1: Part search
        "I need an ice maker for my Whirlpool refrigerator",

        # Test 2: Specific part details
        "Tell me about part PS11752778",

        # Test 3: Compatibility check
        "Is part PS11752778 compatible with model WDT780SAEM1?",

        # Test 4: Installation guide
        "How do I install part PS11752778?",

        # Test 5: Troubleshooting
        "My refrigerator ice maker is not working, what parts do I need?",
    ]

    print("=" * 80)
    print("TESTING WEB-NATIVE PYDANTIC AI AGENT")
    print("=" * 80)
    print("\nThis agent uses WebFetchTool and WebSearchTool to access PartSelect.com")
    print("No custom HTML parsing - just AI-powered web analysis!\n")

    for i, query in enumerate(test_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"TEST {i}: {query}")
        print('=' * 80)

        try:
            # Run the agent
            result = await agent.run(query)

            # Display results
            print(f"\n📝 RESPONSE MESSAGE:\n{result.output.message}\n")

            if result.output.parts:
                print(f"\n🔧 PARTS FOUND ({len(result.output.parts)}):")
                for part in result.output.parts:
                    price = part.get('price', 0)
                    price_str = f"${price:.2f}" if price is not None else "Price N/A"
                    print(f"\n  Part Number: {part.get('part_number', 'N/A')}")
                    print(f"  Name: {part.get('name', 'N/A')}")
                    print(f"  Price: {price_str}")
                    print(f"  Manufacturer: {part.get('manufacturer', 'N/A')}")
                    print(f"  In Stock: {part.get('in_stock', False)}")
                    print(f"  URL: {part.get('url', 'N/A')}")
            else:
                print("\n🔧 PARTS FOUND: None")

            if result.output.source_urls:
                print(f"\n🔗 SOURCE URLS ({len(result.output.source_urls)}):")
                for url in result.output.source_urls:
                    print(f"  - {url}")

            # Show tool usage
            print(f"\n🛠️  TOOL USAGE:")
            usage = result.usage()
            print(f"  Requests: {usage.requests}")
            print(f"  Input tokens: {usage.input_tokens}")
            print(f"  Output tokens: {usage.output_tokens}")
            print(f"  Total tokens: {usage.total_tokens}")

        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 80)
        print("Press Enter to continue to next test...")
        input()


async def interactive_mode():
    """Interactive testing mode"""
    print("\n" + "=" * 80)
    print("INTERACTIVE MODE")
    print("=" * 80)
    print("\nAsk questions about refrigerator and dishwasher parts!")
    print("Type 'quit' to exit\n")

    while True:
        try:
            query = input("\n💬 Your question: ").strip()

            if query.lower() in ['quit', 'exit', 'q']:
                print("\n👋 Goodbye!")
                break

            if not query:
                continue

            print("\n🤔 Processing...\n")

            result = await agent.run(query)

            print(f"\n📝 Response:\n{result.output.message}\n")

            if result.output.parts:
                print(f"\n🔧 Parts Found ({len(result.output.parts)}):")
                for part in result.output.parts:
                    price = part.get('price')
                    price_str = f"${price:.2f}" if price is not None else "Price N/A"
                    print(f"  • {part.get('part_number')} - {part.get('name')} - {price_str}")

            usage = result.usage()
            print(f"\n📊 Usage: {usage.requests} requests, {usage.total_tokens} tokens")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")


async def main():
    """Main test runner"""
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == '--interactive':
        await interactive_mode()
    else:
        await test_agent()


if __name__ == "__main__":
    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ERROR: ANTHROPIC_API_KEY not found in environment")
        print("Please set it in your .env file or environment variables")
        exit(1)

    # Run tests
    asyncio.run(main())
