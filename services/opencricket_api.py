import os

import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://opencricketapi.com/v1"


def _get_data(endpoint, params=None):
    api_key = os.getenv("OPENCRICKET_API_KEY")

    if not api_key:
        raise ValueError("OPENCRICKET_API_KEY is missing from your .env file.")

    response = requests.get(
        f"{BASE_URL}/{endpoint}",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Accept": "application/json",
        },
        params=params,
        timeout=20,
    )
    response.raise_for_status()

    result = response.json()

    if "error" in result:
        raise ValueError(result["error"].get("message", "API request failed"))

    return result.get("data", [])


def get_live_matches():
    return _get_data("live")


def get_recent_matches(limit=3):
    return _get_data("matches", params={"limit": limit})