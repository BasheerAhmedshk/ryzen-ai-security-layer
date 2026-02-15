# src/threat_detection/phishing_detector.py
"""
Phishing Link Detection Module
Uses lightweight ML models for real-time phishing detection
"""

import json
import re
import hashlib
from typing import Dict, Tuple, List
from config.settings import DETECTION_CONFIG, DATA_DIR
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class PhishingDetector:
    """Detects phishing links using heuristics and ML models"""
    
    def __init__(self):
        """Initialize phishing detector with known patterns"""
        self.confidence_threshold = DETECTION_CONFIG['phishing']['confidence_threshold']
        self.patterns_db = self._load_phishing_patterns()
        self.suspicious_domains = self._init_suspicious_domains()
        self.url_regex = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        )
        logger.info("PhishingDetector initialized")
    
    def _load_phishing_patterns(self) -> Dict:
        """Load phishing patterns from database"""
        try:
            patterns_file = DATA_DIR / "phishing_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading phishing patterns: {e}")
        
        # Default patterns if file doesn't exist
        return {
            "keywords": ["verify", "confirm", "update", "validate", "secure"],
            "suspicious_tlds": [".tk", ".ml", ".ga", ".cf"],
        }
    
    def _init_suspicious_domains(self) -> set:
        """Initialize list of known suspicious domains"""
        return {
            "paypa1.com", "amaz0n.com", "go0gle.com", "bank-verify.com",
            "account-confirm.com", "secure-login.com", "update-verify.com"
        }
    
    def detect(self, url: str, context: str = "") -> Dict:
        """
        Detect if a URL is phishing
        
        Args:
            url: URL to check
            context: Additional context (email body, page text, etc.)
        
        Returns:
            Dict with threat assessment
        """
        try:
            # Validate URL format
            if not url or not self._is_valid_url(url):
                return {
                    "is_phishing": False,
                    "confidence": 0.0,
                    "threat_level": "safe",
                    "reasons": ["Invalid URL format"]
                }
            
            # Heuristic-based detection
            features = self._extract_url_features(url)
            features['context_score'] = self._analyze_context(context)
            
            # Calculate threat score
            threat_score = self._calculate_threat_score(features)
            
            # Determine if phishing
            is_phishing = threat_score >= self.confidence_threshold
            
            result = {
                "is_phishing": is_phishing,
                "confidence": min(threat_score, 1.0),
                "threat_level": "high" if is_phishing else "safe",
                "reasons": self._generate_reasons(features),
                "url_hash": hashlib.sha256(url.encode()).hexdigest()[:8]
            }
            
            logger.info(f"Phishing detection - URL: {url[:50]}... - Score: {threat_score:.2f}")
            return result
        
        except Exception as e:
            logger.error(f"Error in phishing detection: {e}")
            return {
                "is_phishing": False,
                "confidence": 0.0,
                "threat_level": "unknown",
                "reasons": ["Error in detection"]
            }
    
    def _is_valid_url(self, url: str) -> bool:
        """Check if URL has valid format"""
        return bool(self.url_regex.match(url))
    
    def _extract_url_features(self, url: str) -> Dict:
        """Extract features from URL for threat scoring"""
        features = {
            "url_length_score": self._score_url_length(url),
            "domain_score": self._score_domain(url),
            "special_char_score": self._score_special_chars(url),
            "ip_address_score": self._score_ip_address(url),
            "subdomain_score": self._score_subdomains(url),
        }
        return features
    
    def _score_url_length(self, url: str) -> float:
        """Score based on URL length (very long URLs are suspicious)"""
        length = len(url)
        if length > 200:
            return 0.8
        elif length > 100:
            return 0.5
        return 0.0
    
    def _score_domain(self, url: str) -> float:
        """Score domain for suspicious characteristics"""
        try:
            # Extract domain
            domain = url.split('/')[2].lower()
            
            # Check if in suspicious list
            if domain in self.suspicious_domains:
                return 0.9
            
            # Check for suspicious TLDs
            for tld in self.patterns_db.get("suspicious_tlds", []):
                if domain.endswith(tld):
                    return 0.7
            
            # Check for look-alike domains
            if self._is_lookalike_domain(domain):
                return 0.7
            
            return 0.0
        except Exception as e:
            logger.warning(f"Error scoring domain: {e}")
            return 0.0
    
    def _is_lookalike_domain(self, domain: str) -> bool:
        """Check if domain looks like a legitimate site"""
        lookalikes = {
            "paypa": ["paypal"],
            "amaz": ["amazon"],
            "goog": ["google"],
            "face": ["facebook"],
        }
        
        for key, similar in lookalikes.items():
            if key in domain:
                for sim in similar:
                    if sim in domain and domain != f"{sim}.com":
                        return True
        return False
    
    def _score_special_chars(self, url: str) -> float:
        """Score based on suspicious special characters"""
        special_chars = url.count('@') + url.count('?')
        if special_chars > 2:
            return 0.6
        return 0.0
    
    def _score_ip_address(self, url: str) -> bool:
        """Check if URL uses IP address instead of domain"""
        ip_pattern = re.compile(r'http[s]?://\d+\.\d+\.\d+\.\d+')
        if ip_pattern.match(url):
            return 0.8
        return 0.0
    
    def _score_subdomains(self, url: str) -> float:
        """Score based on number of subdomains"""
        domain_part = url.split('/')[2]
        subdomain_count = domain_part.count('.')
        if subdomain_count > 3:
            return 0.6
        return 0.0
    
    def _analyze_context(self, context: str) -> float:
        """Analyze surrounding context for phishing indicators"""
        if not context:
            return 0.0
        
        context_lower = context.lower()
        phishing_keywords = self.patterns_db.get("keywords", [])
        
        keyword_count = sum(1 for kw in phishing_keywords if kw in context_lower)
        return min(keyword_count * 0.15, 0.5)
    
    def _calculate_threat_score(self, features: Dict) -> float:
        """Calculate overall threat score from features"""
        scores = list(features.values())
        if not scores:
            return 0.0
        return sum(scores) / len(scores)
    
    def _generate_reasons(self, features: Dict) -> List[str]:
        """Generate human-readable reasons for threat assessment"""
        reasons = []
        
        if features['url_length_score'] > 0.5:
            reasons.append("Unusually long URL")
        if features['domain_score'] > 0.5:
            reasons.append("Suspicious domain name")
        if features['special_char_score'] > 0.5:
            reasons.append("Suspicious special characters in URL")
        if features['ip_address_score'] > 0.5:
            reasons.append("Using IP address instead of domain")
        if features['subdomain_score'] > 0.5:
            reasons.append("Too many subdomains")
        if features['context_score'] > 0.3:
            reasons.append("Context contains phishing keywords")
        
        if not reasons:
            reasons.append("URL appears legitimate")
        
        return reasons

# Demo usage
if __name__ == "__main__":
    detector = PhishingDetector()
    
    test_urls = [
        "https://www.google.com",
        "https://paypa1.com/login",
        "https://192.168.1.1/admin",
        "http://bank-verify.com/update-account?verify=true&confirm=secure",
    ]
    
    for url in test_urls:
        result = detector.detect(url, "Please verify your account")
        print(f"\nURL: {url}")
        print(f"  Phishing: {result['is_phishing']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Reasons: {result['reasons']}")
