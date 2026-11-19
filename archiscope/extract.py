"""Extract and preserve raw historical climate responses."""
import json
from pathlib import Path
import requests
from config import ARCHIVE_URL, DAILY_VARIABLES, RAW_DIR

def fetch_historical(latitude: float, longitude: float, start_date, end_date, timezone: str):
    params = {
        "latitude": latitude, "longitude": longitude,
        "start_date": start_date.isoformat(), "end_date": end_date.isoformat(),
        "daily": ",".join(DAILY_VARIABLES), "timezone": timezone,
        "temperature_unit": "celsius", "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    response = requests.get(ARCHIVE_URL, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if "daily" not in payload or not payload["daily"].get("time"):
        raise ValueError("The API returned no daily climate records for this selection.")
    return payload

def save_raw(payload: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return path
