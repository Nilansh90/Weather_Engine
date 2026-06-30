from flask import Flask, render_template, request

from app.database.db_manager import DatabaseManager

app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


def _prefer_dict_key_getattr(obj, attribute):

    if isinstance(obj, dict) and attribute in obj:
        return obj[attribute]

    try:
        return getattr(obj, attribute)
    except AttributeError:
        pass

    try:
        return obj[attribute]
    except (LookupError, TypeError, KeyError):
        return app.jinja_env.undefined(obj=obj, name=attribute)


app.jinja_env.getattr = _prefer_dict_key_getattr

# ---------------------------------------------------------
# Database
# ---------------------------------------------------------

db = DatabaseManager()


# ---------------------------------------------------------
# Temporary page contexts
# ---------------------------------------------------------

def _model_card(name, icon, description, model_type, inputs, outputs):

    return {
        "name": name,
        "icon": icon,
        "description": description,
        "type": model_type,
        "inputs": inputs,
        "outputs": outputs,
        "status": "Loaded"
    }


def _engine_summary_context():

    # TODO Replace with DatabaseManager query
    return {
        "historical": _model_card("Historical Data", "database", "Historical observations.", "Data", "Cities", "Features"),
        "features": _model_card("Feature Engineering", "sliders", "Temporal and weather features.", "Pipeline", "Raw data", "Feature set"),
        "temperature": _model_card("Temperature", "thermometer-half", "Temperature model.", "Regression", "Features", "Temperature"),
        "pressure": _model_card("Pressure", "speedometer2", "Pressure model.", "Regression", "Features", "Pressure"),
        "moisture": _model_card("Moisture", "droplet", "Moisture model.", "Regression", "Temperature, Pressure", "Humidity"),
        "rain": _model_card("Rain", "cloud-rain", "Rain classifier.", "Classification", "Moisture", "Rain probability"),
        "weather": _model_card("Weather Code", "cloud-sun", "Weather code classifier.", "Classification", "Rain", "Weather code"),
        "consensus": _model_card("Consensus", "check2-circle", "Consistency check.", "Rules", "Model outputs", "Validated forecast"),
        "forecast": _model_card("Forecast", "graph-up-arrow", "Final forecast.", "Output", "Validated forecast", "City forecast"),
        "summary": [
            {"icon": "cpu", "label": "5 models loaded"},
            {"icon": "diagram-3", "label": "Hierarchical DAG ready"},
            {"icon": "shield-check", "label": "Health checks passing"}
        ]
    }


def _pipeline_context():

    # TODO Replace with DatabaseManager query
    return {
        "recharge_time": "06:00",
        "cache_time": "06:02",
        "feature_time": "06:03",
        "inference_time": "06:04",
        "storage_time": "06:05",
        "evaluation_time": "06:06",
        "email_time": "06:07",
        "health_time": "06:08",
        "prediction_time": "06:04",
        "historical_runtime": "1.2s",
        "feature_runtime": "0.8s",
        "tier_one_runtime": "0.4s",
        "tier_two_runtime": "0.3s",
        "tier_three_runtime": "0.3s",
        "tier_four_runtime": "0.2s",
        "consensus_runtime": "0.1s",
        "database_runtime": "0.2s",
        "email_runtime": "0.4s",
        "cities_processed": 5,
        "predictions": 5,
        "runtime": "<2 sec",
        "database_writes": 5,
        "success_rate": "100%"
    }


def _metrics_context():

    # TODO Replace with DatabaseManager query
    return {
        "temperature_mae": 0.85,
        "temperature_trend": "Stable",
        "temperature_trend_class": "text-success",
        "pressure_mae": 0.95,
        "pressure_trend": "Stable",
        "pressure_trend_class": "text-success",
        "moisture_mae": 1.10,
        "moisture_trend": "Stable",
        "moisture_trend_class": "text-success",
        "rain_accuracy": 89,
        "rain_trend": "Stable",
        "rain_trend_class": "text-success",
        "weather_accuracy": 74,
        "weather_trend": "Stable",
        "weather_trend_class": "text-success",
        "pipeline_success": 100,
        "pipeline_trend": "Healthy",
        "pipeline_trend_class": "text-success",
        "runtime": "<2 sec",
        "cities": 5,
        "predictions": 5
    }


def _engine_context():

    # TODO Replace with DatabaseManager query
    return {
        "pipeline": _pipeline_context(),
        "forecast": {
            "city_id": 1,
            "forecast_date": "Tomorrow",
            "temperature": 28,
            "pressure": 1012,
            "dew_point": 18,
            "humidity": 58,
            "rain_probability": 20,
            "wind": 12,
            "cloud_cover": 35,
            "weather_code": 2
        }
    }


def _models_context():

    # TODO Replace with DatabaseManager query
    return {
        "moisture_metrics": {
            "dew_point_max": {"r2": 0.92, "mae": 0.99, "rmse": 1.48},
            "dew_point_min": {"r2": 0.92, "mae": 1.39, "rmse": 2.05},
            "humidity_max": {"r2": 0.85, "mae": 4.74, "rmse": 6.82},
            "humidity_min": {"r2": 0.93, "mae": 3.97, "rmse": 5.31}
        },
        "rain_metrics": {"precision": "0.83", "recall": "0.89", "f1": "0.86"},
        "weather_metrics": {
            "clear_sky": "91%",
            "light_drizzle": "84%",
            "moderate_rain": "78%",
            "heavy_rain": "72%",
            "overcast": "80%"
        }
    }


def _about_context():

    # TODO Replace with DatabaseManager query
    return {
        "stats": {
            "historical_records": "19,000+",
            "predictions_generated": "Daily",
            "forecast_accuracy": "74%"
        }
    }


# ---------------------------------------------------------
# HOME
# ---------------------------------------------------------

@app.route("/")
def home():

    return render_template("home.html", **db.get_home_context())


# ---------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html", **db.get_dashboard_context())


# ---------------------------------------------------------
# ENGINE
# ---------------------------------------------------------

@app.route("/engine")
def engine():

    return render_template(
        "engine.html",
        **db.get_engine_context()
    )


@app.route("/models")
def models():

    return render_template(
        "models.html",
        **db.get_models_context()
    )


@app.route("/architecture")
def architecture():

    return render_template(
        "architecture.html",
        **db.get_architecture_context()
    )


@app.route("/about")
def about():

    return render_template(
        "about.html",
        **db.get_about_context()
    )

@app.route("/history")
def history():
    return render_template(
        "history.html",
        **db.get_history_context(request.args)
    )
# ---------------------------------------------------------
# MAIN
# ---------------------------------------------------------

if __name__ == "__main__":

    app.run(
        debug=True,
        host="127.0.0.1",
        port=5000
    )
