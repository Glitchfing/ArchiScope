"""Clean, validate, standardise and aggregate daily climate data."""
import numpy as np
import pandas as pd
from config import COLUMN_LABELS

REQUIRED = ["date", "mean_temperature_c", "precipitation_mm"]

def transform_payload(payload: dict) -> tuple[pd.DataFrame, pd.DataFrame, dict]:
    daily = payload["daily"]
    frame = pd.DataFrame(daily).rename(columns=COLUMN_LABELS)
    frame = frame.rename(columns={"time": "date"})
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    for col in frame.columns:
        if col != "date":
            frame[col] = pd.to_numeric(frame[col], errors="coerce")
    source_rows = len(frame)
    frame = frame.dropna(subset=["date"]).drop_duplicates(subset=["date"]).sort_values("date")
    duplicate_rows = source_rows - len(frame)
    numeric = [c for c in frame.columns if c != "date"]
    invalid_counts = {}
    for col in numeric:
        before = frame[col].notna().sum()
        if "humidity" in col:
            frame.loc[~frame[col].between(0, 100), col] = np.nan
        elif "precipitation" in col or "radiation" in col or "wind_speed" in col:
            frame.loc[frame[col] < 0, col] = np.nan
        invalid_counts[col] = int(before - frame[col].notna().sum())
    frame["year"] = frame["date"].dt.year
    frame["month"] = frame["date"].dt.month
    frame["month_name"] = frame["date"].dt.strftime("%b")
    frame["season"] = frame["month"].map({
        12:"Winter", 1:"Winter", 2:"Winter",
        3:"Summer", 4:"Summer", 5:"Summer",
        6:"Monsoon", 7:"Monsoon", 8:"Monsoon", 9:"Monsoon",
        10:"Post-monsoon", 11:"Post-monsoon",
    })
    mean_cols = [c for c in numeric if c not in ("precipitation_mm", "shortwave_radiation_mj_m2", "max_wind_speed_kmh", "dominant_wind_direction_deg")]
    agg = {c:"mean" for c in mean_cols}
    if "precipitation_mm" in frame: agg["precipitation_mm"] = "sum"
    if "shortwave_radiation_mj_m2" in frame: agg["shortwave_radiation_mj_m2"] = "sum"
    if "max_wind_speed_kmh" in frame: agg["max_wind_speed_kmh"] = "max"
    monthly = frame.groupby(["year","month","month_name"], as_index=False).agg(agg)
    monthly["days_with_records"] = frame.groupby(["year","month"]).size().values
    stats = {
        "source_rows": source_rows,
        "processed_rows": len(frame),
        "duplicate_or_invalid_date_rows": duplicate_rows,
        "missing_cells": int(frame[numeric].isna().sum().sum()),
        "invalid_values_replaced_with_null": invalid_counts,
        "date_start": frame["date"].min().date().isoformat() if len(frame) else None,
        "date_end": frame["date"].max().date().isoformat() if len(frame) else None,
    }
    return frame, monthly, stats
