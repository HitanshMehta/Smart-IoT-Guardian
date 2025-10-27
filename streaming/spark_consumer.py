from pyspark.sql import SparkSession
from pyspark.sql.functions import *
from pyspark.sql.types import *
import time
import json
import logging
from data_generator.iot_simulator import IoTSensorSimulator
from models.anomaly_detector import StreamingAnomalyDetector, RuleBasedDetector

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class IoTMonitoringAgent:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("IoTMonitoringAgent") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.streaming.stopGracefullyOnShutdown", "true") \
            .master("local[*]") \
            .getOrCreate()
            
        self.spark.sparkContext.setLogLevel("WARN")
        
        # FIXED: Remove num_sensors parameter
        self.simulator = IoTSensorSimulator()  # No arguments needed
        
        # Initialize anomaly detectors
        self.anomaly_detectors = {}
        self.rule_detector = RuleBasedDetector()
        
        self.performance_stats = {
            'total_processed': 0,
            'anomalies_detected': 0,
            'start_time': time.time()
        }
    
    def create_schema(self):
        """Define schema for sensor data"""
        return StructType([
            StructField("sensor_id", StringType(), True),
            StructField("timestamp", StringType(), True),
            StructField("temperature", DoubleType(), True),
            StructField("humidity", DoubleType(), True),
            StructField("pressure", DoubleType(), True),
            StructField("vibration", DoubleType(), True),
            StructField("anomaly_type", StringType(), True)
        ])
    
    def initialize_anomaly_detector(self, sensor_id):
        """Initialize anomaly detector for a sensor"""
        if sensor_id not in self.anomaly_detectors:
            self.anomaly_detectors[sensor_id] = StreamingAnomalyDetector()
            logger.info(f"Initialized anomaly detector for {sensor_id}")
    
    def process_data_batch(self, data_batch):
        """Process a batch of sensor data"""
        if not data_batch:
            return
        
        # Convert to Spark DataFrame
        schema = self.create_schema()
        df = self.spark.createDataFrame(data_batch, schema=schema)
        
        # Process each row
        for row in df.collect():
            sensor_data = row.asDict()
            self.process_single_reading(sensor_data)
    
    def process_single_reading(self, sensor_data):
        """Process single sensor reading"""
        sensor_id = sensor_data['sensor_id']
        
        # Initialize detector for this sensor if needed
        self.initialize_anomaly_detector(sensor_id)
        
        # ML-based anomaly detection
        ml_anomaly, ml_confidence = self.anomaly_detectors[sensor_id].detect_anomaly(sensor_data)
        
        # Rule-based detection
        rule_violations = self.rule_detector.check_rules(sensor_data)
        rule_anomaly = len(rule_violations) > 0
        
        # Update model with new data
        self.anomaly_detectors[sensor_id].update_model(sensor_data)
        
        # Update statistics
        self.performance_stats['total_processed'] += 1
        if ml_anomaly or rule_anomaly:
            self.performance_stats['anomalies_detected'] += 1
        
        # Trigger alerts
        if ml_anomaly or rule_anomaly:
            self.trigger_alert(sensor_data, ml_anomaly, ml_confidence, rule_violations)
        
        # Log processing result
        logger.info(f"Processed {sensor_id}: "
                   f"Temp={sensor_data['temperature']}°C, "
                   f"Humidity={sensor_data['humidity']}%, "
                   f"ML_Anomaly={ml_anomaly}, Rule_Anomaly={rule_anomaly}")
    
    def trigger_alert(self, sensor_data, ml_anomaly, ml_confidence, rule_violations):
        """Trigger appropriate alerts based on anomaly detection"""
        alert_message = f"🚨 ALERT - Sensor {sensor_data['sensor_id']} detected anomaly!\n"
        alert_message += f"Timestamp: {sensor_data['timestamp']}\n"
        alert_message += f"Readings - Temp: {sensor_data['temperature']}°C, "
        alert_message += f"Humidity: {sensor_data['humidity']}%, "
        alert_message += f"Vibration: {sensor_data['vibration']}\n"
        
        if ml_anomaly:
            alert_message += f"ML Detection: ANOMALY (confidence: {ml_confidence:.3f})\n"
        
        if rule_violations:
            alert_message += f"Rule Violations: {', '.join(rule_violations)}\n"
        
        # Print alert with colorful output
        print("=" * 80)
        print("\033[91m" + alert_message + "\033[0m")  # Red color for alerts
        print("=" * 80)
    
    def print_statistics(self):
        """Print performance statistics"""
        elapsed_time = time.time() - self.performance_stats['start_time']
        stats = f"""
📊 Performance Statistics:
----------------------------
Total Records Processed: {self.performance_stats['total_processed']}
Anomalies Detected: {self.performance_stats['anomalies_detected']}
Processing Rate: {self.performance_stats['total_processed'] / elapsed_time:.2f} records/sec
Elapsed Time: {elapsed_time:.2f} seconds
Active Sensors: {len(self.anomaly_detectors)}
        """
        print("\033[94m" + stats + "\033[0m")  # Blue color for stats
    
    def start_monitoring(self, duration_minutes=10):
        """Start the monitoring agent"""
        logger.info("Starting IoT Monitoring Agent...")
        self.simulator.start_streaming(interval=1)  # 1 second interval
        
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        try:
            while time.time() < end_time:
                # Get data from simulator
                data_batch = self.simulator.get_data()
                
                if data_batch:
                    self.process_data_batch(data_batch)
                
                # Print statistics every 30 seconds
                if int(time.time() - start_time) % 30 == 0:
                    self.print_statistics()
                
                time.sleep(0.5)  # Small delay to prevent excessive CPU usage
                
        except KeyboardInterrupt:
            logger.info("Monitoring interrupted by user...")
        finally:
            self.simulator.stop_streaming()
            self.print_statistics()
            logger.info("IoT Monitoring Agent stopped.")
    
    def stop(self):
        """Stop the monitoring agent"""
        self.simulator.stop_streaming()
        self.spark.stop()

if __name__ == "__main__":
    agent = IoTMonitoringAgent()
    try:
        agent.start_monitoring(duration_minutes=10)  # Run for 10 minutes
    except Exception as e:
        logger.error(f"Error in monitoring agent: {e}")
    finally:
        agent.stop()