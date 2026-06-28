#WORKS TO GET 15 YEARS DATA
import json
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import datetime, timedelta
import pytz
import os
import time
import shutil

# 1. Setup
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

# Pathing: Navigate UP from /scripts to /Weather_Project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_PATH = os.path.join(BASE_DIR, 'cities.json')
RAW_DATA_DIR = os.path.join(BASE_DIR, 'data', 'raw')

print("[INIT] Starting historical weather data ingestion...")
print(f"[PATH] Base directory: {BASE_DIR}")
print(f"[PATH] Cities JSON: {JSON_PATH}")
print(f"[PATH] Raw data directory: {RAW_DATA_DIR}")


def clean_raw_data_directory():
    """Remove existing raw data directory if it exists"""
    print("\n[CLEANUP] Checking for existing raw data directory...")
    if os.path.exists(RAW_DATA_DIR):
        print(f"[CLEANUP] Found existing directory: {RAW_DATA_DIR}")
        shutil.rmtree(RAW_DATA_DIR)
        print(f"[CLEANUP] [OK] Deleted existing directory")

    # Create fresh directory
    os.makedirs(RAW_DATA_DIR, exist_ok=True)
    print(f"[CLEANUP] [OK] Created fresh raw data directory")


def run_ingestion():
    """Fetch 15 years of historical weather data from OpenMeteo API"""

    if not os.path.exists(JSON_PATH):
        print(f"[ERROR] {JSON_PATH} not found.")
        return

    print(f"\n[LOAD] Loading cities from {JSON_PATH}...")
    with open(JSON_PATH, 'r') as f:
        cities = json.load(f)['cities']

    print(f"[LOAD] ✓ Loaded {len(cities)} cities:")
    for city in cities:
        print(f"      - {city['name']} (ID: {city['id']}, Lat: {city['lat']}, Lon: {city['lon']})")

    ist = pytz.timezone('Asia/Kolkata')
    today = datetime.now(ist).date()
    fifteen_years_ago = today - timedelta(days=15 * 365)

    print(f"\n[DATE] Today's date (IST): {today}")
    print(f"[DATE] 15 years ago: {fifteen_years_ago}")

    daily_params = [
        "weather_code", "temperature_2m_mean", "temperature_2m_max", "temperature_2m_min",
        "wind_speed_10m_max", "wind_gusts_10m_max", "wind_direction_10m_dominant",
        "shortwave_radiation_sum", "daylight_duration", "precipitation_sum",
        "cloud_cover_mean", "cloud_cover_max", "cloud_cover_min",
        "dew_point_2m_mean", "dew_point_2m_max", "dew_point_2m_min",
        "relative_humidity_2m_mean", "relative_humidity_2m_max", "relative_humidity_2m_min",
        "pressure_msl_mean", "pressure_msl_max", "pressure_msl_min"
    ]

    print(f"[API] ✓ Configured {len(daily_params)} weather parameters")

    # Pause before hitting the API loop
    print("\n[PAUSE] Sleeping for 15 seconds before starting the API ingestion loop...")
    time.sleep(15)

    for idx, city in enumerate(cities):
        print(f"\n{'=' * 70}")
        print(f"[CITY] Processing {city['name']} (ID: {city['id']}) [{idx + 1}/{len(cities)}]")
        print(f"{'=' * 70}")

        # The 45-second wait to hit the ~1 city/minute rate limit
        if idx > 0:
            print(f"[PAUSE] Sleeping for 45 seconds to ensure 1 city/minute limit...")
            time.sleep(45)

        params = {
            "latitude": city["lat"],
            "longitude": city["lon"],
            "start_date": fifteen_years_ago.isoformat(),
            "end_date": today.isoformat(),
            "daily": daily_params,
            "temperature_unit": "celsius",
            "wind_speed_unit": "kmh",
            "precipitation_unit": "mm",
            "pressure_unit": "hpa",
            "timezone": "Asia/Kolkata"
        }

        print(f"[API] Fetching data from {params['start_date']} to {params['end_date']}...")

        try:
            responses = openmeteo.weather_api(
                "https://archive-api.open-meteo.com/v1/archive",
                params=params
            )
            daily = responses[0].Daily()

            print(f"[API] ✓ Successfully fetched data from API")

            # --- FIXED DATE PARSING FOR THE OPEN-METEO SDK ---
            start_epoch = daily.Time()
            end_epoch = daily.TimeEnd()
            step_seconds = daily.Interval()

            # Generate the full range of timestamps natively using Pandas
            time_series = pd.date_range(
                start=pd.to_datetime(start_epoch, unit="s", utc=True),
                end=pd.to_datetime(end_epoch, unit="s", utc=True),
                freq=pd.Timedelta(seconds=step_seconds),
                inclusive="left"
            ).tz_convert('Asia/Kolkata')

            num_days = len(time_series)
            print(f"[DATA] Retrieved {num_days} days of data")
            print(f"[DATA] Date range: {time_series[0].date()} to {time_series[-1].date()}")

            # Create DataFrame
            df = pd.DataFrame({
                "date": time_series.date,
                "time_gmt_5_30": time_series,
                "latitude": city["lat"],
                "longitude": city["lon"],
                "city_id": city["id"],
                "city_name": city["name"],
                "weather_code": daily.Variables(0).ValuesAsNumpy().astype(int),
                "temp_mean_c": daily.Variables(1).ValuesAsNumpy(),
                "temp_max_c": daily.Variables(2).ValuesAsNumpy(),
                "temp_min_c": daily.Variables(3).ValuesAsNumpy(),
                "wind_speed_max_kmh": daily.Variables(4).ValuesAsNumpy(),
                "wind_gusts_max_kmh": daily.Variables(5).ValuesAsNumpy(),
                "wind_direction_dominant_deg": daily.Variables(6).ValuesAsNumpy(),
                "shortwave_radiation_sum_mj_m2": daily.Variables(7).ValuesAsNumpy(),
                "daylight_duration_s": daily.Variables(8).ValuesAsNumpy(),
                "precipitation_sum_mm": daily.Variables(9).ValuesAsNumpy(),
                "cloud_cover_mean_pct": daily.Variables(10).ValuesAsNumpy(),
                "cloud_cover_max_pct": daily.Variables(11).ValuesAsNumpy(),
                "cloud_cover_min_pct": daily.Variables(12).ValuesAsNumpy(),
                "dew_point_mean_c": daily.Variables(13).ValuesAsNumpy(),
                "dew_point_max_c": daily.Variables(14).ValuesAsNumpy(),
                "dew_point_min_c": daily.Variables(15).ValuesAsNumpy(),
                "relative_humidity_mean_pct": daily.Variables(16).ValuesAsNumpy(),
                "relative_humidity_max_pct": daily.Variables(17).ValuesAsNumpy(),
                "relative_humidity_min_pct": daily.Variables(18).ValuesAsNumpy(),
                "pressure_msl_mean_hpa": daily.Variables(19).ValuesAsNumpy(),
                "pressure_msl_max_hpa": daily.Variables(20).ValuesAsNumpy(),
                "pressure_msl_min_hpa": daily.Variables(21).ValuesAsNumpy()
            })

            print(f"[VERIFY] DataFrame shape: {df.shape}")

            # Quality checks
            print(f"\n[QUALITY] Checking data quality...")
            null_counts = df.isnull().sum()
            if null_counts.sum() > 0:
                print(f"[QUALITY] ⚠ Found null values")
            else:
                print(f"[QUALITY] ✓ No null values found")

            # Save to CSV
            csv_filename = f"{city['name'].lower().replace(' ', '_')}.csv"
            csv_path = os.path.join(RAW_DATA_DIR, csv_filename)

            print(f"\n[SAVE] Saving to CSV...")
            df.to_csv(csv_path, index=False)

            file_size = os.path.getsize(csv_path)
            print(f"[SAVE] ✓ File saved: {csv_path} ({file_size / (1024 * 1024):.2f} MB)")

        except Exception as e:
            print(f"[ERROR] Failed to fetch data for {city['name']}: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 70}")
    print(f"[COMPLETE] ✓ Ingestion complete! Total files: {len(os.listdir(RAW_DATA_DIR))}")
    print(f"{'=' * 70}")


if __name__ == "__main__":
    clean_raw_data_directory()

    # Pause between cleaning the directory and starting the main ingestion
    print("\n[PAUSE] Directory cleaned. Sleeping for 15 seconds before ingestion...")
    time.sleep(15)

    run_ingestion()

