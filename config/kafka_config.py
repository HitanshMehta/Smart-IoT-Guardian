KAFKA_CONFIG = {
    'bootstrap_servers': 'localhost:9092',
    'topic': 'iot-sensor-data',
    'consumer_group': 'iot-monitoring-agent'
}

SENSOR_CONFIG = {
    'num_sensors': 5,
    'update_interval': 2,  # seconds
    'anomaly_probability': 0.1  # 10% chance of anomaly
}