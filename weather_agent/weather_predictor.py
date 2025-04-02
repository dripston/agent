import datetime
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from weather_agent.data_fetcher import OpenMeteoFetcher

class WeatherPredictor:
    def __init__(self):
        self.data_fetcher = OpenMeteoFetcher()
        self.models = {
            'temperature': GradientBoostingRegressor(),
            'precipitation': GradientBoostingRegressor(),
            'humidity': GradientBoostingRegressor(),
            'wind_speed': GradientBoostingRegressor()
        }
        self.scalers = {
            'temperature': StandardScaler(),
            'precipitation': StandardScaler(),
            'humidity': StandardScaler(),
            'wind_speed': StandardScaler()
        }
        
    def train(self, location_lat: float, location_lon: float):
        # Fetch last 2 years of data
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - datetime.timedelta(days=730)).strftime("%Y-%m-%d")
        
        historical_data = self.data_fetcher.fetch_historical_data(
            location_lat, location_lon, start_date, end_date
        )
        
        # Prepare features (you might want to add more sophisticated feature engineering)
        features = self._prepare_features(historical_data)
        
        # Train models for each weather parameter
        for param in self.models.keys():
            X = self.scalers[param].fit_transform(features)
            y = historical_data[param].values
            self.models[param].fit(X, y)
    
    def predict(self, location: str, target_date: str) -> dict:
        # In a real implementation, you would need to convert location to lat/lon
        # For this example, we'll use Mumbai's coordinates
        lat, lon = 19.0760, 72.8777
        
        # Get recent data for prediction
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - datetime.timedelta(days=30)).strftime("%Y-%m-%d")
        recent_data = self.data_fetcher.fetch_historical_data(lat, lon, start_date, end_date)
        
        # Prepare features for prediction
        features = self._prepare_features(recent_data)
        
        # Make predictions
        predictions = {}
        confidence_intervals = {}
        for param in self.models.keys():
            X = self.scalers[param].transform(features[-1:])
            pred = self.models[param].predict(X)[0]
            
            # Calculate prediction intervals
            lower, upper = self._calculate_confidence_intervals(X, param)
            
            predictions[param] = round(float(pred), 2)
            confidence_intervals[param] = {
                'lower': round(float(lower), 2),
                'upper': round(float(upper), 2)
            }
        
        # Format response
        return {
            "temperature": f"{predictions['temperature']}°C",
            "rain_probability": f"{min(100, max(0, predictions['precipitation'] * 100))}%",
            "humidity": f"{min(100, max(0, predictions['humidity']))}%",
            "wind_speed": f"{predictions['wind_speed']} km/h",
            "explanation": self._generate_explanation(predictions),
            "confidence_intervals": confidence_intervals
        }
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        features = pd.DataFrame({
            # Temporal features
            'hour': df['timestamp'].dt.hour,
            'day': df['timestamp'].dt.day,
            'month': df['timestamp'].dt.month,
            'season': df['timestamp'].dt.month.map(self._get_season),
            
            # Weather patterns
            'temperature_moving_avg': df['temperature'].rolling(24).mean(),
            'pressure_gradient': df['pressure'].diff(),
            'wind_direction_encoded': self._encode_wind_direction(df['wind_direction']),
            
            # Atmospheric stability indicators
            'temp_humidity_index': df['temperature'] * df['humidity'],
            'pressure_tendency': self._calculate_pressure_tendency(df['pressure']),
            
            # Historical patterns
            'last_24h_rain': df['precipitation'].rolling(24).sum(),
            'temp_range': df['temperature'].rolling(24).max() - df['temperature'].rolling(24).min()
        })
        return features.values
    
    def _generate_explanation(self, predictions: dict) -> str:
        # Generate a human-readable explanation
        if predictions['precipitation'] > 0.5:
            weather_type = "heavy rainfall"
        elif predictions['precipitation'] > 0.2:
            weather_type = "moderate rainfall"
        elif predictions['precipitation'] > 0:
            weather_type = "light rainfall"
        else:
            weather_type = "clear weather"
            
        return f"Based on historical weather patterns, expect {weather_type} with a temperature of {predictions['temperature']}°C"

    def _calculate_confidence_intervals(self, X, param):
        # Placeholder for calculating confidence intervals
        # This should be implemented based on the specific model and its confidence interval calculation
        return (X[0][0] - 0.5, X[0][0] + 0.5)