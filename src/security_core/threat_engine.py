# src/security_core/threat_engine.py
"""
Main Threat Detection Engine
Orchestrates threat detection across all modules with sub-500ms latency
"""

import time
import threading
from typing import Dict, List, Optional
from queue import Queue
from config.settings import DETECTION_CONFIG
from config.logger import SecurityLogger
from src.threat_detection.phishing_detector import PhishingDetector
from src.threat_detection.malware_detector import MalwareDetector
from src.threat_detection.behavior_analyzer import BehaviorAnalyzer, ActionCollector
from src.explainability.threat_explainer import ThreatExplainer

logger = SecurityLogger.get_logger(__name__)

class ThreatEngine:
    """Main engine that coordinates all threat detection systems"""
    
    def __init__(self, enable_async=True):
        """
        Initialize threat engine
        
        Args:
            enable_async: Enable asynchronous threat detection
        """
        self.enable_async = enable_async
        
        # Initialize detection modules
        self.phishing_detector = PhishingDetector()
        self.malware_detector = MalwareDetector()
        self.behavior_analyzer = BehaviorAnalyzer()
        self.action_collector = ActionCollector(self.behavior_analyzer)
        self.threat_explainer = ThreatExplainer()
        
        # Async processing
        self.threat_queue = Queue()
        self.detection_thread = None
        self.is_running = False
        
        # Statistics
        self.stats = {
            "total_threats": 0,
            "phishing_detected": 0,
            "malware_detected": 0,
            "behavioral_anomalies": 0,
            "avg_latency_ms": 0.0,
            "latencies": []
        }
        
        # Threat cache to prevent duplicate alerts
        self.threat_cache = {}
        
        logger.info("ThreatEngine initialized")
    
    def start(self):
        """Start the threat detection engine"""
        if self.enable_async and not self.is_running:
            self.is_running = True
            self.detection_thread = threading.Thread(target=self._process_threats, daemon=True)
            self.detection_thread.start()
            logger.info("ThreatEngine started")
    
    def stop(self):
        """Stop the threat detection engine"""
        if self.is_running:
            self.is_running = False
            if self.detection_thread:
                self.detection_thread.join(timeout=2)
            logger.info("ThreatEngine stopped")
    
    def detect_phishing(self, url: str, context: str = "") -> Dict:
        """Detect phishing threats"""
        start_time = time.time()
        
        try:
            result = self.phishing_detector.detect(url, context)
            
            if result['is_phishing']:
                self.stats['phishing_detected'] += 1
                result['threat_type'] = 'phishing'
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            result['latency_ms'] = latency_ms
            self.stats['latencies'].append(latency_ms)
            
            return result
        
        except Exception as e:
            logger.error(f"Error in phishing detection: {e}")
            return {"is_phishing": False, "error": str(e)}
    
    def detect_malware(self, code: str, source_type: str = "script") -> Dict:
        """Detect malware threats"""
        start_time = time.time()
        
        try:
            result = self.malware_detector.detect(code, source_type)
            
            if result['is_malicious']:
                self.stats['malware_detected'] += 1
                result['threat_type'] = 'malware'
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            result['latency_ms'] = latency_ms
            self.stats['latencies'].append(latency_ms)
            
            return result
        
        except Exception as e:
            logger.error(f"Error in malware detection: {e}")
            return {"is_malicious": False, "error": str(e)}
    
    def analyze_behavior(self, action: Dict) -> Dict:
        """Analyze behavioral anomalies"""
        start_time = time.time()
        
        try:
            result = self.behavior_analyzer.analyze(action)
            
            if result['is_anomaly']:
                self.stats['behavioral_anomalies'] += 1
                result['threat_type'] = 'behavioral'
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            result['latency_ms'] = latency_ms
            self.stats['latencies'].append(latency_ms)
            
            return result
        
        except Exception as e:
            logger.error(f"Error in behavior analysis: {e}")
            return {"is_anomaly": False, "error": str(e)}
    
    def unified_threat_detection(self, threat_input: Dict) -> Dict:
        """
        Unified threat detection across all modules
        
        Args:
            threat_input: Dict with:
                - type: 'url', 'code', 'action'
                - content: Content to analyze
                - context: Optional context
        
        Returns:
            Comprehensive threat assessment
        """
        start_time = time.time()
        threat_type = threat_input.get('type', 'unknown')
        content = threat_input.get('content', '')
        context = threat_input.get('context', '')
        
        try:
            results = {
                "threat_type": threat_type,
                "detected_threats": [],
                "max_confidence": 0.0,
                "requires_action": False,
                "timestamp": time.time()
            }
            
            # Route to appropriate detector
            if threat_type == 'url':
                result = self.detect_phishing(content, context)
                if result.get('is_phishing'):
                    results['detected_threats'].append({
                        'type': 'phishing',
                        'confidence': result['confidence'],
                        'reasons': result.get('reasons', [])
                    })
                    results['max_confidence'] = max(results['max_confidence'], result['confidence'])
                    results['requires_action'] = True
            
            elif threat_type == 'code':
                result = self.detect_malware(content)
                if result.get('is_malicious'):
                    results['detected_threats'].append({
                        'type': 'malware',
                        'confidence': result['confidence'],
                        'reasons': result.get('reasons', [])
                    })
                    results['max_confidence'] = max(results['max_confidence'], result['confidence'])
                    results['requires_action'] = True
            
            elif threat_type == 'action':
                result = self.analyze_behavior(content)
                if result.get('is_anomaly'):
                    results['detected_threats'].append({
                        'type': 'behavioral',
                        'confidence': result['confidence'],
                        'reasons': result.get('reasons', [])
                    })
                    results['max_confidence'] = max(results['max_confidence'], result['confidence'])
                    results['requires_action'] = True
            
            # Update statistics
            if results['requires_action']:
                self.stats['total_threats'] += 1
            
            # Record latency
            latency_ms = (time.time() - start_time) * 1000
            results['latency_ms'] = latency_ms
            self.stats['latencies'].append(latency_ms)
            
            # Generate explanation if threat detected
            if results['requires_action'] and results['detected_threats']:
                threat_data = {
                    'threat_type': results['detected_threats'][0]['type'],
                    'confidence': results['max_confidence'],
                    'reasons': results['detected_threats'][0]['reasons']
                }
                explanation = self.threat_explainer.explain_threat(threat_data)
                results['explanation'] = explanation
            
            logger.info(f"Unified detection - Type: {threat_type} - "
                       f"Threats: {len(results['detected_threats'])} - "
                       f"Latency: {latency_ms:.2f}ms")
            
            return results
        
        except Exception as e:
            logger.error(f"Error in unified detection: {e}")
            return {
                "threat_type": threat_type,
                "error": str(e),
                "requires_action": False
            }
    
    def get_statistics(self) -> Dict:
        """Get detection statistics"""
        stats = self.stats.copy()
        
        # Calculate average latency
        if stats['latencies']:
            stats['avg_latency_ms'] = sum(stats['latencies']) / len(stats['latencies'])
            stats['max_latency_ms'] = max(stats['latencies'])
            stats['min_latency_ms'] = min(stats['latencies'])
            stats['total_latencies_recorded'] = len(stats['latencies'])
        
        return stats
    
    def _process_threats(self):
        """Background thread for processing threat queue"""
        while self.is_running:
            try:
                threat_input = self.threat_queue.get(timeout=1)
                self.unified_threat_detection(threat_input)
            except:
                pass
    
    def queue_threat(self, threat_input: Dict):
        """Queue threat for async processing"""
        if self.enable_async:
            self.threat_queue.put(threat_input)
        else:
            self.unified_threat_detection(threat_input)
    
    def reset_statistics(self):
        """Reset detection statistics"""
        self.stats = {
            "total_threats": 0,
            "phishing_detected": 0,
            "malware_detected": 0,
            "behavioral_anomalies": 0,
            "avg_latency_ms": 0.0,
            "latencies": []
        }
        logger.info("Statistics reset")

# Demo usage
if __name__ == "__main__":
    engine = ThreatEngine()
    engine.start()
    
    # Test phishing detection
    print("=== Testing Phishing Detection ===")
    result = engine.detect_phishing("https://paypa1.com/login", "Please verify your account")
    print(f"Phishing detected: {result.get('is_phishing')} (Confidence: {result.get('confidence'):.2f})")
    print(f"Latency: {result.get('latency_ms'):.2f}ms\n")
    
    # Test malware detection
    print("=== Testing Malware Detection ===")
    code = "eval(atob('c29tZXRoaW5n'));"
    result = engine.detect_malware(code)
    print(f"Malware detected: {result.get('is_malicious')} (Confidence: {result.get('confidence'):.2f})")
    print(f"Latency: {result.get('latency_ms'):.2f}ms\n")
    
    # Test unified detection
    print("=== Testing Unified Detection ===")
    threat = {
        "type": "url",
        "content": "https://bank-verify.com/update",
        "context": "verify your account immediately"
    }
    result = engine.unified_threat_detection(threat)
    print(f"Threats detected: {len(result['detected_threats'])}")
    if result.get('explanation'):
        print(f"Explanation: {result['explanation']['user_friendly']}\n")
    
    # Show statistics
    print("=== Statistics ===")
    stats = engine.get_statistics()
    print(f"Total threats: {stats['total_threats']}")
    print(f"Phishing: {stats['phishing_detected']}")
    print(f"Malware: {stats['malware_detected']}")
    print(f"Avg latency: {stats.get('avg_latency_ms', 0):.2f}ms")
    
    engine.stop()
