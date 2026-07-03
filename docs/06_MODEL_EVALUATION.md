# Model Evaluation


## Regression Metrics


Primary metric:

Mean Absolute Error


Reason:

MAE directly represents average forecasting mistake in physical units.



Examples:

Temperature:

1°C MAE means average error around one degree.



Pressure:

1 hPa MAE means atmospheric pressure deviation.



---


## Classification Metrics


Rain:

Precision

Recall

F1 Score


Recall optimized because missing rainfall events is considered more harmful.



---


## Continuous Evaluation


Every forecast is stored.

After actual observations arrive:

Prediction → Actual Comparison → Error Storage → Dashboard Update


