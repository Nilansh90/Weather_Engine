import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime

from dotenv import load_dotenv

load_dotenv()


class EmailReporter:

    def __init__(self):

        self.sender = os.getenv("EMAIL_ADDRESS")
        self.password = os.getenv("EMAIL_PASSWORD")
        self.receiver = os.getenv("RECIPIENT_EMAIL")

    ########################################################

    def _forecast_section(self, forecast):

        html = f"""

        <h2>🤖 Weather Engine Forecast</h2>

        <table border="1" cellpadding="5">

        <tr><td>Temperature Max</td><td>{forecast['temp_max_c']:.2f} °C</td></tr>

        <tr><td>Temperature Min</td><td>{forecast['temp_min_c']:.2f} °C</td></tr>

        <tr><td>Pressure Max</td><td>{forecast['pressure_msl_max_hpa']:.2f} hPa</td></tr>

        <tr><td>Pressure Min</td><td>{forecast['pressure_msl_min_hpa']:.2f} hPa</td></tr>

        <tr><td>Dew Point Max</td><td>{forecast['dew_point_max_c']:.2f} °C</td></tr>

        <tr><td>Dew Point Min</td><td>{forecast['dew_point_min_c']:.2f} °C</td></tr>

        <tr><td>RH Max</td><td>{forecast['relative_humidity_max_pct']:.2f}%</td></tr>

        <tr><td>RH Min</td><td>{forecast['relative_humidity_min_pct']:.2f}%</td></tr>

        <tr><td>Rain Probability</td><td>{forecast['rain_probability']:.2%}</td></tr>

        <tr><td>Rain Predicted</td><td>{forecast['will_rain']}</td></tr>

        <tr><td>Cloud Cover</td><td>{forecast['cloud_cover_mean_pct']:.2f}%</td></tr>

        <tr><td>Wind Speed</td><td>{forecast['wind_speed_max_kmh']:.2f} km/h</td></tr>

        <tr><td>Wind Gusts</td><td>{forecast['wind_gusts_max_kmh']:.2f} km/h</td></tr>

        <tr><td>Weather Code</td><td>{forecast['weather_code']}</td></tr>

        </table>

        """

        return html


    ########################################################


    def _nwp_section(self, nwp):


        html = f"""

        <h2>🌍 OpenMeteo Forecast</h2>

        <table border="1" cellpadding="5">

        <tr><td>Wind Speed</td><td>{nwp['wind_speed_max_kmh']:.2f}</td></tr>

        <tr><td>Wind Gusts</td><td>{nwp['wind_gusts_max_kmh']:.2f}</td></tr>

        <tr><td>Cloud Cover</td><td>{nwp['cloud_cover_mean_pct']:.2f}</td></tr>

        <tr><td>Rain Amount</td><td>{nwp['precipitation_sum_mm']:.2f}</td></tr>

        <tr><td>Weather Code</td><td>{nwp['weather_code']}</td></tr>

        </table>

        """

        return html


    ########################################################


    def _actual_section(self, actual):


        html = f"""

        <h2>📍 Actual Weather</h2>

        <table border="1" cellpadding="5">

        <tr><td>Temp Max</td><td>{actual['temp_max_c']}</td></tr>

        <tr><td>Temp Min</td><td>{actual['temp_min_c']}</td></tr>

        <tr><td>Pressure Max</td><td>{actual['pressure_msl_max_hpa']}</td></tr>

        <tr><td>Pressure Min</td><td>{actual['pressure_msl_min_hpa']}</td></tr>

        <tr><td>Rainfall</td><td>{actual['precipitation_sum_mm']}</td></tr>

        <tr><td>Cloud Cover</td><td>{actual['cloud_cover_mean_pct']}</td></tr>

        <tr><td>Weather Code</td><td>{actual['weather_code']}</td></tr>

        </table>

        """

        return html


    ########################################################


    def _error_section(self, errors):


        html = f"""

        <h2>📈 Error Analysis</h2>

        <table border="1" cellpadding="5">

        <tr><td>Temperature Error</td><td>{errors['temp_mae']:.2f}</td></tr>

        <tr><td>Pressure Error</td><td>{errors['pressure_mae']:.2f}</td></tr>

        <tr><td>Dew Point Error</td><td>{errors['dew_mae']:.2f}</td></tr>

        <tr><td>Humidity Error</td><td>{errors['rh_mae']:.2f}</td></tr>

        <tr><td>Rain Correct</td><td>{errors['rain_correct']}</td></tr>

        <tr><td>Weather Code Correct</td><td>{errors['weather_correct']}</td></tr>

        </table>

        """

        return html


    ########################################################


    def _pipeline_section(self, pipeline):


        html = f"""

        <h2>⚙ Pipeline Status</h2>

        <table border="1" cellpadding="5">

        <tr><td>Cities Processed</td><td>{pipeline['cities_processed']}</td></tr>

        <tr><td>Cache Hits</td><td>{pipeline['cache_hits']}</td></tr>

        <tr><td>API Calls</td><td>{pipeline['api_calls']}</td></tr>

        <tr><td>Status</td><td>{pipeline['status']}</td></tr>

        </table>

        """

        return html


    ########################################################


    def build_html(self,
                   forecast,
                   nwp,
                   actual,
                   errors,
                   pipeline):



        report_time = datetime.now().strftime(

            "%Y-%m-%d %H:%M"

        )



        html = f"""

        <html>

        <body>

        <h1>🌤 Weather Engine Daily Report</h1>

        <p>

        Generated at : {report_time}

        </p>

        <hr>

        {self._forecast_section(forecast)}

        <hr>

        {self._nwp_section(nwp)}

        <hr>

        {self._actual_section(actual)}

        <hr>

        {self._error_section(errors)}

        <hr>

        {self._pipeline_section(pipeline)}

        </body>

        </html>

        """



        return html


    ########################################################


    def send_daily_report(self,
                          forecast,
                          nwp,
                          actual,
                          errors,
                          pipeline):



        html = self.build_html(

            forecast,
            nwp,
            actual,
            errors,
            pipeline

        )


        message = MIMEMultipart()


        message["From"] = self.sender

        message["To"] = self.receiver

        message["Subject"] = (

            "Weather Engine Daily Report"

        )


        message.attach(

            MIMEText(

                html,

                "html"

            )

        )


        with smtplib.SMTP(

                "smtp.gmail.com",

                587

        ) as smtp:


            smtp.starttls()


            smtp.login(

                self.sender,

                self.password

            )


            smtp.sendmail(

                self.sender,

                self.receiver,

                message.as_string()

            )


        print(

            "Daily weather report sent."

        )