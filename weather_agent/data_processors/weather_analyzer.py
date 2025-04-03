import pandas as pd
import numpy as np
from datetime import datetime

class WeatherAnalyzer:
    def __init__(self):
        self.patterns = {}
    
    def analyze_historical_data(self, data):
        # Convert hourly data to pandas DataFrame
        df = pd.DataFrame({
            'time': pd.to_datetime(data['weather']['hourly']['time']),
            'temp': data['weather']['hourly']['temperature_2m'],
            'precip': data['weather']['hourly']['precipitation'],
            'wind': data['weather']['hourly']['windspeed_10m'],
            'cloud': data['weather']['hourly']['cloudcover']
        })
        
        # Add time-based features
        df['hour'] = df['time'].dt.hour
        df['month'] = df['time'].dt.month
        
        # Calculate patterns
        self.patterns = {
            'hourly_rain_prob': self._calculate_rain_probability(df),
            'temp_patterns': self._analyze_temperature(df),
            'wind_patterns': self._analyze_wind(df),
            'elevation_impact': self._analyze_elevation_impact(df, data['elevation'])
        }
        
        return self.patterns
    
    def _calculate_rain_probability(self, df):
        return df.groupby('hour')['precip'].apply(
            lambda x: (x > 0.1).mean()
        ).to_dict()
    
    def _analyze_temperature(self, df):
        return {
            'hourly_avg': df.groupby('hour')['temp'].mean().to_dict(),
            'monthly_avg': df.groupby('month')['temp'].mean().to_dict()
        }
    
    def _analyze_wind(self, df):
        return {
            'hourly_avg': df.groupby('hour')['wind'].mean().to_dict(),
            'max_wind': df.groupby('hour')['wind'].max().to_dict()
        }
    
    def _analyze_elevation_impact(self, df, elevation):
        if elevation is None:
            return {}
            
        # Handle elevation data whether it's a list or single value
        try:
            if isinstance(elevation, list):
                elevation_value = float(elevation[0])
            else:
                elevation_value = float(elevation)
        except (TypeError, ValueError, IndexError):
            return {}
            
        # Basic elevation impact analysis
        return {
            'elevation_m': elevation_value,
            'temp_correction': -0.0065 * elevation_value,  # Standard lapse rate
            'pressure_factor': np.exp(-elevation_value/7400)  # Atmospheric pressure decay
        }