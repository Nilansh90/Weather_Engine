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

        rows = self.engine.connect().execute(

            text("""

            SELECT p.*

            FROM predictions p

            LEFT JOIN errors e

            ON

                p.city_id = e.city_id

            AND

                p.forecast_date = e.forecast_date

            WHERE

                e.id IS NULL

            AND

                p.forecast_date < CURRENT_DATE

            ORDER BY

                p.forecast_date,
                p.city_id

            """)

        )

        return rows.mappings().all()

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

        return row