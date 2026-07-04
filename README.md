# 🌦️ Weather Engine

![Python](https://img.shields.io/badge/Python-3.11-blue)
![Machine Learning](https://img.shields.io/badge/ML-LightGBM-orange)
![Backend](https://img.shields.io/badge/Backend-Flask-green)
![Database](https://img.shields.io/badge/Database-PostgreSQL-blue)
![Deployment](https://img.shields.io/badge/Deployment-Live-success)

## Hybrid Machine Learning Weather Forecasting System

🌐 **Live Deployment**

https://weather-engine-tanb.onrender.com/


Weather Engine is an end-to-end machine learning engineering system designed to forecast weather conditions using a combination of data-driven machine learning models, external Numerical Weather Prediction (NWP) guidance, automated pipelines and production-style backend architecture.

The project focuses not only on training forecasting models, but on building the complete ecosystem required around applied machine learning:

- Data acquisition pipelines
- Feature engineering systems
- Model inference architecture
- Database persistence
- Automated evaluation
- Monitoring dashboards
- Scheduled production workflows
- User-facing applications


---

# 🚀 System Highlights


- 15+ years of historical weather observations
- 70+ engineered atmospheric features
- Multi-stage hierarchical ML architecture
- Hybrid ML + Numerical Weather Prediction system
- Regression + classification forecasting models
- Automated daily inference pipeline
- Continuous forecast evaluation
- PostgreSQL based storage system
- Flask based monitoring dashboard
- Automated email reporting
- Cloud deployed production workflow


---

# 🧠 Core Engineering Idea


Weather forecasting is not a collection of independent prediction problems.

Atmospheric variables are physically connected.

For example:


Temperature influences:

```
temperature
      |
      v
humidity / dew point
      |
      v
rain probability
      |
      v
weather condition
```


Weather Engine follows this dependency structure.

Instead of:

```
Input Data
    |
    +---- Temperature Model

    +---- Rain Model

    +---- Weather Model
```


The system uses:


```
Historical + External Data

          |
          v

Feature Engineering Layer

          |
          v

Temperature + Pressure Models

          |
          v

Moisture Model

          |
          v

Rain Classification

          |
          v

Weather Code Classification

          |
          v

Hybrid ML + NWP Consensus

          |
          v

Final Forecast
```


This creates a dependency-aware forecasting pipeline rather than isolated predictions.


---


# 🏗 Complete System Architecture


```

                Open-Meteo API
                      |
                      |
                      v

             Data Collection Layer

                      |
                      v

              PostgreSQL Database

                      |
                      v

          Feature Engineering Engine

                      |
                      v

        Hierarchical ML Inference System

                      |
                      v

              Prediction Database

                      |
                      v

             Evaluation Engine

                      |
          -------------------------
          |                       |
          v                       v

   Flask Dashboard        Email Reporting

```


The system is separated into independent modules:

| Layer | Responsibility |
|-|-|
| Data Layer | Fetch and validate atmospheric data |
| Storage Layer | Maintain historical records |
| Feature Layer | Generate ML-ready inputs |
| Model Layer | Forecast atmospheric variables |
| Evaluation Layer | Measure prediction quality |
| Interface Layer | Display forecasts and analytics |
| Automation Layer | Execute daily production workflow |


---


# 🤖 Machine Learning Architecture


Weather Engine uses a hierarchical Directed Acyclic Graph (DAG) forecasting architecture.


## Tier 1 — Stable Atmospheric Variables


## Temperature Forecasting Model


Algorithm:

- LightGBM Gradient Boosting
- Multi-output Regression


Targets:

- Maximum temperature
- Minimum temperature


Feature groups:

### Geographic Features

- City identifier
- Latitude
- Longitude


### Temporal Features

- Year
- Month
- Day
- Day of week


### Cyclical Features

Seasonality is encoded using:


```
month_sin
month_cos

day_sin
day_cos
```


This prevents false distance relationships between calendar values.


### Solar Features

- Daylight duration
- Shortwave radiation


### Historical Features

- Lag values
- Rolling averages
- Recent atmospheric trends



---


## Pressure Forecasting Model


Algorithm:

- LightGBM Multi-output Regression


Targets:

- Maximum pressure
- Minimum pressure


Purpose:

Pressure predictions represent large scale atmospheric patterns and provide additional context for dependent models.


---


# Tier 2 — Moisture Forecasting


Algorithm:

- LightGBM Multi-output Regression


Targets:

- Maximum dew point
- Minimum dew point
- Maximum humidity
- Minimum humidity


Inputs include:

- Base atmospheric features
- Temperature predictions
- Pressure predictions


This follows natural atmospheric dependency.


---


# Tier 3 — Rain Occurrence Model


Problem type:

Binary Classification


Output:

```
Rain

or

No Rain
```


Optimization priority:

High recall


Reason:

Missing rainfall events is more costly than occasional false rainfall predictions.


---


# Tier 4 — Weather Condition Model


Problem:

Multi-class Classification


Predicts final weather state categories.


The final layer combines:


```

ML Prediction

      +

NWP Forecast Guidance

      +

Rule Based Consistency Checks

      =

Final Weather Forecast

```


---


# 🌎 Hybrid ML + NWP Strategy


Pure machine learning was tested for several weather variables.

Some atmospheric components showed natural predictability limits.


## Wind Prediction Experiments


Models tested:

- LightGBM
- CatBoost
- Ensemble models


Result:

Performance saturated despite additional engineering.


Reason:

Wind depends on:

- Pressure gradients
- Terrain interaction
- Large scale atmospheric circulation


Decision:

Use Numerical Weather Prediction wind guidance.


---


## Rain Amount Prediction


Challenges:

- Sparse rainfall events
- Extreme value imbalance
- Rare storm patterns
- Complex atmospheric physics


Decision:

Use NWP precipitation amounts.


---


# ⚙️ Feature Engineering Pipeline


Raw observations are converted into structured ML features.


Feature categories:


## Temporal

- Year
- Month
- Day
- Weekday


## Cyclical

- Month sine/cosine
- Day sine/cosine


## Astronomical

- Sunlight duration
- Solar radiation


## Historical

- Lag features
- Rolling means


## External Atmospheric

- NWP forecasts
- Wind variables
- Rain guidance


## Hierarchical

Outputs from previous ML layers become inputs for later layers.


---


# 🗄 Database Design


Database:

PostgreSQL


Tables:


## weather_data

Stores:

- Historical observations
- Actual measured weather


## predictions

Stores:

- Generated forecasts
- Model outputs
- Forecast metadata


## errors

Stores:

- Prediction vs actual comparison
- Error metrics


## nwp_cache

Stores:

- External forecast values


## email_subscriptions

Stores:

- Approved report users


---


# 📊 Evaluation System


Weather Engine continuously evaluates itself.


Regression metrics:

- Mean Absolute Error
- Root Mean Squared Error
- R² Score


Classification metrics:

- Accuracy
- Precision
- Recall
- F1 Score


Workflow:


```

Prediction Generated

        |

Wait for Actual Observation

        |

Compare Forecast vs Reality

        |

Store Error Metrics

        |

Update Dashboard

```


---


# 🔄 Production Automation


Daily pipeline:


```

GitHub Actions Scheduler

          |

          v

master_script.py

          |

 ------------------------
 |          |           |

Data     Models    Evaluation

          |

          v

Database Update

          |

          v

Email Reports

```



Execution stages:

1. Recharge historical data

2. Fetch latest NWP forecasts

3. Generate features

4. Execute ML models

5. Store predictions

6. Evaluate old forecasts

7. Send forecast reports


Runs automatically every day.


---


# ☁️ Deployment Architecture


| Component | Platform |
|-|-|
| Web Backend | Render |
| Database | Neon PostgreSQL |
| Scheduled ML Worker | GitHub Actions |
| Availability Monitoring | UptimeRobot |



Production flow:


```

GitHub Actions

      |

      v

ML Forecast Engine

      |

      v

Neon PostgreSQL

      |

      v

Render Flask Dashboard

```
---

# 🌿 Branching & Production Strategy


Weather Engine follows a two-branch deployment workflow separating the web application lifecycle from automated machine learning execution.


## Branch Structure


| Branch | Responsibility |
|-|-|
| main | Automated ML pipeline execution |
| production | Live Flask web deployment |


---


## main Branch — ML Automation Layer


The `main` branch controls the scheduled forecasting engine.


Responsibilities:

- Daily data refresh
- Feature generation
- ML inference execution
- Forecast evaluation
- Email report generation


Execution:



---


# 🛠 Technology Stack


## Machine Learning

- LightGBM
- Scikit-Learn
- Joblib


## Data Engineering

- Pandas
- NumPy


## Backend

- Flask
- Jinja2


## Database

- PostgreSQL
- SQLAlchemy


## Visualization

- Plotly


## Automation

- GitHub Actions
- SMTP


## Deployment

- Render
- Neon
- UptimeRobot


## External Data

- Open-Meteo API


---


# 📁 Repository Structure


```
Weather_Engine/

├── app/
│
│   ├── database/
│   ├── flask_app/
│   ├── ml/
│   └── email/
│
├── scripts/
│   └── automation pipeline
│
├── model/
│   └── trained ML models
│
├── docs/
│   └── engineering documentation
│
├── notebooks/
│   └── experimentation
│
├── .github/workflows/
│   └── production automation
│
├── requirements.txt
├── requirements-cron.txt
└── README.md
```


---


# Current Limitations


Weather Engine is an engineering-focused forecasting platform and not a replacement for operational meteorological systems.


Current constraints:

- Limited city coverage
- Extreme weather events require larger datasets
- Some chaotic variables require NWP support
- Daily forecast resolution


---


# Future Improvements


Planned extensions:

- Larger geographic coverage
- Automated retraining pipeline
- Model drift detection
- Forecast versioning
- Advanced ensemble systems
- Higher frequency forecasting


---


# Engineering Philosophy


Weather Engine represents the transition from building individual ML models to designing complete AI-powered software systems.


The focus is on:


✔ Machine Learning Engineering  

✔ Data Engineering  

✔ System Architecture  

✔ Automation  

✔ Evaluation  

✔ Production Deployment  


The goal is not only prediction accuracy, but building reliable infrastructure around intelligent systems.


---


© 2026 Weather Engine  
Hybrid Machine Learning Forecasting System
