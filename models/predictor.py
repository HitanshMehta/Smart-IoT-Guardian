import numpy as np
from sklearn.linear_model import LinearRegression

class TemperaturePredictor:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.temperature_history = {}
    
    def update_history(self, sensor_id, temperature):
        if sensor_id not in self.temperature_history:
            self.temperature_history[sensor_id] = []
        
        self.temperature_history[sensor_id].append(temperature)
        if len(self.temperature_history[sensor_id]) > self.window_size:
            self.temperature_history[sensor_id].pop(0)
    
    def predict_temperature(self, sensor_id, steps=1):
        if sensor_id not in self.temperature_history or len(self.temperature_history[sensor_id]) < 5:
            return None
        
        history = self.temperature_history[sensor_id]
        X = np.arange(len(history)).reshape(-1, 1)
        y = np.array(history)
        
        model = LinearRegression()
        model.fit(X, y)
        
        # Predict next value
        next_time = len(history)
        prediction = model.predict([[next_time]])[0]
        
        return round(prediction, 2)