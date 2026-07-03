# 🌦️ Weather Engine

![Python](https://img.shields.io/badge/Python-3.12-blue)
![Backend](https://img.shields.io/badge/Backend-Flask-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)
![ML](https://img.shields.io/badge/Machine%20Learning-LightGBM-orange)

## Hybrid Machine Learning Weather Forecasting Platform

Weather Engine is an end-to-end machine learning engineering project combining data science, backend development, databases, automation and production-style software architecture into a complete weather forecasting platform.

The system follows a hybrid forecasting approach where internally trained machine learning models predict structured atmospheric patterns, while external Numerical Weather Prediction (NWP) guidance is integrated for highly dynamic weather components.

The objective is not only to train forecasting models, but to engineer the surrounding ecosystem required for real-world ML applications — including data pipelines, persistence, evaluation, monitoring and user-facing interfaces.

---

# 🚀 Project Highlights

- 15+ years of historical weather observations
- 70+ engineered atmospheric features
- 5 specialized machine learning models
- Hybrid ML + Numerical Weather Prediction architecture
- Hierarchical dependency-aware forecasting pipeline
- Automated daily inference workflow
- PostgreSQL persistence layer
- Continuous prediction evaluation
- Flask analytics dashboard
- Automated email forecast reporting

---

# 🏗 System Overview


```
External Weather APIs
          |
          v
Data Collection Pipeline
          |
          v
PostgreSQL Database
          |
          v
Feature Engineering Engine
          |
          v
Hybrid ML Forecasting System
          |
          v
Prediction Storage + Evaluation
          |
          v
Flask Dashboard + Email Reports
```

---

# 🧠 Machine Learning Architecture

Weather Engine uses a hierarchical forecasting architecture inspired by atmospheric dependencies.

Instead of treating every weather variable independently, predictions are generated through multiple connected stages where stable atmospheric variables support more complex predictions.

---

## Tier 1 — Temperature & Pressure Modelling

### Temperature Model

**Algorithm**

- LightGBM
- Multi-output Regression


Predicts:

- Maximum temperature
- Minimum temperature


Feature categories:

- Geographic inputs
- Temporal patterns
- Cyclical features
- Solar radiation
- Historical lag features
- Rolling statistics


### Pressure Model

**Algorithm**

- LightGBM
- Multi-output Regression


Predicts:

- Maximum atmospheric pressure
- Minimum atmospheric pressure


Pressure predictions provide atmospheric context for later forecasting stages.

---

## Tier 2 — Moisture Prediction

**Algorithm**

- LightGBM Multi-output Regression


Predicts:

- Maximum dew point
- Minimum dew point
- Maximum relative humidity
- Minimum relative humidity


The model combines environmental features with outputs from earlier atmospheric layers.

---

## Tier 3 — Rain Classification

Binary classification model predicting rainfall occurrence.

The model prioritizes recall because missing rainfall events is generally more harmful than generating occasional false positives.

---

## Tier 4 — Weather Code Classification

Multi-class classification model predicting final weather conditions.

The final forecast is produced using a hybrid consensus layer:

```
Machine Learning Prediction

        +

Numerical Weather Prediction

        =

Final Forecast
```

---

# 🌎 Why Hybrid ML + NWP?

During experimentation, multiple atmospheric variables were tested using purely data-driven machine learning approaches.

Some variables performed well, while others showed natural predictability limitations.

---

## Wind Forecasting

Models tested:

- LightGBM
- CatBoost
- Ensemble approaches


Observation:

Performance saturated despite additional feature engineering.

Reason:

Wind depends strongly on:

- Pressure gradients
- Terrain interactions
- Large-scale atmospheric circulation


Decision:

Use external Numerical Weather Prediction guidance.

---

## Rain Amount Prediction

Regression-based rainfall amount prediction was evaluated.

Challenges:

- Sparse rainfall distribution
- Rare extreme events
- Strong atmospheric dependency


Decision:

Use physics-based NWP precipitation forecasts.

---

# ⚙️ Data Pipeline


Daily automated workflow:


1. Load monitored city configuration

2. Fetch weather observations

3. Validate and store data

4. Generate model features

5. Execute hierarchical ML inference

6. Apply hybrid forecast logic

7. Store predictions

8. Compare previous forecasts with observations

9. Calculate evaluation metrics

10. Generate reports


---

# 🗄 Database Architecture

Database Engine:

**PostgreSQL**


Main Tables:

| Table | Purpose |
|-|-|
| weather_data | Historical observations |
| predictions | Generated forecasts |
| errors | Prediction evaluation results |
| nwp_cache | External forecast cache |
| email_subscriptions | Forecast report subscribers |

---

# 📊 Evaluation System

Regression metrics:

- MAE
- RMSE
- R² Score


Classification metrics:

- Accuracy
- Precision
- Recall
- F1 Score


Forecasts are continuously evaluated after actual observations become available, creating a feedback loop for long-term monitoring.

---

# 🖥 Dashboard Features


## Forecast Dashboard

Displays:

- Temperature forecasts
- Pressure forecasts
- Humidity and dew point
- Rain probability
- Wind conditions
- Weather classification


## Metrics Dashboard

Tracks:

- Temperature error
- Pressure error
- Moisture performance
- Rain classification accuracy
- Weather code accuracy


## Architecture Dashboard

Shows:

- ML workflow
- Database design
- Automation pipeline
- System components


---

# 🛠 Technology Stack


### Backend

- Python
- Flask
- Jinja2


### Machine Learning

- LightGBM
- Scikit-Learn
- Joblib


### Data Engineering

- Pandas
- NumPy


### Database

- PostgreSQL


### Visualization

- Plotly


### External Systems

- Open-Meteo API
- SMTP


### Frontend

- HTML
- CSS
- Bootstrap Icons


### Development

- Git
- GitHub

---

# 📁 Project Structure


```
Weather_Project/

├── app/
│   ├── database/
│   ├── external/
│   ├── email/
│   ├── flask_app/
│   └── ml/
│
├── scripts/
│   └── automation pipeline
│
├── model/
│   └── trained model artifacts
│
├── notebooks/
│   └── experimentation
│
├── docs/
│   └── engineering documentation
│
├── requirements.txt
└── README.md
```

---

# ⚡ Local Setup


Clone repository:

```bash
git clone https://github.com/Nilansh90/Weather_Project.git

cd Weather_Project
```


Create virtual environment:

```bash
python -m venv .venv
```


Activate:

Windows:

```bash
.venv\Scripts\activate
```


Linux/Mac:

```bash
source .venv/bin/activate
```


Install dependencies:

```bash
pip install -r requirements.txt
```


Create `.env`:

```env
DATABASE_URL=

EMAIL_ADDRESS=

EMAIL_PASSWORD=
```


Initialize database:

```bash
python setup_tasks/db_setup.py
```


Run pipeline:

```bash
python scripts/master_script.py
```


Start Flask application:

```bash
python app/flask_app/server.py
```

---

# 🚀 Deployment

Cloud deployment configuration will be added after production release.

---

# 📚 Documentation

Detailed engineering documentation:

- docs/01_PROJECT_OVERVIEW.md
- docs/02_SYSTEM_ARCHITECTURE.md
- docs/03_MACHINE_LEARNING_ARCHITECTURE.md
- docs/04_DATA_PIPELINE.md
- docs/05_DATABASE_DESIGN.md
- docs/06_MODEL_EVALUATION.md
- docs/07_AUTOMATION_AND_DEPLOYMENT.md
- docs/08_LIMITATIONS_AND_ROADMAP.md

---

# Current Limitations

Weather Engine is an engineering-focused forecasting platform and not a replacement for operational meteorological systems.

Current boundaries:

- Limited geographic coverage
- Extreme events require more historical samples
- Highly chaotic variables require NWP support
- Current forecasts operate at daily resolution

---

# Future Roadmap

Planned improvements:

- Cloud deployment
- Larger geographical coverage
- Automated retraining pipeline
- Model drift monitoring
- Forecast versioning
- Advanced ensemble systems

---

# Engineering Philosophy

Weather Engine represents the transition from isolated machine learning models toward complete AI-powered software systems.

The project focuses on:

✔ Data Engineering  
✔ Machine Learning  
✔ Backend Systems  
✔ Automation  
✔ Evaluation  
✔ Production Engineering  


The goal is not only generating predictions — but building the infrastructure required to operate intelligent systems.

---

# Author

Developed as a full-stack machine learning engineering project exploring production-style AI system design.

---

© 2026 Weather Engine  
Hybrid ML Forecasting Platform
