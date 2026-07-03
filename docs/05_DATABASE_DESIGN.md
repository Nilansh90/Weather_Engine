# Database Architecture


Database:

PostgreSQL


## Tables


## weather_data


Purpose:

Stores verified historical observations.


Contains:

Temperature

Pressure

Humidity

Wind

Rain

Weather Code



---


## predictions


Purpose:

Stores generated forecasts.


Fields:

- Forecast date
- Model outputs
- Confidence
- Metadata



---


## errors


Purpose:

Tracks forecasting performance.


Metrics:

Temperature Error

Pressure Error

Humidity Error

Rain Correct

Weather Code Correct



---


## nwp_cache


Purpose:

Stores external forecast data.



---


## email_subscriptions


Purpose:

Manages forecast report users.

