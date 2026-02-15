# src/explainability/threat_explainer.py
"""
Threat Explainer Module
Generates plain-language explanations for detected threats
"""

import re
from typing import Dict, List
from config.settings import EXPLAINABILITY_CONFIG
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class ThreatExplainer:
    """Generates user-friendly threat explanations"""
    
    def __init__(self):
        """Initialize threat explainer"""
        self.threat_categories = EXPLAINABILITY_CONFIG['threat_categories']
        self.max_length = EXPLAINABILITY_CONFIG['max_explanation_length']
        self.explanation_templates = self._init_templates()
        logger.info("ThreatExplainer initialized")
    
    def _init_templates(self) -> Dict:
        """Initialize explanation templates"""
        return {
            "phishing": {
                "high": "This link appears to be a phishing attempt designed to steal your credentials. Avoid clicking.",
                "medium": "This link may be suspicious. Verify the sender before clicking.",
                "low": "This link seems unusual but may be safe. Use caution.",
            },
            "malware": {
                "high": "Malicious code detected. This could harm your system. Do not execute.",
                "medium": "Suspicious code detected. Please review before proceeding.",
                "low": "This code contains potentially suspicious patterns.",
            },
            "behavioral": {
                "high": "Suspicious activity detected on your system. Investigate immediately.",
                "medium": "Unusual system behavior detected. Monitor your system.",
                "low": "Minor unusual activity detected.",
            },
            "unknown": {
                "high": "Unknown threat detected. Use caution.",
                "medium": "Potential threat detected.",
                "low": "Minor concern detected.",
            }
        }
    
    def explain_threat(self, threat_data: Dict) -> Dict:
        """
        Generate explanation for a detected threat
        
        Args:
            threat_data: Threat detection result containing:
                - threat_type: Type of threat
                - confidence: Confidence score (0-1)
                - reasons: List of detection reasons
                - details: Additional threat details
        
        Returns:
            Dict with explanation
        """
        try:
            threat_type = threat_data.get('threat_type', 'unknown')
            confidence = threat_data.get('confidence', 0.0)
            reasons = threat_data.get('reasons', [])
            
            # Determine severity level
            severity = self._get_severity_level(confidence)
            
            # Generate explanation
            base_explanation = self._get_template_explanation(threat_type, severity)
            detailed_explanation = self._generate_detailed_explanation(threat_type, reasons, severity)
            
            explanation = {
                "threat_type": threat_type,
                "severity": severity,
                "confidence": confidence,
                "user_friendly": base_explanation,
                "detailed": detailed_explanation,
                "recommendations": self._get_recommendations(threat_type, severity),
                "action_items": self._get_action_items(threat_type)
            }
            
            logger.info(f"Explanation generated for {threat_type}: {severity}")
            return explanation
        
        except Exception as e:
            logger.error(f"Error generating explanation: {e}")
            return {
                "threat_type": "unknown",
                "severity": "medium",
                "user_friendly": "A security concern was detected.",
                "detailed": "Unable to generate detailed explanation.",
                "recommendations": ["Review security settings"]
            }
    
    def _get_severity_level(self, confidence: float) -> str:
        """Map confidence score to severity level"""
        if confidence >= 0.85:
            return "high"
        elif confidence >= 0.65:
            return "medium"
        else:
            return "low"
    
    def _get_template_explanation(self, threat_type: str, severity: str) -> str:
        """Get template explanation for threat"""
        templates = self.explanation_templates.get(threat_type, self.explanation_templates['unknown'])
        return templates.get(severity, templates.get('medium', 'Threat detected.'))
    
    def _generate_detailed_explanation(self, threat_type: str, reasons: List[str], severity: str) -> str:
        """Generate detailed explanation combining multiple reasons"""
        if not reasons:
            return "No details available."
        
        # Start with base reason
        details = f"This {threat_type} threat was detected because: "
        
        # Add reasons in readable format
        if len(reasons) == 1:
            details += reasons[0] + "."
        else:
            # Group reasons
            unique_reasons = list(set(reasons))[:3]  # Max 3 reasons
            details += "\n• " + "\n• ".join(unique_reasons)
        
        # Truncate if too long
        if len(details) > self.max_length:
            details = details[:self.max_length-3] + "..."
        
        return details
    
    def _get_recommendations(self, threat_type: str, severity: str) -> List[str]:
        """Get security recommendations for threat"""
        recommendations = {
            "phishing": [
                "Do not click the link",
                "Do not enter your credentials",
                "Report the sender",
                "Verify the official website separately"
            ],
            "malware": [
                "Do not execute the code",
                "Run a full system scan",
                "Update your antivirus",
                "Be cautious with similar files"
            ],
            "behavioral": [
                "Monitor your system activity",
                "Check running processes",
                "Review recent file modifications",
                "Consider system restore if suspicious"
            ]
        }
        
        base_recs = recommendations.get(threat_type, ["Update security software"])
        
        # Adjust recommendations based on severity
        if severity == "high":
            base_recs.append("Take immediate action")
        
        return base_recs
    
    def _get_action_items(self, threat_type: str) -> Dict:
        """Get immediate action items"""
        actions = {
            "phishing": {
                "immediate": "Block this sender/URL",
                "next": "Review similar messages",
                "long_term": "Enable two-factor authentication"
            },
            "malware": {
                "immediate": "Quarantine/delete the file",
                "next": "Run full system scan",
                "long_term": "Keep software updated"
            },
            "behavioral": {
                "immediate": "Monitor the system",
                "next": "Check system logs",
                "long_term": "Improve security practices"
            }
        }
        
        return actions.get(threat_type, {
            "immediate": "Take appropriate action",
            "next": "Monitor the situation",
            "long_term": "Improve security"
        })
    
    def format_for_display(self, explanation: Dict) -> str:
        """Format explanation for UI display"""
        output = f"""
╔════════════════════════════════════════════════════════════╗
║                    SECURITY THREAT ALERT                   ║
╚════════════════════════════════════════════════════════════╝

Threat Type: {explanation.get('threat_type', 'Unknown').upper()}
Severity: {explanation.get('severity', 'Medium').upper()}
Confidence: {explanation.get('confidence', 0.0)*100:.1f}%

─────────────────────────────────────────────────────────────
Alert Message:
{explanation.get('user_friendly', 'Threat detected')}

─────────────────────────────────────────────────────────────
Details:
{explanation.get('detailed', 'No details available')}

─────────────────────────────────────────────────────────────
Recommendations:
"""
        for i, rec in enumerate(explanation.get('recommendations', []), 1):
            output += f"  {i}. {rec}\n"
        
        output += "─────────────────────────────────────────────────────────────\n"
        
        return output

class ExplanationOptimizer:
    """Optimize explanations for different user expertise levels"""
    
    @staticmethod
    def simplify_for_novice(explanation: str) -> str:
        """Simplify technical terms for non-technical users"""
        replacements = {
            "malware": "harmful software",
            "phishing": "fake login attempt",
            "URL": "link",
            "credentials": "username and password",
            "execute": "run",
            "behavioral anomaly": "unusual activity",
        }
        
        simplified = explanation
        for technical, simple in replacements.items():
            simplified = re.sub(technical, simple, simplified, flags=re.IGNORECASE)
        
        return simplified
    
    @staticmethod
    def expand_for_expert(explanation: str) -> str:
        """Add technical details for advanced users"""
        technical_details = {
            "Add hash analysis": " [SHA256 hash available on request]",
            "Add IOC data": " [Indicator of Compromise data logged]",
            "Add MITRE ATT&CK": " [MITRE ATT&CK framework mapping available]",
        }
        
        expanded = explanation
        # Add technical markers
        expanded += "\n\n[Technical Details Available for Advanced Analysis]"
        
        return expanded

# Demo usage
if __name__ == "__main__":
    explainer = ThreatExplainer()
    
    # Example threat
    threat = {
        "threat_type": "phishing",
        "confidence": 0.88,
        "reasons": [
            "Suspicious domain name",
            "Contains phishing keywords",
            "Similar to known phishing pattern"
        ]
    }
    
    explanation = explainer.explain_threat(threat)
    
    print(explainer.format_for_display(explanation))
    
    # Show simplification
    print("\n=== Simplified Explanation ===")
    simplified = ExplanationOptimizer.simplify_for_novice(explanation['user_friendly'])
    print(simplified)
