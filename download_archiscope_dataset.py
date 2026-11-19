"""Download a real starter climate dataset for Mumbai, India (calendar year 2025).

Run: pip install requests pandas && python download_archiscope_dataset.py
Creates raw JSON and daily/monthly CSV files under data/.
"""
from pathlib import Path
import json
import requests
import pandas as pd

LATITUDE, LONGITUDE = 19.0760, 72.8777
START_DATE, END_DATE = "2025-01-01", "2025-12-31"
TIMEZONE = "Asia/Kolkata"
VARIABLES = [
    "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
    "relative_humidity_2m_mean", "precipitation_sum", "wind_speed_10m_mean",
    "wind_speed_10m_max", "wind_direction_10m_dominant", "shortwave_radiation_sum",
]
URL = "https://archive-api.open-meteo.com/v1/archive"
ROOT = Path(__file__).resolve().parent

def main():
    params = {
        "latitude": LATITUDE, "longitude": LONGITUDE,
        "start_date": START_DATE, "end_date": END_DATE,
        "daily": ",".join(VARIABLES), "timezone": TIMEZONE,
        "temperature_unit": "celsius", "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
    }
    response = requests.get(URL, params=params, timeout=60)
    response.raise_for_status()
    payload = response.json()
    if payload.get("error"):
        raise RuntimeError(payload.get("reason", "Open-Meteo API error"))
    (ROOT / "data/raw").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/processed").mkdir(parents=True, exist_ok=True)
    (ROOT / "data/raw/mumbai_2025_raw.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    frame = pd.DataFrame(payload["daily"]).rename(columns={"time":"date"})
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for col in frame.columns:
        if col != "date":
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    frame = frame.dropna(subset=["date"]).drop_duplicates("date").sort_values("date")
    frame.insert(0, "location", "Mumbai, India")
    frame.insert(1, "latitude", LATITUDE)
    frame.insert(2, "longitude", LONGITUDE)
    frame["year"], frame["month"] = frame.date.dt.year, frame.date.dt.month
    frame["month_name"] = frame.date.dt.strftime("%b")
    aggregations = {
        "temperature_2m_mean":"mean", "temperature_2m_max":"mean",
        "temperature_2m_min":"mean", "relative_humidity_2m_mean":"mean",
        "precipitation_sum":"sum", "wind_speed_10m_mean":"mean",
        "wind_speed_10m_max":"max", "shortwave_radiation_sum":"sum",
    }
    monthly = frame.groupby(["year","month","month_name"], as_index=False).agg(
        {k:v for k,v in aggregations.items() if k in frame.columns}
    )
    # Wind direction is circular; keep daily values and do not arithmetic-average them.
    frame.to_csv(ROOT / "data/processed/mumbai_2025_daily.csv", index=False)
    monthly.to_csv(ROOT / "data/processed/mumbai_2025_monthly.csv", index=False)
    print(f"Downloaded {len(frame)} daily records. Files saved under data/.")

if __name__ == "__main__":
    main()
