from pathlib import Path

import joblib

from app.ml.fallback import evaluate_weather_code


class InferenceOrchestrator:


    def __init__(self,
                 feature_pipeline,
                 nwp_client):

        self.fp = feature_pipeline
        self.nwp = nwp_client


        ROOT = Path(__file__).resolve().parents[2]

        MODEL_DIR = ROOT / "model"


        self.temp_model = joblib.load(
            MODEL_DIR /
            "lightgbm_temp_predictor.joblib"
        )


        self.pressure_model = joblib.load(
            MODEL_DIR /
            "lightgbm_pressure_predictor.joblib"
        )


        self.moisture_model = joblib.load(
            MODEL_DIR /
            "moisture_model.joblib"
        )


        self.rain_model = joblib.load(
            MODEL_DIR /
            "precipitation_classifier.joblib"
        )


        self.weather_model = joblib.load(
            MODEL_DIR /
            "weather_multiclass_model.joblib"
        )


    #######################################################

    def predict_temperature(self,
                            tier1):


        pred = self.temp_model.predict(
            tier1
        )[0]


        return {

            'temp_max_c':
                float(pred[0]),


            'temp_min_c':
                float(pred[1])

        }


    #######################################################

    def predict_pressure(self,
                         tier1):


        pred = self.pressure_model.predict(
            tier1
        )[0]



        return {


            'pressure_msl_max_hpa':
                float(pred[0]),


            'pressure_msl_min_hpa':
                float(pred[1])

        }


    #######################################################

    def predict_moisture(self,
                         tier1):


        pred = self.moisture_model.predict(
            tier1
        )[0]


        return {



            'dew_point_max_c':
                float(pred[0]),



            'dew_point_min_c':
                float(pred[1]),



            'relative_humidity_max_pct':
                float(pred[2]),



            'relative_humidity_min_pct':
                float(pred[3])


        }



    #######################################################


    def predict_rain(self,
                     rain_x):



        probability = (


            self.rain_model


            .predict_proba(

                rain_x

            )


        )[0][1]



        rain = probability >= 0.30



        return {


            'rain_probability':

                float(probability),




            'rain':

                bool(rain)

        }



    #######################################################


    def predict_weathercode(self,
                            weather_x):



        pred = self.weather_model.predict(

                    weather_x

                )[0]



        return int(pred)



    #######################################################


    def run_full_dag(self,
                     city_id,
                     target_date):



        tier1 = (

            self.fp

            .build_tier1_features(

                city_id,

                target_date

            )

        )



        city = (

            self.fp

            .db

            .get_city(

                city_id

            )

        )



        nwp = (

            self.nwp.fetch(


                city['latitude'],


                city['longitude'],


                target_date


            )

        )



        ######################################

        temp = self.predict_temperature(

                    tier1

                )



        pressure = self.predict_pressure(

                        tier1

                    )



        moisture = self.predict_moisture(

                        tier1

                    )


        ######################################



        rain_x = (


            self.fp


            .assemble_rain_features(



                    tier1,



                    [


                        temp[

                            'temp_max_c'

                        ],



                        temp[

                            'temp_min_c'

                        ]



                    ],




                    [


                        pressure[

                            'pressure_msl_max_hpa'

                        ],




                        pressure[

                            'pressure_msl_min_hpa'

                        ]

                    ],





                    [


                        moisture[

                            'dew_point_max_c'

                        ],




                        moisture[

                            'dew_point_min_c'

                        ],




                        moisture[

                            'relative_humidity_max_pct'

                        ],




                        moisture[

                            'relative_humidity_min_pct'

                        ]


                    ],




                    nwp


            )

        )



        rain = (

            self.predict_rain(

                rain_x

            )

        )



        ######################################



        weather_x = (


            self.fp


            .assemble_weathercode_features(


                    rain_x,



                    [


                        moisture[

                            'dew_point_max_c'

                        ],




                        moisture[

                            'dew_point_min_c'

                        ],




                        moisture[

                            'relative_humidity_max_pct'

                        ],




                        moisture[

                            'relative_humidity_min_pct'

                        ]


                    ],




                    nwp[

                        'precipitation_sum_mm'

                    ]



            )

        )



        ml_code = (

            self.predict_weathercode(

                    weather_x

            )

        )



        final_code = (


            evaluate_weather_code(



                    ml_code,



                    nwp[

                        'weather_code'

                    ]



            )



        )



        ######################################



        forecast = {



            'city_id':

                city_id,



            'forecast_date':

                target_date,



            **temp,



            **pressure,



            **moisture,



            **rain,



            'wind_speed_max_kmh':

                nwp[

                    'wind_speed_max_kmh'

                ],




            'wind_gusts_max_kmh':

                nwp[

                    'wind_gusts_max_kmh'

                ],




            'wind_direction_dominant_deg':

                nwp[

                    'wind_direction_dominant_deg'

                ],




            'cloud_cover_mean_pct':

                nwp[

                    'cloud_cover_mean_pct'

                ],




            'precipitation_sum_mm':

                nwp[

                    'precipitation_sum_mm'

                ],




            'weather_code':

                final_code


        }



        return forecast