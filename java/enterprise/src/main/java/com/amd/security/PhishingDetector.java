// java/enterprise/src/main/java/com/amd/security/PhishingDetector.java
package com.amd.security;

import java.util.*;
import java.util.regex.Pattern;

/**
 * Java-based Phishing Detector
 * Enterprise-grade threat detection for URL analysis
 */
public class PhishingDetector {
    
    private static final float CONFIDENCE_THRESHOLD = 0.7f;
    private static final Map<String, Float> SUSPICIOUS_DOMAINS;
    private static final Set<String> SUSPICIOUS_TLDS;
    private static final Pattern URL_PATTERN;
    private static final Pattern IP_PATTERN;
    
    static {
        // Initialize suspicious domains
        SUSPICIOUS_DOMAINS = new HashMap<>();
        SUSPICIOUS_DOMAINS.put("paypa1.com", 0.9f);
        SUSPICIOUS_DOMAINS.put("amaz0n.com", 0.9f);
        SUSPICIOUS_DOMAINS.put("go0gle.com", 0.9f);
        SUSPICIOUS_DOMAINS.put("bank-verify.com", 0.95f);
        SUSPICIOUS_DOMAINS.put("account-confirm.com", 0.95f);
        SUSPICIOUS_DOMAINS.put("secure-login.com", 0.9f);
        
        // Initialize suspicious TLDs
        SUSPICIOUS_TLDS = new HashSet<>();
        SUSPICIOUS_TLDS.addAll(Arrays.asList(".tk", ".ml", ".ga", ".cf", ".xyz", ".top"));
        
        // Compile regex patterns
        URL_PATTERN = Pattern.compile(
            "http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),])+"
        );
        IP_PATTERN = Pattern.compile(
            "http[s]?://(\\d+\\.\\d+\\.\\d+\\.\\d+)"
        );
    }
    
    /**
     * Detect phishing threats in URL
     */
    public ThreatDetectionService.ThreatResult detect(String url, String context) {
        // Validate URL
        if (url == null || url.isEmpty() || !isValidUrl(url)) {
            return new ThreatDetectionService.ThreatResult(
                "phishing", 0.0f, false, 
                Collections.singletonList("Invalid URL format")
            );
        }
        
        // Extract features
        URLFeatures features = extractFeatures(url);
        
        // Analyze context
        float contextScore = analyzeContext(context);
        
        // Calculate threat score
        float threatScore = calculateThreatScore(features) * 0.8f + contextScore * 0.2f;
        
        boolean isPhishing = threatScore >= CONFIDENCE_THRESHOLD;
        List<String> reasons = generateReasons(features);
        
        return new ThreatDetectionService.ThreatResult(
            "phishing", 
            Math.min(threatScore, 1.0f), 
            isPhishing, 
            reasons
        );
    }
    
    /**
     * Batch detect multiple URLs
     */
    public List<ThreatDetectionService.ThreatResult> detectBatch(List<String> urls) {
        return urls.parallelStream()
            .map(url -> detect(url, ""))
            .toList();
    }
    
    private URLFeatures extractFeatures(String url) {
        return new URLFeatures(
            scoreUrlLength(url),
            scoreDomain(url),
            scoreSpecialChars(url),
            scoreIpAddress(url),
            scoreSubdomains(url)
        );
    }
    
    private float scoreUrlLength(String url) {
        int length = url.length();
        if (length > 200) return 0.8f;
        if (length > 100) return 0.5f;
        return 0.0f;
    }
    
    private float scoreDomain(String url) {
        try {
            int start = url.indexOf("://") + 3;
            int end = url.indexOf('/', start);
            if (end == -1) end = url.length();
            
            String domain = url.substring(start, end).toLowerCase();
            
            // Check suspicious domains
            if (SUSPICIOUS_DOMAINS.containsKey(domain)) {
                return SUSPICIOUS_DOMAINS.get(domain);
            }
            
            // Check suspicious TLDs
            for (String tld : SUSPICIOUS_TLDS) {
                if (domain.endsWith(tld)) {
                    return 0.7f;
                }
            }
            
            // Check lookalike domains
            if (isLookAlikeDomain(domain)) {
                return 0.7f;
            }
            
            return 0.0f;
        } catch (Exception e) {
            return 0.0f;
        }
    }
    
    private float scoreSpecialChars(String url) {
        int specialCount = 0;
        for (char c : url.toCharArray()) {
            if (c == '@' || c == '?') specialCount++;
        }
        return specialCount > 2 ? 0.6f : 0.0f;
    }
    
    private float scoreIpAddress(String url) {
        return IP_PATTERN.matcher(url).find() ? 0.8f : 0.0f;
    }
    
    private float scoreSubdomains(String url) {
        try {
            int start = url.indexOf("://") + 3;
            int end = url.indexOf('/', start);
            if (end == -1) end = url.length();
            
            String domain = url.substring(start, end);
            int dotCount = 0;
            for (char c : domain.toCharArray()) {
                if (c == '.') dotCount++;
            }
            
            return dotCount > 3 ? 0.6f : 0.0f;
        } catch (Exception e) {
            return 0.0f;
        }
    }
    
    private boolean isLookAlikeDomain(String domain) {
        Map<String, List<String>> lookalikes = new HashMap<>();
        lookalikes.put("paypa", Arrays.asList("paypal"));
        lookalikes.put("amaz", Arrays.asList("amazon"));
        lookalikes.put("goog", Arrays.asList("google"));
        lookalikes.put("face", Arrays.asList("facebook"));
        
        for (Map.Entry<String, List<String>> entry : lookalikes.entrySet()) {
            if (domain.contains(entry.getKey())) {
                for (String similar : entry.getValue()) {
                    if (domain.contains(similar) && !domain.equals(similar + ".com")) {
                        return true;
                    }
                }
            }
        }
        return false;
    }
    
    private boolean isValidUrl(String url) {
        return URL_PATTERN.matcher(url).find();
    }
    
    private float analyzeContext(String context) {
        if (context == null || context.isEmpty()) {
            return 0.0f;
        }
        
        String contextLower = context.toLowerCase();
        String[] phishingKeywords = {"verify", "confirm", "update", "validate", "secure"};
        
        int keywordCount = 0;
        for (String keyword : phishingKeywords) {
            if (contextLower.contains(keyword)) {
                keywordCount++;
            }
        }
        
        return Math.min(keywordCount * 0.15f, 0.5f);
    }
    
    private float calculateThreatScore(URLFeatures features) {
        float total = features.urlLengthScore + 
                     features.domainScore + 
                     features.specialCharScore + 
                     features.ipAddressScore + 
                     features.subdomainScore;
        return total / 5.0f;
    }
    
    private List<String> generateReasons(URLFeatures features) {
        List<String> reasons = new ArrayList<>();
        
        if (features.urlLengthScore > 0.5f) {
            reasons.add("Unusually long URL");
        }
        if (features.domainScore > 0.5f) {
            reasons.add("Suspicious domain name");
        }
        if (features.specialCharScore > 0.5f) {
            reasons.add("Suspicious special characters");
        }
        if (features.ipAddressScore > 0.5f) {
            reasons.add("Using IP address instead of domain");
        }
        if (features.subdomainScore > 0.5f) {
            reasons.add("Too many subdomains");
        }
        
        if (reasons.isEmpty()) {
            reasons.add("URL appears legitimate");
        }
        
        return reasons;
    }
    
    // Inner class for URL features
    private static class URLFeatures {
        float urlLengthScore;
        float domainScore;
        float specialCharScore;
        float ipAddressScore;
        float subdomainScore;
        
        URLFeatures(float urlLength, float domain, float specialChar, 
                   float ipAddress, float subdomain) {
            this.urlLengthScore = urlLength;
            this.domainScore = domain;
            this.specialCharScore = specialChar;
            this.ipAddressScore = ipAddress;
            this.subdomainScore = subdomain;
        }
    }
}
