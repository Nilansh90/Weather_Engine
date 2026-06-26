from __future__ import annotations
import argparse
import collections
import datetime as dt
import json
import os
import statistics
import sys
import time
from typing import Any, Dict, List, Optional

try:
    import requests
    import psycopg2
    from dotenv import load_dotenv
except ImportError:
    print("Please install required packages: pip install requests psycopg2-binary python-dotenv")
    sys.exit(1)

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

API_URL = "https://api.open-meteo.com/v1/forecast"
TIMEZONE = "Asia/Kolkata"


def parse_args():
    p = argparse.ArgumentParser()
    p.add_argument("--cities", default="cities.json", help="Path to cities.json")
    p.add_argument("--days", type=int, default=16, help="Number of days to fetch")
    return p.parse_args()


def iso_date(d: dt.date) -> str:
    return d.isoformat()


def start_end_dates(days: int) -> tuple[str, str, List[dt.date]]:
    today = dt.datetime.now(dt.timezone.utc).astimezone(dt.timezone(dt.timedelta(hours=5, minutes=30)))
    end_date = today.date()
    start_date = end_date - dt.timedelta(days=days - 1)
    dates = [start_date + dt.timedelta(days=i) for i in range((end_date - start_date).days + 1)]
    return start_date.isoformat(), end_date.isoformat(), dates


def safe_float(x: Any) -> Optional[float]:
    try:
        if x is None:
            return None
        return float(x)
    except Exception:
        return None


def most_common(values: List[Any]) -> Optional[Any]:
    if not values:
        return None
    cnt = collections.Counter(values)
    return cnt.most_common(1)[0][0]


def ensure_table(conn):
    print("Checking database table structure...")
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS weather_data (
                id SERIAL PRIMARY KEY,
                date DATE NOT NULL,
                time_gmt_5_30 TIMESTAMPTZ NOT NULL,
                latitude REAL,
                longitude REAL,
                city_id TEXT,
                city_name TEXT,
                weather_code INTEGER,
                temp_mean_c REAL,
                temp_max_c REAL,
                temp_min_c REAL,
                wind_speed_max_kmh REAL,
                wind_gusts_max_kmh REAL,
                wind_direction_dominant_deg REAL,
                shortwave_radiation_sum_mj_m2 REAL,
                daylight_duration_s INTEGER,
                precipitation_sum_mm REAL,
                cloud_cover_mean_pct REAL,
                cloud_cover_max_pct REAL,
                cloud_cover_min_pct REAL,
                dew_point_mean_c REAL,
                dew_point_max_c REAL,
                dew_point_min_c REAL,
                relative_humidity_mean_pct REAL,
                relative_humidity_max_pct REAL,
                relative_humidity_min_pct REAL,
                pressure_msl_mean_hpa REAL,
                pressure_msl_max_hpa REAL,
                pressure_msl_min_hpa REAL,
                UNIQUE(date, city_id)
            )
        """)
    conn.commit()


def fetch_for_city(lat: float, lon: float, start_date: str, end_date: str) -> Dict[str, Any]:
    print(f"  -> Fetching API data for ({lat}, {lon}) from {start_date} to {end_date}...")
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start_date,
        "end_date": end_date,
        "hourly": ",".join([
            "temperature_2m", "dewpoint_2m", "relativehumidity_2m", "pressure_msl",
            "cloudcover", "shortwave_radiation", "precipitation", "windspeed_10m",
            "windgusts_10m", "winddirection_10m", "weathercode"
        ]),
        "daily": ",".join([
            "weathercode", "shortwave_radiation_sum", "precipitation_sum",
            "windspeed_10m_max", "windgusts_10m_max", "winddirection_10m_dominant",
            "sunrise", "sunset"
        ]),
        "timezone": TIMEZONE,
        "windspeed_unit": "kmh",
    }
    r = requests.get(API_URL, params=params, timeout=30)
    r.raise_for_status()
    return r.json()


def aggregate_for_dates(response: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    hourly = response.get("hourly", {})
    daily = response.get("daily", {})
    result: Dict[str, Dict[str, Any]] = {}

    times = hourly.get("time", [])
    hourly_vars = [
        "temperature_2m", "dewpoint_2m", "relativehumidity_2m", "pressure_msl",
        "cloudcover", "shortwave_radiation", "precipitation", "windspeed_10m",
        "windgusts_10m", "winddirection_10m", "weathercode"
    ]
    per_date_vals: Dict[str, Dict[str, List[float]]] = {}
    per_date_codes: Dict[str, List[int]] = {}

    for i, t in enumerate(times):
        date_part = t.split("T")[0]
        per_date_vals.setdefault(date_part, {k: [] for k in hourly_vars})
        for var in hourly_vars:
            arr = hourly.get(var)
            if not arr: continue
            v = arr[i]
            if v is None: continue
            if var == "weathercode":
                per_date_codes.setdefault(date_part, []).append(int(v))
            else:
                try:
                    per_date_vals[date_part][var].append(float(v))
                except Exception:
                    continue

    for date, vals in per_date_vals.items():
        rec: Dict[str, Any] = {}

        def mean_or_none(a): return statistics.mean(a) if a else None

        rec["temp_mean_c"] = mean_or_none(vals.get("temperature_2m", []))
        rec["temp_max_c"] = max(vals.get("temperature_2m", [])) if vals.get("temperature_2m") else None
        rec["temp_min_c"] = min(vals.get("temperature_2m", [])) if vals.get("temperature_2m") else None
        rec["dew_point_mean_c"] = mean_or_none(vals.get("dewpoint_2m", []))
        rec["dew_point_max_c"] = max(vals.get("dewpoint_2m", [])) if vals.get("dewpoint_2m") else None
        rec["dew_point_min_c"] = min(vals.get("dewpoint_2m", [])) if vals.get("dewpoint_2m") else None
        rec["relative_humidity_mean_pct"] = mean_or_none(vals.get("relativehumidity_2m", []))
        rec["relative_humidity_max_pct"] = max(vals.get("relativehumidity_2m", [])) if vals.get(
            "relativehumidity_2m") else None
        rec["relative_humidity_min_pct"] = min(vals.get("relativehumidity_2m", [])) if vals.get(
            "relativehumidity_2m") else None
        rec["pressure_msl_mean_hpa"] = mean_or_none(vals.get("pressure_msl", []))
        rec["pressure_msl_max_hpa"] = max(vals.get("pressure_msl", [])) if vals.get("pressure_msl") else None
        rec["pressure_msl_min_hpa"] = min(vals.get("pressure_msl", [])) if vals.get("pressure_msl") else None
        rec["cloud_cover_mean_pct"] = mean_or_none(vals.get("cloudcover", []))
        rec["cloud_cover_max_pct"] = max(vals.get("cloudcover", [])) if vals.get("cloudcover") else None
        rec["cloud_cover_min_pct"] = min(vals.get("cloudcover", [])) if vals.get("cloudcover") else None
        rec["wind_speed_max_kmh"] = max(vals.get("windspeed_10m", [])) if vals.get("windspeed_10m") else None
        rec["wind_gusts_max_kmh"] = max(vals.get("windgusts_10m", [])) if vals.get("windgusts_10m") else None
        rec["wind_direction_dominant_deg"] = mean_or_none(vals.get("winddirection_10m", []))
        rec["precipitation_sum_mm"] = sum(vals.get("precipitation", [])) if vals.get("precipitation") else None
        rec["shortwave_radiation_sum_mj_m2"] = None

        codes = per_date_codes.get(date, [])
        rec["weather_code"] = most_common(codes) if codes else None
        result[date] = rec

    daily_time = daily.get("time", [])
    if daily_time:
        for i, d in enumerate(daily_time):
            rec = result.setdefault(d, {})

            def safe_daily(key):
                arr = daily.get(key)
                return arr[i] if arr and i < len(arr) else None

            sw = safe_daily("shortwave_radiation_sum")
            if sw is not None:
                rec["shortwave_radiation_sum_mj_m2"] = safe_float(sw)
            else:
                rec.setdefault("shortwave_radiation_sum_mj_m2", None)

            wdm = safe_daily("winddirection_10m_dominant")
            if wdm is not None: rec["wind_direction_dominant_deg"] = safe_float(wdm)
            wsm = safe_daily("windspeed_10m_max")
            if wsm is not None: rec["wind_speed_max_kmh"] = safe_float(wsm)
            wgm = safe_daily("windgusts_10m_max")
            if wgm is not None: rec["wind_gusts_max_kmh"] = safe_float(wgm)
            psum = safe_daily("precipitation_sum")
            if psum is not None: rec["precipitation_sum_mm"] = safe_float(psum)

            sunrise, sunset = safe_daily("sunrise"), safe_daily("sunset")
            if sunrise and sunset:
                try:
                    sr = dt.datetime.fromisoformat(sunrise)
                    ss = dt.datetime.fromisoformat(sunset)
                    rec["daylight_duration_s"] = int((ss - sr).total_seconds())
                except Exception:
                    rec["daylight_duration_s"] = None

    return result


def insert_rows(conn, city, aggregates, dates):
    cur = conn.cursor()
    inserted, skipped = 0, 0
    for d in dates:
        date_s = iso_date(d)
        if date_s not in aggregates:
            skipped += 1
            continue

        city_id = str(city.get("city_id") or city.get("id") or city.get("name"))
        cur.execute("SELECT 1 FROM weather_data WHERE date = %s AND city_id = %s LIMIT 1", (date_s, city_id))
        if cur.fetchone():
            skipped += 1
            continue

        rec = aggregates[date_s]
        time_gmt_5_30 = f"{date_s} 00:00:00+05:30"

        params = (
            date_s, time_gmt_5_30, safe_float(city.get("latitude")), safe_float(city.get("longitude")),
            city_id, city.get("city_name") or city.get("name"), rec.get("weather_code"),
            rec.get("temp_mean_c"), rec.get("temp_max_c"), rec.get("temp_min_c"),
            rec.get("wind_speed_max_kmh"), rec.get("wind_gusts_max_kmh"), rec.get("wind_direction_dominant_deg"),
            rec.get("shortwave_radiation_sum_mj_m2"), rec.get("daylight_duration_s"),
            rec.get("precipitation_sum_mm"), rec.get("cloud_cover_mean_pct"),
            rec.get("cloud_cover_max_pct"), rec.get("cloud_cover_min_pct"),
            rec.get("dew_point_mean_c"), rec.get("dew_point_max_c"), rec.get("dew_point_min_c"),
            rec.get("relative_humidity_mean_pct"), rec.get("relative_humidity_max_pct"),
            rec.get("relative_humidity_min_pct"), rec.get("pressure_msl_mean_hpa"),
            rec.get("pressure_msl_max_hpa"), rec.get("pressure_msl_min_hpa")
        )

        cur.execute("""
            INSERT INTO weather_data (
                date, time_gmt_5_30, latitude, longitude, city_id, city_name, weather_code,
                temp_mean_c, temp_max_c, temp_min_c, wind_speed_max_kmh, wind_gusts_max_kmh,
                wind_direction_dominant_deg, shortwave_radiation_sum_mj_m2, daylight_duration_s,
                precipitation_sum_mm, cloud_cover_mean_pct, cloud_cover_max_pct, cloud_cover_min_pct,
                dew_point_mean_c, dew_point_max_c, dew_point_min_c,
                relative_humidity_mean_pct, relative_humidity_max_pct, relative_humidity_min_pct,
                pressure_msl_mean_hpa, pressure_msl_max_hpa, pressure_msl_min_hpa
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, params)
        inserted += 1
    conn.commit()
    cur.close()
    return inserted, skipped


def main():
    args = parse_args()

    # 1. Read cities.json
    if not os.path.exists(args.cities):
        print(f"Error: The file {args.cities} was not found in this directory.")
        sys.exit(1)

    with open(args.cities, "r", encoding="utf-8") as fh:
        raw_data = json.load(fh)

    # Handle if the JSON is an object containing a "cities" array
    if isinstance(raw_data, dict) and "cities" in raw_data:
        cities = raw_data["cities"]
    else:
        cities = raw_data

    if not isinstance(cities, list):
        print("Error: cities.json must contain a JSON array of objects.")
        sys.exit(1)

    print(f"Found {len(cities)} cities in {args.cities}.")

    # 2. Setup dates and DB
    start_date, end_date, dates = start_end_dates(args.days)
    if not DATABASE_URL:
        print("Error: DATABASE_URL not found in environment or .env file.")
        sys.exit(1)

    print("Opening connection to PostgreSQL...")
    conn = psycopg2.connect(DATABASE_URL)
    ensure_table(conn)

    # 3. Main Loop
    total_inserted = 0
    total_skipped = 0

    for city in cities:
        city_name = city.get("city_name") or city.get("name", "Unknown City")
        # Check for both "latitude"/"lat" and "longitude"/"lon"
        lat = city.get("latitude") if city.get("latitude") is not None else city.get("lat")
        lon = city.get("longitude") if city.get("longitude") is not None else city.get("lon")

        # Ensure lat/lon are properly formatted for insert_rows later
        city["latitude"] = lat
        city["longitude"] = lon

        if lat is None or lon is None:
            print(f"Skipping {city_name}: Missing latitude or longitude.")
            continue

        print(f"\n--- Processing: {city_name} ---")
        try:
            # Added 1-second delay to protect against API rate limits
            time.sleep(1.0)
            resp = fetch_for_city(lat, lon, start_date, end_date)

            # Aggregate the data
            aggs = aggregate_for_dates(resp)

            # Shortwave radiation fallback
            hourly = resp.get("hourly", {})
            if "shortwave_radiation" in hourly and "time" in hourly:
                times = hourly["time"]
                sw = hourly.get("shortwave_radiation", [])
                per_date_sw = {}
                for i, t in enumerate(times):
                    date_part = t.split("T")[0]
                    try:
                        v = float(sw[i])
                        per_date_sw.setdefault(date_part, []).append(v)
                    except Exception:
                        pass
                for date_s, arr in per_date_sw.items():
                    if date_s in aggs and aggs[date_s].get("shortwave_radiation_sum_mj_m2") is None:
                        total_wsm2 = sum(arr) * 3600.0
                        aggs[date_s]["shortwave_radiation_sum_mj_m2"] = total_wsm2 / 1e6

            # Insert into Postgres
            ins, sk = insert_rows(conn, city, aggs, dates)
            print(f"  -> {city_name} finished: {ins} inserted, {sk} skipped (already existed).")
            total_inserted += ins
            total_skipped += sk

        except Exception as e:
            print(f"  !! Error processing {city_name}: {e}")
            continue

    conn.close()
    print(f"\nAll done! Total rows inserted: {total_inserted}, Total skipped: {total_skipped}.")


if __name__ == '__main__':
    main()