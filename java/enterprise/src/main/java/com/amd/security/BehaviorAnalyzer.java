package com.amd.security;

import java.util.*;

public class BehaviorAnalyzer {
    
    public float analyze(Map<String, Object> systemData) {
        if (systemData == null || systemData.isEmpty()) {
            return 0.0f;
        }
        
        float anomalyScore = 0.0f;
        
        // Check for suspicious behaviors
        if (systemData.containsKey("process_count")) {
            Integer count = (Integer) systemData.get("process_count");
            if (count > 50) anomalyScore += 0.3f;
        }
        
        if (systemData.containsKey("network_connections")) {
            Integer connections = (Integer) systemData.get("network_connections");
            if (connections > 100) anomalyScore += 0.3f;
        }
        
        if (systemData.containsKey("file_changes")) {
            Integer changes = (Integer) systemData.get("file_changes");
            if (changes > 200) anomalyScore += 0.4f;
        }
        
        return Math.min(anomalyScore, 1.0f);
    }
}