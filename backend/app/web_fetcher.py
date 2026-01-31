import httpx
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

BASE_URL = "https://www.partselect.com"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


async def fetch_page(url: str) -> BeautifulSoup | None:
    """Fetch and parse a webpage"""
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
            logger.info(f"Fetching URL: {url}")
            response = await client.get(url)
            logger.info(f"Response status: {response.status_code} for URL: {url}")

            if response.status_code == 404:
                logger.error(f"404 Not Found: {url} - The part may not exist or URL format is incorrect")
                return None

            response.raise_for_status()

            # Log a snippet of the response to verify we got HTML
            content_preview = response.text[:500] if response.text else "EMPTY"
            logger.debug(f"Response preview (first 500 chars): {content_preview}")

            return BeautifulSoup(response.text, "html.parser")
    except httpx.HTTPStatusError as e:
        logger.error(f"HTTP error fetching {url}: Status {e.response.status_code}")
        return None
    except httpx.TimeoutException:
        logger.error(f"Timeout fetching {url}")
        return None
    except Exception as e:
        logger.error(f"Error fetching {url}: {type(e).__name__} - {e}")
        return None


async def search_parts(query: str, limit: int = 10) -> list[dict]:
    """Search PartSelect for parts matching the query

    Uses the PartSelect search API which redirects to results.
    Falls back gracefully if elements are not found.

    IMPORTANT: When searching for a specific part number (e.g., PS11752778),
    PartSelect redirects directly to the product detail page. This function
    detects this case and extracts the single product from the detail page.
    """
    import urllib.parse

    # URL encode the query to handle special characters
    encoded_query = urllib.parse.quote(query)

    # Use the API search endpoint (it will redirect to the appropriate page)
    search_url = f"{BASE_URL}/api/search/?searchterm={encoded_query}&trackSearchType=combinedsearch&trackSearchLocation=header&siteId=1&autocompleteModelId="

    logger.info(f"Searching PartSelect for: {query} (limit: {limit})")

    # Use httpx directly to track redirects and get final URL
    final_url = ""
    try:
        async with httpx.AsyncClient(headers=HEADERS, timeout=10.0, follow_redirects=True) as client:
            response = await client.get(search_url)
            final_url = str(response.url)
            logger.info(f"Search URL redirected to: {final_url}")

            if response.status_code != 200:
                logger.warning(f"Non-200 status code: {response.status_code}")
                return []

            soup = BeautifulSoup(response.text, "html.parser")
    except Exception as e:
        logger.error(f"Error fetching search page: {e}")
        return []

    if not soup:
        logger.warning(f"Failed to fetch search page for query: {query}")
        return []

    parts = []

    # Check if we were redirected to a product detail page
    # This happens when searching for a specific part number (e.g., PS11752778)
    main_elem = soup.select_one("[data-page-type='PartDetail']")
    if main_elem or (".htm" in final_url and "-" in final_url):
        logger.info("Detected redirect to product detail page - extracting single product")

        # Extract product data from the detail page's data attributes
        data_elem = soup.select_one("[data-price][data-brand][data-inventory-id]")
        if data_elem:
            try:
                # Extract data from attributes
                price_str = data_elem.get("data-price", "0")
                try:
                    price = float(price_str)
                except ValueError:
                    price = 0.0

                manufacturer = data_elem.get("data-brand", "Unknown")
                availability = data_elem.get("data-availability", "").lower()
                in_stock = availability == "instock"
                inventory_id = data_elem.get("data-inventory-id", "")

                # Extract part number from inventory ID
                part_number = f"PS{inventory_id}" if inventory_id else query

                # Extract full name from page title
                title_tag = soup.find("title")
                full_name = "Unknown Part"
                if title_tag:
                    full_name = title_tag.text.replace("– PartSelect.com", "").replace("Official", "").strip()

                # Extract image
                image_url = ""
                img_elem = soup.select_one("img[itemprop='image'], .pd__img img, .main-image img")
                if img_elem:
                    image_url = img_elem.get("src", "") or img_elem.get("data-src", "")
                    if image_url and not image_url.startswith("http"):
                        image_url = f"{BASE_URL}{image_url}" if image_url.startswith("/") else f"{BASE_URL}/{image_url}"

                # Get canonical URL
                canonical = soup.find("link", rel="canonical")
                part_url = final_url
                if canonical and canonical.get("href"):
                    part_url = canonical.get("href")

                logger.info(f"Extracted product from detail page: {part_number} - {full_name} - ${price}")

                return [{
                    "part_number": part_number,
                    "name": full_name,
                    "price": price,
                    "image_url": image_url,
                    "manufacturer": manufacturer,
                    "in_stock": in_stock,
                    "part_select_url": part_url,
                }]
            except Exception as e:
                logger.error(f"Error extracting product from detail page: {e}", exc_info=True)
        else:
            logger.warning("On detail page but couldn't find data attributes")

    # If not a product detail page, try search results selectors
    # Try multiple selector strategies for different PartSelect layouts
    selector_strategies = [
        ".ps-part-item",
        ".part-item",
        ".product-item",
        ".search-result-item",
        "[data-part]",
        "div.pd__wrapper",  # Common PartSelect layout
        ".mega-m__part",    # Another common layout
        ".nf__part",        # "Not found" fallback parts
    ]

    items = []
    for selector in selector_strategies:
        items = soup.select(selector)
        if items:
            logger.info(f"Found {len(items)} items using selector: {selector}")
            break

    if not items:
        logger.warning(f"No parts found for query: {query}")
        return []

    for item in items[:limit]:
        try:
            # Extract part number with multiple strategies
            part_number = "N/A"
            for selector in [".part-number", "[data-part-number]", ".pd__number", ".megasku"]:
                elem = item.select_one(selector)
                if elem:
                    part_number = elem.text.strip()
                    break

            # Extract name
            name = "Unknown Part"
            for selector in [".part-name", "h2", "h3", ".pd__title", ".part-title"]:
                elem = item.select_one(selector)
                if elem:
                    name = elem.text.strip()
                    break

            # Extract price with robust parsing
            price = 0.0
            for selector in [".price", "[data-price]", ".pd__price", ".part-price"]:
                elem = item.select_one(selector)
                if elem:
                    price_str = elem.text.strip()
                    # Remove currency symbols and commas
                    price_str = price_str.replace("$", "").replace(",", "").replace("USD", "").strip()
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        continue

            # Extract image URL
            image_url = ""
            image = item.select_one("img")
            if image:
                # Try src, data-src, data-lazy-src
                image_url = (
                    image.get("src", "")
                    or image.get("data-src", "")
                    or image.get("data-lazy-src", "")
                )
                # Make absolute URL if relative
                if image_url and not image_url.startswith("http"):
                    image_url = f"{BASE_URL}{image_url}" if image_url.startswith("/") else f"{BASE_URL}/{image_url}"

            # Extract manufacturer
            manufacturer = "Unknown"
            for selector in [".manufacturer", ".brand", ".pd__brand", ".part-manufacturer"]:
                elem = item.select_one(selector)
                if elem:
                    manufacturer = elem.text.strip()
                    break

            # Check stock status
            in_stock = "in stock" in item.text.lower() or "available" in item.text.lower()

            # Extract part URL
            part_url = BASE_URL
            href = item.select_one("a")
            if href and href.get("href"):
                href_val = href.get("href", "")
                if href_val.startswith("http"):
                    part_url = href_val
                elif href_val.startswith("/"):
                    part_url = f"{BASE_URL}{href_val}"
                else:
                    part_url = f"{BASE_URL}/{href_val}"

            # Only add parts that have at least a part number or name
            if part_number != "N/A" or name != "Unknown Part":
                parts.append(
                    {
                        "part_number": part_number,
                        "name": name,
                        "price": price,
                        "image_url": image_url,
                        "manufacturer": manufacturer,
                        "in_stock": in_stock,
                        "part_select_url": part_url,
                    }
                )
        except Exception as e:
            logger.error(f"Error parsing part item: {e}", exc_info=True)
            continue

    logger.info(f"Successfully parsed {len(parts)} parts from search results")
    return parts


async def get_part_details(part_number: str) -> dict | None:
    """Get detailed information for a specific part

    Extracts comprehensive part information including specs, images, compatibility,
    and reviews from the part detail page.

    PartSelect uses the API search endpoint which redirects to the actual part page.
    """
    import urllib.parse

    # Use the search API to find the part (it will redirect to the part page)
    encoded_query = urllib.parse.quote(part_number)
    search_url = f"{BASE_URL}/api/search/?searchterm={encoded_query}&trackSearchType=combinedsearch&trackSearchLocation=header&siteId=1&autocompleteModelId="

    logger.info(f"Fetching details for part: {part_number} using search API")

    soup = await fetch_page(search_url)
    if not soup:
        logger.error(f"Failed to fetch part details page for: {part_number}")
        logger.error(f"This could mean: 1) Network error, 2) Part doesn't exist, 3) Search returned no results")
        return None

    try:
        # Extract title from page title or h1
        full_name = "Unknown Part"
        title_tag = soup.find("title")
        if title_tag:
            # Title format: "Official Whirlpool WPW10321304 Refrigerator Door Shelf Bin – PartSelect.com"
            full_name = title_tag.text.replace("– PartSelect.com", "").replace("Official", "").strip()

        if full_name == "Unknown Part":
            h1 = soup.find("h1")
            if h1:
                full_name = h1.text.strip()

        # Check if we're on a search results page instead of a part page
        # This happens when an invalid part number is entered
        if "search" in full_name.lower() or "suggested" in full_name.lower() or "results" in full_name.lower():
            logger.warning(f"Part {part_number} not found - redirected to search results page")
            return None

        # Additional check: if there's no price data attribute, it's not a valid part page
        if not soup.select_one("[data-price]"):
            logger.warning(f"Part {part_number} not found - no price data on page")
            return None

        # Extract description
        description = ""
        for selector in [
            ".description",
            ".product-description",
            ".pd__desc",
            "[itemprop='description']",
        ]:
            desc_elem = soup.select_one(selector)
            if desc_elem:
                description = desc_elem.text.strip()
                break

        # Extract price from data-price attribute (more reliable)
        price = 0.0
        price_elem = soup.select_one("[data-price]")
        if price_elem:
            price_str = price_elem.get("data-price", "0")
            try:
                price = float(price_str)
                logger.info(f"Extracted price: ${price}")
            except ValueError:
                logger.warning(f"Failed to parse price: {price_str}")

        # Fallback to text-based price extraction
        if price == 0.0:
            for selector in [".price", ".pd__price", ".product-price"]:
                price_elem = soup.select_one(selector)
                if price_elem:
                    price_str = price_elem.text.strip()
                    price_str = price_str.replace("$", "").replace(",", "").replace("USD", "").strip()
                    try:
                        price = float(price_str)
                        break
                    except ValueError:
                        continue

        # Extract images - try multiple selectors
        image_urls = []
        for img in soup.select(
            ".product-image img, .pd__img img, .part-image img, [itemprop='image']"
        ):
            src = img.get("src", "") or img.get("data-src", "")
            if src and src not in image_urls:
                # Make absolute URL
                if not src.startswith("http"):
                    src = f"{BASE_URL}{src}" if src.startswith("/") else f"{BASE_URL}/{src}"
                image_urls.append(src)

        # If no images found, add a placeholder
        if not image_urls:
            image_urls.append("")

        # Extract manufacturer from data-brand attribute or page content
        manufacturer = "Unknown"
        brand_elem = soup.select_one("[data-brand]")
        if brand_elem:
            manufacturer = brand_elem.get("data-brand", "Unknown")
            logger.info(f"Extracted manufacturer: {manufacturer}")

        # Fallback to text-based manufacturer extraction
        if manufacturer == "Unknown":
            for selector in [".manufacturer", ".brand", ".pd__brand", "[itemprop='brand']"]:
                mfr_elem = soup.select_one(selector)
                if mfr_elem:
                    manufacturer = mfr_elem.text.strip()
                    break

        # Check stock status from data-availability attribute
        in_stock = False
        availability_elem = soup.select_one("[data-availability]")
        if availability_elem:
            availability = availability_elem.get("data-availability", "").lower()
            in_stock = availability == "instock"
            logger.info(f"Stock status: {availability}")

        # Fallback to text-based stock check
        if not in_stock:
            in_stock = (
                "in stock" in soup.text.lower()
                or "available" in soup.text.lower()
                or "ships" in soup.text.lower()
            )

        # Extract rating
        avg_rating = None
        for selector in [".rating", "[data-rating]", "[itemprop='ratingValue']"]:
            rating_elem = soup.select_one(selector)
            if rating_elem:
                try:
                    rating_text = rating_elem.text.strip()
                    # Extract just the number (e.g., "4.5 stars" -> 4.5)
                    import re

                    match = re.search(r"(\d+\.?\d*)", rating_text)
                    if match:
                        avg_rating = float(match.group(1))
                        break
                except ValueError:
                    continue

        # Extract number of reviews
        num_reviews = 0
        for selector in [
            ".review-count",
            ".num-reviews",
            "[itemprop='reviewCount']",
        ]:
            review_elem = soup.select_one(selector)
            if review_elem:
                try:
                    import re

                    match = re.search(r"(\d+)", review_elem.text)
                    if match:
                        num_reviews = int(match.group(1))
                        break
                except ValueError:
                    continue

        # Extract compatible models
        compatible_models = []
        for selector in [
            ".compatible-models",
            ".model-list",
            ".fits-models",
            "[data-models]",
        ]:
            models_section = soup.select_one(selector)
            if models_section:
                # Try to find individual model elements
                for model_elem in models_section.select(".model, .model-number, li, a"):
                    model_text = model_elem.text.strip()
                    if model_text and len(model_text) > 3:  # Filter out noise
                        compatible_models.append(model_text)

        # Determine installation difficulty based on keywords
        difficulty = "moderate"
        page_text = soup.text.lower()
        if any(word in page_text for word in ["easy", "simple", "basic"]):
            difficulty = "easy"
        elif any(
            word in page_text
            for word in ["difficult", "complex", "professional", "expert"]
        ):
            difficulty = "difficult"

        # Extract warranty info
        warranty_info = "Standard warranty"
        for selector in [".warranty", ".warranty-info", "[data-warranty]"]:
            warranty_elem = soup.select_one(selector)
            if warranty_elem:
                warranty_info = warranty_elem.text.strip()
                break

        # Extract the canonical URL from the page
        part_url = f"{BASE_URL}/{part_number}"
        canonical = soup.find("link", rel="canonical")
        if canonical and canonical.get("href"):
            part_url = canonical.get("href")
            if not part_url.startswith("http"):
                part_url = f"{BASE_URL}{part_url}" if part_url.startswith("/") else f"{BASE_URL}/{part_url}"

        logger.info(f"Successfully extracted details for part: {part_number}, URL: {part_url}")

        return {
            "part_number": part_number,
            "full_name": full_name,
            "description": description,
            "price": price,
            "image_urls": image_urls,
            "manufacturer": manufacturer,
            "in_stock": in_stock,
            "avg_rating": avg_rating,
            "num_reviews": num_reviews,
            "compatible_models": compatible_models,
            "installation_difficulty": difficulty,
            "warranty_info": warranty_info,
            "part_select_url": part_url,
        }
    except Exception as e:
        logger.error(f"Error extracting part details for {part_number}: {e}", exc_info=True)
        return None


async def check_compatibility(part_number: str, model_number: str) -> dict:
    """Check if a part is compatible with a model

    Uses multiple strategies to determine compatibility:
    1. Check if model is in the part's compatible models list
    2. Fuzzy matching for model number variations
    3. Search for the model to find alternative parts
    """
    logger.info(f"Checking compatibility: part {part_number} with model {model_number}")

    part_details = await get_part_details(part_number)

    if not part_details:
        logger.warning(f"Part {part_number} not found, cannot check compatibility")
        return {
            "is_compatible": False,
            "confidence": "unlikely",
            "explanation": f"Unable to find part {part_number}. Please verify the part number is correct.",
            "alternative_parts": [],
        }

    compatible_models = part_details.get("compatible_models", [])

    # Strategy 1: Direct match
    is_compatible = model_number.upper() in [m.upper() for m in compatible_models]

    if is_compatible:
        logger.info(f"Direct compatibility match found for {model_number}")
        return {
            "is_compatible": True,
            "confidence": "confirmed",
            "explanation": f"Part {part_number} is confirmed compatible with model {model_number}.",
            "alternative_parts": [],
        }

    # Strategy 2: Fuzzy matching - check for partial matches
    # Model numbers often have variations (e.g., WDT780SAEM1 vs WDT780SAEM)
    model_base = model_number.upper().rstrip("0123456789")  # Remove trailing numbers
    fuzzy_match = False

    for compatible_model in compatible_models:
        compatible_base = compatible_model.upper().rstrip("0123456789")
        if (
            model_base in compatible_model.upper()
            or compatible_base in model_number.upper()
        ):
            fuzzy_match = True
            logger.info(
                f"Fuzzy match found: {model_number} matches {compatible_model}"
            )
            return {
                "is_compatible": True,
                "confidence": "likely",
                "explanation": f"Part {part_number} is likely compatible with model {model_number}. "
                f"It fits similar model {compatible_model}. Please verify before purchasing.",
                "alternative_parts": [],
            }

    # Strategy 3: No match found - search for alternative parts for this model
    logger.info(
        f"No compatibility found. Searching for alternative parts for model {model_number}"
    )

    alternative_parts = []
    try:
        # Search for parts that fit this model
        alt_search_results = await search_parts(model_number, limit=3)
        alternative_parts = [p["part_number"] for p in alt_search_results]
    except Exception as e:
        logger.error(f"Error searching for alternative parts: {e}")

    explanation = f"Part {part_number} does not appear to be compatible with model {model_number}."
    if compatible_models:
        explanation += f" This part fits models: {', '.join(compatible_models[:5])}"
        if len(compatible_models) > 5:
            explanation += f" and {len(compatible_models) - 5} others"
    else:
        explanation += " Compatible models information is not available."

    if alternative_parts:
        explanation += f" We found {len(alternative_parts)} alternative parts that may fit your model."

    return {
        "is_compatible": False,
        "confidence": "unlikely",
        "explanation": explanation,
        "alternative_parts": alternative_parts,
    }


async def get_installation_guide(part_number: str) -> dict | None:
    """Get installation instructions for a part

    Scrapes the part detail page to extract:
    - Installation difficulty
    - YouTube video IDs for installation guides
    - PDF manuals if available
    - Repair difficulty rating
    """
    import urllib.parse
    import re

    # Use the search API to find the part (it will redirect to the part page)
    encoded_query = urllib.parse.quote(part_number)
    search_url = f"{BASE_URL}/api/search/?searchterm={encoded_query}&trackSearchType=combinedsearch&trackSearchLocation=header&siteId=1&autocompleteModelId="

    logger.info(f"Fetching installation guide for part: {part_number}")

    soup = await fetch_page(search_url)
    if not soup:
        logger.error(f"Failed to fetch installation guide page for: {part_number}")
        return None

    try:
        # Check if we're on a valid part page
        title_tag = soup.find("title")
        if title_tag:
            title_text = title_tag.text.lower()
            if "search" in title_text or "suggested" in title_text or "results" in title_text:
                logger.warning(f"Part {part_number} not found - cannot get installation guide")
                return None

        # Additional check: if there's no price data, it's not a valid part page
        if not soup.select_one("[data-price]"):
            logger.warning(f"Part {part_number} not found - cannot get installation guide")
            return None

        # Extract YouTube video IDs from data-yt-init attributes
        video_elements = soup.find_all(attrs={"data-yt-init": True})
        video_ids = []
        for elem in video_elements:
            video_id = elem.get("data-yt-init")
            if video_id and video_id not in video_ids:
                video_ids.append(video_id)

        logger.info(f"Found {len(video_ids)} installation videos: {video_ids}")

        # Primary video URL (first one found)
        video_url = f"https://www.youtube.com/watch?v={video_ids[0]}" if video_ids else None

        # Determine difficulty from repair rating or page text
        difficulty = "moderate"
        page_text = soup.text.lower()

        # Look for difficulty indicators
        if "easy install" in page_text or "simple replacement" in page_text:
            difficulty = "easy"
        elif "difficult" in page_text or "professional" in page_text or "complex" in page_text:
            difficulty = "difficult"

        # Check for repair difficulty data
        repair_rating_elem = soup.select_one("[data-easy-flag]")
        if repair_rating_elem:
            difficulty = "easy"

        # Estimate time based on difficulty
        time_estimates = {
            "easy": 15,
            "moderate": 30,
            "difficult": 60
        }
        estimated_time = time_estimates.get(difficulty, 30)

        # Create generic installation steps
        # Note: Detailed step-by-step instructions are typically in the YouTube videos
        # The website doesn't have structured step data we can reliably scrape
        steps = []

        # Skip pattern matching as it picks up Q&A and review content
        # Just provide generic steps and rely on videos for detailed instructions
        if True:  # Always use generic steps
            steps = [
                {
                    "step_number": 1,
                    "instruction": "Unplug the appliance and ensure it is safe to work on",
                    "image_url": None,
                    "warning": "Safety critical - ensure power is disconnected",
                },
                {
                    "step_number": 2,
                    "instruction": "Remove the old part following the reverse of the installation process",
                    "image_url": None,
                    "warning": None,
                },
                {
                    "step_number": 3,
                    "instruction": "Install the new part in the correct position",
                    "image_url": None,
                    "warning": None,
                },
                {
                    "step_number": 4,
                    "instruction": "Reconnect power and test the appliance",
                    "image_url": None,
                    "warning": None,
                },
            ]

        # Look for PDF manuals
        pdf_url = None
        pdf_links = soup.find_all("a", href=re.compile(r"\.pdf$", re.IGNORECASE))
        if pdf_links:
            pdf_url = pdf_links[0].get("href")
            if pdf_url and not pdf_url.startswith("http"):
                pdf_url = f"{BASE_URL}{pdf_url}" if pdf_url.startswith("/") else f"{BASE_URL}/{pdf_url}"

        # Determine tools required based on part type and page content
        tools_required = ["Screwdriver"]
        if "pliers" in page_text:
            tools_required.append("Pliers")
        if "wrench" in page_text or "socket" in page_text:
            tools_required.append("Wrench")
        if "drill" in page_text:
            tools_required.append("Drill")

        logger.info(f"Installation guide for {part_number}: difficulty={difficulty}, videos={len(video_ids)}, steps={len(steps)}")

        return {
            "part_number": part_number,
            "difficulty": difficulty,
            "estimated_time_minutes": estimated_time,
            "tools_required": tools_required,
            "steps": steps,
            "video_url": video_url,
            "pdf_url": pdf_url,
        }

    except Exception as e:
        logger.error(f"Error extracting installation guide for {part_number}: {e}", exc_info=True)
        return None


async def diagnose_issue(
    appliance_type: str, brand: str, symptom: str
) -> dict:
    """Diagnose appliance issues and suggest parts"""
    # Map of common symptoms to likely causes and parts
    symptom_map = {
        "ice maker not working": {
            "likely_causes": ["Water line blocked", "Ice maker assembly failure", "Freezer temperature too warm"],
            "parts": ["ice maker assembly", "water line", "water filter"],
        },
        "not cooling": {
            "likely_causes": ["Compressor issue", "Refrigerant leak", "Condenser fan broken"],
            "parts": ["compressor", "condenser fan", "start relay"],
        },
        "water leak": {
            "likely_causes": ["Drain line clogged", "Water supply line damaged"],
            "parts": ["drain line", "water line", "water pump"],
        },
    }

    # Find matching symptoms
    matching = symptom_map.get(symptom.lower(), {})
    likely_causes = matching.get("likely_causes", ["Unknown cause"])
    search_terms = matching.get("parts", [symptom])

    # Search for recommended parts
    recommended_parts = []
    for term in search_terms[:2]:  # Limit to 2 searches
        parts = await search_parts(term, limit=2)
        recommended_parts.extend(parts[:1])  # Take 1 part from each search

    return {
        "likely_causes": likely_causes,
        "recommended_parts": recommended_parts,
        "diy_difficulty": "moderate",
        "troubleshooting_steps": [
            "Check that the appliance is plugged in and powered on",
            "Check for any visible damage or loose connections",
            "Try a full power cycle (unplug for 5 minutes, plug back in)",
            "If problem persists, consider replacement parts above",
        ],
    }


async def search_by_model(model_number: str) -> dict:
    """Find all parts compatible with a specific model

    Scrapes the PartSelect model page to extract parts.
    Parts are displayed using .mega-m__part class on modern PartSelect pages.
    """
    import re

    # Search for the model on PartSelect
    search_url = f"{BASE_URL}/Models/{model_number}/"
    logger.info(f"Searching for parts by model: {model_number}")

    soup = await fetch_page(search_url)
    if not soup:
        logger.warning(f"Failed to fetch model page for: {model_number}")
        return {
            "model_number": model_number,
            "appliance_info": "Model not found",
            "common_parts": [],
            "all_parts_count": 0,
            "parts_by_category": {},
        }

    # Extract appliance info from page title
    appliance_info = f"Parts for model {model_number}"
    title_tag = soup.find("title")
    if title_tag:
        appliance_info = title_tag.text.replace("- OEM Parts & Repair Help - PartSelect.com", "").strip()

    all_parts = []

    # Modern PartSelect uses .mega-m__part for part items
    part_items = soup.select(".mega-m__part")
    logger.info(f"Found {len(part_items)} parts for model {model_number}")

    for part_item in part_items:
        try:
            # Extract link to get part number and URL
            link = part_item.select_one("a[href*='PS'], a[href*='.htm']")
            if not link:
                continue

            href = link.get("href", "")

            # Extract part number from URL (format: /PS{number}-Brand-...)
            part_number = "N/A"
            ps_match = re.search(r"/(PS\d+)-", href)
            if ps_match:
                part_number = ps_match.group(1)

            # Build full URL
            part_url = href
            if href.startswith("/"):
                part_url = f"{BASE_URL}{href}"

            # Extract name from .mega-m__part__name
            name_elem = part_item.select_one(".mega-m__part__name")
            name = name_elem.text.strip() if name_elem else "Unknown Part"

            # Extract price from .mega-m__part__price
            price = 0.0
            price_elem = part_item.select_one(".mega-m__part__price")
            if price_elem:
                price_text = price_elem.text.strip()
                price_match = re.search(r"\$?([\d,]+\.?\d*)", price_text)
                if price_match:
                    try:
                        price = float(price_match.group(1).replace(",", ""))
                    except ValueError:
                        pass

            # Extract image URL (uses lazy loading)
            image_url = ""
            img_elem = part_item.select_one("img")
            if img_elem:
                image_url = img_elem.get("data-src", "") or img_elem.get("src", "")
                # Skip base64 placeholders
                if image_url.startswith("data:"):
                    image_url = img_elem.get("data-src", "")
                if image_url and not image_url.startswith("http"):
                    image_url = f"{BASE_URL}{image_url}" if image_url.startswith("/") else f"https:{image_url}"

            # Only add if we have meaningful data
            if part_number != "N/A" or name != "Unknown Part":
                all_parts.append({
                    "part_number": part_number,
                    "name": name,
                    "price": price,
                    "image_url": image_url,
                    "manufacturer": "",  # Not easily available on this page
                    "in_stock": True,  # Assume in stock since it's shown
                    "part_select_url": part_url,
                })
        except Exception as e:
            logger.error(f"Error parsing part from model page: {e}", exc_info=True)
            continue

    logger.info(f"Successfully extracted {len(all_parts)} parts for model {model_number}")

    return {
        "model_number": model_number,
        "appliance_info": appliance_info,
        "common_parts": all_parts[:10],  # Top 10 common parts
        "all_parts_count": len(all_parts),
        "parts_by_category": {},  # Categories not available on this page layout
    }
