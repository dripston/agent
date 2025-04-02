import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error

class WeatherValidator:
    def __init__(self):
        self.metrics = {}
    
    def validate_predictions(self, predictions: dict, actual: pd.DataFrame):
        for parameter in predictions.keys():
            mse = mean_squared_error(actual[parameter], predictions[parameter])
            mae = mean_absolute_error(actual[parameter], predictions[parameter])
            
            self.metrics[parameter] = {
                'rmse': np.sqrt(mse),
                'mae': mae
            }
        
        return self.metrics
    
    def generate_report(self):
        report = "Weather Prediction Validation Report\n"
        report += "================================\n\n"
        
        for parameter, metrics in self.metrics.items():
            report += f"{parameter.capitalize()}:\n"
            report += f"  RMSE: {metrics['rmse']:.2f}\n"
            report += f"  MAE: {metrics['mae']:.2f}\n\n"
        
        return report 