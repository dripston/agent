import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from weather_agent.data_collectors.weather_historical import HistoricalWeather
from weather_agent.data_processors.weather_analyzer import WeatherAnalyzer

def analyze_location_weather(lat, lon):
    # Collect historical data
    collector = HistoricalWeather()
    historical_data = collector.get_historical_data(lat, lon)
    
    # Analyze patterns
    analyzer = WeatherAnalyzer()
    patterns = analyzer.analyze_historical_data(historical_data)
    
    # Print location and elevation
    print(f"Weather Analysis for Peenya, Bangalore")
    print(f"Coordinates: {lat}°N, {lon}°E")
    print(f"Elevation: {historical_data['elevation'][0]}m")
    
    # Temperature analysis
    print("\nTemperature Patterns:")
    print("Peak Temperature:", max(patterns['temp_patterns']['hourly_avg'].values()), "°C")
    print("Lowest Temperature:", min(patterns['temp_patterns']['hourly_avg'].values()), "°C")
    print("\nHourly Temperature Breakdown:")
    for hour, temp in patterns['temp_patterns']['hourly_avg'].items():
        time_period = "Night" if 0 <= hour < 6 else "Morning" if 6 <= hour < 12 else "Afternoon" if 12 <= hour < 17 else "Evening"
        print(f"{hour:02d}:00 - {temp:.1f}°C ({time_period})")
    
    # Rain probability analysis
    print("\nRain Probability Analysis:")
    rain_hours = {hour: prob for hour, prob in patterns['hourly_rain_prob'].items() if prob > 0.2}
    if rain_hours:
        print("Likely Rain Hours:")
        for hour, prob in rain_hours.items():
            print(f"{hour:02d}:00 - {prob*100:.1f}% chance of rain")
    else:
        print("No significant rain probability detected")
    
    # Wind patterns
    print("\nWind Patterns:")
    max_wind_hour = max(patterns['wind_patterns']['hourly_avg'].items(), key=lambda x: x[1])
    print(f"Peak Wind Speed: {patterns['wind_patterns']['max_wind'][max_wind_hour[0]]:.1f} km/h at {max_wind_hour[0]:02d}:00")

# Example usage for Bangalore (Peenya)
analyze_location_weather(13.0234, 77.5144)