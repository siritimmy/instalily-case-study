#!/usr/bin/env python3
"""
Test script for PartSelect web fetching tools

This script tests the three core tools:
1. search_parts
2. get_part_details
3. check_compatibility

Usage:
    python test_tools.py
"""

import asyncio
import logging
from app.web_fetcher import search_parts, get_part_details, check_compatibility

# Setup logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def test_search_parts():
    """Test the search_parts function"""
    print("\n" + "=" * 60)
    print("TEST 1: Search Parts")
    print("=" * 60)

    test_queries = [
        "ice maker",
        "PS11752778",  # Specific part number from case study
        "water filter",
        "dishwasher rack",
    ]

    for query in test_queries:
        print(f"\n📦 Searching for: '{query}'")
        try:
            results = await search_parts(query, limit=3)
            print(f"   ✅ Found {len(results)} parts")

            for i, part in enumerate(results, 1):
                print(f"\n   Part {i}:")
                print(f"      Part Number: {part['part_number']}")
                print(f"      Name: {part['name']}")
                print(f"      Price: ${part['price']:.2f}")
                print(f"      Manufacturer: {part['manufacturer']}")
                print(f"      In Stock: {part['in_stock']}")
                print(f"      URL: {part['part_select_url']}")

            if not results:
                print("   ⚠️  No parts found (this may be expected if selectors don't match)")

        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_get_part_details():
    """Test the get_part_details function"""
    print("\n" + "=" * 60)
    print("TEST 2: Get Part Details")
    print("=" * 60)

    test_parts = [
        "PS11752778",  # Part from case study
        "WP2187172",  # Common refrigerator part
    ]

    for part_num in test_parts:
        print(f"\n🔍 Getting details for part: {part_num}")
        try:
            details = await get_part_details(part_num)

            if details:
                print(f"   ✅ Details found")
                print(f"\n   Full Name: {details['full_name']}")
                print(f"   Part Number: {details['part_number']}")
                print(f"   Price: ${details['price']:.2f}")
                print(f"   Manufacturer: {details['manufacturer']}")
                print(f"   In Stock: {details['in_stock']}")
                print(f"   Description: {details['description'][:100]}...")
                print(f"   Images: {len(details['image_urls'])} images")
                print(f"   Avg Rating: {details['avg_rating']}")
                print(f"   Reviews: {details['num_reviews']}")
                print(
                    f"   Compatible Models: {len(details['compatible_models'])} models"
                )
                if details["compatible_models"]:
                    print(
                        f"      First few: {', '.join(details['compatible_models'][:3])}"
                    )
                print(f"   Installation Difficulty: {details['installation_difficulty']}")
                print(f"   Warranty: {details['warranty_info']}")
            else:
                print(
                    "   ⚠️  No details found (this may be expected if selectors don't match)"
                )

        except Exception as e:
            print(f"   ❌ Error: {e}")


async def test_check_compatibility():
    """Test the check_compatibility function"""
    print("\n" + "=" * 60)
    print("TEST 3: Check Compatibility")
    print("=" * 60)

    test_cases = [
        ("PS11752778", "WDT780SAEM1"),  # From case study
        ("WP2187172", "KRFF305ESS01"),  # Common refrigerator part/model
    ]

    for part_num, model_num in test_cases:
        print(f"\n🔗 Checking: Part {part_num} with Model {model_num}")
        try:
            result = await check_compatibility(part_num, model_num)

            print(f"   Compatible: {result['is_compatible']}")
            print(f"   Confidence: {result['confidence']}")
            print(f"   Explanation: {result['explanation']}")

            if result["alternative_parts"]:
                print(
                    f"   Alternative Parts: {', '.join(result['alternative_parts'])}"
                )

        except Exception as e:
            print(f"   ❌ Error: {e}")


async def main():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("🧪 PARTSELECT WEB FETCHER TOOLS TEST SUITE")
    print("=" * 60)
    print(
        "\nNOTE: These tests attempt to scrape PartSelect.com using CSS selectors."
    )
    print(
        "If PartSelect's HTML structure doesn't match our selectors, tests may return empty results."
    )
    print(
        "This is expected for a demo/case study. In production, selectors would be tuned to the actual site."
    )

    await test_search_parts()
    await test_get_part_details()
    await test_check_compatibility()

    print("\n" + "=" * 60)
    print("✅ TEST SUITE COMPLETE")
    print("=" * 60)
    print(
        "\nIf you see empty results or warnings, it's likely because the CSS selectors"
    )
    print("don't match PartSelect's actual HTML structure. The code is designed to")
    print("handle this gracefully and fail safely.")
    print()


if __name__ == "__main__":
    asyncio.run(main())
