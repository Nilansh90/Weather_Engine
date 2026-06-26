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

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
import pandas as pd
import os


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

        INSERT INTO nwp_cache


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
            conn.execute(

                query,

                nwp

            )
