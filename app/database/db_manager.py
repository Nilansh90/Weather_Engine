"""
app/database/db_manager.py

Repository class responsible for reading historical weather data
from PostgreSQL.

It abstracts SQL queries away from the rest of the application.

Used by:
    - FeaturePipeline
    - InferenceOrchestrator
    - Flask dashboard
    - Error calculations
"""
import numpy as np
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
import os
from sqlalchemy import text
from datetime import date, timedelta


load_dotenv()


class DatabaseManager:

    def __init__(self):

        database_url = os.getenv("DATABASE_URL")

        if database_url is None:
            raise ValueError(
                "DATABASE_URL not found in .env"
            )

        self.engine = create_engine(database_url)


    ###########################################################
    # CITY INFORMATION
    ###########################################################

    def get_city(self, city_id: int) -> dict:
        """
        Returns latitude, longitude and city name.

        Example
        -------
        {
            'latitude':25.21,
            'longitude':73.73,
            'city_name':'Pilani'
        }
        """

        query = text("""

            SELECT DISTINCT

                latitude,
                longitude,
                city_name

            FROM weather_data

            WHERE city_id = :city_id

            LIMIT 1

        """)

        df = pd.read_sql(

            query,

            self.engine,

            params={

                "city_id": city_id

            }

        )

        if df.empty:
            raise ValueError(

                f"City ID {city_id} not found"

            )

        return df.iloc[0].to_dict()



    ###########################################################
    # OBSERVATION FOR ONE DAY
    ###########################################################

    def get_day(self,
                city_id: int,
                target_date):


        query = text("""

            SELECT *

            FROM weather_data


            WHERE city_id = :city_id


            AND date = :target_date


        """)


        df = pd.read_sql(

            query,

            self.engine,


            params={

                "city_id": city_id,

                "target_date": target_date

            }

        )


        if df.empty:

            raise ValueError(

                f"No data found for city "

                f"{city_id} "

                f"on "

                f"{target_date}"

            )


        return df.iloc[0]



    ###########################################################
    # PREVIOUS N DAYS
    ###########################################################

    def get_last_n_days(self,
                        city_id: int,
                        end_date,
                        n: int):


        query = text("""

            SELECT *

            FROM weather_data


            WHERE city_id = :city_id


            AND date <= :end_date


            ORDER BY date DESC


            LIMIT :n


        """)



        df = pd.read_sql(

            query,

            self.engine,


            params={

                "city_id": city_id,

                "end_date": end_date,

                "n": n

            }

        )


        if df.empty:

            raise ValueError(

                f"No historical data found"

            )


        return df




    ###########################################################
    # ALL CITY IDS
    ###########################################################

    def get_all_city_ids(self):


        query = text("""

            SELECT DISTINCT city_id


            FROM weather_data


            ORDER BY city_id


        """)



        df = pd.read_sql(

            query,

            self.engine

        )



        return (

            df["city_id"]

            .tolist()

        )




    ###########################################################
    # DATE RANGE
    ###########################################################

    def get_between_dates(self,
                          city_id,
                          start_date,
                          end_date):



        query = text("""

            SELECT *


            FROM weather_data


            WHERE city_id = :city_id


            AND date


            BETWEEN


            :start_date


            AND


            :end_date


            ORDER BY date


        """)



        return pd.read_sql(

            query,

            self.engine,


            params={

                "city_id": city_id,

                "start_date": start_date,

                "end_date": end_date

            }

        )



    ###########################################################
    # LATEST DATE AVAILABLE
    ###########################################################

    def latest_date(self):



        query = text("""

            SELECT MAX(date)


            FROM weather_data


        """)



        df = pd.read_sql(

            query,

            self.engine

        )



        return df.iloc[0, 0]




    ###########################################################
    # CLOSE CONNECTION
    ###########################################################

    def close(self):

        self.engine.dispose()

    def get_cached_nwp(
            self,
            latitude,
            longitude,
            forecast_date
    ):

        query = text("""

            SELECT *


            FROM nwp_cache


            WHERE latitude=:lat


            AND longitude=:lon


            AND forecast_date=:date


        """)

        df = pd.read_sql(

            query,

            self.engine,

            params={

                "lat": latitude,

                "lon": longitude,

                "date": forecast_date

            }

        )

        if df.empty:
            return None

        return df.iloc[0].to_dict()

    def save_nwp_cache(

            self,

            nwp

    ):

        query = text("""

        INSERT INTO nwp_cache (

            latitude,
            longitude,
            forecast_date,

            wind_speed_max_kmh,
            wind_gusts_max_kmh,
            wind_direction_dominant_deg,

            wind_dir_sin,
            wind_dir_cos,

            cloud_cover_mean_pct,

            precipitation_sum_mm,

            weather_code,

            created_at

        )

        VALUES(

            :latitude,
            :longitude,
            :forecast_date,

            :wind_speed_max_kmh,
            :wind_gusts_max_kmh,
            :wind_direction_dominant_deg,

            :wind_dir_sin,
            :wind_dir_cos,

            :cloud_cover_mean_pct,

            :precipitation_sum_mm,

            :weather_code,

            NOW()

        )

        ON CONFLICT
        (
            latitude,
            longitude,
            forecast_date
        )

        DO NOTHING

        """)

        with self.engine.begin() as conn:
            clean = {}

            for key, value in nwp.items():

                if isinstance(value, np.generic):

                    clean[key] = value.item()

                else:

                    clean[key] = value

            conn.execute(query, clean)



    def save_prediction(self, prediction):

        query = text("""

        INSERT INTO predictions (

            city_id,
            forecast_date,

            temp_max_c,
            temp_min_c,

            pressure_msl_max_hpa,
            pressure_msl_min_hpa,

            dew_point_max_c,
            dew_point_min_c,

            relative_humidity_max_pct,
            relative_humidity_min_pct,

            wind_speed_max_kmh,
            wind_gusts_max_kmh,
            wind_direction_dominant_deg,

            cloud_cover_mean_pct,

            rain_probability,

            will_rain,

            precipitation_sum_mm,

            weather_code

        )

        VALUES (

            :city_id,
            :forecast_date,

            :temp_max_c,
            :temp_min_c,

            :pressure_msl_max_hpa,
            :pressure_msl_min_hpa,

            :dew_point_max_c,
            :dew_point_min_c,

            :relative_humidity_max_pct,
            :relative_humidity_min_pct,

            :wind_speed_max_kmh,
            :wind_gusts_max_kmh,
            :wind_direction_dominant_deg,

            :cloud_cover_mean_pct,

            :rain_probability,

            :will_rain,

            :precipitation_sum_mm,

            :weather_code

        )

        ON CONFLICT (city_id, forecast_date)

        DO UPDATE SET

            temp_max_c=EXCLUDED.temp_max_c,
            temp_min_c=EXCLUDED.temp_min_c,

            pressure_msl_max_hpa=EXCLUDED.pressure_msl_max_hpa,
            pressure_msl_min_hpa=EXCLUDED.pressure_msl_min_hpa,

            dew_point_max_c=EXCLUDED.dew_point_max_c,
            dew_point_min_c=EXCLUDED.dew_point_min_c,

            relative_humidity_max_pct=EXCLUDED.relative_humidity_max_pct,
            relative_humidity_min_pct=EXCLUDED.relative_humidity_min_pct,

            wind_speed_max_kmh=EXCLUDED.wind_speed_max_kmh,
            wind_gusts_max_kmh=EXCLUDED.wind_gusts_max_kmh,
            wind_direction_dominant_deg=EXCLUDED.wind_direction_dominant_deg,

            cloud_cover_mean_pct=EXCLUDED.cloud_cover_mean_pct,

            rain_probability=EXCLUDED.rain_probability,

            will_rain=EXCLUDED.will_rain,

            precipitation_sum_mm=EXCLUDED.precipitation_sum_mm,

            weather_code=EXCLUDED.weather_code

        """)

        with self.engine.begin() as conn:
            conn.execute(query, prediction)

    def get_prediction(
            self,
            city_id,
            forecast_date
    ):

        query = text("""

        SELECT *

        FROM predictions

        WHERE city_id=:city_id

        AND forecast_date=:forecast_date

        """)

        df = pd.read_sql(

            query,

            self.engine,

            params={

                "city_id": city_id,

                "forecast_date": forecast_date

            }

        )

        if df.empty:
            return None

        return df.iloc[0].to_dict()

    def save_metrics(self, metrics):

        query = text("""

        INSERT INTO metrics(

            city_id,

            forecast_date,

            temp_mae,

            pressure_mae,

            dew_mae,

            rh_mae,

            rain_correct,

            weather_correct

        )

        VALUES(

            :city_id,

            :forecast_date,

            :temp_mae,

            :pressure_mae,

            :dew_mae,

            :rh_mae,

            :rain_correct,

            :weather_correct

        )

        """)

        with self.engine.begin() as conn:
            conn.execute(query, metrics)

    def get_metrics(
            self,
            city_id,
            forecast_date
    ):

        query = text("""

        SELECT *

        FROM metrics

        WHERE city_id=:city_id

        AND forecast_date=:forecast_date

        ORDER BY created_at DESC

        LIMIT 1

        """)

        df = pd.read_sql(

            query,

            self.engine,

            params={

                "city_id": city_id,

                "forecast_date": forecast_date

            }

        )

        if df.empty:
            return None

        return df.iloc[0].to_dict()

    def update_actual(
            self,
            city_id,
            target_date,
            actual
    ):

        query = text("""

        UPDATE weather_data

        SET

            weather_code=:weather_code,

            temp_mean_c=:temp_mean_c,

            temp_max_c=:temp_max_c,

            temp_min_c=:temp_min_c,

            wind_speed_max_kmh=:wind_speed_max_kmh,

            wind_gusts_max_kmh=:wind_gusts_max_kmh,

            wind_direction_dominant_deg=:wind_direction_dominant_deg,

            shortwave_radiation_sum_mj_m2=:shortwave_radiation_sum_mj_m2,

            daylight_duration_s=:daylight_duration_s,

            precipitation_sum_mm=:precipitation_sum_mm,

            cloud_cover_mean_pct=:cloud_cover_mean_pct,

            cloud_cover_max_pct=:cloud_cover_max_pct,

            cloud_cover_min_pct=:cloud_cover_min_pct,

            dew_point_mean_c=:dew_point_mean_c,

            dew_point_max_c=:dew_point_max_c,

            dew_point_min_c=:dew_point_min_c,

            relative_humidity_mean_pct=:relative_humidity_mean_pct,

            relative_humidity_max_pct=:relative_humidity_max_pct,

            relative_humidity_min_pct=:relative_humidity_min_pct,

            pressure_msl_mean_hpa=:pressure_msl_mean_hpa,

            pressure_msl_max_hpa=:pressure_msl_max_hpa,

            pressure_msl_min_hpa=:pressure_msl_min_hpa

        WHERE city_id=:city_id

        AND date=:target_date

        """)

        params = actual.copy()

        params["city_id"] = city_id

        params["target_date"] = target_date

        with self.engine.begin() as conn:
            conn.execute(query, params)

    def get_all_cities(self):

        query = """
            SELECT
                city_id,
                city_name,
                latitude,
                longitude
            FROM weather_data
            GROUP BY
                city_id,
                city_name,
                latitude,
                longitude
            ORDER BY city_id;
        """

        df = pd.read_sql(query, self.engine)

        return df.to_dict(orient="records")

    def get_cached_nwp(
            self,
            latitude,
            longitude,
            forecast_date
    ):

        query = text("""
            SELECT *
            FROM nwp_cache
            WHERE
                ABS(latitude - :latitude) < 0.001
            AND ABS(longitude - :longitude) < 0.001
            AND forecast_date = :forecast_date
            LIMIT 1
        """)

        df = pd.read_sql(
            query,
            self.engine,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "forecast_date": forecast_date
            }
        )

        if df.empty:
            return None

        return df.iloc[0].to_dict()

    def get_cached_nwp_or_raise(
            self,
            latitude,
            longitude,
            forecast_date
    ):

        nwp = self.get_cached_nwp(
            latitude,
            longitude,
            forecast_date
        )

        if nwp is None:
            raise RuntimeError(
                "NWP cache missing.\n"
                "Run fetch_weather.py first."
            )

        return nwp

    from sqlalchemy import text

    def get_actual_weather(
            self,
            city_id,
            forecast_date
    ):

        with self.engine.connect() as conn:
            row = conn.execute(

                text("""

                SELECT *

                FROM weather_data

                WHERE

                    city_id = :city_id

                AND

                    date = :forecast_date

                LIMIT 1

                """),

                {

                    "city_id": city_id,

                    "forecast_date": forecast_date

                }

            ).mappings().first()

        return row

    from sqlalchemy import text

    def update_actuals(
            self,
            city_id,
            forecast_date,
            actual
    ):

        query = text("""

            UPDATE predictions

            SET

                actual_temp_max_c = :temp_max_c,
                actual_temp_min_c = :temp_min_c,

                actual_pressure_msl_max_hpa = :pressure_max,
                actual_pressure_msl_min_hpa = :pressure_min,

                actual_dew_point_max_c = :dew_max,
                actual_dew_point_min_c = :dew_min,

                actual_relative_humidity_max_pct = :humidity_max,
                actual_relative_humidity_min_pct = :humidity_min,

                actual_wind_speed_max_kmh = :wind_speed,
                actual_wind_gusts_max_kmh = :wind_gust,
                actual_wind_direction_dominant_deg = :wind_direction,

                actual_cloud_cover_mean_pct = :cloud_cover,

                actual_precipitation_sum_mm = :rain,

                actual_weather_code = :weather_code,

                actual_updated_at = NOW()

            WHERE

                city_id = :city_id

            AND forecast_date = :forecast_date

        """)

        with self.engine.begin() as conn:
            conn.execute(

                query,

                {

                    "city_id": city_id,

                    "forecast_date": forecast_date,

                    "temp_max_c": actual["temp_max_c"],
                    "temp_min_c": actual["temp_min_c"],

                    "pressure_max": actual["pressure_msl_max_hpa"],
                    "pressure_min": actual["pressure_msl_min_hpa"],

                    "dew_max": actual["dew_point_max_c"],
                    "dew_min": actual["dew_point_min_c"],

                    "humidity_max": actual["relative_humidity_max_pct"],
                    "humidity_min": actual["relative_humidity_min_pct"],

                    "wind_speed": actual["wind_speed_max_kmh"],
                    "wind_gust": actual["wind_gusts_max_kmh"],
                    "wind_direction": actual["wind_direction_dominant_deg"],

                    "cloud_cover": actual["cloud_cover_mean_pct"],

                    "rain": actual["precipitation_sum_mm"],

                    "weather_code": actual["weather_code"]

                }

            )

    def get_predictions_without_errors(self):

        with self.engine.connect() as conn:
            total = conn.execute(text("SELECT COUNT(*) FROM predictions")).scalar()

            # print("Predictions table count:", total)

            past = conn.execute(text("""
                SELECT COUNT(*)
                FROM predictions
                WHERE forecast_date < CURRENT_DATE
            """)).scalar()

            # print("Past predictions:", past)

            rows = conn.execute(text("""
                SELECT p.*
                FROM predictions p
                LEFT JOIN errors e
                  ON p.city_id = e.city_id
                 AND p.forecast_date = e.forecast_date
                WHERE e.id IS NULL
                  AND p.forecast_date < CURRENT_DATE
            """))

            result = rows.mappings().all()

            # print("Returned rows:", len(result))

            return result

    def save_error(
            self,
            error
    ):

        with self.engine.begin() as conn:
            conn.execute(

                text("""

                INSERT INTO errors(

                    city_id,
                    forecast_date,

                    temp_max_error,
                    temp_min_error,

                    pressure_max_error,
                    pressure_min_error,

                    dew_point_max_error,
                    dew_point_min_error,

                    humidity_max_error,
                    humidity_min_error,

                    wind_speed_error,
                    wind_gust_error,

                    cloud_cover_error,

                    precipitation_error,

                    rain_correct,

                    weather_code_correct

                )

                VALUES(

                    :city_id,
                    :forecast_date,

                    :temp_max_error,
                    :temp_min_error,

                    :pressure_max_error,
                    :pressure_min_error,

                    :dew_point_max_error,
                    :dew_point_min_error,

                    :humidity_max_error,
                    :humidity_min_error,

                    :wind_speed_error,
                    :wind_gust_error,

                    :cloud_cover_error,

                    :precipitation_error,

                    :rain_correct,

                    :weather_code_correct

                )

                ON CONFLICT

                (city_id,forecast_date)

                DO NOTHING

                """),

                error

            )

    from sqlalchemy import text

    ...

    def get_error(
        self,
        city_id,
        forecast_date
        ):

        with self.engine.connect() as conn:

            row = conn.execute(

            text("""

            SELECT *

            FROM errors

            WHERE

                city_id = :city_id

            AND

                forecast_date = :forecast_date

            LIMIT 1

            """),

            {

                "city_id": city_id,

                "forecast_date": forecast_date

            }

        ).mappings().first()

        if row is None:

            return None

        return {

        "temp_mae":

            (

                (row["temp_max_error"] or 0)

                +

                (row["temp_min_error"] or 0)

            ) / 2,

        "pressure_mae":

            (

                (row["pressure_max_error"] or 0)

                +

                (row["pressure_min_error"] or 0)

            ) / 2,

        "dew_mae":

            (

                (row["dew_point_max_error"] or 0)

                +

                (row["dew_point_min_error"] or 0)

            ) / 2,

        "rh_mae":

            (

                (row["humidity_max_error"] or 0)

                +

                (row["humidity_min_error"] or 0)

            ) / 2,

        "rain_correct":

            row["rain_correct"],

        "weather_correct":

            row["weather_code_correct"]

    }


    ###########################################################
    # FLASK HOME PAGE
    ###########################################################

    def get_home_context(self):

        forecast_date = self._next_forecast_date()

        return {
            "forecast_date": forecast_date,
            "cities": self._get_home_city_forecasts(forecast_date),
            "pipeline": self._get_home_pipeline(forecast_date),
            "engine": self._get_home_engine(),
            "metrics": self._get_home_metrics(),
            "quality": self._get_home_quality(),
            "health": self._get_home_health(forecast_date)
        }

    def _next_forecast_date(self):

        latest_prediction_date = self._scalar("""
            SELECT MAX(forecast_date)
            FROM predictions
        """)

        if latest_prediction_date is not None:
            return latest_prediction_date

        latest_weather_date = self.latest_date()

        if latest_weather_date is None:
            return date.today() + timedelta(days=1)

        return latest_weather_date + timedelta(days=1)

    def _get_home_city_forecasts(self, forecast_date):

        rows = self._rows("""
            SELECT
                p.city_id,
                COALESCE(c.city_name, 'City ' || p.city_id) AS city_name,
                p.forecast_date,
                p.temp_max_c,
                p.temp_min_c,
                p.pressure_msl_max_hpa,
                p.pressure_msl_min_hpa,
                p.relative_humidity_max_pct,
                p.relative_humidity_min_pct,
                p.wind_speed_max_kmh,
                p.cloud_cover_mean_pct,
                p.rain_probability,
                p.weather_code,
                p.precipitation_sum_mm,
                e.temp_max_error,
                e.temp_min_error,
                e.pressure_max_error,
                e.pressure_min_error,
                e.rain_correct,
                e.weather_code_correct
            FROM predictions p
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = p.city_id
            LEFT JOIN errors e
                ON e.city_id = p.city_id
               AND e.forecast_date = p.forecast_date - INTERVAL '1 day'
            WHERE p.forecast_date = :forecast_date
            ORDER BY p.city_id
        """, {"forecast_date": forecast_date})

        return [
            {
                "city_name": row["city_name"],
                "prediction": self._format_home_prediction(row),
                "performance": self._format_home_performance(row)
            }
            for row in rows
        ]

    def _format_home_prediction(self, row):

        temp_max = self._round(row["temp_max_c"])
        temp_min = self._round(row["temp_min_c"])
        humidity_max = self._round(row["relative_humidity_max_pct"])
        humidity_min = self._round(row["relative_humidity_min_pct"])
        pressure_max = self._round(row["pressure_msl_max_hpa"])
        pressure_min = self._round(row["pressure_msl_min_hpa"])
        weather_code = row["weather_code"]

        return {
            "weather_icon": self._weather_icon(weather_code),
            "confidence": self._forecast_confidence(row),
            "temperature": self._average(temp_max, temp_min),
            "weather_summary": self._weather_summary(weather_code),
            "temp_max": temp_max,
            "temp_min": temp_min,
            "humidity": self._average(humidity_max, humidity_min),
            "rain_probability": self._round(row["rain_probability"]),
            "wind_speed": self._round(row["wind_speed_max_kmh"]),
            "pressure": self._average(pressure_max, pressure_min),
            "cloud_cover": self._round(row["cloud_cover_mean_pct"]),
            "weather_code": weather_code,
            "generated_time": self._format_date(row["forecast_date"])
        }

    def _format_home_performance(self, row):

        temp_mae = self._average_abs(
            row["temp_max_error"],
            row["temp_min_error"]
        )
        pressure_mae = self._average_abs(
            row["pressure_max_error"],
            row["pressure_min_error"]
        )
        weather_accuracy = 100 if row["weather_code_correct"] else 0

        return {
            "temp_mae": temp_mae,
            "temp_mae_class": self._mae_class(temp_mae, 2),
            "pressure_mae": pressure_mae,
            "pressure_mae_class": self._mae_class(pressure_mae, 3),
            "weather_accuracy": weather_accuracy,
            "weather_accuracy_class": self._accuracy_class(weather_accuracy),
            "rain_correct": "Yes" if row["rain_correct"] else "No",
            "rain_correct_class": "text-success" if row["rain_correct"] else "text-danger"
        }

    def _get_home_pipeline(self, forecast_date):

        prediction_count = self._scalar("""
            SELECT COUNT(*)
            FROM predictions
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        city_count = self._scalar("""
            SELECT COUNT(DISTINCT city_id)
            FROM weather_data
        """)

        nwp_count = self._scalar("""
            SELECT COUNT(*)
            FROM nwp_cache
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        error_count = self._scalar("""
            SELECT COUNT(*)
            FROM errors
            WHERE forecast_date = :evaluation_date
        """, {"evaluation_date": forecast_date - timedelta(days=1)})

        return {
            "recharge_time": self._latest_table_time("weather_data"),
            "cache_time": self._latest_table_time("nwp_cache"),
            "feature_time": "Derived",
            "inference_time": self._latest_table_time("predictions"),
            "storage_time": self._latest_table_time("predictions"),
            "evaluation_time": self._latest_table_time("errors"),
            "email_time": "Queued",
            "health_time": self._format_date(date.today()),
            "cities_processed": prediction_count or city_count or 0,
            "predictions": prediction_count or 0,
            "runtime": "Database",
            "database_writes": (prediction_count or 0) + (error_count or 0),
            "success_rate": self._percent(prediction_count, city_count),
            "cache_entries": nwp_count or 0
        }

    def _get_home_metrics(self):

        row = self._row("""
            SELECT
                AVG(ABS(temp_max_error) + ABS(temp_min_error)) / 2 AS temperature_mae,
                AVG(ABS(pressure_max_error) + ABS(pressure_min_error)) / 2 AS pressure_mae,
                AVG(ABS(dew_point_max_error) + ABS(dew_point_min_error)) / 2 AS moisture_mae,
                AVG(CASE WHEN rain_correct THEN 1.0 ELSE 0.0 END) * 100 AS rain_accuracy,
                AVG(CASE WHEN weather_code_correct THEN 1.0 ELSE 0.0 END) * 100 AS weather_accuracy
            FROM errors
        """)

        prediction_count = self._scalar("SELECT COUNT(*) FROM predictions")
        error_count = self._scalar("SELECT COUNT(*) FROM errors")

        temperature_mae = self._round(row["temperature_mae"])
        pressure_mae = self._round(row["pressure_mae"])
        moisture_mae = self._round(row["moisture_mae"])
        rain_accuracy = self._round(row["rain_accuracy"])
        weather_accuracy = self._round(row["weather_accuracy"])
        pipeline_success = self._percent(error_count, prediction_count)

        return {
            "temperature_mae": temperature_mae,
            "temperature_trend": "Live",
            "temperature_trend_class": self._mae_class(temperature_mae, 2),
            "pressure_mae": pressure_mae,
            "pressure_trend": "Live",
            "pressure_trend_class": self._mae_class(pressure_mae, 3),
            "moisture_mae": moisture_mae,
            "moisture_trend": "Live",
            "moisture_trend_class": self._mae_class(moisture_mae, 5),
            "rain_accuracy": rain_accuracy,
            "rain_trend": "Live",
            "rain_trend_class": self._accuracy_class(rain_accuracy),
            "weather_accuracy": weather_accuracy,
            "weather_trend": "Live",
            "weather_trend_class": self._accuracy_class(weather_accuracy),
            "pipeline_success": pipeline_success,
            "pipeline_trend": "Live",
            "pipeline_trend_class": self._accuracy_class(pipeline_success)
        }

    def _get_home_quality(self):

        metrics = self._get_home_metrics()

        return {
            "temperature": self._quality_from_mae(metrics["temperature_mae"], 10),
            "pressure": self._quality_from_mae(metrics["pressure_mae"], 10),
            "moisture": self._quality_from_mae(metrics["moisture_mae"], 20),
            "rain": metrics["rain_accuracy"],
            "weather": metrics["weather_accuracy"]
        }

    def _get_home_health(self, forecast_date):

        prediction_count = self._scalar("""
            SELECT COUNT(*)
            FROM predictions
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        nwp_count = self._scalar("""
            SELECT COUNT(*)
            FROM nwp_cache
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        return {
            "models_loaded": "Live",
            "models_badge": "badge-success",
            "database": "Connected",
            "database_badge": "badge-success",
            "scheduler": "Operational",
            "scheduler_badge": "badge-success",
            "email": "Configured",
            "email_badge": "badge-success",
            "cache": "Ready" if nwp_count else "Empty",
            "cache_badge": "badge-success" if nwp_count else "badge-warning",
            "forecast_badge": "badge-success" if prediction_count else "badge-warning"
        }

    def _get_home_engine(self):

        return {
            "historical": self._home_model_card("Historical Data", "database", "weather_data observations.", "PostgreSQL", "Cities", "Features"),
            "features": self._home_model_card("Feature Engineering", "sliders", "Temporal and NWP features.", "Pipeline", "Raw data", "Feature set"),
            "temperature": self._home_model_card("Temperature", "thermometer-half", "Temperature model.", "Regression", "Features", "Temperature"),
            "pressure": self._home_model_card("Pressure", "speedometer2", "Pressure model.", "Regression", "Features", "Pressure"),
            "moisture": self._home_model_card("Moisture", "droplet", "Moisture model.", "Regression", "Temperature, Pressure", "Humidity"),
            "rain": self._home_model_card("Rain", "cloud-rain", "Rain classifier.", "Classification", "Moisture", "Rain probability"),
            "weather": self._home_model_card("Weather Code", "cloud-sun", "Weather code classifier.", "Classification", "Rain", "Weather code"),
            "consensus": self._home_model_card("Consensus", "check2-circle", "Validation layer.", "Rules", "Model outputs", "Validated forecast"),
            "forecast": self._home_model_card("Forecast", "graph-up-arrow", "Stored city forecast.", "PostgreSQL", "Validated forecast", "Home cards"),
            "summary": [
                {"icon": "database", "label": f"{self._scalar('SELECT COUNT(*) FROM predictions') or 0} stored predictions"},
                {"icon": "geo-alt", "label": f"{self._scalar('SELECT COUNT(DISTINCT city_id) FROM weather_data') or 0} configured cities"},
                {"icon": "clipboard-data", "label": f"{self._scalar('SELECT COUNT(*) FROM errors') or 0} evaluated forecasts"}
            ]
        }

    def _home_model_card(self, name, icon, description, model_type, inputs, outputs):

        return {
            "name": name,
            "icon": icon,
            "description": description,
            "type": model_type,
            "inputs": inputs,
            "outputs": outputs,
            "status": "Live"
        }

    def _latest_table_time(self, table_name):

        columns = self._table_columns(table_name)

        if "created_at" in columns:
            value = self._scalar(f"SELECT MAX(created_at) FROM {table_name}")
            return self._format_date(value)

        if table_name == "weather_data":
            value = self._scalar("SELECT MAX(date) FROM weather_data")
            return self._format_date(value)

        if table_name == "predictions":
            value = self._scalar("SELECT MAX(forecast_date) FROM predictions")
            return self._format_date(value)

        if table_name == "errors":
            value = self._scalar("SELECT MAX(forecast_date) FROM errors")
            return self._format_date(value)

        return "-"

    def _table_columns(self, table_name):

        rows = self._rows("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_schema = 'public'
            AND table_name = :table_name
        """, {"table_name": table_name})

        return {row["column_name"] for row in rows}

    def _scalar(self, query, params=None):

        with self.engine.connect() as conn:
            return conn.execute(text(query), params or {}).scalar()

    def _row(self, query, params=None):

        with self.engine.connect() as conn:
            row = conn.execute(text(query), params or {}).mappings().first()

        if row is None:
            return {}

        return dict(row)

    def _rows(self, query, params=None):

        with self.engine.connect() as conn:
            rows = conn.execute(text(query), params or {}).mappings().all()

        return [dict(row) for row in rows]

    def _round(self, value, digits=1):

        if value is None:
            return 0

        return round(float(value), digits)

    def _average(self, *values):

        clean = [float(value) for value in values if value is not None]

        if not clean:
            return 0

        return round(sum(clean) / len(clean), 1)

    def _average_abs(self, *values):

        clean = [abs(float(value)) for value in values if value is not None]

        if not clean:
            return 0

        return round(sum(clean) / len(clean), 2)

    def _percent(self, numerator, denominator):

        if not numerator or not denominator:
            return 0

        return round((float(numerator) / float(denominator)) * 100)

    def _quality_from_mae(self, value, scale):

        return max(0, min(100, round(100 - ((value or 0) / scale) * 100)))

    def _mae_class(self, value, threshold):

        if value is None:
            return "text-muted"

        return "text-success" if value <= threshold else "text-warning"

    def _accuracy_class(self, value):

        if value is None:
            return "text-muted"

        return "text-success" if value >= 70 else "text-warning"

    def _forecast_confidence(self, row):

        rain_probability = row["rain_probability"] or 0
        precipitation = row["precipitation_sum_mm"] or 0

        if precipitation > 0 and rain_probability >= 50:
            return 90

        if precipitation == 0 and rain_probability < 50:
            return 85

        return 75

    def _weather_icon(self, weather_code):

        if weather_code in (0,):
            return "sun"

        if weather_code in (1, 2):
            return "cloud-sun"

        if weather_code in (3,):
            return "cloud"

        if weather_code in (51, 53, 55, 61, 63, 65, 80, 81, 82):
            return "cloud-rain"

        return "cloud-sun"

    def _weather_summary(self, weather_code):

        summaries = {
            0: "Clear sky",
            1: "Mainly clear",
            2: "Partly cloudy",
            3: "Overcast",
            51: "Light drizzle",
            53: "Moderate drizzle",
            55: "Dense drizzle",
            61: "Slight rain",
            63: "Moderate rain",
            65: "Heavy rain",
            80: "Rain showers",
            81: "Moderate showers",
            82: "Violent showers"
        }

        return summaries.get(weather_code, f"Weather code {weather_code}")

    def _format_date(self, value):

        if value is None:
            return "-"

        if hasattr(value, "strftime"):
            return value.strftime("%Y-%m-%d")

        return str(value)


    ###########################################################
    # FLASK DASHBOARD PAGE
    ###########################################################

    def get_dashboard_context(self):

        return {
            "metrics": self.get_dashboard_metrics(),
            "pipeline": self.get_pipeline_status(),
            "predictions": self.get_latest_predictions(5),
            "errors": self.get_recent_errors(5),
            "city_summary": self.get_city_summary()
        }

    def get_dashboard_metrics(self, forecast_date):

        error_metrics = self._get_home_metrics()

        city_count = self._scalar("""
            SELECT COUNT(DISTINCT city_id)
            FROM weather_data
        """)

        prediction_count = self._scalar("""
            SELECT COUNT(*)
            FROM predictions
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        return {
            "temperature_mae": error_metrics["temperature_mae"],
            "pressure_mae": error_metrics["pressure_mae"],
            "moisture_mae": error_metrics["moisture_mae"],
            "rain_accuracy": error_metrics["rain_accuracy"],
            "weather_accuracy": error_metrics["weather_accuracy"],
            "runtime": self._dashboard_runtime_label(forecast_date),
            "cities": city_count or 0,
            "predictions": prediction_count or 0
        }

    def _get_dashboard_model_performance(self):

        row = self._row("""
            SELECT
                AVG(ABS(temp_max_error) + ABS(temp_min_error)) / 2 AS temperature_mae,
                AVG(ABS(pressure_max_error) + ABS(pressure_min_error)) / 2 AS pressure_mae,
                AVG(ABS(dew_point_max_error) + ABS(dew_point_min_error)) / 2 AS dew_mae,
                AVG(ABS(humidity_max_error) + ABS(humidity_min_error)) / 2 AS humidity_mae,
                AVG(CASE WHEN rain_correct THEN 1.0 ELSE 0.0 END) * 100 AS rain_accuracy,
                AVG(CASE WHEN weather_code_correct THEN 1.0 ELSE 0.0 END) * 100 AS weather_accuracy,
                MAX(forecast_date) AS latest_evaluation
            FROM errors
        """)

        moisture_mae = self._average(
            self._round(row["dew_mae"]),
            self._round(row["humidity_mae"])
        )
        latest_evaluation = self._format_date(row["latest_evaluation"])

        return {
            "temperature": self._dashboard_model_card(
                f"MAE {self._round(row['temperature_mae'])}",
                latest_evaluation,
                15,
                self._mae_indicator(row["temperature_mae"], 2)
            ),
            "pressure": self._dashboard_model_card(
                f"MAE {self._round(row['pressure_mae'])}",
                latest_evaluation,
                15,
                self._mae_indicator(row["pressure_mae"], 3)
            ),
            "moisture": self._dashboard_model_card(
                f"MAE {moisture_mae}",
                latest_evaluation,
                19,
                self._mae_indicator(moisture_mae, 5)
            ),
            "rain": self._dashboard_model_card(
                f"{self._round(row['rain_accuracy'])}%",
                latest_evaluation,
                21,
                self._accuracy_indicator(row["rain_accuracy"])
            ),
            "weather_code": self._dashboard_model_card(
                f"{self._round(row['weather_accuracy'])}%",
                latest_evaluation,
                23,
                self._accuracy_indicator(row["weather_accuracy"])
            )
        }

    def _dashboard_model_card(self, score, training_date, features, indicator):

        return {
            "score": score,
            "training_date": training_date,
            "status": "Evaluated",
            "features": features,
            "indicator": indicator
        }

    def _get_dashboard_pipeline(self, forecast_date):

        return {
            "recharge_time": self._latest_table_time("weather_data"),
            "cache_time": self._latest_table_time("nwp_cache"),
            "prediction_time": self._latest_table_time("predictions"),
            "evaluation_time": self._latest_table_time("errors"),
            "email_time": self._dashboard_email_time(forecast_date)
        }

    def _get_dashboard_city_metrics(self):

        rows = self._rows("""
            SELECT
                e.city_id,
                COALESCE(c.city_name, 'City ' || e.city_id) AS city_name,
                AVG(ABS(e.temp_max_error) + ABS(e.temp_min_error)) / 2 AS temperature_mae,
                AVG(ABS(e.pressure_max_error) + ABS(e.pressure_min_error)) / 2 AS pressure_mae,
                AVG(CASE WHEN e.rain_correct THEN 1.0 ELSE 0.0 END) * 100 AS rain_accuracy,
                AVG(CASE WHEN e.weather_code_correct THEN 1.0 ELSE 0.0 END) * 100 AS weather_accuracy,
                COUNT(*) AS forecast_count
            FROM errors e
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = e.city_id
            GROUP BY
                e.city_id,
                c.city_name
            ORDER BY e.city_id
        """)

        return [
            {
                "name": row["city_name"],
                "temperature_mae": self._round(row["temperature_mae"]),
                "pressure_mae": self._round(row["pressure_mae"]),
                "rain_accuracy": self._round(row["rain_accuracy"]),
                "weather_accuracy": self._round(row["weather_accuracy"]),
                "forecast_count": row["forecast_count"],
                "status": self._city_status(row)
            }
            for row in rows
        ]

    def _get_dashboard_latest_forecasts(self, limit=10):

        timestamp_column = self._prediction_timestamp_column()
        prediction_time_sql = (
            f"p.{timestamp_column}"
            if timestamp_column is not None
            else "p.forecast_date"
        )

        rows = self._rows(f"""
            SELECT
                p.city_id,
                COALESCE(c.city_name, 'City ' || p.city_id) AS city_name,
                p.forecast_date,
                p.temp_max_c,
                p.temp_min_c,
                p.pressure_msl_max_hpa,
                p.pressure_msl_min_hpa,
                p.relative_humidity_max_pct,
                p.relative_humidity_min_pct,
                p.rain_probability,
                p.weather_code,
                {prediction_time_sql} AS prediction_time
            FROM predictions p
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = p.city_id
            ORDER BY
                p.forecast_date DESC,
                p.city_id
            LIMIT :limit
        """, {"limit": limit})

        return [
            {
                "city": row["city_name"],
                "forecast_date": self._format_date(row["forecast_date"]),
                "temperature": self._average(
                    self._round(row["temp_max_c"]),
                    self._round(row["temp_min_c"])
                ),
                "pressure": self._average(
                    self._round(row["pressure_msl_max_hpa"]),
                    self._round(row["pressure_msl_min_hpa"])
                ),
                "humidity": self._average(
                    self._round(row["relative_humidity_max_pct"]),
                    self._round(row["relative_humidity_min_pct"])
                ),
                "rain_probability": self._round(row["rain_probability"]),
                "weather_code": row["weather_code"],
                "prediction_time": self._format_date(row["prediction_time"]),
                "status": "Stored"
            }
            for row in rows
        ]

    def _dashboard_runtime_label(self, forecast_date):

        prediction_count = self._scalar("""
            SELECT COUNT(*)
            FROM predictions
            WHERE forecast_date = :forecast_date
        """, {"forecast_date": forecast_date})

        if prediction_count:
            return f"{prediction_count} records"

        return "No run"

    def _dashboard_email_time(self, forecast_date):

        error_count = self._scalar("""
            SELECT COUNT(*)
            FROM errors
            WHERE forecast_date = :evaluation_date
        """, {"evaluation_date": forecast_date - timedelta(days=1)})

        if error_count:
            return self._format_date(forecast_date - timedelta(days=1))

        return "-"

    def _prediction_timestamp_column(self):

        columns = self._table_columns("predictions")

        for column in ("created_at", "prediction_generated", "updated_at"):
            if column in columns:
                return column

        return None

    def _city_status(self, row):

        rain_accuracy = row["rain_accuracy"] or 0
        weather_accuracy = row["weather_accuracy"] or 0
        temperature_mae = row["temperature_mae"] or 0
        pressure_mae = row["pressure_mae"] or 0

        if (
                rain_accuracy >= 70
                and weather_accuracy >= 70
                and temperature_mae <= 3
                and pressure_mae <= 5
        ):
            return "Healthy"

        return "Watch"

    def _mae_indicator(self, value, threshold):

        if value is None:
            return "No evaluations"

        if float(value) <= threshold:
            return "Within target"

        return "Needs review"

    def _accuracy_indicator(self, value):

        if value is None:
            return "No evaluations"

        if float(value) >= 70:
            return "Within target"

        return "Needs review"


    ###########################################################
    # FLASK HISTORY PAGE
    ###########################################################

    def get_history_context(self, args):

        filters = self._history_filters(args)
        forecasts = self._get_history_forecasts(filters)

        return {
            "cities": self._get_history_cities(),
            "filters": filters,
            "weather_codes": self._get_history_weather_codes(),
            "summary": self._get_history_summary(filters),
            "forecasts": forecasts,
            "selected_forecast": self._get_history_selected_forecast(
                args.get("forecast_id"),
                forecasts
            ),
            "accuracy": self._get_history_accuracy(),
            "history_events": self._get_history_events()
        }

    def _history_filters(self, args):

        return {
            "city": args.get("city", ""),
            "city_dropdown": args.get("city_dropdown", ""),
            "date_range": args.get("date_range", ""),
            "from_date": args.get("from_date", ""),
            "to_date": args.get("to_date", ""),
            "weather_code": args.get("weather_code", ""),
            "status": args.get("status", "")
        }

    def _get_history_cities(self):

        rows = self._rows("""
            SELECT
                city_id,
                MAX(city_name) AS city_name
            FROM weather_data
            GROUP BY city_id
            ORDER BY city_id
        """)

        return [
            {
                "id": str(row["city_id"]),
                "name": row["city_name"]
            }
            for row in rows
        ]

    def _get_history_weather_codes(self):

        rows = self._rows("""
            SELECT DISTINCT weather_code
            FROM predictions
            WHERE weather_code IS NOT NULL
            ORDER BY weather_code
        """)

        return [
            {
                "value": str(row["weather_code"]),
                "label": self._weather_summary(row["weather_code"])
            }
            for row in rows
        ]

    def _get_history_forecasts(self, filters, limit=100):

        where_sql, params = self._history_where(filters)
        params["limit"] = limit

        rows = self._rows(f"""
            SELECT
                p.city_id,
                COALESCE(c.city_name, 'City ' || p.city_id) AS city_name,
                p.forecast_date,
                p.temp_max_c,
                p.temp_min_c,
                p.pressure_msl_max_hpa,
                p.pressure_msl_min_hpa,
                p.rain_probability,
                p.weather_code,
                a.temp_max_c AS actual_temp_max_c,
                a.temp_min_c AS actual_temp_min_c,
                e.rain_correct,
                e.weather_code_correct
            FROM predictions p
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = p.city_id
            LEFT JOIN weather_data a
                ON a.city_id = p.city_id
               AND a.date = p.forecast_date
            LEFT JOIN errors e
                ON e.city_id = p.city_id
               AND e.forecast_date = p.forecast_date
            {where_sql}
            ORDER BY
                p.forecast_date DESC,
                p.city_id
            LIMIT :limit
        """, params)

        return [self._format_history_row(row) for row in rows]

    def _format_history_row(self, row):

        forecast_id = (
            f"{row['city_id']}|"
            f"{self._format_date(row['forecast_date'])}"
        )

        return {
            "id": forecast_id,
            "forecast_date": self._format_date(row["forecast_date"]),
            "city": row["city_name"],
            "forecast_temp_max": self._round(row["temp_max_c"]),
            "forecast_temp_min": self._round(row["temp_min_c"]),
            "actual_temp_max": self._display_value(row["actual_temp_max_c"]),
            "actual_temp_min": self._display_value(row["actual_temp_min_c"]),
            "pressure": self._average(
                self._round(row["pressure_msl_max_hpa"]),
                self._round(row["pressure_msl_min_hpa"])
            ),
            "rain_probability": self._round(row["rain_probability"]),
            "weather_code": row["weather_code"],
            "status": self._history_status(row)
        }

    def _get_history_summary(self, filters):

        where_sql, params = self._history_where(filters, alias="p")

        forecast_row = self._row(f"""
            SELECT
                COUNT(*) AS forecasts,
                COUNT(DISTINCT p.city_id) AS cities
            FROM predictions p
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = p.city_id
            LEFT JOIN errors e
                ON e.city_id = p.city_id
               AND e.forecast_date = p.forecast_date
            {where_sql}
        """, params)

        metric_row = self._row(f"""
            SELECT
                AVG(ABS(e.temp_max_error) + ABS(e.temp_min_error)) / 2 AS temp_mae,
                AVG(ABS(e.pressure_max_error) + ABS(e.pressure_min_error)) / 2 AS pressure_mae,
                AVG(CASE WHEN e.rain_correct THEN 1.0 ELSE 0.0 END) * 100 AS rain_accuracy,
                AVG(CASE WHEN e.weather_code_correct THEN 1.0 ELSE 0.0 END) * 100 AS weather_accuracy
            FROM predictions p
            LEFT JOIN (
                SELECT
                    city_id,
                    MAX(city_name) AS city_name
                FROM weather_data
                GROUP BY city_id
            ) c ON c.city_id = p.city_id
            INNER JOIN errors e
                ON e.city_id = p.city_id
               AND e.forecast_date = p.forecast_date
            {where_sql}
        """, params)

        return {
            "forecasts": forecast_row["forecasts"] or 0,
            "cities": forecast_row["cities"] or 0,
            "temp_mae": self._round(metric_row["temp_mae"]),
            "pressure_mae": self._round(metric_row["pressure_mae"]),
            "rain_accuracy": self._round(metric_row["rain_accuracy"]),
            "weather_accuracy": self._round(metric_row["weather_accuracy"])
        }

    def _get_history_selected_forecast(self, forecast_id, forecasts):

        row = None

        if forecast_id:
            row = self._get_history_selected_row(forecast_id)

        if row is None and forecasts:
            row = self._get_history_selected_row(forecasts[0]["id"])

        if row is None:
            return {
                "status": "-",
                "forecast_date": "-",
                "prediction_generated": "-",
                "forecast_temperature": "-",
                "actual_temperature": "-",
                "pressure": "-",
                "humidity": "-",
                "rain_probability": "-",
                "weather_code": "-"
            }

        return {
            "status": self._history_status(row),
            "forecast_date": self._format_date(row["forecast_date"]),
            "prediction_generated": self._format_date(
                row.get("prediction_time")
            ),
            "forecast_temperature": (
                f"{self._round(row['temp_max_c'])} / "
                f"{self._round(row['temp_min_c'])}"
            ),
            "actual_temperature": (
                f"{self._display_value(row['actual_temp_max_c'])} / "
                f"{self._display_value(row['actual_temp_min_c'])}"
            ),
            "pressure": self._average(
                self._round(row["pressure_msl_max_hpa"]),
                self._round(row["pressure_msl_min_hpa"])
            ),
            "humidity": self._average(
                self._round(row["relative_humidity_max_pct"]),
                self._round(row["relative_humidity_min_pct"])
            ),
            "rain_probability": self._round(row["rain_probability"]),
            "weather_code": row["weather_code"]
        }

    def _get_history_selected_row(self, forecast_id):

        try:
            city_id, forecast_date = forecast_id.split("|", 1)
        except ValueError:
            return None

        timestamp_column = self._prediction_timestamp_column()
        prediction_time_sql = (
            f"p.{timestamp_column}"
            if timestamp_column is not None
            else "p.forecast_date"
        )

        return self._row(f"""
            SELECT
                p.city_id,
                p.forecast_date,
                p.temp_max_c,
                p.temp_min_c,
                p.pressure_msl_max_hpa,
                p.pressure_msl_min_hpa,
                p.relative_humidity_max_pct,
                p.relative_humidity_min_pct,
                p.rain_probability,
                p.weather_code,
                {prediction_time_sql} AS prediction_time,
                a.temp_max_c AS actual_temp_max_c,
                a.temp_min_c AS actual_temp_min_c,
                e.rain_correct,
                e.weather_code_correct
            FROM predictions p
            LEFT JOIN weather_data a
                ON a.city_id = p.city_id
               AND a.date = p.forecast_date
            LEFT JOIN errors e
                ON e.city_id = p.city_id
               AND e.forecast_date = p.forecast_date
            WHERE p.city_id = :city_id
            AND p.forecast_date = :forecast_date
            LIMIT 1
        """, {
            "city_id": int(city_id),
            "forecast_date": forecast_date
        })

    def _get_history_accuracy(self):

        row = self._row("""
            SELECT
                100 - LEAST(
                    AVG(ABS(temp_max_error) + ABS(temp_min_error)) / 2,
                    100
                ) AS temperature_current,
                100 - LEAST(
                    AVG(ABS(pressure_max_error) + ABS(pressure_min_error)) / 2,
                    100
                ) AS pressure_current,
                AVG(CASE WHEN weather_code_correct THEN 1.0 ELSE 0.0 END) * 100 AS weather_current,
                MAX(forecast_date) AS updated
            FROM errors
        """)

        best = self._row("""
            SELECT
                MAX(100 - LEAST((ABS(temp_max_error) + ABS(temp_min_error)) / 2, 100)) AS temperature_best,
                MAX(100 - LEAST((ABS(pressure_max_error) + ABS(pressure_min_error)) / 2, 100)) AS pressure_best,
                MAX(CASE WHEN weather_code_correct THEN 100 ELSE 0 END) AS weather_best
            FROM errors
        """)

        updated = self._format_date(row["updated"])

        return {
            "temperature": self._accuracy_card(
                row["temperature_current"],
                best["temperature_best"],
                updated
            ),
            "pressure": self._accuracy_card(
                row["pressure_current"],
                best["pressure_best"],
                updated
            ),
            "weather": self._accuracy_card(
                row["weather_current"],
                best["weather_best"],
                updated
            )
        }

    def _accuracy_card(self, current, best, updated):

        current_value = self._round(current)
        best_value = self._round(best)

        return {
            "current": f"{current_value}%",
            "trend": self._accuracy_indicator(current_value),
            "best": f"{best_value}%",
            "updated": updated
        }

    def _get_history_events(self):

        return {
            "forecast_created": self._latest_table_time("predictions"),
            "evaluation_completed": self._latest_table_time("errors"),
            "email_sent": self._dashboard_email_time(self._next_forecast_date()),
            "database_updated": self._latest_table_time("weather_data")
        }

    def _history_where(self, filters, alias="p"):

        clauses = []
        params = {}

        if filters["city"]:
            clauses.append("LOWER(c.city_name) LIKE :city")
            params["city"] = f"%{filters['city'].lower()}%"

        if filters["city_dropdown"]:
            clauses.append(f"{alias}.city_id = :city_id")
            params["city_id"] = int(filters["city_dropdown"])

        if filters["weather_code"]:
            clauses.append(f"{alias}.weather_code = :weather_code")
            params["weather_code"] = int(filters["weather_code"])

        start_date, end_date = self._history_date_bounds(filters)

        if start_date:
            clauses.append(f"{alias}.forecast_date >= :start_date")
            params["start_date"] = start_date

        if end_date:
            clauses.append(f"{alias}.forecast_date <= :end_date")
            params["end_date"] = end_date

        if filters["status"]:
            clauses.append(self._history_status_clause(filters["status"]))

        if not clauses:
            return "", params

        return "WHERE " + " AND ".join(clauses), params

    def _history_date_bounds(self, filters):

        if filters["date_range"] == "7d":
            return date.today() - timedelta(days=7), None

        if filters["date_range"] == "15d":
            return date.today() - timedelta(days=15), None

        if filters["date_range"] == "30d":
            return date.today() - timedelta(days=30), None

        return filters["from_date"] or None, filters["to_date"] or None

    def _history_status_clause(self, status):

        if status == "matched":
            return "e.rain_correct IS TRUE AND e.weather_code_correct IS TRUE"

        if status == "partial":
            return """
                (
                    e.rain_correct IS NOT NULL
                    OR e.weather_code_correct IS NOT NULL
                )
                AND NOT (
                    e.rain_correct IS TRUE
                    AND e.weather_code_correct IS TRUE
                )
            """

        if status == "pending":
            return "e.city_id IS NULL"

        return "1 = 1"

    def _history_status(self, row):

        if row["rain_correct"] is None and row["weather_code_correct"] is None:
            return "Pending"

        if row["rain_correct"] is True and row["weather_code_correct"] is True:
            return "Matched"

        return "Partial"

    def _display_value(self, value):

        if value is None:
            return "-"

        return self._round(value)

    ###########################################################
    # FLASK ENGINE CONTEXT
    ###########################################################

    def get_engine_context(self):

        return {

            "pipeline": self.get_pipeline_statistics(),

            "forecast": self.get_latest_prediction_summary()

        }

    ###########################################################
    # FLASK MODELS CONTEXT
    ###########################################################

    def get_models_context(self):

        return {

            "moisture_metrics": {

                "dew_point_max": {
                    "r2": 0.92,
                    "mae": 0.99,
                    "rmse": 1.48
                },

                "dew_point_min": {
                    "r2": 0.92,
                    "mae": 1.39,
                    "rmse": 2.05
                },

                "humidity_max": {
                    "r2": 0.85,
                    "mae": 4.74,
                    "rmse": 6.82
                },

                "humidity_min": {
                    "r2": 0.93,
                    "mae": 3.97,
                    "rmse": 5.31
                }

            },

            "rain_metrics": {

                "precision": 0.83,
                "recall": 0.89,
                "f1": 0.86

            },

            "weather_metrics": {

                "accuracy": 73.58

            }

        }

    ###########################################################
    # FLASK ARCHITECTURE CONTEXT
    ###########################################################

    def get_architecture_context(self):

        stats = self.get_pipeline_statistics()

        return {

            "stats": stats

        }

    ###########################################################
    # FLASK ABOUT CONTEXT
    ###########################################################

    def get_about_context(self):

        return {

            "stats": {

                "historical_records": self.get_historical_record_count(),

                "predictions_generated": self.get_prediction_count(),

                "forecast_accuracy": "74%"

            }

        }

    ###########################################################
    # HELPER METHODS
    ###########################################################

    def get_historical_record_count(self):

        query = text("""

            SELECT COUNT(*)

            FROM weather_data

        """)

        with self.engine.connect() as conn:
            return conn.execute(query).scalar()

    def get_prediction_count(self):

        query = text("""

            SELECT COUNT(*)

            FROM predictions

        """)

        with self.engine.connect() as conn:
            return conn.execute(query).scalar()

    def get_engine_context(self):

        latest_prediction = self.get_latest_prediction_summary()
        pipeline = self.get_pipeline_statistics()
        cities = self.get_all_cities()

        return {
            "pipeline": pipeline,
            "forecast": latest_prediction,
            "cities_processed": len(cities)
        }

    def get_pipeline_statistics(self):

        historical_records = self.get_historical_record_count()
        prediction_records = self.get_prediction_count()
        cities = self.get_all_cities()
        latest_prediction = self.get_latest_prediction_summary()

        return {

            "historical_records": historical_records,

            "prediction_records": prediction_records,

            "cities": len(cities),

            "latest_prediction": latest_prediction,

            "pipeline_status": "Operational"

        }

    def get_latest_prediction_summary(self):

        query = text("""
            SELECT *
            FROM predictions
            ORDER BY forecast_date DESC, created_at DESC
            LIMIT 1
        """)

        with self.engine.connect() as conn:
            row = conn.execute(query).mappings().first()

        return dict(row) if row else {}

