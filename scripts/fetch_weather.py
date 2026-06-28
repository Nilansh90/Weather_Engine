from datetime import date, timedelta
from pathlib import Path
import sys

# --------------------------------------------------------
# Allow imports from project root
# --------------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

# --------------------------------------------------------
# Imports
# --------------------------------------------------------

from app.database.db_manager import DatabaseManager
from app.external.nwp_client import NWPClient


def main():

    print("\n" + "=" * 60)
    print("        WEATHER ENGINE - NWP CACHE BUILDER")
    print("=" * 60)

    forecast_date = date.today() + timedelta(days=1)

    print(f"\nForecast Date : {forecast_date}\n")

    # ----------------------------------------------------
    # Initialize
    # ----------------------------------------------------

    db = DatabaseManager()

    nwp = NWPClient(db)

    cities = db.get_all_cities()

    total = len(cities)

    success = 0

    failed = 0

    # ----------------------------------------------------
    # Loop over every city
    # ----------------------------------------------------

    for index, city in enumerate(cities, start=1):

        city_name = city["city_name"]

        city_id = city["city_id"]

        latitude = city["latitude"]

        longitude = city["longitude"]

        print(f"[{index}/{total}] {city_name}")

        try:

            nwp.fetch(

                latitude=latitude,
                longitude=longitude,
                target_date=forecast_date

            )

            success += 1

            print("   ✓ Forecast cached\n")

        except Exception as e:

            failed += 1

            print(f"   ✗ Failed : {e}\n")

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    print("=" * 60)

    print("CACHE BUILD COMPLETE\n")

    print(f"Cities Processed : {total}")
    print(f"Successful       : {success}")
    print(f"Failed           : {failed}")

    if failed == 0:
        print("\nPipeline Status  : SUCCESS")
    else:
        print("\nPipeline Status  : PARTIAL FAILURE")

    print("=" * 60)


if __name__ == "__main__":
    main()