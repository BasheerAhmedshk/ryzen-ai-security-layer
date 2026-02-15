// cpp/threat_engine/python_bindings.hpp
#pragma once

#include "phishing_detector.hpp"
#include <memory>
#include <cstring>

/**
 * C bindings for Python ctypes integration
 * Provides C interface to C++ classes
 */

extern "C" {
    // Opaque pointer types for Python
    typedef void* PhishingDetectorHandle;
    typedef void* ThreatResultHandle;

    // Create detector instance
    PhishingDetectorHandle create_phishing_detector() {
        return new amd_security::threat_detection::PhishingDetector();
    }

    // Destroy detector instance
    void destroy_phishing_detector(PhishingDetectorHandle handle) {
        delete static_cast<amd_security::threat_detection::PhishingDetector*>(handle);
    }

    // Detect phishing threat
    // Returns: 1 if phishing, 0 if safe, -1 if error
    int detect_phishing(PhishingDetectorHandle handle, 
                       const char* url, 
                       const char* context,
                       float* confidence_out,
                       char* threat_level_out,
                       char* reasons_out) {
        try {
            auto detector = static_cast<amd_security::threat_detection::PhishingDetector*>(handle);
            auto result = detector->detect(url, context ? context : "");
            
            *confidence_out = result.confidence;
            std::strcpy(threat_level_out, result.threat_level.c_str());
            
            // Concatenate reasons
            std::string reasons_str;
            for (size_t i = 0; i < result.reasons.size(); ++i) {
                reasons_str += result.reasons[i];
                if (i < result.reasons.size() - 1) {
                    reasons_str += " | ";
                }
            }
            std::strcpy(reasons_out, reasons_str.c_str());
            
            return result.is_phishing ? 1 : 0;
        } catch (...) {
            return -1;
        }
    }

    // Batch detect phishing
    int detect_phishing_batch(PhishingDetectorHandle handle,
                             const char** urls,
                             int url_count,
                             float* confidences_out,
                             int* results_out) {
        try {
            auto detector = static_cast<amd_security::threat_detection::PhishingDetector*>(handle);
            
            std::vector<std::string> url_list(urls, urls + url_count);
            auto results = detector->detect_batch(url_list);
            
            for (int i = 0; i < url_count; ++i) {
                confidences_out[i] = results[i].confidence;
                results_out[i] = results[i].is_phishing ? 1 : 0;
            }
            
            return url_count;
        } catch (...) {
            return -1;
        }
    }

    // Get version info
    const char* get_cpp_version() {
        return "AMD Security Layer C++ v1.0.0";
    }

    // Get build info
    const char* get_build_info() {
        return "Built with AVX2/OpenMP for AMD Ryzen optimization";
    }
}
