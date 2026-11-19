from archiscope.transform import transform_payload

def test_transform_builds_daily_and_monthly():
    payload = {"daily": {
        "time": ["2025-01-01", "2025-01-02"],
        "temperature_2m_mean": [25, 27],
        "temperature_2m_max": [30, 32],
        "temperature_2m_min": [20, 22],
        "relative_humidity_2m_mean": [60, 65],
        "precipitation_sum": [0, 4],
        "wind_speed_10m_mean": [10, 12],
        "wind_speed_10m_max": [20, 22],
        "wind_direction_10m_dominant": [90, 100],
        "shortwave_radiation_sum": [15, 16],
    }}
    daily, monthly, stats = transform_payload(payload)
    assert len(daily) == 2
    assert len(monthly) == 1
    assert monthly.loc[0, "precipitation_mm"] == 4
    assert stats["processed_rows"] == 2
