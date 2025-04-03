from datetime import datetime, timedelta

class OpenMeteoHistorical:
    def __init__(self):
        self.base_url = "https://archive-api.open-meteo.com/v1/archive"
        
    def get_hourly_history(self, location):
        # Get 5 years of hourly data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=5*365)
        
        params = {
            "latitude": location['lat'],
            "longitude": location['lon'],
            "start_date": start_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "hourly": ["temperature_2m", "precipitation", "cloudcover",
                      "windspeed_10m", "winddirection_10m"]
        }
        
        return self._fetch_and_process_data(params)