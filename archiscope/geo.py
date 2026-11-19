"""Location lookup using the Open-Meteo geocoding API."""
import requests
from config import GEOCODING_URL

def search_location(name: str, count: int = 5) -> list[dict]:
    if not name or not name.strip():
        raise ValueError("Enter a city or place name.")
    response = requests.get(
        GEOCODING_URL,
        params={"name": name.strip(), "count": count, "language": "en", "format": "json"},
        timeout=20,
    )
    response.raise_for_status()
    return response.json().get("results", [])
