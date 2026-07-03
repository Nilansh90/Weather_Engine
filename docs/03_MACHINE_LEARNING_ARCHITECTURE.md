# Machine Learning Architecture


## Design Philosophy


Traditional ML forecasting approaches attempt to predict every atmospheric variable independently.


Weather Engine follows a dependency-aware hybrid strategy.


Variables with strong historical patterns:

- Temperature
- Pressure
- Moisture


are predicted internally.


Variables dominated by chaotic physical processes:

- Wind
- Cloud dynamics
- Rainfall quantity


are retrieved through Numerical Weather Prediction.


Tier 1:

Temperature
Pressure


        ↓


Tier 2:

Moisture


        ↓


Tier 3:

Rain Classification


        ↓


Tier 4:

Weather Code


        ↓


Hybrid Consensus


## Temperature Model


Type:

Multi Output Regression


Algorithm:

LightGBM


Targets:

- Maximum temperature
- Minimum temperature


Input Features:

Geographical:
- Latitude
- Longitude
- City ID


Temporal:

- Year
- Month encoding
- Day encoding


Astronomical:

- Daylight duration
- Shortwave radiation


Historical:

- Lag features
- Rolling statistics



Performance:

Temp Max MAE: 1.12°C

Temp Min MAE: 0.98°C


## Pressure Model


Purpose:

Estimate atmospheric pressure trends required for downstream weather prediction.


Model:

LightGBM Multi Output Regression


Targets:

- Pressure maximum
- Pressure minimum


Performance:

Pressure Max MAE: 1.05 hPa

Pressure Min MAE: 0.76 hPa


## Wind Forecasting Decision


Initial Approach:

Internal machine learning regression


Models tested:

- LightGBM
- CatBoost
- Ensembles


Observation:

Training performance increased but validation performance saturated around R² ≈ 0.65.


Conclusion:

Wind behaviour depends heavily on:

- Pressure gradients
- Terrain
- Regional atmospheric systems


Decision:

Shift wind prediction to external Numerical Weather Prediction.


## Rain Amount Forecasting


Initial Approach:

Tweedie regression


Problem:

Rainfall quantity contains:

- Zero inflation
- Extreme events
- High variance


Final Decision:

Use NWP rainfall predictions because physical atmospheric simulation handles precipitation dynamics better.


## Hybrid Consensus Filter


The final weather state is not determined by ML alone.


Process:


ML prediction

+

NWP forecast

↓

Agreement Check

↓

Final Weather Code


This improves operational reliability.
