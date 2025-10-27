from kafka import KafkaProducer
import json
import time
import logging
from data_generator.iot_simulator import IoTSensorSimulator
from config.kafka_config import KAFKA_CONFIG, SENSOR_CONFIG

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTDataProducer:
    def __init__(self):
        self.producer = KafkaProducer(
            bootstrap_servers=KAFKA_CONFIG['bootstrap_servers'],
            value_serializer=lambda x: json.dumps(x).encode('utf-8'),
            acks='all',
            retries=3
        )
        self.topic = KAFKA_CONFIG['topic']
        self.simulator = IoTSensorSimulator(SENSOR_CONFIG['num_sensors'])
        
    def produce_data(self, duration_minutes=60):
        """Produce sensor data for specified duration"""
        logger.info(f"Starting IoT data production for {duration_minutes} minutes")
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                sensor_data_batch = self.simulator.generate_all_sensors_data()
                
                for data in sensor_data_batch:
                    self.producer.send(self.topic, value=data)
                    logger.info(f"Produced data: {data['sensor_id']} - Temp: {data['temperature']}°C")
                
                # Wait before next batch
                time.sleep(SENSOR_CONFIG['update_interval'])
                
        except KeyboardInterrupt:
            logger.info("Stopping data production...")
        finally:
            self.producer.flush()
            self.producer.close()
            logger.info("Producer closed")

if __name__ == "__main__":
    producer = IoTDataProducer()
    producer.produce_data(duration_minutes=120)  # Run for 2 hours