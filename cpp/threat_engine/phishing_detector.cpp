// cpp/threat_engine/phishing_detector.cpp
#include "phishing_detector.hpp"
#include <algorithm>
#include <sstream>
#include <cmath>
#include <openssl/sha.h>
#include <iomanip>

namespace amd_security {
namespace threat_detection {

PhishingDetector::PhishingDetector() {
    // Initialize suspicious domains
    suspicious_domains = {
        {"paypa1.com", 0.9f},
        {"amaz0n.com", 0.9f},
        {"go0gle.com", 0.9f},
        {"bank-verify.com", 0.95f},
        {"account-confirm.com", 0.95f},
        {"secure-login.com", 0.9f}
    };

    // Initialize suspicious TLDs
    suspicious_tlds = {".tk", ".ml", ".ga", ".cf", ".xyz", ".top"};

    // Initialize regex patterns
    try {
        suspicious_patterns.emplace_back(R"(http[s]?:\/\/\d+\.\d+\.\d+\.\d+)"); // IP addresses
        suspicious_patterns.emplace_back(R"(@)");  // @ symbol
        suspicious_patterns.emplace_back(R"(\?)");  // Question mark
    } catch (const std::regex_error& e) {
        // Log error
    }
}

PhishingDetector::~PhishingDetector() = default;

ThreatResult PhishingDetector::detect(const std::string& url, const std::string& context) {
    ThreatResult result;
    result.url_hash = sha256(url);

    // Validate URL
    if (url.empty() || !is_valid_url(url)) {
        result.is_phishing = false;
        result.confidence = 0.0f;
        result.threat_level = "safe";
        result.reasons.push_back("Invalid URL format");
        return result;
    }

    // Extract features
    URLFeatures features = extract_features(url);

    // Add context analysis
    float context_score = 0.0f;
    if (!context.empty()) {
        std::string context_lower = context;
        std::transform(context_lower.begin(), context_lower.end(), 
                      context_lower.begin(), ::tolower);
        
        const std::vector<std::string> phishing_keywords = {
            "verify", "confirm", "update", "validate", "secure"
        };
        
        int keyword_count = 0;
        for (const auto& kw : phishing_keywords) {
            if (context_lower.find(kw) != std::string::npos) {
                keyword_count++;
            }
        }
        context_score = std::min(keyword_count * 0.15f, 0.5f);
    }

    // Calculate threat score
    float threat_score = calculate_threat_score(features);
    threat_score = (threat_score * 0.8f) + (context_score * 0.2f);

    result.confidence = std::min(threat_score, 1.0f);
    result.is_phishing = threat_score >= CONFIDENCE_THRESHOLD;
    result.threat_level = result.is_phishing ? "high" : "safe";
    result.reasons = extract_reasons(features);

    return result;
}

std::vector<ThreatResult> PhishingDetector::detect_batch(const std::vector<std::string>& urls) {
    std::vector<ThreatResult> results;
    results.reserve(urls.size());

    // Use OpenMP for parallel processing (SIMD optimization)
    #pragma omp parallel for
    for (size_t i = 0; i < urls.size(); ++i) {
        results[i] = detect(urls[i]);
    }

    return results;
}

PhishingDetector::URLFeatures PhishingDetector::extract_features(const std::string& url) {
    URLFeatures features;
    features.url_length_score = score_url_length(url);
    features.domain_score = score_domain(url);
    features.special_char_score = score_special_chars(url);
    features.ip_address_score = score_ip_address(url);
    features.subdomain_score = score_subdomains(url);
    return features;
}

float PhishingDetector::score_url_length(const std::string& url) {
    size_t length = url.length();
    if (length > 200) return 0.8f;
    if (length > 100) return 0.5f;
    return 0.0f;
}

float PhishingDetector::score_domain(const std::string& url) {
    try {
        size_t start = url.find("://") + 3;
        size_t end = url.find('/', start);
        if (end == std::string::npos) end = url.length();
        
        std::string domain = url.substr(start, end - start);
        std::transform(domain.begin(), domain.end(), domain.begin(), ::tolower);

        // Check suspicious domains
        auto it = suspicious_domains.find(domain);
        if (it != suspicious_domains.end()) {
            return it->second;
        }

        // Check suspicious TLDs
        for (const auto& tld : suspicious_tlds) {
            if (domain.find(tld) != std::string::npos) {
                return 0.7f;
            }
        }

        // Check lookalike domains
        if (is_lookalike_domain(domain)) {
            return 0.7f;
        }

        return 0.0f;
    } catch (...) {
        return 0.0f;
    }
}

float PhishingDetector::score_special_chars(const std::string& url) {
    int special_count = std::count(url.begin(), url.end(), '@') +
                        std::count(url.begin(), url.end(), '?');
    if (special_count > 2) return 0.6f;
    return 0.0f;
}

float PhishingDetector::score_ip_address(const std::string& url) {
    // Check for IP address pattern
    std::regex ip_pattern(R"(http[s]?://\d+\.\d+\.\d+\.\d+)");
    return std::regex_search(url, ip_pattern) ? 0.8f : 0.0f;
}

float PhishingDetector::score_subdomains(const std::string& url) {
    try {
        size_t start = url.find("://") + 3;
        size_t end = url.find('/', start);
        if (end == std::string::npos) end = url.length();
        
        std::string domain = url.substr(start, end - start);
        int subdomain_count = std::count(domain.begin(), domain.end(), '.');
        
        if (subdomain_count > 3) return 0.6f;
        return 0.0f;
    } catch (...) {
        return 0.0f;
    }
}

float PhishingDetector::calculate_threat_score(const URLFeatures& features) {
    float total = features.url_length_score + 
                  features.domain_score + 
                  features.special_char_score + 
                  features.ip_address_score + 
                  features.subdomain_score;
    
    return total / 5.0f;
}

bool PhishingDetector::is_lookalike_domain(const std::string& domain) {
    const std::map<std::string, std::vector<std::string>> lookalikes = {
        {"paypa", {"paypal"}},
        {"amaz", {"amazon"}},
        {"goog", {"google"}},
        {"face", {"facebook"}}
    };

    for (const auto& [key, similar] : lookalikes) {
        if (domain.find(key) != std::string::npos) {
            for (const auto& sim : similar) {
                if (domain.find(sim) != std::string::npos && 
                    domain != sim + ".com") {
                    return true;
                }
            }
        }
    }
    return false;
}

bool PhishingDetector::is_valid_url(const std::string& url) {
    std::regex url_regex(R"(http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),])+)");
    return std::regex_search(url, url_regex);
}

std::vector<std::string> PhishingDetector::extract_reasons(const URLFeatures& features) {
    std::vector<std::string> reasons;
    
    if (features.url_length_score > 0.5f) {
        reasons.push_back("Unusually long URL");
    }
    if (features.domain_score > 0.5f) {
        reasons.push_back("Suspicious domain name");
    }
    if (features.special_char_score > 0.5f) {
        reasons.push_back("Suspicious special characters");
    }
    if (features.ip_address_score > 0.5f) {
        reasons.push_back("Using IP address instead of domain");
    }
    if (features.subdomain_score > 0.5f) {
        reasons.push_back("Too many subdomains");
    }
    
    if (reasons.empty()) {
        reasons.push_back("URL appears legitimate");
    }
    
    return reasons;
}

std::string PhishingDetector::sha256(const std::string& input) {
    unsigned char hash[SHA256_DIGEST_LENGTH];
    SHA256(reinterpret_cast<const unsigned char*>(input.c_str()), 
           input.length(), hash);
    
    std::stringstream ss;
    for (int i = 0; i < 8; ++i) {  // First 8 bytes for short hash
        ss << std::hex << std::setw(2) << std::setfill('0') 
           << static_cast<int>(hash[i]);
    }
    return ss.str();
}

} // namespace threat_detection
} // namespace amd_security
