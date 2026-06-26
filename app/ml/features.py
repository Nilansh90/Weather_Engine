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

    def build_tier1_features(self,
                             city_id,
                             target_date):


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



        roll = self._roll3(

                    city_id,

                    target_date

                )



        features = {

            'latitude':

                city['latitude'],



            'longitude':

                city['longitude'],



            'city_id':

                city_id,



            'year':

                temporal['year'],



            'day_of_week':

                temporal['day_of_week'],



            'month_sin':

                temporal['month_sin'],


            'month_cos':

                temporal['month_cos'],


            'day_sin':

                temporal['day_sin'],


            'day_cos':

                temporal['day_cos'],




            'shortwave_radiation_sum_mj_m2':

                lag[

                'shortwave_radiation_sum_mj_m2'

                ],




            'daylight_duration_s':

                lag[

                'daylight_duration_s'

                ],




            'temp_max_lag1':

                lag['temp_max_c'],




            'temp_min_lag1':

                lag['temp_min_c'],




            'temp_max_roll3':

                roll['temp_max_roll3'],




            'temp_min_roll3':

                roll['temp_min_roll3']

        }



        return pd.DataFrame(

            [features]

        )


########################################################
# STATIC HELPERS
########################################################


    @staticmethod
    def assemble_rain_features(


            tier1,


            temp_pred,


            pressure_pred,


            moisture_pred,


            nwp

    ):



        return pd.DataFrame([{



            'latitude':

                tier1['latitude'].iloc[0],



            'longitude':

                tier1['longitude'].iloc[0],



            'city_id':

                tier1['city_id'].iloc[0],




            'year':

                tier1['year'].iloc[0],




            'day_of_week':

                tier1['day_of_week'].iloc[0],




            'month_sin':

                tier1['month_sin'].iloc[0],




            'month_cos':

                tier1['month_cos'].iloc[0],




            'day_sin':

                tier1['day_sin'].iloc[0],




            'day_cos':

                tier1['day_cos'].iloc[0],




            'shortwave_radiation_sum_mj_m2':

                tier1['shortwave_radiation_sum_mj_m2'].iloc[0],




            'daylight_duration_s':

                tier1['daylight_duration_s'].iloc[0],




            'temp_max_c':

                temp_pred[0],




            'temp_min_c':

                temp_pred[1],




            'pressure_msl_max_hpa':

                pressure_pred[0],




            'pressure_msl_min_hpa':

                pressure_pred[1],




            'wind_speed_max_kmh':

                nwp['wind_speed'],




            'wind_dir_sin':

                nwp['wind_dir_sin'],




            'wind_dir_cos':

                nwp['wind_dir_cos'],




            'dew_point_max_c':

                moisture_pred[0],




            'dew_point_min_c':

                moisture_pred[1],




            'cloud_cover_mean_pct':

                nwp['cloud_cover']

        }])



########################################################


    @staticmethod
    def assemble_weathercode_features(


            rain_features,


            moisture_pred,


            rain_amount

    ):



        df = rain_features.copy()



        df[

            'relative_humidity_max_pct'

        ] = moisture_pred[2]



        df[

            'precipitation_sum_mm'

        ] = rain_amount



        return df