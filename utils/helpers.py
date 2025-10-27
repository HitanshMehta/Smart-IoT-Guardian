import json
import time
from datetime import datetime

def format_timestamp():
    return datetime.utcnow().isoformat()

def calculate_statistics(data_points):
    """Calculate basic statistics from data points"""
    if not data_points:
        return {}
    
    temperatures = [d['temperature'] for d in data_points]
    humidities = [d['humidity'] for d in data_points]
    
    return {
        'avg_temperature': sum(temperatures) / len(temperatures),
        'avg_humidity': sum(humidities) / len(humidities),
        'max_temperature': max(temperatures),
        'min_temperature': min(temperatures),
        'data_points_processed': len(data_points)
    }

class PerformanceMonitor:
    """Monitor system performance"""
    def __init__(self):
        self.start_time = time.time()
        self.processed_count = 0
        
    def increment_count(self):
        self.processed_count += 1
        
    def get_stats(self):
        elapsed = time.time() - self.start_time
        return {
            'total_processed': self.processed_count,
            'elapsed_time': elapsed,
            'processing_rate': self.processed_count / elapsed if elapsed > 0 else 0
        }