# Data Pipeline


## Daily Execution Flow


1. Load City Configuration


Input:

cities.json


Contains:

- City ID
- Name
- Coordinates


---


2. Fetch Weather Observations


Retrieves:

- Temperature
- Pressure
- Humidity
- Wind
- Rain
- Weather condition


---


3. Feature Generation


Creates:

Temporal Features:

- Year
- Month
- Day


Cyclical:

- sin/cos transformations


Historical:

- Lag values
- Rolling averages


External:

- NWP variables



---


4. Run Forecast Engine


Execution:

Load Models

↓

Generate Predictions

↓

Apply Hybrid Logic

↓

Store Forecasts


---


5. Evaluation


When actual weather arrives:


Prediction

vs

Observation


Metrics calculated:

- MAE
- Classification accuracy
