"""
Groww API utilities for fetching mutual fund details and stock holdings.
"""
import requests
import uuid
import urllib.parse
import sys
import os
import logging
import re
from typing import Dict, List, Optional

# Add python_scripts to path for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
python_scripts_dir = os.path.dirname(os.path.dirname(script_dir))
if python_scripts_dir not in sys.path:
    sys.path.insert(0, python_scripts_dir)


# Get logger for this module
logger = logging.getLogger(__name__)


def _clean_mf_name_for_search(mf_name: str) -> str:
    """
    Clean mutual fund name for API search query.
    Removes plan keywords and normalizes whitespace.
    
    Args:
        mf_name: Name of the mutual fund
        
    Returns:
        Cleaned search query string
    """
    # 1. Convert to lowercase
    query = mf_name.lower()
    
    # 2. Remove plan/option keywords
    for word in ["direct", "regular", "plan", "dividend", "growth"]:
        query = query.replace(word, "")
    
    # 3. Strip whitespace from start and end
    query = query.strip()
    
    # 4. Replace multiple spaces with a single space
    query = re.sub(r'\s+', ' ', query)
    
    # 5. Add "fund" at the end if not present
    if "fund" not in query:
        query = query + " fund"
    
    return query


def get_mf_search_id_api(mf_name: str) -> Optional[str]:
    """
    Search for a mutual fund via API and return the search_id.
    
    Args:
        mf_name: Name of the mutual fund to search for
        
    Returns:
        search_id if found, None otherwise
    """
    # Clean the query
    cleaned_query = _clean_mf_name_for_search(mf_name)
    encoded_query = urllib.parse.quote(cleaned_query)
    
    logger.info(f"[API METHOD] Sending query to search API | mf_name={mf_name} | query={cleaned_query}")
    
    url = f"https://groww.in/v1/api/search/v3/query/global/st_p_query?page=0&query={encoded_query}&size=6&web=true"
    
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "X-APP-ID": "growwWeb",
        "X-DEVICE-ID": "aebe7f48-c5cc-5d23-9ccb-3d24555484a1",
        "X-REQUEST-ID": str(uuid.uuid4()),
        "x-device-type": "desktop",
        "x-platform": "web"
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract search_id from response by finding exact title match
        if "data" in data and "content" in data["data"]:
            content = data["data"]["content"]
            logger.info(f"[API METHOD] Returned {len(content)} results | mf_name={mf_name}")
            
            # Iterate through results to find exact match
            for item in content:
                title = item.get("title", "")
                if title.lower() == cleaned_query and "search_id" in item:
                    search_id = item["search_id"]
                    logger.info(f"[API METHOD] Found exact match | mf_name={mf_name} | search_id={search_id}")
                    return search_id
        
        logger.warning(
            f"Exact match search_id not found in API response | "
            f"mf_name={mf_name} | "
            f"cleaned_query={cleaned_query} | "
            f"request_url={url} | "
            f"response_status={response.status_code} | "
            f"response_body={data}"
        )
        return None
        
    except requests.RequestException as e:
        logger.warning(
            f"API search failed | "
            f"mf_name={mf_name} | "
            f"error={e}"
        )
        return None


def get_mf_search_id_fallback(mf_name: str, remove_plan: bool = True) -> str:
    """
    Transform mutual fund name to Groww search_id format (fallback method).
    
    Args:
        mf_name: Name of the mutual fund
        remove_plan: Whether to remove "plan" keyword from the name
        
    Returns:
        Transformed search_id string
    """
    # 1. Convert to lowercase
    search_id = mf_name.lower()
    
    # 2. Remove "plan" keyword (optional)
    if remove_plan:
        search_id = search_id.replace("plan", "")
    
    # 3. Strip whitespace from start and end
    search_id = search_id.strip()
    
    # 4. Replace multiple spaces with a single space
    search_id = re.sub(r'\s+', ' ', search_id)
    
    # 5. Replace spaces with "-"
    search_id = search_id.replace(" ", "-")
    
    # 6. Replace special characters with "-"
    search_id = re.sub(r'[^a-z0-9\-]', '-', search_id)
    
    logger.info(f"[FALLBACK METHOD] Generated search_id | mf_name={mf_name} | remove_plan={remove_plan} | search_id={search_id}")
    return search_id


def get_mf_search_id(mf_name: str) -> str:
    """
    Get search_id for a mutual fund. Tries API first, falls back to string transformation.
    
    Args:
        mf_name: Name of the mutual fund
        
    Returns:
        search_id string
    """
    # Try API first
    search_id = get_mf_search_id_api(mf_name)
    if search_id:
        return search_id
    
    # Fallback to string transformation
    logger.info(f"Using fallback search_id for mf_name={mf_name}")
    return get_mf_search_id_fallback(mf_name)


def _fetch_mf_details(search_id: str) -> Optional[Dict]:
    """
    Fetch mutual fund details from API.
    
    Args:
        search_id: The search_id for the API
        
    Returns:
        Dictionary with MF details including holdings, or None if failed
    """
    url = f"https://groww.in/v1/api/data/mf/web/v4/scheme/search/{search_id}"
    
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/142.0.0.0 Safari/537.36",
        "X-APP-ID": "growwWeb",
        "X-DEVICE-ID": "aebe7f48-c5cc-5d23-9ccb-3d24555484a1",
        "X-REQUEST-ID": str(uuid.uuid4()),
        "x-device-type": "desktop",
        "x-platform": "web"
    }
    
    response = None
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        result = response.json()
        logger.info(f"[FETCH] Successfully fetched MF details | search_id={search_id}")
        return result
    except requests.RequestException as e:
        response_status = response.status_code if response is not None else None
        response_body = response.text if response is not None else None
        logger.warning(
            f"Failed to fetch MF details | "
            f"search_id={search_id} | "
            f"request_url={url} | "
            f"response_status={response_status} | "
            f"response_body={response_body} | "
            f"error={e}"
        )
        return None


def get_mf_details(mf_name: str) -> Optional[Dict]:
    """
    Get mutual fund details. Tries API search_id first, falls back to string transformation.
    
    Args:
        mf_name: Name of the mutual fund
        
    Returns:
        Dictionary with MF details including holdings, or None if all methods fail
    """
    logger.info(f"[START] Getting MF details | mf_name={mf_name}")
    
    # Step 1: Try with API search_id first
    logger.info(f"[STEP 1] Trying API method first | mf_name={mf_name}")
    api_search_id = get_mf_search_id_api(mf_name)
    if api_search_id:
        logger.info(f"[STEP 1] API search_id found | mf_name={mf_name} | api_search_id={api_search_id}")
        result = _fetch_mf_details(api_search_id)
        if result:
            logger.info(f"[SUCCESS] Got MF details via API method | mf_name={mf_name}")
            return result
        logger.info(f"[STEP 1] API method failed to fetch details, will try fallback | mf_name={mf_name}")
    else:
        logger.info(f"[STEP 1] API method did not find search_id, will try fallback | mf_name={mf_name}")
    
    # Step 2: Fallback with "plan" removed
    logger.info(f"[STEP 2] Trying fallback method (with plan removed) | mf_name={mf_name}")
    fallback_search_id = get_mf_search_id_fallback(mf_name, remove_plan=True)
    
    result = _fetch_mf_details(fallback_search_id)
    if result:
        logger.info(f"[SUCCESS] Got MF details via fallback method (plan removed) | mf_name={mf_name}")
        return result
    
    # Step 3: Fallback without removing "plan"
    logger.info(f"[STEP 3] Trying fallback method (with plan kept) | mf_name={mf_name}")
    fallback_search_id_with_plan = get_mf_search_id_fallback(mf_name, remove_plan=False)
    
    result = _fetch_mf_details(fallback_search_id_with_plan)
    if result:
        logger.info(f"[SUCCESS] Got MF details via fallback method (plan kept) | mf_name={mf_name}")
        return result
    
    # All methods failed - log error and return None to continue with next MF
    logger.error(f"[FAILED] All methods failed (API, fallback with plan removed, fallback with plan kept) | mf_name={mf_name}")
    return None


def get_mf_stock_holdings(mf_name: str) -> List[Dict]:
    """
    Get stock holdings for a mutual fund.
    
    Args:
        mf_name: Name of the mutual fund
        
    Returns:
        List of dictionaries with stock holding information (empty list if failed)
    """
    logger.info(f"[START] Getting stock holdings | mf_name={mf_name}")
    
    # Get the MF details (handles API + fallback internally)
    mf_details = get_mf_details(mf_name)
    
    # If all methods failed, return empty list
    if mf_details is None:
        logger.warning(f"[END] Skipping MF due to fetch failure | mf_name={mf_name}")
        return []
    
    # Extract holdings from the response
    holdings = []
    if "holdings" in mf_details:
        holdings = mf_details["holdings"]
    elif "data" in mf_details and "holdings" in mf_details["data"]:
        holdings = mf_details["data"]["holdings"]
    
    logger.info(f"[END] Found {len(holdings)} stock holdings | mf_name={mf_name}")
    return holdings

