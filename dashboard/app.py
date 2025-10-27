import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime
import time
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data_generator.iot_simulator import IoTSensorSimulator
from models.anomaly_detector import RuleBasedDetector
from models.ml_anomaly_detector import MLAnomalyDetector
from models.predictor import TemperaturePredictor
from config.locations import CITIES

class DashboardManager:
    def __init__(self):
        self.simulator = IoTSensorSimulator()
        self.ml_detector = MLAnomalyDetector()
        self.predictor = TemperaturePredictor()
        self.historical_data = []
        self.running = False
        
        # NEW: Data scanning and anomaly tracking
        self.total_data_scanned = 0
        self.total_anomalies_detected = 0
        self.session_start_time = datetime.now()
        
    def start_simulation(self):
        if not self.running:
            self.simulator.start_streaming(interval=2)
            self.running = True
            # Reset counters when starting new session
            self.session_start_time = datetime.now()
            
    def stop_simulation(self):
        if self.running:
            self.simulator.stop_streaming()
            self.running = False
    
    def get_latest_data(self, city_filter=None):
        data_batch = self.simulator.get_data()
        
        # NEW: Update data scanning counter
        self.total_data_scanned += len(data_batch)
        
        for data in data_batch:
            # Rule-based detection
            rule_violations = RuleBasedDetector.check_rules(data)
            if rule_violations:
                data['alert'] = True
                data['alert_reasons'] = rule_violations
                data['alert_type'] = 'rule_based'
                # NEW: Update anomaly counter
                self.total_anomalies_detected += 1
            else:
                data['alert'] = False
                data['alert_reasons'] = []
                data['alert_type'] = 'none'
            
            # ML-based detection
            ml_anomaly, ml_confidence = self.ml_detector.update_and_predict(data)
            if ml_anomaly:
                data['ml_alert'] = True
                data['ml_confidence'] = ml_confidence
                if not data['alert']:  # If rule-based didn't catch it
                    data['alert'] = True
                    data['alert_type'] = 'ml_based'
                    data['alert_reasons'].append(f"ML Anomaly (conf: {ml_confidence:.3f})")
                    # NEW: Update anomaly counter for ML-only detections
                    self.total_anomalies_detected += 1
            else:
                data['ml_alert'] = False
            
            # Update predictor
            self.predictor.update_history(data['sensor_id'], data['temperature'])
            
            self.historical_data.append(data)
            
            # Keep only last 200 records
            if len(self.historical_data) > 200:
                self.historical_data = self.historical_data[-200:]
        
        if city_filter and city_filter != "all":
            return [d for d in self.historical_data if d['city'] == city_filter]
        
        return self.historical_data

def main():
    st.set_page_config(
        page_title="IoT Monitoring Agent",
        page_icon="📊",
        layout="wide"
    )
    
    # Initialize session state
    if 'dashboard' not in st.session_state:
        st.session_state.dashboard = DashboardManager()
    
    dashboard = st.session_state.dashboard
    
    # Clean CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        border: 1px solid #ddd;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-critical {
        background: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        color: black !important;
    }
    .alert-ml {
        background: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 5px;
        color: black !important;
    }
    .alert-critical strong, .alert-ml strong {
        color: black !important;
    }
    .alert-critical span, .alert-ml span {
        color: black !important;
    }
    .city-header {
        background: #e3f2fd;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
        color: black !important;
    }
    .city-header h4 {
        color: black !important;
    }
    .city-header p {
        color: black !important;
    }
    .stats-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    .stats-number {
        font-size: 2rem;
        font-weight: bold;
        margin: 0;
    }
    .stats-label {
        font-size: 1rem;
        opacity: 0.9;
        margin: 0;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🌐 IoT Monitoring Agent")
    st.sidebar.markdown("---")
    
    # City filter
    cities = ["all"] + list(CITIES.keys())
    selected_city = st.sidebar.selectbox(
        "📍 Monitor City",
        cities,
        format_func=lambda x: "🌍 All Cities" if x == "all" else CITIES[x]['name']
    )
    
    # Controls
    st.sidebar.markdown("---")
    st.sidebar.subheader("Controls")
    
    col1, col2 = st.sidebar.columns(2)
    with col1:
        if st.button("▶️ Start Stream", use_container_width=True):
            dashboard.start_simulation()
    with col2:
        if st.button("⏹️ Stop", use_container_width=True):
            dashboard.stop_simulation()
    
    auto_refresh = st.sidebar.checkbox("🔄 Auto-refresh", value=True)
    refresh_rate = st.sidebar.slider("Refresh Rate (sec)", 2, 10, 3)
    
    # NEW: Data Statistics in Sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📈 Data Statistics")
    
    st.sidebar.metric("Total Data Scanned", f"{dashboard.total_data_scanned:,}")
    st.sidebar.metric("Total Anomalies", f"{dashboard.total_anomalies_detected:,}")
    
    # Calculate anomaly rate
    anomaly_rate = (dashboard.total_anomalies_detected / dashboard.total_data_scanned * 100) if dashboard.total_data_scanned > 0 else 0
    st.sidebar.metric("Anomaly Rate", f"{anomaly_rate:.1f}%")
    
    # Session duration
    session_duration = datetime.now() - dashboard.session_start_time
    hours, remainder = divmod(int(session_duration.total_seconds()), 3600)
    minutes, seconds = divmod(remainder, 60)
    st.sidebar.metric("Session Time", f"{hours:02d}:{minutes:02d}:{seconds:02d}")
    
  
    
    if not dashboard.running:
        st.info("🚀 Click 'Start Stream' to begin real-time monitoring with ML anomaly detection!")
    
    # Get data
    data = dashboard.get_latest_data(selected_city)
    
    if data:
        df = pd.DataFrame(data)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        latest_data = df.sort_values('timestamp').groupby('sensor_id').last().reset_index()
        
        # NEW: Data Scanning Statistics Section
        st.subheader("🔍 Data Scanning & Anomaly Analytics")
        
        stats_col1, stats_col2, stats_col3, stats_col4 = st.columns(4)
        
        with stats_col1:
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{dashboard.total_data_scanned:,}</p>
                <p class="stats-label">Total Data Points Scanned</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col2:
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{dashboard.total_anomalies_detected:,}</p>
                <p class="stats-label">Total Anomalies Detected</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col3:
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{anomaly_rate:.1f}%</p>
                <p class="stats-label">Overall Anomaly Rate</p>
            </div>
            """, unsafe_allow_html=True)
        
        with stats_col4:
            current_alerts = len(latest_data[latest_data['alert'] == True])
            st.markdown(f"""
            <div class="stats-card">
                <p class="stats-number">{current_alerts}</p>
                <p class="stats-label">Current Active Alerts</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time Metrics
        st.subheader("📊 Real-time System Metrics")
        
        cols = st.columns(4)
        total_sensors = len(latest_data)
        active_alerts = len(latest_data[latest_data['alert'] == True])
        avg_temp = latest_data['temperature'].mean()
        avg_humidity = latest_data['humidity'].mean()
        
        with cols[0]:
            st.metric("📡 Active Sensors", total_sensors)
        with cols[1]:
            st.metric("🚨 Active Alerts", active_alerts)
        with cols[2]:
            st.metric("🌡️ Avg Temperature", f"{avg_temp:.1f}°C")
        with cols[3]:
            st.metric("💧 Avg Humidity", f"{avg_humidity:.1f}%")
        
        # Advanced Analytics Section
        st.subheader("🤖 Advanced Analytics")
        
        # ML vs Rule-based Comparison
        col1, col2, col3 = st.columns(3)
        
        ml_anomalies = len([d for d in latest_data.to_dict('records') if d.get('ml_alert', False)])
        rule_anomalies = len([d for d in latest_data.to_dict('records') if d.get('alert_type') == 'rule_based'])
        ml_only_anomalies = len([d for d in latest_data.to_dict('records') if d.get('alert_type') == 'ml_based'])
        
        with col1:
            st.metric("🧠 ML Detected", ml_anomalies)
        with col2:
            st.metric("📋 Rules Detected", rule_anomalies)
       
        
        # Predictive Analytics
        st.subheader("🔮 Temperature Forecasting")
        
        if len(latest_data) > 0:
            pred_cols = st.columns(min(4, len(latest_data)))
            displayed_sensors = set()
            
            for idx, sensor in enumerate(latest_data.to_dict('records')):
                if sensor['sensor_id'] not in displayed_sensors and idx < 4:
                    with pred_cols[idx]:
                        prediction = dashboard.predictor.predict_temperature(sensor['sensor_id'])
                        current_temp = sensor['temperature']
                        
                        if prediction:
                            trend = "📈" if prediction > current_temp else "📉" if prediction < current_temp else "➡️"
                            delta = f"{prediction - current_temp:+.1f}°C"
                            st.metric(
                                f"{sensor['sensor_id']} {trend}",
                                f"{current_temp}°C",
                                delta=delta,
                                delta_color="normal" if abs(prediction - current_temp) < 2 else "inverse"
                            )
                        displayed_sensors.add(sensor['sensor_id'])
        
        # City Status
        st.subheader("🏙️ Global City Status")
        
        if selected_city == "all":
            for city, config in CITIES.items():
                city_sensors = latest_data[latest_data['city'] == city]
                alert_count = len(city_sensors[city_sensors['alert'] == True])
                ml_alerts = len([d for d in city_sensors.to_dict('records') if d.get('ml_alert', False)])
                
                st.markdown(f"""
                <div class="city-header">
                    <h4 style="color: black; margin: 0;">📍 {config['name']}</h4>
                    <p style="color: black; margin: 0;">
                        📡 Sensors: {len(city_sensors)} | 
                        🌡️ Temp: {city_sensors['temperature'].mean():.1f}°C | 
                        🚨 Alerts: {alert_count} |
                        🧠 ML: {ml_alerts}
                    </p>
                </div>
                """, unsafe_allow_html=True)
        else:
            city_sensors = latest_data[latest_data['city'] == selected_city]
            ml_alerts = len([d for d in city_sensors.to_dict('records') if d.get('ml_alert', False)])
            
            st.markdown(f"""
            <div class="city-header">
                <h3 style="color: black; margin: 0;">📍 {CITIES[selected_city]['name']}</h3>
                <p style="color: black; margin: 0;">
                    📡 Active Sensors: {len(city_sensors)} | 
                    🧠 ML Detections: {ml_alerts}
                </p>
            </div>
            """, unsafe_allow_html=True)
        
        # Real-time Charts
        st.subheader("📈 Real-time Sensor Data Stream")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Temperature Trend**")
            if len(df) > 1:
                temp_df = df.groupby('timestamp')['temperature'].mean().reset_index()
                st.line_chart(temp_df.set_index('timestamp')['temperature'])
        
        with col2:
            st.write("**Humidity Trend**")
            if len(df) > 1:
                humidity_df = df.groupby('timestamp')['humidity'].mean().reset_index()
                st.line_chart(humidity_df.set_index('timestamp')['humidity'])
        
        # Anomaly Detection Alerts
        st.subheader("🚨 Intelligent Anomaly Detection")
        
        alerts_df = latest_data[latest_data['alert'] == True]
        if not alerts_df.empty:
            for _, alert in alerts_df.iterrows():
                alert_class = "alert-ml" if alert['alert_type'] == 'ml_based' else "alert-critical"
                detection_source = "🧠 ML Detection" if alert['alert_type'] == 'ml_based' else "📋 Rule-based"
                
                st.markdown(f"""
                <div class="{alert_class}">
                    <strong style="color: black;">{detection_source} | {alert['city_name']} - {alert['sensor_id']}</strong><br>
                    <span style="color: black;">🌡️ Temperature: {alert['temperature']}°C | 💧 Humidity: {alert['humidity']}% | 📊 Vibration: {alert['vibration']:.2f}</span><br>
                    <span style="color: black;">🔍 Issues: {', '.join(alert['alert_reasons'])}</span>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.success("✅ No anomalies detected - All systems operating normally")
        
        # System Performance
        st.subheader("⚡ System Performance Metrics")
        
        perf_cols = st.columns(4)
        with perf_cols[0]:
            st.metric("Data Processed", len(dashboard.historical_data))
        with perf_cols[1]:
            processing_rate = len(data) / refresh_rate if refresh_rate > 0 else 0
            st.metric("Processing Rate", f"{processing_rate:.1f} rec/sec")
        with perf_cols[2]:
            ml_status = "Trained" if dashboard.ml_detector.is_trained else "Training"
            st.metric("ML Model", ml_status)
        with perf_cols[3]:
            if dashboard.ml_detector.is_trained and len(dashboard.ml_detector.data_buffer) > 0:
                buffer_size = len(dashboard.ml_detector.data_buffer)
                st.metric("Training Data", f"{buffer_size} samples")
        
        # Raw Data Stream
        st.subheader("📋 Live Data Stream")
        display_df = latest_data[['sensor_id', 'city_name', 'temperature', 'humidity', 'vibration', 'alert', 'alert_type']]
        
        # Color coding for alerts
        def color_alerts(val):
            if val == True:
                return 'background-color: #ffebee'
            elif val == 'ml_based':
                return 'background-color: #fff3e0'
            return ''
        
        styled_df = display_df.style.applymap(color_alerts, subset=['alert', 'alert_type'])
        st.dataframe(styled_df, use_container_width=True, height=300)
    
    # Auto-refresh
    if auto_refresh and dashboard.running:
        time.sleep(refresh_rate)
        st.rerun()

if __name__ == "__main__":
    main()

