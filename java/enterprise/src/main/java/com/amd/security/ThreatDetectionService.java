package com.amd.security;

import java.util.*;

public class ThreatDetectionService {
    
    private PhishingDetector phishingDetector;
    private MalwareDetector malwareDetector;
    private BehaviorAnalyzer behaviorAnalyzer;
    
    public ThreatDetectionService() {
        this.phishingDetector = new PhishingDetector();
        this.malwareDetector = new MalwareDetector();
        this.behaviorAnalyzer = new BehaviorAnalyzer();
    }
    
    public Map<String, Object> detectThreat(String threatType, String content) {
        Map<String, Object> result = new HashMap<>();
        
        switch(threatType.toLowerCase()) {
            case "url":
            case "phishing":
                float phishingScore = phishingDetector.detect(content);
                result.put("type", "phishing");
                result.put("score", phishingScore);
                result.put("is_threat", phishingScore > 0.7);
                break;
                
            case "code":
            case "malware":
                float malwareScore = malwareDetector.detect(content);
                result.put("type", "malware");
                result.put("score", malwareScore);
                result.put("is_threat", malwareScore > 0.7);
                break;
                
            default:
                result.put("type", "unknown");
                result.put("score", 0.0);
                result.put("is_threat", false);
        }
        
        result.put("timestamp", System.currentTimeMillis());
        return result;
    }
    
    public Map<String, Object> analyzeBehavior(Map<String, Object> systemData) {
        Map<String, Object> result = new HashMap<>();
        
        float anomalyScore = behaviorAnalyzer.analyze(systemData);
        result.put("anomaly_score", anomalyScore);
        result.put("is_anomaly", anomalyScore > 0.6);
        result.put("timestamp", System.currentTimeMillis());
        
        return result;
    }
    
    public Map<String, Object> detectBatch(List<String> urls) {
        Map<String, Object> results = new HashMap<>();
        List<Map<String, Object>> detections = new ArrayList<>();
        
        for (String url : urls) {
            detections.add(detectThreat("url", url));
        }
        
        results.put("total", urls.size());
        results.put("detections", detections);
        results.put("timestamp", System.currentTimeMillis());
        
        return results;
    }
}