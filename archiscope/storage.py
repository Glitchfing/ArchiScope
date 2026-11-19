"""Persist cleaned daily and monthly data in SQLite and CSV."""
import sqlite3
from pathlib import Path
import pandas as pd

def load_outputs(daily: pd.DataFrame, monthly: pd.DataFrame, db_path: Path, processed_dir: Path, slug: str):
    db_path.parent.mkdir(parents=True, exist_ok=True)
    processed_dir.mkdir(parents=True, exist_ok=True)
    daily_csv = processed_dir / f"{slug}_daily.csv"
    monthly_csv = processed_dir / f"{slug}_monthly.csv"
    daily.to_csv(daily_csv, index=False)
    monthly.to_csv(monthly_csv, index=False)
    with sqlite3.connect(db_path) as conn:
        daily.to_sql("daily_climate", conn, if_exists="replace", index=False)
        monthly.to_sql("monthly_climate", conn, if_exists="replace", index=False)
    return daily_csv, monthly_csv
