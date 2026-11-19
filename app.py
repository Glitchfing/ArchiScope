"""ArchiScope: climate intelligence for preliminary architectural site analysis."""
from datetime import date, timedelta
from pathlib import Path
import re
import streamlit as st
import pandas as pd
import plotly.express as px
from config import APP_NAME, RAW_DIR, PROCESSED_DIR, DB_PATH, TIMEZONE
from archiscope.geo import search_location
from archiscope.extract import fetch_historical, save_raw
from archiscope.transform import transform_payload
from archiscope.storage import load_outputs
from archiscope.insights import build_insights
from archiscope.report import create_pdf_report

st.set_page_config(page_title=APP_NAME, page_icon="🏛️", layout="wide")
st.title("🏛️ ArchiScope")
st.caption("Climate intelligence for preliminary architectural site analysis")
st.info("ArchiScope turns historical climate records into a traceable site-analysis starting point. It is not a certified engineering assessment or building simulation.")

with st.sidebar:
    st.header("Site selection")
    city_query = st.text_input("City / place", "Mumbai")
    if st.button("Find locations", use_container_width=True):
        try:
            st.session_state["locations"] = search_location(city_query)
        except Exception as exc:
            st.error(f"Location lookup failed: {exc}")
    locations = st.session_state.get("locations", [])
    if locations:
        choices = {f'{x["name"]}, {x.get("admin1", "")}, {x.get("country", "")} ({x["latitude"]:.3f}, {x["longitude"]:.3f})': x for x in locations}
        selected_label = st.selectbox("Choose a match", list(choices))
        selected = choices[selected_label]
    else:
        selected = {"name":"Mumbai","latitude":19.0760,"longitude":72.8777,"country":"India","timezone":TIMEZONE}
        st.caption("Default location: Mumbai, India. Search to select another place.")
    today = date.today()
    default_start = today - timedelta(days=365)
    start = st.date_input("Start date", default_start, min_value=date(1940,1,1), max_value=today-timedelta(days=5))
    end = st.date_input("End date", today-timedelta(days=5), min_value=date(1940,1,1), max_value=today-timedelta(days=5))
    timezone = st.text_input("Timezone", selected.get("timezone") or TIMEZONE)
    run = st.button("Run climate ETL", type="primary", use_container_width=True)

if run:
    if start > end:
        st.error("Start date must be on or before end date.")
    else:
        with st.spinner("Extracting historical climate data and running ETL..."):
            try:
                payload = fetch_historical(selected["latitude"], selected["longitude"], start, end, timezone)
                slug = re.sub(r"[^a-z0-9]+", "_", selected["name"].lower()).strip("_") or "site"
                raw_path = save_raw(payload, RAW_DIR / f"{slug}_{start}_{end}_raw.json")
                daily, monthly, stats = transform_payload(payload)
                daily_csv, monthly_csv = load_outputs(daily, monthly, DB_PATH, PROCESSED_DIR, f"{slug}_{start}_{end}")
                st.session_state["analysis"] = {
                    "payload":payload, "daily":daily, "monthly":monthly, "stats":stats,
                    "location":selected, "start":start, "end":end, "raw_path":raw_path,
                    "daily_csv":daily_csv, "monthly_csv":monthly_csv, "slug":slug,
                }
                st.success(f"ETL completed: {len(daily):,} daily records processed.")
            except Exception as exc:
                st.error(f"ETL failed: {exc}")
                st.caption("Check the selected date range, internet connection and Open-Meteo service availability.")

data = st.session_state.get("analysis")
if not data:
    st.subheader("Start with a site")
    st.markdown("1. Search for a city or use the Mumbai default.\n2. Select a historical date range.\n3. Run the ETL pipeline to fetch, validate, aggregate and store climate data.")
    st.markdown("**Data source:** [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)")
    st.stop()

daily, monthly, stats = data["daily"], data["monthly"], data["stats"]
loc = data["location"]
st.markdown(f"**{loc['name']}, {loc.get('admin1','')}, {loc.get('country','')}** · {loc['latitude']:.4f}, {loc['longitude']:.4f} · {data['start']} to {data['end']}")
overview, climate, pipeline, insights, reports = st.tabs(["Overview","Climate analysis","ETL pipeline","Architectural observations","Reports"])

with overview:
    st.subheader("Climate snapshot")
    summary = daily.select_dtypes("number").mean(numeric_only=True).to_dict()
    total_rain = daily["precipitation_mm"].sum(min_count=1) if "precipitation_mm" in daily else None
    kpis = [
        ("Mean temperature", f"{summary.get('mean_temperature_c', float('nan')):.1f} °C"),
        ("Mean humidity", f"{summary.get('mean_relative_humidity_pct', float('nan')):.1f}%"),
        ("Total precipitation", f"{total_rain:.1f} mm" if pd.notna(total_rain) else "N/A"),
        ("Mean wind speed", f"{summary.get('mean_wind_speed_kmh', float('nan')):.1f} km/h"),
    ]
    cols = st.columns(4)
    for col, (label, value) in zip(cols, kpis):
        col.metric(label, value)
    if "shortwave_radiation_mj_m2" in daily:
        st.metric("Cumulative shortwave radiation", f"{daily['shortwave_radiation_mj_m2'].sum(min_count=1):.1f} MJ/m²")
    st.caption("Metrics summarize available daily reanalysis records for the selected coordinates and period.")

with climate:
    st.subheader("Monthly climate patterns")
    if "mean_temperature_c" in monthly:
        st.plotly_chart(px.line(monthly, x="month_name", y=["mean_temperature_c","max_temperature_c","min_temperature_c"], markers=True, title="Monthly temperature (°C)"), use_container_width=True)
    if "precipitation_mm" in monthly:
        st.plotly_chart(px.bar(monthly, x="month_name", y="precipitation_mm", title="Monthly precipitation total (mm)"), use_container_width=True)
    if "mean_relative_humidity_pct" in monthly:
        st.plotly_chart(px.line(monthly, x="month_name", y="mean_relative_humidity_pct", markers=True, title="Mean relative humidity (%)"), use_container_width=True)
    if "mean_wind_speed_kmh" in monthly:
        st.plotly_chart(px.line(monthly, x="month_name", y="mean_wind_speed_kmh", markers=True, title="Mean wind speed (km/h)"), use_container_width=True)
    if "shortwave_radiation_mj_m2" in monthly:
        st.plotly_chart(px.bar(monthly, x="month_name", y="shortwave_radiation_mj_m2", title="Monthly shortwave radiation (MJ/m²)"), use_container_width=True)
    if "dominant_wind_direction_deg" in daily:
        wind = daily.dropna(subset=["dominant_wind_direction_deg"])
        if not wind.empty:
            st.plotly_chart(px.histogram(wind, x="dominant_wind_direction_deg", nbins=16, title="Distribution of daily dominant wind direction (degrees)"), use_container_width=True)
            st.caption("This histogram is a simple directional distribution, not a meteorological wind-rose calculation.")

with pipeline:
    st.subheader("Execution metrics")
    a,b,c,d = st.columns(4)
    a.metric("Source records", stats["source_rows"])
    b.metric("Processed records", stats["processed_rows"])
    c.metric("Missing numeric cells", stats["missing_cells"])
    d.metric("Duplicate / invalid date rows", stats["duplicate_or_invalid_date_rows"])
    st.write("**Invalid values changed to null**")
    st.json(stats["invalid_values_replaced_with_null"])
    st.write("**Outputs written**")
    st.code(f"Raw JSON: {data['raw_path']}\nDaily CSV: {data['daily_csv']}\nMonthly CSV: {data['monthly_csv']}\nSQLite: {DB_PATH}")
    st.dataframe(daily.head(20), use_container_width=True)

with insights:
    st.subheader("Rule-based preliminary observations")
    insights_list = build_insights({
        "mean_temperature_c": daily["mean_temperature_c"].mean() if "mean_temperature_c" in daily else None,
        "mean_relative_humidity_pct": daily["mean_relative_humidity_pct"].mean() if "mean_relative_humidity_pct" in daily else None,
        "precipitation_mm": daily["precipitation_mm"].sum() if "precipitation_mm" in daily else None,
        "mean_wind_speed_kmh": daily["mean_wind_speed_kmh"].mean() if "mean_wind_speed_kmh" in daily else None,
        "shortwave_radiation_mj_m2": daily["shortwave_radiation_mj_m2"].sum() if "shortwave_radiation_mj_m2" in daily else None,
    })
    for item in insights_list:
        with st.container(border=True):
            st.markdown(f"**{item['parameter']}** · {item['measured']}")
            st.caption(f"Rule: {item['rule']}")
            st.write(item["observation"])
    st.warning("These are transparent screening observations only. Thresholds are simple project rules, not statutory comfort limits, climate classifications or professional design advice.")

with reports:
    st.subheader("Download outputs")
    st.download_button("Daily climate CSV", daily.to_csv(index=False).encode("utf-8"), "archiscope_daily.csv", "text/csv")
    st.download_button("Monthly summary CSV", monthly.to_csv(index=False).encode("utf-8"), "archiscope_monthly.csv", "text/csv")
    try:
        pdf = create_pdf_report(loc, data["start"], data["end"], daily, monthly, insights_list)
        st.download_button("Site analysis PDF report", pdf, "archiscope_site_report.pdf", "application/pdf")
    except Exception as exc:
        st.error(f"PDF report could not be generated: {exc}")

st.divider()
st.caption("Source: Open-Meteo Historical Weather API (ERA5 / ERA5-Land reanalysis, depending on availability). Grid-cell data may differ from conditions at an individual building site.")
