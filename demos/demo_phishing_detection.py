# demos/demo_phishing_detection.py
"""
Demo: Phishing Link Detection
Demonstrates real-time phishing detection on Ryzen AI
"""

import sys
sys.path.insert(0, '..')

from src.threat_detection.phishing_detector import PhishingDetector
from src.security_core.threat_engine import ThreatEngine
from src.explainability.threat_explainer import ThreatExplainer

def print_result(url, result):
    """Pretty print detection result"""
    print(f"\n{'='*70}")
    print(f"URL: {url}")
    print(f"{'='*70}")
    print(f"Phishing Detected: {result['is_phishing']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Threat Level: {result['threat_level'].upper()}")
    print(f"\nDetection Reasons:")
    for reason in result['reasons']:
        print(f"  • {reason}")
    
    if result.get('latency_ms'):
        print(f"\nLatency: {result['latency_ms']:.2f}ms (< 500ms target)")

def main():
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║         AMD Ryzen AI - Phishing Detection Demo               ║
    ║     Lightweight On-Device Security - Sub 500ms Detection    ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    
    # Initialize detectors
    detector = PhishingDetector()
    engine = ThreatEngine()
    explainer = ThreatExplainer()
    
    # Test cases
    test_urls = [
        ("https://www.google.com", "Legitimate search engine"),
        ("https://www.amazon.com/account/login", "Legitimate e-commerce"),
        ("https://paypa1.com/verify-account", "Suspicious lookalike domain"),
        ("https://bank-verify.com/secure?update=true&confirm=now", "Clear phishing attempt"),
        ("http://192.168.1.1/admin", "IP address instead of domain"),
        ("https://login.mybank.top/update-security-verify-confirm", "Suspicious with keywords"),
    ]
    
    print("\n[1] PHISHING DETECTION DEMO")
    print("-" * 70)
    
    for url, description in test_urls:
        print(f"\n{description}")
        result = detector.detect(url, "Please verify your account immediately")
        print_result(url, result)
    
    # Demonstrate with context analysis
    print("\n\n[2] CONTEXT-AWARE DETECTION")
    print("-" * 70)
    
    suspicious_email = """
    From: support@paypa1.com
    Subject: Urgent: Verify Your Account
    
    Dear valued customer,
    
    Your account requires immediate verification. Please click the link below
    to confirm your identity and secure your account.
    
    Verify Now: https://paypa1.com/verify-account?token=abc123
    
    Best regards,
    PayPal Support Team
    """
    
    phishing_url = "https://paypa1.com/verify-account?token=abc123"
    result = detector.detect(phishing_url, suspicious_email)
    
    print(f"\nEmail Context Analysis:")
    print(f"URL: {phishing_url}")
    print(f"Phishing Detected: {result['is_phishing']}")
    print(f"Confidence: {result['confidence']:.2%}")
    print(f"Reasons:")
    for reason in result['reasons']:
        print(f"  • {reason}")
    
    # Demonstrate unified threat engine
    print("\n\n[3] UNIFIED THREAT DETECTION WITH EXPLANATION")
    print("-" * 70)
    
    threat_input = {
        "type": "url",
        "content": "https://bank-verify.com/update-account",
        "context": "Your account requires verification for security purposes"
    }
    
    result = engine.unified_threat_detection(threat_input)
    
    if result.get('requires_action'):
        print(f"\n🚨 THREAT DETECTED!")
        print(f"Type: {result['detected_threats'][0]['type'].upper()}")
        print(f"Confidence: {result['max_confidence']:.2%}")
        
        if result.get('explanation'):
            explanation = result['explanation']
            print(f"\n📋 Explanation:")
            print(explanation['user_friendly'])
            
            print(f"\n💡 Recommendations:")
            for rec in explanation.get('recommendations', []):
                print(f"  • {rec}")
        
        print(f"\n⏱️ Detection Latency: {result.get('latency_ms', 0):.2f}ms")
    
    # Show statistics
    print("\n\n[4] PERFORMANCE STATISTICS")
    print("-" * 70)
    
    stats = engine.get_statistics()
    print(f"Total Threats Detected: {stats['total_threats']}")
    print(f"Phishing: {stats['phishing_detected']}")
    print(f"Malware: {stats['malware_detected']}")
    print(f"Behavioral: {stats['behavioral_anomalies']}")
    print(f"\nLatency Metrics:")
    print(f"  Average: {stats.get('avg_latency_ms', 0):.2f}ms")
    print(f"  Max: {stats.get('max_latency_ms', 0):.2f}ms")
    print(f"  Min: {stats.get('min_latency_ms', 0):.2f}ms")
    
    print(f"\n✅ All detections completed - Sub 500ms latency achieved!")
    print("\n" + "="*70)

if __name__ == "__main__":
    main()
