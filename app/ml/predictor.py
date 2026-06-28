from pathlib import Path

import joblib

from app.ml.fallback import evaluate_weather_code


class InferenceOrchestrator:

    def __init__(
            self,
            feature_pipeline
    ):

        self.fp = feature_pipeline



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
        # print("\nTier1 dtypes")
        # print(tier1.dtypes)
        #
        # print("\nTier1 values")
        # print(tier1)
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
        # print(
        #     self.pressure_model.estimators_[0].booster_.feature_name()
        # )
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

    def predict_moisture(self, moisture_features):
        pred = self.moisture_model.predict(
            moisture_features
        )[0]

        return {

            "dew_point_max_c": float(pred[0]),

            "dew_point_min_c": float(pred[1]),

            "relative_humidity_max_pct": float(pred[2]),

            "relative_humidity_min_pct": float(pred[3])

        }
    #######################################################

    def predict_rain(self, rain_x):
        probability = float(self.rain_model.predict_proba(
            rain_x
        )[0][1])

        return {

            "rain_probability": float(probability),

            "will_rain": bool(probability >= 0.30)

        }
    #######################################################

    def predict_weathercode(self, weather_x):
        pred = self.weather_model.predict(
            weather_x
        )[0]

        return int(pred)



    #######################################################

    def run_full_dag(
            self,
            city_id,
            target_date,
            nwp
    ):
        temp_features = self.fp.build_temperature_features(
            city_id,
            target_date
        )

        pressure_features = self.fp.build_pressure_features(
            city_id,
            target_date
        )

        # Temporary until moisture builder is added
        moisture_features = self.fp.build_moisture_features(
            city_id,
            target_date,
            nwp
        )

        temp = self.predict_temperature(
            temp_features
        )

        pressure = self.predict_pressure(
            pressure_features
        )

        moisture = self.predict_moisture(
            moisture_features
        )


        ######################################

        rain_x = self.fp.build_rain_features(

            temp_features,

            temp,

            pressure,

            moisture,

            nwp

        )


        rain = (

            self.predict_rain(

                rain_x

            )

        )



        ######################################

        weather_x = self.fp.build_weathercode_features(

            rain_x,

            moisture,

            nwp

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

    def debug_feature_names(self):
        print("\nTemperature")
        print(
            self.temp_model.estimators_[0].booster_.feature_name()
        )

        print("\nPressure")
        print(
            self.pressure_model.estimators_[0].booster_.feature_name()
        )

        print("\nMoisture")
        print(
            self.moisture_model.estimators_[0].booster_.feature_name()
        )

        print("\nRain")
        print(
            self.rain_model.booster_.feature_name()
        )

        print("\nWeather")
        print(
            self.weather_model.booster_.feature_name()
        )