import os
import requests
from typing import Optional
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv

load_dotenv()

GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def fetch_satellite_image(lat: float, lng: float) -> Optional[Image.Image]:
    """
    Fetch a 400x400 satellite image for a given location using Google Static Maps API.
    """
    if not GOOGLE_MAPS_API_KEY:
        return None

    url = "https://maps.googleapis.com/maps/api/staticmap"
    params = {
        "center": f"{lat},{lng}",
        "zoom": 20,
        "size": "400x400",
        "maptype": "satellite",
        "key": GOOGLE_MAPS_API_KEY
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        
        # Check if we got an actual image (not an error image)
        if "image" not in response.headers.get("Content-Type", ""):
            return None
            
        return Image.open(BytesIO(response.content))
    except Exception as e:
        print(f"Error fetching satellite image: {e}")
        return None
