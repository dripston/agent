# Remove this line since we already have the proper import below
# import datetime
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from .data_fetcher import OpenMeteoFetcher  # Note the relative import

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
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        
        historical_data = self.data_fetcher.fetch_historical_data(
            location_lat, location_lon, start_date, end_date
        )
        
        # Debug: Print available columns
        print("Available columns:", historical_data.columns.tolist())
        
        # Map OpenMeteo columns to our model parameters and handle missing values
        column_mapping = {
            'temperature': 'temperature',
            'precipitation': 'precipitation',
            'humidity': 'humidity',
            'wind_speed': 'wind_speed'
        }
        
        # Create new columns with mapped names and fill NaN values
        for model_param, api_param in column_mapping.items():
            if api_param in historical_data.columns:
                historical_data[model_param] = historical_data[api_param].ffill().bfill().fillna(0)
            else:
                raise Exception(f"Required column {api_param} not found in data. Available columns: {historical_data.columns.tolist()}")
        
        # Prepare features
        features = self._prepare_features(historical_data)
        
        # Train models for each weather parameter
        for param in self.models.keys():
            try:
                X = self.scalers[param].fit_transform(features)
                y = historical_data[param].values
                # Double check for any remaining NaN values
                if np.any(np.isnan(y)):
                    raise Exception(f"NaN values found in {param} target data")
                self.models[param].fit(X, y)
            except Exception as e:
                raise Exception(f"Error training {param} model: {str(e)}")

        return {"message": "Models trained successfully"}

    def predict(self, location: str, target_date: str) -> dict:
        lat, lon = 19.0760, 72.8777
        
        # Get recent data for prediction
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        recent_data = self.data_fetcher.fetch_historical_data(lat, lon, start_date, end_date)
        
        # Map OpenMeteo columns to our model parameters
        column_mapping = {
            'temperature': 'temperature',
            'precipitation': 'precipitation',
            'humidity': 'humidity',
            'wind_speed': 'wind_speed'
        }
        
        # Create new columns with mapped names and fill NaN values
        for model_param, api_param in column_mapping.items():
            if api_param in recent_data.columns:
                recent_data[model_param] = recent_data[api_param].fillna(method='ffill').fillna(method='bfill').fillna(0)
        
        # Prepare features for prediction
        features = self._prepare_features(recent_data)
        
        # Make predictions
        predictions = {}
        confidence_intervals = {}
        
        # Check if models are trained and make predictions
        for param, model in self.models.items():
            try:
                if hasattr(model, 'n_features_in_'):  # Check if model is trained
                    X = self.scalers[param].transform(features[-1:])
                    pred = model.predict(X)[0]
                    
                    # Calculate prediction intervals
                    lower, upper = self._calculate_confidence_intervals(X, param)
                    
                    predictions[param] = round(float(pred), 2)
                    confidence_intervals[param] = {
                        'lower': round(float(lower), 2),
                        'upper': round(float(upper), 2)
                    }
                else:
                    raise Exception("Model not trained")
            except Exception as e:
                raise Exception(f"Error predicting {param}: {str(e)}")
        
        # Format and return response
        return {
            "temperature": f"{predictions['temperature']}°C",
            "rain_probability": f"{min(100, max(0, predictions['precipitation'] * 100))}%",
            "humidity": f"{min(100, max(0, predictions['humidity']))}%",
            "wind_speed": f"{predictions['wind_speed']} km/h",
            "explanation": self._generate_explanation(predictions),
            "confidence_intervals": confidence_intervals
        }
    
    def _prepare_features(self, df: pd.DataFrame) -> np.ndarray:
        # Fill NaN values in the input data
        df = df.ffill().bfill()
        
        # Create a copy of the dataframe to avoid modifying the original
        df_copy = df.copy()
        
        features = pd.DataFrame({
            # Temporal features
            'hour': df_copy['timestamp'].dt.hour,
            'day': df_copy['timestamp'].dt.day,
            'month': df_copy['timestamp'].dt.month,
            'season': df_copy['timestamp'].dt.month.map(self._get_season),
            
            # Weather patterns
            'temperature_moving_avg': df_copy.get('temperature', pd.Series(0, index=df_copy.index)).rolling(24, min_periods=1).mean(),
            'pressure_gradient': df_copy.get('pressure', pd.Series(0, index=df_copy.index)).diff().fillna(0),
            
            # Atmospheric stability indicators
            'temp_humidity_index': (df_copy.get('temperature', pd.Series(0, index=df_copy.index)) * 
                                  df_copy.get('humidity', pd.Series(50, index=df_copy.index))),
            'pressure_tendency': self._calculate_pressure_tendency(df_copy.get('pressure', pd.Series(0, index=df_copy.index))),
            
            # Historical patterns
            'last_24h_rain': df_copy.get('precipitation', pd.Series(0, index=df_copy.index)).rolling(24, min_periods=1).sum(),
            'temp_range': (df_copy.get('temperature', pd.Series(0, index=df_copy.index)).rolling(24, min_periods=1).max() - 
                         df_copy.get('temperature', pd.Series(0, index=df_copy.index)).rolling(24, min_periods=1).min())
        })
        
        # Fill any remaining NaN values with 0
        features = features.fillna(0)
        
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

    def _get_season(self, month: int) -> int:
        if month in [12, 1, 2]:
            return 0  # Winter
        elif month in [3, 4, 5]:
            return 1  # Spring
        elif month in [6, 7, 8]:
            return 2  # Summer
        else:
            return 3  # Fall

    def _encode_wind_direction(self, direction):
        # Convert wind direction to radians for cyclic feature
        return np.sin(direction * np.pi / 180)

    def _calculate_pressure_tendency(self, pressure):
        # Calculate 3-hour pressure change
        return pressure.diff(periods=3)

    def predict_micro_location(self, city: str, area: str, target_date: str) -> dict:
        location_data = self.micro_location_mapper.get_coordinates(city, area)
        
        # Get hourly predictions for the next 24 hours
        hourly_predictions = {}
        for hour in range(24):
            features = self._prepare_micro_features(location_data, hour)
            predictions = self._get_hourly_prediction(features)
            
            if predictions['precipitation'] > 0.2:  # Significant rain threshold
                hourly_predictions[hour] = {
                    "rain_probability": f"{predictions['precipitation'] * 100:.1f}%",
                    "intensity": self._get_rain_intensity(predictions['precipitation']),
                    "duration": self._estimate_duration(hour, predictions),
                    "specific_location": self._get_specific_location(location_data, predictions)
                }
        
        return self._format_micro_prediction(hourly_predictions)

    def _get_specific_location(self, location_data, predictions):
        # Use terrain data and wind patterns to predict exact rain location
        base_lat, base_lon = location_data['lat'], location_data['lon']
        wind_direction = predictions['wind_direction']
        wind_speed = predictions['wind_speed']
        
        # Calculate affected area radius based on precipitation intensity
        affected_radius = self._calculate_affected_radius(predictions['precipitation'])
        
        return {
            "center": {"lat": base_lat, "lon": base_lon},
            "radius": affected_radius,
            "direction": wind_direction,
            "landmarks": self._get_nearby_landmarks(base_lat, base_lon)
        }