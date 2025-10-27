import json
import time
import random
import numpy as np
from datetime import datetime
from threading import Thread
from queue import Queue
from config.locations import CITIES

class IoTSensorSimulator:
    def __init__(self):
        self.sensor_states = {}
        self.data_queue = Queue()
        self.running = False
        self.initialize_sensors()
    
    def initialize_sensors(self):
        """Initialize sensors with REALISTIC base values"""
        sensor_id = 0
        for city, config in CITIES.items():
            for i in range(config['sensor_count']):
                # REALISTIC base values that don't change dramatically
                base_temp = random.uniform(config['base_temp'][0], config['base_temp'][1])
                base_humidity = random.uniform(config['base_humidity'][0], config['base_humidity'][1])
                
                self.sensor_states[sensor_id] = {
                    'sensor_id': f"sensor_{sensor_id}",
                    'city': city,
                    'city_name': config['name'],
                    'country': config['country'],
                    'base_temp_range': config['base_temp'],
                    'temperature': base_temp,
                    'humidity': base_humidity,
                    'pressure': random.uniform(1010.0, 1020.0),
                    'vibration': random.uniform(0.0, 0.3),
                    'last_update': datetime.utcnow()
                }
                sensor_id += 1
    
    def generate_sensor_data(self, sensor_id):
        """Generate REALISTIC sensor data with minimal fluctuations"""
        state = self.sensor_states[sensor_id]
        city_config = CITIES[state['city']]
        anomaly_type = 'normal'
        
        # VERY SMALL, REALISTIC fluctuations
        temp_change = random.uniform(-0.1, 0.1)  # Max 0.1°C change
        humidity_change = random.uniform(-0.3, 0.3)  # Max 0.3% change
        pressure_change = random.uniform(-0.05, 0.05)
        vibration_change = random.uniform(-0.01, 0.01)
        
        # RARE anomalies (1% chance)
        if random.random() < 0.15:
            anomaly_type = random.choice(['temp_spike', 'temp_drop', 'vibration_spike'])
            if anomaly_type == 'temp_spike':
                temp_change += random.uniform(2.0, 5.0)  # Small, realistic spike
            elif anomaly_type == 'temp_drop':
                temp_change -= random.uniform(2.0, 4.0)  # Small, realistic drop
            elif anomaly_type == 'vibration_spike':
                vibration_change += random.uniform(0.5, 2.0)  # Realistic vibration
        
        # Update state with REALISTIC bounds
        base_min, base_max = state['base_temp_range']
        realistic_min = base_min - 5.0  # Allow small variations
        realistic_max = base_max + 5.0
        
        new_temperature = max(realistic_min, min(realistic_max, state['temperature'] + temp_change))
        new_humidity = max(30.0, min(95.0, state['humidity'] + humidity_change))
        new_pressure = max(1000.0, min(1030.0, state['pressure'] + pressure_change))
        new_vibration = max(0.0, min(3.0, state['vibration'] + vibration_change))
        
        # Update state
        self.sensor_states[sensor_id].update({
            'temperature': new_temperature,
            'humidity': new_humidity,
            'pressure': new_pressure,
            'vibration': new_vibration,
            'last_update': datetime.utcnow()
        })
        
        sensor_data = {
            'sensor_id': state['sensor_id'],
            'city': state['city'],
            'city_name': state['city_name'],
            'country': state['country'],
            'timestamp': datetime.utcnow().isoformat(),
            'temperature': round(new_temperature, 2),
            'humidity': round(new_humidity, 2),
            'pressure': round(new_pressure, 2),
            'vibration': round(new_vibration, 2),
            'anomaly_type': anomaly_type
        }
        
        return sensor_data
    
    def start_streaming(self, interval=2):
        """Start streaming data"""
        self.running = True
        
        def stream_data():
            while self.running:
                for sensor_id in self.sensor_states.keys():
                    data = self.generate_sensor_data(sensor_id)
                    self.data_queue.put(data)
                time.sleep(interval)
        
        thread = Thread(target=stream_data, daemon=True)
        thread.start()
        print(f"📡 Started IoT sensor streaming with {len(self.sensor_states)} sensors")
    
    def stop_streaming(self):
        self.running = False
    
    def get_data(self):
        data_batch = []
        while not self.data_queue.empty():
            try:
                data_batch.append(self.data_queue.get_nowait())
            except:
                break
        return data_batch