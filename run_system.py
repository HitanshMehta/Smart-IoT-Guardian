#!/usr/bin/env python3
"""
ADS Mini Project - Fixed System Runner
Handles missing components and uses correct import names
"""

import threading
import time
import logging
import sys
import os
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('system.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("SystemRunner")

class IoTMonitoringSystem:
    def __init__(self):
        self.threads = []
        self.running = False
        self.components = {}
    
    def safe_import(self, module_name, class_name=None):
        """Safely import a module or class"""
        try:
            if class_name:
                module = __import__(module_name, fromlist=[class_name])
                return getattr(module, class_name)
            else:
                return __import__(module_name)
        except ImportError as e:
            logger.warning(f"Could not import {module_name}.{class_name if class_name else ''}: {e}")
            return None
        except Exception as e:
            logger.warning(f"Error importing {module_name}.{class_name if class_name else ''}: {e}")
            return None
    
    def initialize_components(self):
        """Initialize all available system components"""
        logger.info("Initializing system components...")
        
        # Try to import and initialize each component
        components_to_try = [
            ('data_generator.iot_simulator', 'IoTSimulator', 'data_generator'),
            ('streaming.kafka_producer', 'KafkaDataProducer', 'kafka_producer'),
            ('streaming.spark_consumer', 'SparkStreamProcessor', 'spark_consumer'),
            ('models.anomaly_detector', 'AnomalyDetector', 'anomaly_detector'),
            ('models.alert_manager', 'AlertManager', 'alert_manager'),
            ('dashboard.app', None, 'dashboard'),  # No specific class for dashboard
        ]
        
        for module_path, class_name, component_name in components_to_try:
            try:
                if class_name:
                    component_class = self.safe_import(module_path, class_name)
                    if component_class:
                        # Create a simple config dictionary
                        config = {'kafka_broker': 'localhost:9092', 'spark_master': 'local[*]'}
                        self.components[component_name] = component_class(config)
                        logger.info(f"✅ Initialized {component_name}")
                    else:
                        logger.warning(f"❌ Could not initialize {component_name}")
                else:
                    # For modules like dashboard
                    component_module = self.safe_import(module_path)
                    if component_module:
                        self.components[component_name] = component_module
                        logger.info(f"✅ Initialized {component_name}")
                    else:
                        logger.warning(f"❌ Could not initialize {component_name}")
                        
            except Exception as e:
                logger.warning(f"❌ Failed to initialize {component_name}: {e}")
        
        logger.info(f"Successfully initialized {len(self.components)} out of {len(components_to_try)} components")
        return len(self.components) > 0  # Return True if at least one component initialized
    
    def start_data_generation(self):
        """Start IoT data generation if available"""
        if 'data_generator' not in self.components:
            logger.warning("Data generator not available - skipping")
            return
        
        def generate_data():
            logger.info("Starting IoT data generation...")
            while self.running:
                try:
                    # Try different possible method names
                    generator = self.components['data_generator']
                    if hasattr(generator, 'generate_sample'):
                        generator.generate_sample()
                    elif hasattr(generator, 'generate_data'):
                        generator.generate_data()
                    elif hasattr(generator, 'run'):
                        generator.run()
                    else:
                        logger.warning("Data generator has no recognizable method")
                        break
                    time.sleep(2)  # Generate data every 2 seconds
                except Exception as e:
                    logger.error(f"Data generation error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=generate_data, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_kafka_producer(self):
        """Start Kafka producer if available"""
        if 'kafka_producer' not in self.components:
            logger.warning("Kafka producer not available - skipping")
            return
        
        def produce_messages():
            logger.info("Starting Kafka producer...")
            while self.running:
                try:
                    producer = self.components['kafka_producer']
                    if hasattr(producer, 'produce_message'):
                        producer.produce_message()
                    elif hasattr(producer, 'send_message'):
                        producer.send_message()
                    elif hasattr(producer, 'run'):
                        producer.run()
                    time.sleep(1)
                except Exception as e:
                    logger.error(f"Kafka producer error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=produce_messages, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_spark_consumer(self):
        """Start Spark consumer if available"""
        if 'spark_consumer' not in self.components:
            logger.warning("Spark consumer not available - skipping")
            return
        
        def start_spark():
            logger.info("Starting Spark streaming consumer...")
            try:
                consumer = self.components['spark_consumer']
                if hasattr(consumer, 'start_streaming'):
                    consumer.start_streaming()
                elif hasattr(consumer, 'run'):
                    consumer.run()
                elif hasattr(consumer, 'start'):
                    consumer.start()
            except Exception as e:
                logger.error(f"Spark consumer error: {e}")
        
        thread = threading.Thread(target=start_spark, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_anomaly_detection(self):
        """Start anomaly detection if available"""
        if 'anomaly_detector' not in self.components:
            logger.warning("Anomaly detector not available - skipping")
            return
        
        def detect_anomalies():
            logger.info("Starting anomaly detection...")
            while self.running:
                try:
                    detector = self.components['anomaly_detector']
                    if hasattr(detector, 'process_stream'):
                        detector.process_stream()
                    elif hasattr(detector, 'detect_anomalies'):
                        detector.detect_anomalies()
                    elif hasattr(detector, 'run'):
                        detector.run()
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"Anomaly detection error: {e}")
                    time.sleep(5)
        
        thread = threading.Thread(target=detect_anomalies, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_alert_manager(self):
        """Start alert manager if available"""
        if 'alert_manager' not in self.components:
            logger.warning("Alert manager not available - skipping")
            return
        
        def manage_alerts():
            logger.info("Starting alert manager...")
            while self.running:
                try:
                    alert_mgr = self.components['alert_manager']
                    if hasattr(alert_mgr, 'check_alerts'):
                        alert_mgr.check_alerts()
                    elif hasattr(alert_mgr, 'process_alerts'):
                        alert_mgr.process_alerts()
                    elif hasattr(alert_mgr, 'run'):
                        alert_mgr.run()
                    time.sleep(5)
                except Exception as e:
                    logger.error(f"Alert manager error: {e}")
                    time.sleep(10)
        
        thread = threading.Thread(target=manage_alerts, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_dashboard(self):
        """Start dashboard if available"""
        if 'dashboard' not in self.components:
            logger.warning("Dashboard not available - skipping")
            return
        
        def run_dashboard():
            logger.info("Starting dashboard...")
            try:
                dashboard = self.components['dashboard']
                if hasattr(dashboard, 'run_server'):
                    dashboard.run_server(host='0.0.0.0', port=8050, debug=False)
                else:
                    logger.warning("Dashboard has no run_server method")
            except Exception as e:
                logger.error(f"Dashboard error: {e}")
        
        thread = threading.Thread(target=run_dashboard, daemon=True)
        thread.start()
        self.threads.append(thread)
    
    def start_system(self):
        """Start all available components"""
        logger.info("🚀 Starting ADS IoT Monitoring System...")
        self.running = True
        
        # Initialize available components
        if not self.initialize_components():
            logger.warning("No components could be initialized - running in minimal mode")
        
        # Start available components with delays
        components_start_order = [
            ('data_generator', self.start_data_generation, 2),
            ('kafka_producer', self.start_kafka_producer, 1),
            ('spark_consumer', self.start_spark_consumer, 1),
            ('anomaly_detector', self.start_anomaly_detection, 1),
            ('alert_manager', self.start_alert_manager, 1),
            ('dashboard', self.start_dashboard, 1),
        ]
        
        for component_name, start_method, delay in components_start_order:
            if component_name in self.components:
                start_method()
                time.sleep(delay)
            else:
                logger.warning(f"Skipping {component_name} - not available")
        
        logger.info("✅ Available system components started!")
        logger.info("📊 System is running... Press Ctrl+C to stop")
        return True
    
    def stop_system(self):
        """Stop the system gracefully"""
        logger.info("🛑 Stopping system...")
        self.running = False
        
        # Wait for threads to finish
        for thread in self.threads:
            thread.join(timeout=3)
        
        logger.info("✅ System stopped successfully")

def main():
    """Main entry point"""
    system = IoTMonitoringSystem()
    
    try:
        system.start_system()
        
        # Keep main thread alive
        while system.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        logger.info("Received Ctrl+C...")
    except Exception as e:
        logger.error(f"System error: {e}")
    finally:
        system.stop_system()

if __name__ == "__main__":
    main()