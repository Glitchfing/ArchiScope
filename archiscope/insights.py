"""Transparent rule-based observations, not engineering recommendations."""

def build_insights(summary: dict) -> list[dict]:
    items = []
    t = summary.get("mean_temperature_c")
    if t is not None:
        if t >= 30:
            items.append({"parameter":"Temperature","measured":f"{t:.1f} °C average","rule":"Average temperature >= 30 °C","observation":"The selected period has a high mean air temperature. Review solar exposure, shading, envelope heat gain and passive cooling strategies during detailed design."})
        elif t <= 18:
            items.append({"parameter":"Temperature","measured":f"{t:.1f} °C average","rule":"Average temperature <= 18 °C","observation":"The selected period has a relatively low mean air temperature. Review seasonal heat retention and outdoor comfort requirements."})
        else:
            items.append({"parameter":"Temperature","measured":f"{t:.1f} °C average","rule":"18 °C < average < 30 °C","observation":"The mean temperature is within this project's broad screening band; monthly extremes should still guide design exploration."})
    h = summary.get("mean_relative_humidity_pct")
    if h is not None and h >= 70:
        items.append({"parameter":"Humidity","measured":f"{h:.1f}% average","rule":"Average relative humidity >= 70%","observation":"Persistently humid conditions may warrant closer study of ventilation, condensation risk and moisture management."})
    p = summary.get("precipitation_mm")
    if p is not None and p >= 1000:
        items.append({"parameter":"Rainfall","measured":f"{p:.0f} mm total","rule":"Period rainfall >= 1,000 mm","observation":"Substantial rainfall over the selected period makes site drainage, runoff pathways and rainwater management important topics for further assessment."})
    w = summary.get("mean_wind_speed_kmh")
    if w is not None and w >= 15:
        items.append({"parameter":"Wind","measured":f"{w:.1f} km/h average","rule":"Average wind speed >= 15 km/h","observation":"The period's mean wind speed supports investigating orientation and controlled openings; local wind studies are needed before design decisions."})
    s = summary.get("shortwave_radiation_mj_m2")
    if s is not None:
        items.append({"parameter":"Solar radiation","measured":f"{s:.1f} MJ/m² cumulative","rule":"Descriptive metric; no threshold applied","observation":"Shortwave radiation is reported as cumulative solar energy, not sunshine duration. Examine monthly variation for facade and shading studies."})
    return items
