// java/enterprise/src/main/java/com/amd/security/ThreatDetectionService.java
package com.amd.security;

import java.util.*;
import java.util.concurrent.*;
import java.util.stream.Collectors;
import java.security.MessageDigest;
import java.nio.charset.StandardCharsets;

/**
 * Enterprise Threat Detection Service
 * Provides scalable threat detection with caching and async processing
 */
public class ThreatDetectionService {
    
    private final PhishingDetector phishingDetector;
    private final MalwareDetector malwareDetector;
    private final BehaviorAnalyzer behaviorAnalyzer;
    private final ExecutorService executorService;
    private final Map<String, ThreatResult> resultCache;
    private final int cacheSize;
    
    public ThreatDetectionService(int threadPoolSize, int cacheSizeLimit) {
        this.phishingDetector = new PhishingDetector();
        this.malwareDetector = new MalwareDetector();
        this.behaviorAnalyzer = new BehaviorAnalyzer();
        this.executorService = Executors.newFixedThreadPool(threadPoolSize);
        this.resultCache = Collections.synchronizedMap(
            new LinkedHashMap<String, ThreatResult>(cacheSizeLimit, 0.75f, true) {
                @Override
                protected boolean removeEldestEntry(Map.Entry eldest) {
                    return size() > cacheSize;
                }
            }
        );
        this.cacheSize = cacheSizeLimit;
    }
    
    /**
     * Detect phishing threats
     */
    public ThreatResult detectPhishing(String url, String context) {
        String cacheKey = "phishing:" + hashString(url);
        
        // Check cache
        if (resultCache.containsKey(cacheKey)) {
            return resultCache.get(cacheKey);
        }
        
        ThreatResult result = phishingDetector.detect(url, context);
        resultCache.put(cacheKey, result);
        return result;
    }
    
    /**
     * Detect malware asynchronously
     */
    public CompletableFuture<ThreatResult> detectMalwareAsync(String code) {
        return CompletableFuture.supplyAsync(() -> {
            String cacheKey = "malware:" + hashString(code);
            
            if (resultCache.containsKey(cacheKey)) {
                return resultCache.get(cacheKey);
            }
            
            ThreatResult result = malwareDetector.detect(code);
            resultCache.put(cacheKey, result);
            return result;
        }, executorService);
    }
    
    /**
     * Analyze behavior anomalies
     */
    public ThreatResult analyzeBehavior(Map<String, Object> action) {
        return behaviorAnalyzer.analyze(action);
    }
    
    /**
     * Unified threat detection with batch processing
     */
    public List<ThreatResult> unifiedDetectionBatch(List<ThreatInput> threats) {
        return threats.parallelStream()
            .map(threat -> detectThreat(threat))
            .collect(Collectors.toList());
    }
    
    /**
     * Single unified threat detection
     */
    public ThreatResult detectThreat(ThreatInput threat) {
        switch (threat.getType()) {
            case "url":
                return detectPhishing((String) threat.getContent(), 
                                     threat.getContext());
            case "code":
                return malwareDetector.detect((String) threat.getContent());
            case "action":
                return analyzeBehavior((Map<String, Object>) threat.getContent());
            default:
                return ThreatResult.safe();
        }
    }
    
    /**
     * Get detection statistics
     */
    public DetectionStatistics getStatistics() {
        return new DetectionStatistics(
            resultCache.size(),
            resultCache.values().stream()
                .filter(ThreatResult::isThreat)
                .count(),
            resultCache.values().stream()
                .filter(r -> "phishing".equals(r.getThreatType()))
                .count()
        );
    }
    
    /**
     * Clear cache
     */
    public void clearCache() {
        resultCache.clear();
    }
    
    /**
     * Shutdown service gracefully
     */
    public void shutdown() {
        executorService.shutdown();
        try {
            if (!executorService.awaitTermination(30, TimeUnit.SECONDS)) {
                executorService.shutdownNow();
            }
        } catch (InterruptedException e) {
            executorService.shutdownNow();
            Thread.currentThread().interrupt();
        }
    }
    
    private String hashString(String input) {
        try {
            MessageDigest digest = MessageDigest.getInstance("SHA-256");
            byte[] hash = digest.digest(input.getBytes(StandardCharsets.UTF_8));
            return bytesToHex(hash).substring(0, 8);
        } catch (Exception e) {
            return Integer.toHexString(input.hashCode());
        }
    }
    
    private String bytesToHex(byte[] bytes) {
        StringBuilder hexString = new StringBuilder();
        for (byte b : bytes) {
            String hex = Integer.toHexString(0xff & b);
            if (hex.length() == 1) hexString.append('0');
            hexString.append(hex);
        }
        return hexString.toString();
    }
    
    // Inner classes for threat detection
    public static class ThreatInput {
        private final String type;  // "url", "code", "action"
        private final Object content;
        private final String context;
        
        public ThreatInput(String type, Object content, String context) {
            this.type = type;
            this.content = content;
            this.context = context;
        }
        
        public String getType() { return type; }
        public Object getContent() { return content; }
        public String getContext() { return context; }
    }
    
    public static class ThreatResult {
        private final String threatType;
        private final float confidence;
        private final boolean isThreat;
        private final List<String> reasons;
        private final long timestamp;
        
        public ThreatResult(String threatType, float confidence, boolean isThreat, 
                           List<String> reasons) {
            this.threatType = threatType;
            this.confidence = confidence;
            this.isThreat = isThreat;
            this.reasons = reasons;
            this.timestamp = System.currentTimeMillis();
        }
        
        public static ThreatResult safe() {
            return new ThreatResult("none", 0.0f, false, 
                                  Collections.singletonList("No threat detected"));
        }
        
        public String getThreatType() { return threatType; }
        public float getConfidence() { return confidence; }
        public boolean isThreat() { return isThreat; }
        public List<String> getReasons() { return reasons; }
        public long getTimestamp() { return timestamp; }
        
        @Override
        public String toString() {
            return String.format(
                "ThreatResult{type='%s', confidence=%.2f, threat=%s}",
                threatType, confidence, isThreat
            );
        }
    }
    
    public static class DetectionStatistics {
        private final long cacheSize;
        private final long threatsDetected;
        private final long phishingCount;
        
        public DetectionStatistics(long cacheSize, long threatsDetected, 
                                  long phishingCount) {
            this.cacheSize = cacheSize;
            this.threatsDetected = threatsDetected;
            this.phishingCount = phishingCount;
        }
        
        public long getCacheSize() { return cacheSize; }
        public long getThreatsDetected() { return threatsDetected; }
        public long getPhishingCount() { return phishingCount; }
        
        @Override
        public String toString() {
            return String.format(
                "DetectionStatistics{cache=%d, threats=%d, phishing=%d}",
                cacheSize, threatsDetected, phishingCount
            );
        }
    }
}
