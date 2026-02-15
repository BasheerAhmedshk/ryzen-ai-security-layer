# src/security_core/alert_manager.py
"""
Alert Manager
Manages threat alerts, notifications, and user interactions
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Optional
from config.settings import ALERT_CONFIG, DATABASE_CONFIG
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class Alert:
    """Represents a single threat alert"""
    
    def __init__(self, threat_data: Dict):
        """Initialize alert from threat data"""
        self.id = self._generate_id()
        self.timestamp = datetime.now()
        self.threat_type = threat_data.get('threat_type', 'unknown')
        self.confidence = threat_data.get('confidence', 0.0)
        self.severity = self._calculate_severity(threat_data.get('confidence', 0.0))
        self.user_message = threat_data.get('user_message', 'Security threat detected')
        self.details = threat_data.get('details', {})
        self.explanation = threat_data.get('explanation', {})
        self.is_dismissed = False
        self.actions_taken = []
    
    def _generate_id(self) -> str:
        """Generate unique alert ID"""
        return f"alert_{int(time.time()*1000)}"
    
    def _calculate_severity(self, confidence: float) -> str:
        """Calculate alert severity"""
        if confidence >= 0.85:
            return "critical"
        elif confidence >= 0.65:
            return "high"
        elif confidence >= 0.45:
            return "medium"
        else:
            return "low"
    
    def dismiss(self):
        """Dismiss the alert"""
        self.is_dismissed = True
    
    def log_action(self, action: str):
        """Log user action on alert"""
        self.actions_taken.append({
            "action": action,
            "timestamp": datetime.now().isoformat()
        })
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat(),
            "threat_type": self.threat_type,
            "confidence": self.confidence,
            "severity": self.severity,
            "message": self.user_message,
            "details": self.details,
            "explanation": self.explanation,
            "dismissed": self.is_dismissed,
            "actions": self.actions_taken
        }

class AlertManager:
    """Manages threat alerts and notifications"""
    
    def __init__(self):
        """Initialize alert manager"""
        self.alerts: List[Alert] = []
        self.alert_callbacks = []  # Callbacks for alert listeners
        self.alert_timeout = ALERT_CONFIG.get('alert_timeout_seconds', 10)
        self.auto_dismiss = ALERT_CONFIG.get('auto_dismiss', True)
        self.log_file = DATABASE_CONFIG.get('threat_db_path')
        
        logger.info("AlertManager initialized")
    
    def create_alert(self, threat_data: Dict) -> Alert:
        """
        Create and register a new threat alert
        
        Args:
            threat_data: Threat detection result
        
        Returns:
            Created Alert object
        """
        try:
            alert = Alert(threat_data)
            self.alerts.append(alert)
            
            # Log alert
            self._log_alert(alert)
            
            # Notify listeners
            self._notify_listeners(alert)
            
            logger.info(f"Alert created: {alert.id} - {alert.threat_type} "
                       f"({alert.severity}) - Confidence: {alert.confidence:.2f}")
            
            return alert
        
        except Exception as e:
            logger.error(f"Error creating alert: {e}")
            return None
    
    def get_active_alerts(self) -> List[Alert]:
        """Get list of active (non-dismissed) alerts"""
        return [a for a in self.alerts if not a.is_dismissed]
    
    def get_alert_by_id(self, alert_id: str) -> Optional[Alert]:
        """Get alert by ID"""
        for alert in self.alerts:
            if alert.id == alert_id:
                return alert
        return None
    
    def dismiss_alert(self, alert_id: str, reason: str = "") -> bool:
        """Dismiss an alert"""
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.dismiss()
            if reason:
                alert.log_action(f"dismissed_reason: {reason}")
            logger.info(f"Alert dismissed: {alert_id}")
            return True
        return False
    
    def log_user_action(self, alert_id: str, action: str) -> bool:
        """Log user action on alert"""
        alert = self.get_alert_by_id(alert_id)
        if alert:
            alert.log_action(action)
            logger.info(f"Action logged for alert {alert_id}: {action}")
            return True
        return False
    
    def register_listener(self, callback):
        """Register callback for alert notifications"""
        self.alert_callbacks.append(callback)
    
    def _notify_listeners(self, alert: Alert):
        """Notify all registered listeners of new alert"""
        for callback in self.alert_callbacks:
            try:
                callback(alert)
            except Exception as e:
                logger.error(f"Error in alert callback: {e}")
    
    def _log_alert(self, alert: Alert):
        """Log alert to file"""
        try:
            alert_dict = alert.to_dict()
            # In production, this would write to a database
            logger.info(f"Alert logged: {json.dumps(alert_dict)}")
        except Exception as e:
            logger.error(f"Error logging alert: {e}")
    
    def get_alert_statistics(self) -> Dict:
        """Get alert statistics"""
        active_alerts = self.get_active_alerts()
        
        stats = {
            "total_alerts": len(self.alerts),
            "active_alerts": len(active_alerts),
            "dismissed_alerts": len(self.alerts) - len(active_alerts),
            "by_severity": {},
            "by_type": {}
        }
        
        for alert in self.alerts:
            # Count by severity
            severity = alert.severity
            stats['by_severity'][severity] = stats['by_severity'].get(severity, 0) + 1
            
            # Count by type
            threat_type = alert.threat_type
            stats['by_type'][threat_type] = stats['by_type'].get(threat_type, 0) + 1
        
        return stats
    
    def export_alerts(self, format: str = "json") -> str:
        """Export alerts in specified format"""
        alerts_data = [alert.to_dict() for alert in self.alerts]
        
        if format == "json":
            return json.dumps(alerts_data, indent=2, default=str)
        elif format == "csv":
            # Simple CSV export
            lines = ["ID,Type,Severity,Confidence,Timestamp,Dismissed"]
            for alert in self.alerts:
                lines.append(f"{alert.id},{alert.threat_type},{alert.severity},"
                           f"{alert.confidence:.2f},{alert.timestamp},"
                           f"{alert.is_dismissed}")
            return "\n".join(lines)
        else:
            return json.dumps(alerts_data, indent=2, default=str)
    
    def clear_alerts(self, days_old: int = 30):
        """Clear old alerts"""
        cutoff_time = datetime.now().timestamp() - (days_old * 24 * 3600)
        
        alerts_to_remove = []
        for alert in self.alerts:
            if alert.timestamp.timestamp() < cutoff_time:
                alerts_to_remove.append(alert)
        
        for alert in alerts_to_remove:
            self.alerts.remove(alert)
        
        logger.info(f"Cleared {len(alerts_to_remove)} old alerts")
        return len(alerts_to_remove)

class AlertFormatter:
    """Formats alerts for different output formats"""
    
    @staticmethod
    def format_for_ui(alert: Alert) -> Dict:
        """Format alert for UI display"""
        return {
            "id": alert.id,
            "icon": AlertFormatter._get_icon(alert.threat_type),
            "title": f"{alert.threat_type.title()} Threat Detected",
            "message": alert.user_message,
            "severity": alert.severity,
            "color": AlertFormatter._get_color(alert.severity),
            "action_buttons": AlertFormatter._get_actions(alert.threat_type),
            "details": alert.explanation.get('user_friendly', '')
        }
    
    @staticmethod
    def _get_icon(threat_type: str) -> str:
        """Get appropriate icon for threat type"""
        icons = {
            "phishing": "🎣",
            "malware": "🦠",
            "behavioral": "⚠️",
            "unknown": "❓"
        }
        return icons.get(threat_type, "⚠️")
    
    @staticmethod
    def _get_color(severity: str) -> str:
        """Get color for severity level"""
        colors = {
            "critical": "#FF0000",  # Red
            "high": "#FFA500",      # Orange
            "medium": "#FFFF00",    # Yellow
            "low": "#0000FF"        # Blue
        }
        return colors.get(severity, "#808080")
    
    @staticmethod
    def _get_actions(threat_type: str) -> List[Dict]:
        """Get action buttons for threat type"""
        actions = {
            "phishing": [
                {"label": "Block", "action": "block", "color": "danger"},
                {"label": "Report", "action": "report", "color": "warning"},
                {"label": "Details", "action": "details", "color": "info"}
            ],
            "malware": [
                {"label": "Quarantine", "action": "quarantine", "color": "danger"},
                {"label": "Scan", "action": "scan", "color": "warning"},
                {"label": "Details", "action": "details", "color": "info"}
            ],
            "behavioral": [
                {"label": "Stop", "action": "stop", "color": "danger"},
                {"label": "Monitor", "action": "monitor", "color": "warning"},
                {"label": "Details", "action": "details", "color": "info"}
            ]
        }
        return actions.get(threat_type, [
            {"label": "Dismiss", "action": "dismiss", "color": "secondary"}
        ])

# Demo usage
if __name__ == "__main__":
    manager = AlertManager()
    
    # Create some alerts
    threat_data_1 = {
        "threat_type": "phishing",
        "confidence": 0.92,
        "user_message": "Suspicious phishing link detected",
        "details": {"url": "https://paypa1.com/login"}
    }
    
    threat_data_2 = {
        "threat_type": "malware",
        "confidence": 0.78,
        "user_message": "Malicious code detected",
        "details": {"code": "eval(...)"}
    }
    
    alert1 = manager.create_alert(threat_data_1)
    alert2 = manager.create_alert(threat_data_2)
    
    print("=== Active Alerts ===")
    for alert in manager.get_active_alerts():
        formatted = AlertFormatter.format_for_ui(alert)
        print(f"\n{formatted['icon']} {formatted['title']}")
        print(f"  Severity: {formatted['severity']}")
        print(f"  Message: {formatted['message']}")
    
    # Dismiss one
    manager.dismiss_alert(alert1.id, "User confirmed action")
    
    print("\n=== Alert Statistics ===")
    stats = manager.get_alert_statistics()
    for key, value in stats.items():
        print(f"{key}: {value}")
