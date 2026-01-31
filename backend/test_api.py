"""
Test script to explore PartSelect's API and understand its response format
"""
import asyncio
import httpx
import json

async def test_partselect_api(part_number: str):
    """Test the PartSelect API with a part number"""

    # The API endpoint format provided by the user
    api_url = f"https://www.partselect.com/api/search/?searchterm={part_number}&trackSearchType=combinedsearch&trackSearchLocation=header&siteId=1&autocompleteModelId="

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    print(f"\n{'='*80}")
    print(f"Testing PartSelect API with part number: {part_number}")
    print(f"{'='*80}\n")
    print(f"URL: {api_url}\n")

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(api_url)

            print(f"Status Code: {response.status_code}")
            print(f"Final URL: {response.url}")
            if str(response.url) != api_url:
                print(f"⚠️  Redirected from: {api_url}")
            print(f"Content-Type: {response.headers.get('content-type', 'Unknown')}\n")

            if response.status_code == 200:
                # Check if response is JSON
                content_type = response.headers.get('content-type', '')

                if 'application/json' in content_type:
                    print("✅ Response is JSON")
                    data = response.json()
                    print(f"\nJSON Response Structure:")
                    print(json.dumps(data, indent=2)[:2000])  # First 2000 chars
                    print("\n... (truncated)")

                    # Save full response for inspection
                    with open(f'api_response_{part_number}.json', 'w') as f:
                        json.dump(data, f, indent=2)
                    print(f"\n✅ Full response saved to: api_response_{part_number}.json")

                else:
                    print("⚠️  Response is HTML")
                    print(f"\nFirst 1000 characters of response:")
                    print(response.text[:1000])

                    # Save HTML response
                    with open(f'api_response_{part_number}.html', 'w') as f:
                        f.write(response.text)
                    print(f"\n✅ Full response saved to: api_response_{part_number}.html")
            else:
                print(f"❌ Request failed with status {response.status_code}")
                print(f"Response: {response.text[:500]}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

    print(f"\n{'='*80}")

    # Also test the direct part URL format
    print(f"\nTesting direct part URL format...")
    print(f"{'='*80}\n")

    direct_url = f"https://www.partselect.com/{part_number}"
    print(f"URL: {direct_url}\n")

    try:
        async with httpx.AsyncClient(headers=headers, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(direct_url)
            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                # Check if we got redirected
                if str(response.url) != direct_url:
                    print(f"⚠️  Redirected to: {response.url}")

                print(f"\nFirst 1000 characters of page:")
                print(response.text[:1000])

                # Save for inspection
                with open(f'part_page_{part_number}.html', 'w') as f:
                    f.write(response.text)
                print(f"\n✅ Page saved to: part_page_{part_number}.html")
            else:
                print(f"❌ Request failed with status {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {type(e).__name__} - {e}")

if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print("Usage: python test_api.py <part_number>")
        print("Example: python test_api.py PS11752778")
        sys.exit(1)

    part_number = sys.argv[1]
    asyncio.run(test_partselect_api(part_number))
