"""
Debug script to test part number fetching and identify issues
Usage: python debug_part.py <part_number>
"""
import asyncio
import sys
import logging
from app.web_fetcher import get_part_details, get_installation_guide

# Set up detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def debug_part(part_number: str):
    """Debug a specific part number to see what's happening"""
    print(f"\n{'='*80}")
    print(f"DEBUGGING PART NUMBER: {part_number}")
    print(f"{'='*80}\n")

    # Test 1: Get Part Details
    print("TEST 1: Fetching Part Details")
    print("-" * 80)
    details = await get_part_details(part_number)

    if details:
        print("✅ SUCCESS: Part details retrieved")
        print(f"\nPart Number: {details['part_number']}")
        print(f"Full Name: {details['full_name']}")
        print(f"Price: ${details['price']}")
        print(f"Manufacturer: {details['manufacturer']}")
        print(f"In Stock: {details['in_stock']}")
        print(f"Description: {details['description'][:100]}..." if details['description'] else "No description")
        print(f"Compatible Models Count: {len(details['compatible_models'])}")
        if details['compatible_models']:
            print(f"First 5 compatible models: {details['compatible_models'][:5]}")
        print(f"URL: {details['part_select_url']}")
    else:
        print("❌ FAILED: Could not retrieve part details")
        print("Check the logs above for HTTP status codes and error messages")

    # Test 2: Get Installation Guide
    print(f"\n{'='*80}")
    print("TEST 2: Fetching Installation Guide")
    print("-" * 80)
    guide = await get_installation_guide(part_number)

    if guide:
        print("✅ Installation guide retrieved")
        print(f"\nPart Number: {guide['part_number']}")
        print(f"Difficulty: {guide['difficulty']}")
        print(f"Estimated Time: {guide['estimated_time_minutes']} minutes")
        print(f"Tools Required: {guide['tools_required']}")
        print(f"Number of Steps: {len(guide['steps'])}")
        print("\nSteps:")
        for step in guide['steps']:
            warning = f" [⚠️  {step['warning']}]" if step['warning'] else ""
            print(f"  {step['step_number']}. {step['instruction']}{warning}")
        print(f"\nVideo URL: {guide['video_url'] or 'None'}")
        print(f"PDF URL: {guide['pdf_url'] or 'None'}")
    else:
        print("❌ FAILED: Could not retrieve installation guide")

    print(f"\n{'='*80}")
    print("DEBUG COMPLETE")
    print(f"{'='*80}\n")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python debug_part.py <part_number>")
        print("Example: python debug_part.py PS11752778")
        sys.exit(1)

    part_number = sys.argv[1]
    asyncio.run(debug_part(part_number))
