from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from app.database.db_manager import DatabaseManager


def abs_error(a, b):

    if a is None or b is None:
        return None

    return abs(float(a) - float(b))


def main():

    print("=" * 65)
    print("        WEATHER ENGINE - ERROR CALCULATION")
    print("=" * 65)

    db = DatabaseManager()

    predictions = db.get_predictions_without_errors()

    total = len(predictions)

    success = 0

    failed = 0

    for prediction in predictions:

        print(

            f"[{prediction['city_id']}] "
            f"{prediction['forecast_date']}"

        )

        actual = db.get_actual_weather(

            prediction["city_id"],

            prediction["forecast_date"]

        )

        if actual is None:

            print("   Actual weather unavailable\n")

            failed += 1

            continue

        error = {

            "city_id":

                prediction["city_id"],

            "forecast_date":

                prediction["forecast_date"],

            "temp_max_error":

                abs_error(
                    prediction["temp_max_c"],
                    actual["temp_max_c"]
                ),

            "temp_min_error":

                abs_error(
                    prediction["temp_min_c"],
                    actual["temp_min_c"]
                ),

            "pressure_max_error":

                abs_error(
                    prediction["pressure_msl_max_hpa"],
                    actual["pressure_msl_max_hpa"]
                ),

            "pressure_min_error":

                abs_error(
                    prediction["pressure_msl_min_hpa"],
                    actual["pressure_msl_min_hpa"]
                ),

            "dew_point_max_error":

                abs_error(
                    prediction["dew_point_max_c"],
                    actual["dew_point_max_c"]
                ),

            "dew_point_min_error":

                abs_error(
                    prediction["dew_point_min_c"],
                    actual["dew_point_min_c"]
                ),

            "humidity_max_error":

                abs_error(
                    prediction["relative_humidity_max_pct"],
                    actual["relative_humidity_max_pct"]
                ),

            "humidity_min_error":

                abs_error(
                    prediction["relative_humidity_min_pct"],
                    actual["relative_humidity_min_pct"]
                ),

            "wind_speed_error":

                abs_error(
                    prediction["wind_speed_max_kmh"],
                    actual["wind_speed_max_kmh"]
                ),

            "wind_gust_error":

                abs_error(
                    prediction["wind_gusts_max_kmh"],
                    actual["wind_gusts_max_kmh"]
                ),

            "cloud_cover_error":

                abs_error(
                    prediction["cloud_cover_mean_pct"],
                    actual["cloud_cover_mean_pct"]
                ),

            "precipitation_error":

                abs_error(
                    prediction["precipitation_sum_mm"],
                    actual["precipitation_sum_mm"]
                ),

            "rain_correct":

                (

                    prediction["will_rain"]

                    ==

                    (

                        actual["precipitation_sum_mm"] > 0

                    )

                ),

            "weather_code_correct":

                (

                    prediction["weather_code"]

                    ==

                    actual["weather_code"]

                )

        }

        db.save_error(error)

        success += 1

        print("   ✓ Error calculated\n")

    print("=" * 65)

    print("Processed :", total)

    print("Successful:", success)

    print("Skipped   :", failed)

    print("=" * 65)

    db.close()


if __name__ == "__main__":
    main()