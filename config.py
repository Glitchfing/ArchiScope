"""Shared configuration for ArchiScope."""
from pathlib import Path

APP_NAME = "ArchiScope"
ROOT = Path(__file__).resolve().parent
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
DB_PATH = ROOT / "data" / "archiscope.sqlite"

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
TIMEZONE = "Asia/Kolkata"

DAILY_VARIABLES = [
    "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
    "relative_humidity_2m_mean", "precipitation_sum",
    "wind_speed_10m_mean", "wind_speed_10m_max",
    "wind_direction_10m_dominant", "shortwave_radiation_sum",
]

COLUMN_LABELS = {
    "temperature_2m_mean": "mean_temperature_c",
    "temperature_2m_max": "max_temperature_c",
    "temperature_2m_min": "min_temperature_c",
    "relative_humidity_2m_mean": "mean_relative_humidity_pct",
    "precipitation_sum": "precipitation_mm",
    "wind_speed_10m_mean": "mean_wind_speed_kmh",
    "wind_speed_10m_max": "max_wind_speed_kmh",
    "wind_direction_10m_dominant": "dominant_wind_direction_deg",
    "shortwave_radiation_sum": "shortwave_radiation_mj_m2",
}
