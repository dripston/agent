from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from datetime import datetime, timedelta
import uvicorn

from weather_agent.weather_predictor import WeatherPredictor
from weather_agent.data_fetcher import OpenMeteoFetcher
from weather_agent.training.model_trainer import WeatherModelTrainer
from weather_agent.validation.validator import WeatherValidator

app = FastAPI(title="Weather Prediction AI Agent")

class WeatherRequest(BaseModel):
    location: str
    date: str

class WeatherResponse(BaseModel):
    location: str
    date: str
    forecast: dict
    confidence: dict

weather_predictor = WeatherPredictor()

@app.post("/train")
async def train_models():
    try:
        # Initialize components
        fetcher = OpenMeteoFetcher()
        trainer = WeatherModelTrainer()
        
        # Fetch training data (last 2 years)
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")
        
        # Mumbai coordinates (example)
        data = fetcher.fetch_historical_data(19.0760, 72.8777, start_date, end_date)
        
        # Train models
        trainer.train(data)
        
        return {"message": "Models trained successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/predict_weather", response_model=WeatherResponse)
async def predict_weather(request: WeatherRequest):
    try:
        forecast = weather_predictor.predict(request.location, request.date)
        confidence = {
            "temperature": 0.85,
            "precipitation": 0.75,
            "humidity": 0.80,
            "wind_speed": 0.70
        }
        
        return WeatherResponse(
            location=request.location,
            date=request.date,
            forecast=forecast,
            confidence=confidence
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)