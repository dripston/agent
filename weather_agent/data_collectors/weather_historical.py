import requests
from datetime import datetime, timedelta
import json
import os

class HistoricalWeather:
    def __init__(self):
        self.api_url = "https://archive-api.open-meteo.com/v1/archive"
        self.elevation_cache_file = "c:/Users/drips/agent-2/weather_agent/data/elevation_cache.json"
        
    def get_historical_data(self, lat, lon):
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
            "end_date": datetime.now().strftime("%Y-%m-%d"),
            "hourly": ["temperature_2m", "precipitation", "windspeed_10m", 
                      "winddirection_10m", "cloudcover", "pressure_msl"],
            "timezone": "auto"
        }
        
        weather_data = requests.get(self.api_url, params=params).json()
        elevation_data = self._get_elevation(lat, lon)
        
        return {
            "weather": weather_data,
            "elevation": elevation_data,
            "metadata": {
                "location": {"lat": lat, "lon": lon},
                "timestamp": datetime.now().isoformat()
            }
        }
    
    def _get_elevation(self, lat, lon):
        # Using Open-Meteo's geocoding API which includes elevation data
        elevation_api = f"https://api.open-meteo.com/v1/elevation"
        params = {
            "latitude": lat,
            "longitude": lon
        }
        
        try:
            response = requests.get(elevation_api, params=params)
            data = response.json()
            return data.get('elevation', None)
        except Exception as e:
            print(f"Error fetching elevation data: {e}")
            return None