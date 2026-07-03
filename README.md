# 🌦️ Weather Engine

## Hybrid Machine Learning Weather Forecasting Platform

Weather Engine is an end-to-end machine learning engineering project that combines data science, backend development, automation, databases and production-style software architecture to build a complete weather forecasting system.

The platform predicts atmospheric conditions using a hybrid approach: internally trained machine learning models handle predictable weather variables, while external Numerical Weather Prediction (NWP) guidance is integrated for highly chaotic atmospheric components.

The goal of this project is not only building forecasting models, but engineering the complete ecosystem required around machine learning systems — data pipelines, storage, evaluation, monitoring and user-facing applications.

---

## 🚀 Project Highlights

- 15+ years of historical weather observations
- 70+ engineered atmospheric features
- 5 specialized machine learning models
- Hybrid ML + NWP forecasting architecture
- Automated daily prediction pipeline
- PostgreSQL-backed persistence layer
- Continuous forecast evaluation system
- Interactive Flask monitoring dashboard
- Automated email forecast reports

---

# System Overview


External Weather APIs

        ↓

Data Collection Pipeline

        ↓

PostgreSQL Database

        ↓

Feature Engineering Engine

        ↓

Hybrid ML Forecasting System

        ↓

Prediction Storage + Evaluation

        ↓

Flask Dashboard + Email Reports


---

# Machine Learning Architecture

Weather Engine follows a dependency-aware hierarchical forecasting design.

Instead of predicting all variables independently, models execute according to atmospheric relationships.



## Tier 1 — Stable Atmospheric Variables

### Temperature Model

Algorithm:

- LightGBM
- Multi-output regression


Predicts:

- Maximum temperature
- Minimum temperature


Uses:

- Geographic features
- Temporal patterns
- Solar radiation
- Historical lag features
- Rolling statistics


---

### Pressure Model

Algorithm:

- LightGBM
- Multi-output regression


Predicts:

- Maximum pressure
- Minimum pressure


Pressure outputs help represent larger atmospheric trends.

---

## Tier 2 — Moisture Model


Algorithm:

- LightGBM Multi-output Regression


Predicts:

- Dew point maximum
- Dew point minimum
- Relative humidity maximum
- Relative humidity minimum


Uses temperature and atmospheric features generated from previous stages.

---

## Tier 3 — Rain Classification


Binary classification model predicting rainfall occurrence.


Optimized for recall because missing actual rainfall events is considered more costly than false alarms.


---

## Tier 4 — Weather Code Classification


Multi-class classification system predicting final atmospheric conditions.


The final prediction passes through a hybrid consensus system combining:

Machine Learning Prediction

+

Numerical Weather Prediction

=

Final Forecast


---

# Why Hybrid ML + NWP?


During development, multiple atmospheric variables were experimentally modeled using pure machine learning.


However, some variables showed natural predictability limitations.


## Wind Prediction

Tested:

- LightGBM
- CatBoost
- Ensemble models


Observation:

Validation performance saturated despite extensive feature engineering.


Reason:

Wind depends heavily on:

- Regional pressure gradients
- Terrain effects
- Large scale atmospheric movement


Final decision:

Use external Numerical Weather Prediction.


---

## Rain Amount Prediction


Rainfall quantity prediction was tested using regression approaches.

Challenges:

- Highly imbalanced rainfall distribution
- Rare extreme rainfall events
- Complex atmospheric physics


Final decision:

Use physics-based NWP rainfall forecasts.


---

# Data Pipeline


Daily execution workflow:


1. Load city configuration

2. Fetch weather observations

3. Store validated data

4. Generate features

5. Execute ML inference pipeline

6. Apply hybrid forecasting logic

7. Store predictions

8. Compare previous forecasts with actual data

9. Update performance metrics

10. Generate reports


---

# Database Architecture


Database:

PostgreSQL


Main tables:


### weather_data

Stores historical weather observations.


### predictions

Stores generated forecasts.


### errors

Stores prediction vs actual evaluation results.


### nwp_cache

Stores external numerical forecast data.


### email_subscriptions

Stores approved forecast report users.


---

# Model Evaluation


Regression models are evaluated using:


- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- R² Score


Classification models use:


- Accuracy
- Precision
- Recall
- F1 Score


Every forecast is evaluated after actual observations become available, creating a continuous feedback loop.


---

# Technology Stack


## Programming

- Python


## Backend

- Flask
- Jinja2


## Database

- PostgreSQL


## Machine Learning

- LightGBM
- Scikit-Learn
- Joblib


## Data Processing

- Pandas
- NumPy


## Visualization

- Plotly


## External Data

- Open-Meteo API


## Frontend

- HTML
- CSS
- Bootstrap Icons


## Automation

- Python scripts
- SMTP email service


## Development

- Git
- GitHub


---

# Dashboard Features


## Forecast Interface

Displays:

- Temperature forecasts
- Pressure predictions
- Moisture variables
- Rain probability
- Wind conditions
- Weather classification


---

## Performance Dashboard

Tracks:

- Temperature MAE
- Pressure MAE
- Humidity errors
- Rain prediction accuracy
- Weather code performance


---

## Architecture Dashboard

Visualizes:

- ML pipeline
- System workflow
- Database structure
- Automation pipeline


---

# Current Limitations


Weather Engine is an engineering-focused forecasting platform and not a replacement for operational meteorological systems.


Current boundaries:


- Training coverage limited to selected cities

- Extreme weather events remain challenging due to limited historical examples

- Highly chaotic atmospheric variables require NWP assistance

- Current forecasting resolution is daily rather than hourly


---

# Future Improvements


Planned extensions:


- Cloud deployment

- Larger geographic coverage

- Automated model retraining

- Model drift monitoring

- Forecast versioning

- Higher resolution forecasts

- Advanced ensemble systems


---

# Engineering Philosophy


Weather Engine represents the transition from building isolated machine learning models to designing complete AI-powered software systems.


The project emphasizes:


✔ Data Engineering

✔ Machine Learning

✔ Backend Architecture

✔ Automation

✔ Evaluation

✔ Production Thinking


The objective is not only generating predictions — but building the complete infrastructure required to operate and monitor intelligent systems.


---

# Documentation


Detailed engineering documentation:


- `docs/01_PROJECT_OVERVIEW.md`

- `docs/02_SYSTEM_ARCHITECTURE.md`

- `docs/03_MACHINE_LEARNING_ARCHITECTURE.md`

- `docs/04_DATA_PIPELINE.md`

- `docs/05_DATABASE_DESIGN.md`

- `docs/06_MODEL_EVALUATION.md`

- `docs/07_AUTOMATION_AND_DEPLOYMENT.md`

- `docs/08_LIMITATIONS_AND_ROADMAP.md`


---

# Author

Developed as a full-stack machine learning engineering project exploring production-style AI system design.

---

© 2026 Weather Engine  
Hybrid ML Forecasting Platform