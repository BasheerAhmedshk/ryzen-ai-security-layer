# demos/threat_alert_demo.py
"""
Demo: Threat Alert Generation and Management
Demonstrates alert creation, user interaction, and notifications
"""

import sys
sys.path.insert(0, '..')

from src.security_core.threat_engine import ThreatEngine
from src.security_core.alert_manager import AlertManager, AlertFormatter

def print_alert_ui(formatted_alert):
    """Print alert in UI format"""
    print(f"""
    ╔════════════════════════════════════════════════════════════════╗
    ║  {formatted_alert['icon']} {formatted_alert['title']}
    ╚════════════════════════════════════════════════════════════════╝
    
    Message: {formatted_alert['message']}
    Severity: {formatted_alert['severity'].upper()}
    
    {formatted_alert['details']}
    
    ┌────────────────────────────────────────────────────────────────┐
    │ Actions:                                                        │
    """)
    
    for action in formatted_alert['action_buttons']:
        print(f"    [{action['label']}] ", end="")
    
    print("""
    └────────────────────────────────────────────────────────────────┘
    """)

def main():
    print("""
    ╔════════════════════════════════════════════════════════════════╗
    ║        AMD Ryzen AI - Threat Alert Management Demo            ║
    ║           Real-time Notifications & User Actions              ║
    ╚════════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize systems
    engine = ThreatEngine()
    manager = AlertManager()
    
    # Set up alert listener
    def on_alert(alert):
        print(f"\n🔔 Alert Notification: {alert.threat_type} ({alert.severity})")
    
    manager.register_listener(on_alert)
    
    print("\n[1] PHISHING THREAT DETECTION & ALERT")
    print("-" * 70)
    
    # Detect phishing threat
    result = engine.detect_phishing("https://paypa1.com/login", "Verify account")
    
    if result.get('is_phishing'):
        # Create alert
        alert_data = {
            "threat_type": "phishing",
            "confidence": result['confidence'],
            "user_message": "Suspicious phishing link detected. Do not click!",
            "details": result,
            "explanation": {
                "user_friendly": "This appears to be a phishing attempt. "
                                "The domain name resembles PayPal but is suspicious.",
                "recommendations": [
                    "Do not click the link",
                    "Do not enter your credentials",
                    "Report the sender"
                ]
            }
        }
        
        alert = manager.create_alert(alert_data)
        formatted = AlertFormatter.format_for_ui(alert)
        print_alert_ui(formatted)
    
    print("\n[2] MALWARE DETECTION & ALERT")
    print("-" * 70)
    
    # Detect malware
    malicious_code = "eval(atob('c29tZWhpZGRlbmNvZGU='));"
    result = engine.detect_malware(malicious_code)
    
    if result.get('is_malicious'):
        alert_data = {
            "threat_type": "malware",
            "confidence": result['confidence'],
            "user_message": "Malicious script detected!",
            "details": result,
            "explanation": {
                "user_friendly": "This code contains obfuscation and unsafe functions.",
                "recommendations": [
                    "Do not execute this code",
                    "Run a system scan",
                    "Update your antivirus"
                ]
            }
        }
        
        alert = manager.create_alert(alert_data)
        formatted = AlertFormatter.format_for_ui(alert)
        print_alert_ui(formatted)
    
    print("\n[3] BEHAVIORAL ANOMALY DETECTION")
    print("-" * 70)
    
    from src.threat_detection.behavior_analyzer import ActionCollector
    
    collector = ActionCollector(engine.behavior_analyzer)
    
    # Simulate suspicious behavior
    print("\nSimulating suspicious registry modification...")
    result = collector.log_registry_modification(
        "HKLM\\System\\dangerous_registry_edit",
        "malicious_value"
    )
    
    if result.get('is_anomaly'):
        alert_data = {
            "threat_type": "behavioral",
            "confidence": result['confidence'],
            "user_message": "Suspicious system activity detected",
            "details": result,
            "explanation": {
                "user_friendly": "Unusual system modification detected.",
                "recommendations": [
                    "Monitor your system",
                    "Check recent modifications",
                    "Consider restoring system"
                ]
            }
        }
        
        alert = manager.create_alert(alert_data)
        formatted = AlertFormatter.format_for_ui(alert)
        print_alert_ui(formatted)
    
    print("\n[4] ACTIVE ALERTS MANAGEMENT")
    print("-" * 70)
    
    active = manager.get_active_alerts()
    print(f"\nTotal Active Alerts: {len(active)}")
    
    for i, alert in enumerate(active, 1):
        print(f"\n{i}. Alert {alert.id}")
        print(f"   Type: {alert.threat_type.upper()}")
        print(f"   Severity: {alert.severity.upper()}")
        print(f"   Confidence: {alert.confidence:.2%}")
        print(f"   Timestamp: {alert.timestamp}")
    
    print("\n[5] USER ACTIONS & ALERT DISMISSAL")
    print("-" * 70)
    
    if active:
        alert_to_dismiss = active[0]
        print(f"\nDismissing alert: {alert_to_dismiss.id}")
        
        # Log user action
        manager.log_user_action(alert_to_dismiss.id, "clicked_details")
        manager.log_user_action(alert_to_dismiss.id, "reported_threat")
        
        # Dismiss alert
        manager.dismiss_alert(alert_to_dismiss.id, "User confirmed safe action")
        print("✅ Alert dismissed")
    
    print("\n[6] ALERT STATISTICS & REPORTING")
    print("-" * 70)
    
    stats = manager.get_alert_statistics()
    print(f"\nAlert Statistics:")
    print(f"  Total Alerts: {stats['total_alerts']}")
    print(f"  Active Alerts: {stats['active_alerts']}")
    print(f"  Dismissed Alerts: {stats['dismissed_alerts']}")
    
    print(f"\nBy Severity:")
    for severity, count in stats['by_severity'].items():
        print(f"  {severity.upper()}: {count}")
    
    print(f"\nBy Type:")
    for threat_type, count in stats['by_type'].items():
        print(f"  {threat_type.upper()}: {count}")
    
    print("\n[7] ALERT EXPORT")
    print("-" * 70)
    
    print("\nExporting alerts (JSON format):")
    json_export = manager.export_alerts(format="json")
    print(json_export[:300] + "..." if len(json_export) > 300 else json_export)
    
    print("\n\n" + "="*70)
    print("✅ Threat Alert Management Demo Completed!")
    print("="*70)

if __name__ == "__main__":
    main()
