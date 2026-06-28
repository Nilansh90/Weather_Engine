from datetime import date, timedelta
from pathlib import Path
import sys
import traceback

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
from app.ml.features import FeaturePipeline
from app.ml.predictor import InferenceOrchestrator


def main():

    print("\n" + "=" * 65)
    print("           WEATHER ENGINE - DAILY PREDICTION")
    print("=" * 65)

    forecast_date = date.today() + timedelta(days=1)

    print(f"\nForecast Date : {forecast_date}\n")

    # ---------------------------------------------------
    # Initialize objects
    # ---------------------------------------------------

    db = DatabaseManager()

    fp = FeaturePipeline(db)

    predictor = InferenceOrchestrator(fp)

    # predictor.debug_feature_names()
    #
    # raise SystemExit

    cities = db.get_all_cities()

    total = len(cities)

    success = 0

    failed = 0

    # ---------------------------------------------------
    # Prediction Loop
    # ---------------------------------------------------

    for index, city in enumerate(cities, start=1):

        city_id = city["city_id"]

        city_name = city["city_name"]

        latitude = city["latitude"]

        longitude = city["longitude"]

        print(f"[{index}/{total}] {city_name}")

        try:

            # ------------------------------------------
            # Read cached NWP
            # ------------------------------------------

            nwp = db.get_cached_nwp(
                latitude,
                longitude,
                forecast_date
            )

            if nwp is None:
                raise RuntimeError(
                    f"NWP cache missing for {city_name}"
                )

            # ------------------------------------------
            # Run entire DAG
            # ------------------------------------------

            forecast = predictor.run_full_dag(

                city_id,

                forecast_date,

                nwp

            )

            # ------------------------------------------
            # Save prediction
            # ------------------------------------------

            db.save_prediction(

                forecast

            )

            success += 1

            print("   ✓ Prediction Saved\n")

        except Exception:

            failed += 1

            print("   ✗ Prediction Failed\n")

            traceback.print_exc()

            print()

    # ---------------------------------------------------
    # Summary
    # ---------------------------------------------------

    print("=" * 65)

    print("PREDICTION PIPELINE COMPLETE\n")

    print(f"Cities Processed : {total}")

    print(f"Successful       : {success}")

    print(f"Failed           : {failed}")

    if failed == 0:

        print("\nPipeline Status  : SUCCESS")

    else:

        print("\nPipeline Status  : PARTIAL FAILURE")

    print("=" * 65)

    db.close()


if __name__ == "__main__":
    main()