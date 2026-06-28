from datetime import timedelta

import numpy as np
import pandas as pd


class FeaturePipeline:

    def __init__(self, db):
        self.db = db


    ########################################################
    # PRIVATE HELPERS
    ########################################################

    def _make_temporal(self, target_date):

        year = target_date.year

        month = target_date.month

        day_of_year = target_date.timetuple().tm_yday

        day_of_week = target_date.weekday()


        return {

            'year': year,

            'day_of_week': day_of_week,


            'month_sin':
                np.sin(2*np.pi*month/12),

            'month_cos':
                np.cos(2*np.pi*month/12),


            'day_sin':
                np.sin(2*np.pi*day_of_year/365),

            'day_cos':
                np.cos(2*np.pi*day_of_year/365)

        }


    ########################################################

    def _city(self,
              city_id):

        return self.db.get_city(
                    city_id
               )


    ########################################################

    def _yesterday(self,
                   city_id,
                   target_date):

        yesterday = (

            target_date

            -

            timedelta(days=1)

        )



        return self.db.get_day(

                    city_id,

                    yesterday

                )


    ########################################################

    def _roll3(self,
               city_id,
               target_date):


        yesterday = (

                target_date

                -

                timedelta(days=1)

        )



        df = self.db.get_last_n_days(

                    city_id,

                    yesterday,

                    3

                )



        return {

            'temp_max_roll3':
                df['temp_max_c'].mean(),


            'temp_min_roll3':
                df['temp_min_c'].mean()

        }


    ########################################################
    # TIER 1
    ########################################################

    def build_temperature_features(
            self,
            city_id,
            target_date
    ):
        city = self._city(city_id)

        temporal = self._make_temporal(target_date)

        lag = self._yesterday(
            city_id,
            target_date
        )

        roll = self._roll3(
            city_id,
            target_date
        )

        features = {

            "latitude":
                city["latitude"],

            "longitude":
                city["longitude"],

            "city_id":
                city_id,

            "year":
                temporal["year"],

            "day_of_week":
                temporal["day_of_week"],

            "month_sin":
                temporal["month_sin"],

            "month_cos":
                temporal["month_cos"],

            "day_sin":
                temporal["day_sin"],

            "day_cos":
                temporal["day_cos"],

            "shortwave_radiation_sum_mj_m2":
                lag["shortwave_radiation_sum_mj_m2"],

            "daylight_duration_s":
                lag["daylight_duration_s"],

            "temp_max_lag1":
                lag["temp_max_c"],

            "temp_min_lag1":
                lag["temp_min_c"],

            "temp_max_roll3":
                roll["temp_max_roll3"],

            "temp_min_roll3":
                roll["temp_min_roll3"]

        }

        df = pd.DataFrame([features])

        df["city_id"] = df["city_id"].astype("category")

        return df

    def build_pressure_features(
            self,
            city_id,
            target_date
    ):
        city = self._city(city_id)

        temporal = self._make_temporal(target_date)

        lag = self._yesterday(
            city_id,
            target_date
        )

        features = {

            "latitude":
                city["latitude"],

            "longitude":
                city["longitude"],

            "city_id":
                city_id,

            "year":
                temporal["year"],

            "day_of_week":
                temporal["day_of_week"],

            "month_sin":
                temporal["month_sin"],

            "month_cos":
                temporal["month_cos"],

            "day_sin":
                temporal["day_sin"],

            "day_cos":
                temporal["day_cos"],

            "shortwave_radiation_sum_mj_m2":
                lag["shortwave_radiation_sum_mj_m2"],

            "daylight_duration_s":
                lag["daylight_duration_s"],

            "pressure_max_lag1":
                lag["pressure_msl_max_hpa"],

            "pressure_min_lag1":
                lag["pressure_msl_min_hpa"],

            "pressure_mean_lag1":
                (
                        lag["pressure_msl_max_hpa"]
                        +
                        lag["pressure_msl_min_hpa"]
                ) / 2

        }

        df = pd.DataFrame([features])

        df["city_id"] = df["city_id"].astype("category")

        return df

    def build_moisture_features(
            self,
            city_id,
            target_date,
            nwp
    ):
        city = self._city(
            city_id
        )

        temporal = self._make_temporal(
            target_date
        )

        lag = self._yesterday(
            city_id,
            target_date
        )

        features = {

            ####################################################
            # Location
            ####################################################

            "latitude":
                city["latitude"],

            "longitude":
                city["longitude"],

            "city_id":
                city_id,

            ####################################################
            # External NWP
            ####################################################

            "wind_speed_max_kmh":
                nwp["wind_speed_max_kmh"],

            "wind_gusts_max_kmh":
                nwp["wind_gusts_max_kmh"],

            "wind_dir_sin":
                nwp["wind_dir_sin"],

            "wind_dir_cos":
                nwp["wind_dir_cos"],

            ####################################################
            # Solar
            ####################################################

            "shortwave_radiation_sum_mj_m2":
                lag["shortwave_radiation_sum_mj_m2"],

            "daylight_duration_s":
                lag["daylight_duration_s"],

            ####################################################
            # Calendar
            ####################################################

            "year":
                temporal["year"],

            "day_of_week":
                temporal["day_of_week"],

            "month_sin":
                temporal["month_sin"],

            "month_cos":
                temporal["month_cos"],

            "day_sin":
                temporal["day_sin"],

            "day_cos":
                temporal["day_cos"],

            ####################################################
            # Moisture lag
            ####################################################

            "dew_point_max_lag1":
                lag["dew_point_max_c"],

            "dew_point_min_lag1":
                lag["dew_point_min_c"],

            "relative_humidity_max_lag1":
                lag["relative_humidity_max_pct"],

            "relative_humidity_min_lag1":
                lag["relative_humidity_min_pct"],

            ####################################################
            # Temperature lag
            ####################################################

            "temp_mean_c_lag1":
                (
                        lag["temp_max_c"]
                        +
                        lag["temp_min_c"]
                ) / 2,

            "temp_max_c_lag1":
                lag["temp_max_c"],

            "temp_min_c_lag1":
                lag["temp_min_c"],

            ####################################################
            # Pressure lag
            ####################################################

            "pressure_msl_mean_hpa_lag1":
                (
                        lag["pressure_msl_max_hpa"]
                        +
                        lag["pressure_msl_min_hpa"]
                ) / 2,

            "pressure_msl_max_hpa_lag1":
                lag["pressure_msl_max_hpa"],

            "pressure_msl_min_hpa_lag1":
                lag["pressure_msl_min_hpa"],

            ####################################################
            # Duplicate lag features
            # (exactly as present during training)
            ####################################################

            "dew_point_max_c_lag1":
                lag["dew_point_max_c"],

            "dew_point_min_c_lag1":
                lag["dew_point_min_c"],

            "relative_humidity_max_pct_lag1":
                lag["relative_humidity_max_pct"],

            "relative_humidity_min_pct_lag1":
                lag["relative_humidity_min_pct"]

        }

        df = pd.DataFrame([features])

        df["city_id"] = df["city_id"].astype("category")

        return df


########################################################
# STATIC HELPERS
########################################################


    @staticmethod
    def build_rain_features(

            temp_features,
            temp_prediction,
            pressure_prediction,
            moisture_prediction,
            nwp
    ):
        features = {

            "latitude":
                temp_features["latitude"].iloc[0],

            "longitude":
                temp_features["longitude"].iloc[0],

            "city_id":
                temp_features["city_id"].iloc[0],

            "year":
                temp_features["year"].iloc[0],

            "day_of_week":
                temp_features["day_of_week"].iloc[0],

            "month_sin":
                temp_features["month_sin"].iloc[0],

            "month_cos":
                temp_features["month_cos"].iloc[0],

            "day_sin":
                temp_features["day_sin"].iloc[0],

            "day_cos":
                temp_features["day_cos"].iloc[0],

            "shortwave_radiation_sum_mj_m2":
                temp_features["shortwave_radiation_sum_mj_m2"].iloc[0],

            "daylight_duration_s":
                temp_features["daylight_duration_s"].iloc[0],

            "temp_max_c":
                temp_prediction["temp_max_c"],

            "temp_min_c":
                temp_prediction["temp_min_c"],

            "pressure_msl_max_hpa":
                pressure_prediction["pressure_msl_max_hpa"],

            "pressure_msl_min_hpa":
                pressure_prediction["pressure_msl_min_hpa"],

            "wind_speed_max_kmh":
                nwp["wind_speed_max_kmh"],

            "wind_dir_sin":
                nwp["wind_dir_sin"],

            "wind_dir_cos":
                nwp["wind_dir_cos"],

            "dew_point_max_c":
                moisture_prediction["dew_point_max_c"],

            "dew_point_min_c":
                moisture_prediction["dew_point_min_c"],

            "cloud_cover_mean_pct":
                nwp["cloud_cover_mean_pct"]

        }

        df = pd.DataFrame([features])

        df["city_id"] = df["city_id"].astype("category")

        return df



########################################################


    @staticmethod
    @staticmethod
    def build_weathercode_features(
            rain_features,
            moisture_prediction,
            nwp
    ):
        features = {

            "latitude":
                rain_features["latitude"].iloc[0],

            "longitude":
                rain_features["longitude"].iloc[0],

            "city_id":
                rain_features["city_id"].iloc[0],

            "year":
                rain_features["year"].iloc[0],

            "day_of_week":
                rain_features["day_of_week"].iloc[0],

            "month_sin":
                rain_features["month_sin"].iloc[0],

            "month_cos":
                rain_features["month_cos"].iloc[0],

            "day_sin":
                rain_features["day_sin"].iloc[0],

            "day_cos":
                rain_features["day_cos"].iloc[0],

            "shortwave_radiation_sum_mj_m2":
                rain_features["shortwave_radiation_sum_mj_m2"].iloc[0],

            "daylight_duration_s":
                rain_features["daylight_duration_s"].iloc[0],

            "temp_max_c":
                rain_features["temp_max_c"].iloc[0],

            "temp_min_c":
                rain_features["temp_min_c"].iloc[0],

            "pressure_msl_max_hpa":
                rain_features["pressure_msl_max_hpa"].iloc[0],

            "pressure_msl_min_hpa":
                rain_features["pressure_msl_min_hpa"].iloc[0],

            "wind_speed_max_kmh":
                rain_features["wind_speed_max_kmh"].iloc[0],

            "wind_dir_sin":
                rain_features["wind_dir_sin"].iloc[0],

            "wind_dir_cos":
                rain_features["wind_dir_cos"].iloc[0],

            "dew_point_max_c":
                rain_features["dew_point_max_c"].iloc[0],

            "dew_point_min_c":
                rain_features["dew_point_min_c"].iloc[0],

            "relative_humidity_max_pct":
                moisture_prediction["relative_humidity_max_pct"],

            "cloud_cover_mean_pct":
                rain_features["cloud_cover_mean_pct"].iloc[0],

            "precipitation_sum_mm":
                nwp["precipitation_sum_mm"]

        }

        df = pd.DataFrame([features])

        df["city_id"] = df["city_id"].astype("category")

        return df