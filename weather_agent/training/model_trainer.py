import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
import joblib

class WeatherModelTrainer:
    def __init__(self):
        self.models = {
            'temperature': RandomForestRegressor(),
            'precipitation': RandomForestRegressor(),
            'humidity': RandomForestRegressor(),
            'wind_speed': RandomForestRegressor()
        }
        self.model_path = 'weather_agent/models/saved/'
    
    def train(self, data: pd.DataFrame):
        for parameter, model in self.models.items():
            print(f"Training {parameter} model...")
            
            # Prepare features
            X = self._prepare_features(data)
            y = data[parameter]
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
            
            # Train model
            model.fit(X_train, y_train)
            
            # Save model
            joblib.dump(model, f"{self.model_path}{parameter}_model.pkl")
            
            # Evaluate
            score = model.score(X_test, y_test)
            print(f"{parameter} model R² score: {score:.3f}")
    
    def _prepare_features(self, data: pd.DataFrame):
        features = pd.DataFrame({
            'hour': data['timestamp'].dt.hour,
            'day': data['timestamp'].dt.day,
            'month': data['timestamp'].dt.month,
            'cloud_cover': data['cloud_cover'],
            'satellite_temperature': data['satellite_temperature'],
            'precipitation_intensity': data['precipitation_intensity'],
            'ground_temperature': data['ground_temperature'],
            'soil_moisture': data['soil_moisture']
        })
        return features 