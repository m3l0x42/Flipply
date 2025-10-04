import httpx
import base64
import time
from functools import lru_cache
import os 
from dotenv import load_dotenv
load_dotenv()

SANDBOX_API_URL = "https://api.sandbox.ebay.com"

_token_cache = {"token": None, "expires_at": 0}

def get_ebay_token():
    """
    Gets a valid eBay application token, using a cache to avoid re-fetching.
    """
    now = time.time()
    if _token_cache["token"] and _token_cache["expires_at"] > now + 60:
        return _token_cache["token"]

    client_id = os.environ["CLIENT_ID"]
    client_secret = os.environ["CLIENT_SECRET"]
    creds = f"{client_id}:{client_secret}".encode()
    b64_creds = base64.b64encode(creds).decode()
    
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {b64_creds}",
    }
    data = {
        "grant_type": "client_credentials",
        "scope": "https://api.ebay.com/oauth/api_scope",
    }
    
    url = f"{SANDBOX_API_URL}/identity/v1/oauth2/token"
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, data=data)
        response.raise_for_status()
        token_data = response.json()
        
        _token_cache["token"] = token_data["access_token"]
        _token_cache["expires_at"] = now + token_data["expires_in"]
        
        return _token_cache["token"]

async def search_items(query: str, limit: int = 10):
    """
    Searches for items and returns a cleaned-up list.
    """
    token = get_ebay_token()
    url = f"{SANDBOX_API_URL}/buy/browse/v1/item_summary/search"
    headers = {
        "Authorization": f"Bearer {token}",
        "X-EBAY-C-MARKETPLACE-ID": "EBAY_US",
    }
    params = {"q": query, "limit": limit}
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()