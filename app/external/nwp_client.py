import time
import requests
import numpy as np

from datetime import datetime




class NWPClient:



    def __init__(

            self,

            db,

            sleep_seconds=0.3

    ):



        self.db = db


        self.sleep = sleep_seconds



        self.base_url = (

            "https://api.open-meteo.com/v1/forecast"

        )




###############################################################


    def fetch(


            self,


            latitude,


            longitude,


            target_date


    ):



        cached = (

            self.db.get_cached_nwp(


                    latitude,


                    longitude,


                    target_date


            )

        )



        if cached:


            return cached




        result = self._download(


                    latitude,


                    longitude,


                    target_date


                )




        self.db.save_nwp_cache(


                result

        )




        time.sleep(


            self.sleep

        )



        return result





###############################################################



    def _download(


            self,


            latitude,


            longitude,


            target_date


    ):



        params = {


            "latitude":

                latitude,



            "longitude":

                longitude,



            "daily":


            ",".join([


                "weather_code",


                "precipitation_sum",


                "cloud_cover_mean",


                "wind_speed_10m_max",


                "wind_gusts_10m_max",


                "wind_direction_10m_dominant"

            ]),




            "start_date": target_date.isoformat(),
            "end_date": target_date.isoformat(),



            "timezone":

                "GMT"



        }




        r = requests.get(


                self.base_url,


                params=params,


                timeout=10


        )



        r.raise_for_status()



        j = r.json()



        daily = j["daily"]




        direction = (

            daily[


                "wind_direction_10m_dominant"

            ][0]

        )




        return {



            "latitude":

                latitude,



            "longitude":

                longitude,



            "forecast_date":

                target_date,




            "wind_speed_max_kmh":


                daily[


                    "wind_speed_10m_max"

                ][0],




            "wind_gusts_max_kmh":


                daily[


                    "wind_gusts_10m_max"

                ][0],




            "wind_direction_dominant_deg":


                direction,




            "wind_dir_sin": float(np.sin(np.deg2rad(direction))),
            "wind_dir_cos": float(np.cos(np.deg2rad(direction))),




            "cloud_cover_mean_pct":



                daily[


                    "cloud_cover_mean"

                ][0],




            "precipitation_sum_mm":



                daily[


                    "precipitation_sum"

                ][0],




            "weather_code":



                daily[


                    "weather_code"

                ][0]



        }