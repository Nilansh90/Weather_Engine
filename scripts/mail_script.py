from datetime import date, timedelta
from pathlib import Path
import sys
import traceback
import time

from pathlib import Path
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[2]

load_dotenv(ROOT / ".env")

# -------------------------------------------------------
# Allow imports from project root
# -------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# -------------------------------------------------------
# Imports
# -------------------------------------------------------

from app.database.db_manager import DatabaseManager
from app.email.mailer import EmailReporter


def main():

    print("\n" + "=" * 65)
    print("          WEATHER ENGINE - EMAIL REPORT")
    print("=" * 65)

    db = DatabaseManager()

    reporter = EmailReporter()

    forecast_date = date.today() + timedelta(days=1)

    actual_date = date.today() - timedelta(days=1)

    try:

        cities = db.get_all_cities()

        pipeline = {

            "cities_processed": len(cities),

            "cache_hits": len(cities),

            "api_calls": 0,

            "status": "SUCCESS"

        }

        for city in cities:

            city_id = city["city_id"]

            city_name = city["city_name"]

            print(f"Preparing report for {city_name}")

            # ------------------------------------------
            # Tomorrow Forecast
            # ------------------------------------------

            forecast = db.get_prediction(

                city_id,

                forecast_date

            )

            if forecast is None:

                print(f"Skipping {city_name} (forecast missing)")

                continue

            # ------------------------------------------
            # Cached NWP
            # ------------------------------------------

            nwp = db.get_cached_nwp(

                city["latitude"],

                city["longitude"],

                forecast_date

            )

            # ------------------------------------------
            # Yesterday Actual
            # ------------------------------------------

            actual = db.get_actual_weather(

                city_id,

                actual_date

            )

            # ------------------------------------------
            # Yesterday Errors
            # ------------------------------------------

            errors = db.get_error(

                city_id,

                actual_date

            )

            if actual is None:

                actual = {

                    "temp_max_c": "-",

                    "temp_min_c": "-",

                    "pressure_msl_max_hpa": "-",

                    "pressure_msl_min_hpa": "-",

                    "precipitation_sum_mm": "-",

                    "cloud_cover_mean_pct": "-",

                    "weather_code": "-"

                }

            if errors is None:

                errors = {

                    "temp_mae": 0,

                    "pressure_mae": 0,

                    "dew_mae": 0,

                    "rh_mae": 0,

                    "rain_correct": "-",

                    "weather_correct": "-"

                }

            reporter.send_daily_report(

                forecast,

                nwp,

                actual,

                errors,

                pipeline

            )

            print(f"✓ Email sent for {city_name}")
            time.sleep(3)
        print("\nReport generation complete.")

    except Exception:

        traceback.print_exc()

    finally:

        db.close()


if __name__ == "__main__":

    main()