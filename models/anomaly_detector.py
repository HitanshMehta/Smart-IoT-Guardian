import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
import joblib
import json

class StreamingAnomalyDetector:
    def __init__(self, contamination=0.1):
        self.model = IsolationForest(
            contamination=contamination,
            random_state=42,
            n_estimators=100
        )
        self.scaler = StandardScaler()
        self.is_fitted = False
        self.window_size = 100
        self.data_buffer = []
        
    def extract_features(self, sensor_data):
        """Extract features from sensor data for anomaly detection"""
        features = [
            sensor_data['temperature'],
            sensor_data['humidity'], 
            sensor_data['pressure'],
            sensor_data['vibration'],
            # Derived features
            abs(sensor_data['temperature'] - 22.5),  # Distance from ideal temp
            sensor_data['vibration'] * 10,  # Amplified vibration
        ]
        return np.array(features).reshape(1, -1)
    
    def update_model(self, new_data_point):
        """Update the model with new data point (online learning)"""
        self.data_buffer.append(new_data_point)
        
        # Keep only recent data
        if len(self.data_buffer) > self.window_size:
            self.data_buffer.pop(0)
            
        # Retrain model periodically
        if len(self.data_buffer) >= 50 and len(self.data_buffer) % 20 == 0:
            self._retrain_model()
    
    def _retrain_model(self):
        """Retrain the model with current data buffer"""
        if len(self.data_buffer) < 10:
            return
            
        features = np.vstack([self.extract_features(data)[0] for data in self.data_buffer])
        
        if not self.is_fitted:
            scaled_features = self.scaler.fit_transform(features)
            self.model.fit(scaled_features)
            self.is_fitted = True
        else:
            scaled_features = self.scaler.transform(features)
            self.model.fit(scaled_features)
    
    def detect_anomaly(self, sensor_data):
        """Detect if current sensor reading is anomalous"""
        if not self.is_fitted or len(self.data_buffer) < 10:
            return False, 0.0
            
        features = self.extract_features(sensor_data)
        scaled_features = self.scaler.transform(features)
        
        prediction = self.model.predict(scaled_features)
        anomaly_score = self.model.decision_function(scaled_features)
        
        is_anomaly = prediction[0] == -1
        confidence = abs(anomaly_score[0])
        
        return is_anomaly, confidence

class RuleBasedDetector:
    """Simple rule-based anomaly detector"""
    
    @staticmethod
    def check_rules(sensor_data):
        rules_violated = []
        
        # Realistic temperature thresholds
        if sensor_data['temperature'] > 38.0:  # Critical high
            rules_violated.append(f"Critical high temperature: {sensor_data['temperature']}°C")
        elif sensor_data['temperature'] > 35.0:  # Warning high
            rules_violated.append(f"High temperature: {sensor_data['temperature']}°C")
        elif sensor_data['temperature'] < 0.0:  # Critical low
            rules_violated.append(f"Critical low temperature: {sensor_data['temperature']}°C")
        elif sensor_data['temperature'] < 5.0:  # Warning low
            rules_violated.append(f"Low temperature: {sensor_data['temperature']}°C")
            
        # Humidity thresholds
        if sensor_data['humidity'] > 90.0:
            rules_violated.append(f"High humidity: {sensor_data['humidity']}%")
        elif sensor_data['humidity'] < 20.0:
            rules_violated.append(f"Low humidity: {sensor_data['humidity']}%")
            
        # Vibration thresholds
        if sensor_data['vibration'] > 2.0:
            rules_violated.append(f"High vibration: {sensor_data['vibration']}")
            
        return rules_violated