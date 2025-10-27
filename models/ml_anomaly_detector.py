import numpy as np
from sklearn.ensemble import IsolationForest

class MLAnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(contamination=0.1, random_state=42)
        self.is_trained = False
        self.data_buffer = []
        
    def extract_features(self, sensor_data):
        """Extract features for ML model"""
        return np.array([
            sensor_data['temperature'],
            sensor_data['humidity'],
            sensor_data['vibration'],
            abs(sensor_data['temperature'] - 25),  # Deviation from normal
            sensor_data['humidity'] / 100.0,       # Normalized humidity
        ]).reshape(1, -1)
    
    def update_and_predict(self, sensor_data):
        """Online learning and prediction"""
        features = self.extract_features(sensor_data)
        
        # Add to buffer
        self.data_buffer.append(features.flatten())
        if len(self.data_buffer) > 100:
            self.data_buffer.pop(0)
        
        # Retrain periodically
        if len(self.data_buffer) >= 50 and len(self.data_buffer) % 20 == 0:
            self.model.fit(self.data_buffer)
            self.is_trained = True
        
        # Predict if trained
        if self.is_trained:
            prediction = self.model.predict(features)
            score = self.model.decision_function(features)
            return prediction[0] == -1, abs(score[0])
        
        return False, 0.0