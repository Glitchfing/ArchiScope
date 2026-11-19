# ArchiScope

**Climate intelligence for preliminary architectural site analysis.**

ArchiScope helps architecture students, architects and researchers explore location-specific historical climate patterns relevant to early site understanding. It consolidates daily weather variables through a reproducible ETL workflow and presents charts, execution metrics, transparent rule-based observations and downloadable reports.

## Problem

Environmental information relevant to architectural site analysis—temperature, humidity, rainfall, wind and solar radiation—is often distributed across datasets and websites. Collecting, cleaning and interpreting it manually takes time. ArchiScope provides one repeatable workflow to retrieve and inspect these variables for a selected location and historical period.

## Features

- City/place search using Open-Meteo Geocoding API
- Historical daily data extraction using Open-Meteo Archive API
- Raw JSON preservation
- Pandas-based type conversion, duplicate/date checks and basic range validation
- Monthly aggregations and SQLite persistence
- Interactive climate charts for temperature, precipitation, humidity, wind and shortwave radiation
- ETL execution metrics and data preview
- Transparent threshold-based preliminary architectural observations
- Daily/monthly CSV and PDF report downloads

## Architecture

```text
Streamlit UI
   ├── Open-Meteo Geocoding API
   └── Open-Meteo Historical Weather API
             |
          Extract
             ├── Raw JSON archive
             |
          Transform (Pandas)
             ├── parse and standardise
             ├── validate and handle nulls
             └── monthly aggregation
             |
          Load
             ├── SQLite
             ├── daily CSV
             └── monthly CSV
             |
          Dashboard, observations and PDF report
```

## Stack

Python, Streamlit, Pandas, NumPy, Requests, SQLite, Plotly, ReportLab and Matplotlib.

## Run locally

Python 3.10+ recommended.

```bash
git clone https://github.com/Glitchfing/ArchiScope.git
cd ArchiScope
python -m venv .venv
# Windows PowerShell:
.venv\\Scripts\\Activate.ps1
# macOS/Linux:
# source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Search for a location in the sidebar, select the date range and click **Run climate ETL**. The app defaults to Mumbai if no location has been searched.

## Data source and interpretation

- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [Open-Meteo Geocoding API](https://open-meteo.com/en/docs/geocoding-api)

The archive endpoint supplies historical reanalysis data. These are gridded estimates and not necessarily observations measured at the exact building site. Coverage, spatial resolution and variable availability vary by product and period. The app displays returned values and basic data-quality metrics rather than fabricating missing records.

The solar variable is **shortwave radiation energy (MJ/m²)**, not sunshine duration. The current wind-direction chart is a simple distribution of daily dominant direction, not a full meteorological wind rose.

## Outputs

Runtime data is written locally:
- `data/raw/<site>_<period>_raw.json`
- `data/processed/<site>_<period>_daily.csv`
- `data/processed/<site>_<period>_monthly.csv`
- `data/archiscope.sqlite`

Generated data and local databases are excluded from Git by default.

## Scope and limitations

Architectural observations are simple, explicit screening rules. They are not statutory comfort thresholds, formal climate classification, professional design recommendations, drainage calculations, structural analysis or building-energy simulation. Validate all design decisions with site surveys, local codes, specialists and appropriate engineering tools.

## Future extensions

- True wind-rose visualisation using circular statistics
- Compare multiple sites and years
- Seasonal anomaly and year-on-year analysis
- Additional climate normals and extreme-event indicators
- GIS layers and terrain context
- Configurable, sourced thresholds and report templates

## License

Add a license before distributing or reusing this project publicly.
