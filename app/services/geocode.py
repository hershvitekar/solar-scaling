import os
import requests
from typing import Tuple, Optional
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_coordinates(address: str) -> Tuple[Optional[float], Optional[float]]:
    """
    Convert a free-text address to latitude and longitude using Google Maps Geocoding API.
    """
    if not GOOGLE_MAPS_API_KEY:
        # Fallback coordinates for Chhatrapati Sambhajinagar if API key is missing
        # This is for demo/testing purposes when API key isn't provided yet
        return 19.8762, 75.3433 

    # Ensure the search is focused on the target city
    search_query = address
    if "chhatrapati sambhajinagar" not in address.lower() and "aurangabad" not in address.lower():
        search_query += ", Chhatrapati Sambhajinagar, Maharashtra, India"

    url = "https://maps.googleapis.com/maps/api/geocode/json"
    params = {
        "address": search_query,
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=5)
        response.raise_for_status()
        data = response.json()

        if data["status"] == "OK":
            location = data["results"][0]["geometry"]["location"]
            return location["lat"], location["lng"]
        else:
            print(f"Geocoding error: {data['status']}")
            return None, None
    except Exception as e:
        print(f"Geocoding API request failed: {e}")
        return None, None
