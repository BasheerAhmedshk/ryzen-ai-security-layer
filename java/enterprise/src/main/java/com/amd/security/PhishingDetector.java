package com.amd.security;

public class PhishingDetector {
    
    public float detect(String url) {
        if (url == null || url.isEmpty()) {
            return 0.0f;
        }
        
        float score = 0.0f;
        String lowerUrl = url.toLowerCase();
        
        // Check suspicious patterns
        if (lowerUrl.contains("paypal") || lowerUrl.contains("paypa1")) score += 0.3f;
        if (lowerUrl.contains("amazon") || lowerUrl.contains("amaz0n")) score += 0.3f;
        if (lowerUrl.contains("@")) score += 0.2f;
        if (lowerUrl.contains("://") && !lowerUrl.startsWith("https://")) score += 0.2f;
        if (lowerUrl.length() > 200) score += 0.1f;
        
        return Math.min(score, 1.0f);
    }
}