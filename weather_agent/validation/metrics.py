class ForecastValidator:
    def validate_forecast(self, predictions, actual_weather):
        metrics = {
            'rmse': self._calculate_rmse(predictions, actual_weather),
            'mae': self._calculate_mae(predictions, actual_weather),
            'skill_score': self._calculate_skill_score(predictions, actual_weather),
            'reliability': self._assess_reliability(predictions, actual_weather)
        }
        return metrics 