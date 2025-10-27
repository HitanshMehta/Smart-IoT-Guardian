from datetime import datetime, timedelta

class AlertManager:
    def __init__(self):
        self.alert_history = {}
        self.escalation_rules = {
            'critical': {'count': 3, 'within_minutes': 5},
            'warning': {'count': 5, 'within_minutes': 10}
        }
    
    def check_escalation(self, sensor_id, alert_level):
        now = datetime.utcnow()
        if sensor_id not in self.alert_history:
            self.alert_history[sensor_id] = []
        
        # Clean old alerts
        self.alert_history[sensor_id] = [
            alert_time for alert_time in self.alert_history[sensor_id]
            if now - alert_time < timedelta(minutes=10)
        ]
        
        # Add current alert
        self.alert_history[sensor_id].append(now)
        
        # Check escalation
        recent_alerts = [
            alert_time for alert_time in self.alert_history[sensor_id]
            if now - alert_time < timedelta(minutes=self.escalation_rules[alert_level]['within_minutes'])
        ]
        
        if len(recent_alerts) >= self.escalation_rules[alert_level]['count']:
            return f"🚨 ESCALATED: {sensor_id} has {len(recent_alerts)} {alert_level} alerts in last {self.escalation_rules[alert_level]['within_minutes']} minutes!"
        
        return None