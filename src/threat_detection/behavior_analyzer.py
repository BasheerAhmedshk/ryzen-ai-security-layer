# src/threat_detection/behavior_analyzer.py
"""
Behavioral Anomaly Detection Module
Detects suspicious system actions and behavioral patterns
"""

import time
from typing import Dict, List
from collections import deque
from config.settings import DETECTION_CONFIG
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class BehaviorAnalyzer:
    """Analyzes system behavior for anomalies"""
    
    def __init__(self):
        """Initialize behavior analyzer"""
        self.threshold = DETECTION_CONFIG['behavior']['anomaly_threshold']
        self.window_size = DETECTION_CONFIG['behavior']['window_size']
        self.action_history = deque(maxlen=self.window_size)
        
        # Define normal vs suspicious actions
        self.suspicious_actions = {
            "file_access": ["system_files", "registry_access", "credential_store"],
            "network": ["unexpected_connection", "data_exfiltration", "c2_communication"],
            "process": ["hidden_process", "privilege_escalation", "process_injection"],
            "registry": ["dangerous_registry_edit", "startup_modification"],
        }
        
        logger.info("BehaviorAnalyzer initialized")
    
    def analyze(self, action: Dict) -> Dict:
        """
        Analyze a user action for suspicious behavior
        
        Args:
            action: Action to analyze with format:
                {
                    'type': 'file_access|network|process|registry',
                    'details': {...},
                    'timestamp': float
                }
        
        Returns:
            Dict with anomaly assessment
        """
        try:
            if not action or 'type' not in action:
                return {
                    "is_anomaly": False,
                    "confidence": 0.0,
                    "threat_level": "safe",
                    "reasons": []
                }
            
            # Add to history
            self.action_history.append(action)
            
            # Calculate action risk
            action_risk = self._calculate_action_risk(action)
            
            # Analyze behavioral patterns
            pattern_score = self._analyze_patterns()
            
            # Combined anomaly score
            anomaly_score = (action_risk * 0.6 + pattern_score * 0.4)
            
            is_anomaly = anomaly_score >= self.threshold
            
            result = {
                "is_anomaly": is_anomaly,
                "confidence": min(anomaly_score, 1.0),
                "threat_level": "high" if is_anomaly else "safe",
                "action_risk": action_risk,
                "pattern_score": pattern_score,
                "reasons": self._generate_reasons(action, action_risk, pattern_score)
            }
            
            if is_anomaly:
                logger.warning(f"Anomaly detected: {action['type']} - Score: {anomaly_score:.2f}")
            
            return result
        
        except Exception as e:
            logger.error(f"Error in behavior analysis: {e}")
            return {
                "is_anomaly": False,
                "confidence": 0.0,
                "threat_level": "unknown",
                "reasons": ["Error in analysis"]
            }
    
    def _calculate_action_risk(self, action: Dict) -> float:
        """Calculate risk score for a single action"""
        action_type = action.get('type', '')
        details = action.get('details', {})
        
        # Check if action type is suspicious
        suspicious_categories = self.suspicious_actions.get(action_type, [])
        
        # Check if this specific action matches any suspicious patterns
        for detail_key, detail_value in details.items():
            for suspicious_pattern in suspicious_categories:
                if suspicious_pattern.lower() in str(detail_value).lower():
                    return 0.8
        
        # Default moderate risk for uncommon actions
        return 0.3
    
    def _analyze_patterns(self) -> float:
        """Analyze patterns in action history"""
        if len(self.action_history) < 3:
            return 0.0
        
        pattern_score = 0.0
        
        # Pattern 1: High frequency of suspicious actions
        recent_actions = list(self.action_history)[-10:]
        suspicious_count = sum(1 for a in recent_actions 
                             if a.get('type') in ['process', 'registry'])
        if suspicious_count > 5:
            pattern_score += 0.4
        
        # Pattern 2: Repeated similar actions (potential exploitation)
        action_types = [a.get('type') for a in recent_actions]
        same_type_count = max([action_types.count(t) for t in set(action_types)])
        if same_type_count > 7:
            pattern_score += 0.3
        
        # Pattern 3: Rapid succession of actions (potential automated attack)
        if len(recent_actions) >= 2:
            time_diffs = []
            for i in range(1, len(recent_actions)):
                t1 = recent_actions[i-1].get('timestamp', 0)
                t2 = recent_actions[i].get('timestamp', 0)
                if t2 - t1 > 0:
                    time_diffs.append(t2 - t1)
            
            if time_diffs and all(td < 0.1 for td in time_diffs[-5:]):  # Actions < 100ms apart
                pattern_score += 0.3
        
        return min(pattern_score, 0.8)
    
    def _generate_reasons(self, action: Dict, action_risk: float, pattern_score: float) -> List[str]:
        """Generate human-readable reasons for anomaly detection"""
        reasons = []
        
        action_type = action.get('type', 'unknown')
        
        if action_risk > 0.6:
            reasons.append(f"Suspicious {action_type} action detected")
        
        if pattern_score > 0.5:
            reasons.append("Unusual pattern in system actions")
        
        if action.get('details', {}).get('elevated_privileges'):
            reasons.append("Action requires elevated privileges")
        
        if action.get('details', {}).get('hidden'):
            reasons.append("Hidden/stealth activity detected")
        
        if not reasons:
            reasons.append("Action appears normal")
        
        return reasons

class ActionCollector:
    """Collects and logs system actions"""
    
    def __init__(self, analyzer: BehaviorAnalyzer):
        """Initialize action collector"""
        self.analyzer = analyzer
        logger.info("ActionCollector initialized")
    
    def log_file_access(self, file_path: str, operation: str, elevated: bool = False) -> Dict:
        """Log file access action"""
        action = {
            "type": "file_access",
            "details": {
                "file_path": file_path,
                "operation": operation,
                "elevated_privileges": elevated
            },
            "timestamp": time.time()
        }
        return self.analyzer.analyze(action)
    
    def log_network_activity(self, destination: str, port: int, protocol: str) -> Dict:
        """Log network activity"""
        action = {
            "type": "network",
            "details": {
                "destination": destination,
                "port": port,
                "protocol": protocol
            },
            "timestamp": time.time()
        }
        return self.analyzer.analyze(action)
    
    def log_process_action(self, process_name: str, action: str, hidden: bool = False) -> Dict:
        """Log process action"""
        action_obj = {
            "type": "process",
            "details": {
                "process_name": process_name,
                "action": action,
                "hidden": hidden
            },
            "timestamp": time.time()
        }
        return self.analyzer.analyze(action_obj)
    
    def log_registry_modification(self, key_path: str, value: str) -> Dict:
        """Log registry modification"""
        action = {
            "type": "registry",
            "details": {
                "key_path": key_path,
                "value": value
            },
            "timestamp": time.time()
        }
        return self.analyzer.analyze(action)

# Demo usage
if __name__ == "__main__":
    analyzer = BehaviorAnalyzer()
    collector = ActionCollector(analyzer)
    
    # Simulate normal actions
    print("=== Normal Actions ===")
    result = collector.log_file_access("C:\\Users\\Documents\\file.txt", "read")
    print(f"File access: {result['is_anomaly']} (confidence: {result['confidence']:.2f})")
    
    result = collector.log_network_activity("google.com", 443, "https")
    print(f"Network: {result['is_anomaly']} (confidence: {result['confidence']:.2f})")
    
    # Simulate suspicious actions
    print("\n=== Suspicious Actions ===")
    result = collector.log_registry_modification("HKLM\\System\\dangerous_registry_edit", "malware")
    print(f"Registry: {result['is_anomaly']} (confidence: {result['confidence']:.2f})")
    print(f"Reasons: {result['reasons']}")
    
    result = collector.log_process_action("cmd.exe", "hidden_process", hidden=True)
    print(f"Process: {result['is_anomaly']} (confidence: {result['confidence']:.2f})")
    print(f"Reasons: {result['reasons']}")
