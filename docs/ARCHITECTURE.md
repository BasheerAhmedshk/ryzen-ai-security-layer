# docs/ARCHITECTURE.md
# AMD Ryzen AI Security Layer - Architecture Documentation

## System Overview

The AMD Ryzen AI Security Layer is a lightweight, on-device threat detection system that leverages AMD Ryzen AI hardware (NPU + GPU) to provide real-time cybersecurity with sub-500ms latency and zero cloud dependency.

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER/SYSTEM INPUTS                          │
│        (URLs, Code, System Actions, Network Traffic)            │
└────────────────────────┬────────────────────────────────────────┘
                         │
         ┌───────────────┼───────────────┐
         │               │               │
         ▼               ▼               ▼
    ┌─────────┐    ┌──────────┐    ┌──────────┐
    │Phishing │    │ Malware  │    │Behavior  │
    │Detector │    │ Detector │    │ Analyzer │
    └────┬────┘    └────┬─────┘    └────┬─────┘
         │               │               │
         └───────────────┼───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │   THREAT ENGINE (Orchestrator) │
         │   - Unified threat scoring    │
         │   - Multi-model integration   │
         │   - Latency monitoring        │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │  HARDWARE ACCELERATION LAYER   │
         │  - ONNX Runtime Manager        │
         │  - ROCm (AMD GPU/NPU)          │
         │  - Model Optimization          │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │   EXPLAINABILITY LAYER         │
         │   - Plain-language alerts     │
         │   - Threat explanations       │
         │   - Action recommendations    │
         └───────────────┬───────────────┘
                         │
         ┌───────────────┴───────────────┐
         │   ALERT MANAGEMENT             │
         │   - Alert generation           │
         │   - User notifications         │
         │   - Action logging             │
         └───────────────┬───────────────┘
                         │
         ┌───────────────▼───────────────┐
         │    USER INTERFACE              │
         │  - Desktop notifications       │
         │  - Browser alerts              │
         │  - Settings panel              │
         └─────────────────────────────────┘
```

## Core Components

### 1. Threat Detection Layer

#### Phishing Detector
- **Location**: `src/threat_detection/phishing_detector.py`
- **Functionality**:
  - URL feature extraction (length, domain, special chars, subdomains)
  - Domain reputation analysis
  - Lookalike domain detection
  - Context-aware analysis
- **Output**: Phishing score (0-1) with confidence

#### Malware Detector
- **Location**: `src/threat_detection/malware_detector.py`
- **Functionality**:
  - Suspicious function detection
  - Code obfuscation analysis
  - Script injection patterns
  - Encoded content detection
- **Output**: Malware threat score with reasoning

#### Behavior Analyzer
- **Location**: `src/threat_detection/behavior_analyzer.py`
- **Functionality**:
  - System action monitoring
  - Behavioral pattern analysis
  - Anomaly scoring
  - Pattern-based threat identification
- **Output**: Anomaly confidence score with behavioral analysis

### 2. Hardware Acceleration Layer

#### ONNX Runtime Manager
- **Location**: `src/hardware_acceleration/onnx_runtime_manager.py`
- **Purpose**: Manages lightweight ML model inference
- **Features**:
  - Multi-provider support (GPU, CPU)
  - Model caching
  - Batch inference
  - Performance optimization

#### ROCm Accelerator
- **Location**: `src/hardware_acceleration/rocm_accelerator.py`
- **Purpose**: Leverages AMD GPU/NPU for acceleration
- **Features**:
  - Device detection and management
  - Memory pooling
  - Mixed precision support
  - Performance benchmarking

#### NPU Optimizer
- **Location**: `src/hardware_acceleration/rocm_accelerator.py`
- **Purpose**: Specialized optimizations for Ryzen AI NPU
- **Features**:
  - NPU-specific quantization
  - Latency optimization
  - Power efficiency

### 3. Security Core

#### Threat Engine
- **Location**: `src/security_core/threat_engine.py`
- **Purpose**: Orchestrates all threat detection modules
- **Capabilities**:
  - Unified threat detection
  - Multi-detector coordination
  - Async threat processing
  - Performance tracking
  - Sub-500ms latency guarantee

#### Alert Manager
- **Location**: `src/security_core/alert_manager.py`
- **Purpose**: Manages threat alerts and user notifications
- **Features**:
  - Alert creation and tracking
  - Dismissal management
  - Action logging
  - Statistics and reporting
  - Export functionality

### 4. Explainability Layer

#### Threat Explainer
- **Location**: `src/explainability/threat_explainer.py`
- **Purpose**: Generates user-friendly threat explanations
- **Features**:
  - Template-based explanations
  - Severity-adjusted messaging
  - Actionable recommendations
  - Technical detail levels

## Data Flow

### Phishing Detection Flow
```
URL Input
    ↓
URL Validation
    ↓
Feature Extraction (length, domain, chars, subdomains)
    ↓
Domain Analysis (reputation, lookalike check)
    ↓
Context Analysis (if provided)
    ↓
Threat Score Calculation
    ↓
Alert Generation (if score > threshold)
    ↓
Explanation Generation
    ↓
User Notification
```

### Malware Detection Flow
```
Code Input
    ↓
Code Analysis
    ├─ Suspicious Functions
    ├─ Obfuscation Detection
    ├─ Injection Patterns
    └─ Encoded Content
    ↓
Threat Score Calculation
    ↓
Alert Generation (if score > threshold)
    ↓
Explanation Generation
    ↓
User Notification
```

### Behavioral Anomaly Flow
```
System Action Input
    ↓
Action Classification
    ↓
Risk Scoring
    ├─ Individual Action Risk
    └─ Pattern Analysis
    ↓
Anomaly Score Calculation
    ↓
Alert Generation (if score > threshold)
    ↓
Explanation Generation
    ↓
User Notification
```

## Performance Characteristics

### Latency Targets
- **Phishing Detection**: < 50ms
- **Malware Detection**: < 100ms
- **Behavioral Analysis**: < 100ms
- **Total E2E Latency**: < 500ms

### Resource Usage
- **Memory**: < 200MB baseline
- **GPU Memory**: < 1GB (with acceleration)
- **CPU Usage**: < 5% (idle), < 20% (detection)
- **Power**: < 1W (NPU), < 5W (GPU)

## Security Properties

### Privacy
- ✅ All processing on-device
- ✅ No data transmission
- ✅ No cloud dependency
- ✅ Local logging only

### Explainability
- ✅ Plain-language alerts
- ✅ Reason enumeration
- ✅ Confidence scores
- ✅ Action recommendations

### Scalability
- ✅ Works on laptops
- ✅ Deployable on enterprises
- ✅ Educational institution compatible
- ✅ Minimal resource footprint

## Integration Points

### Browser Integration
- Could integrate with Chromium security modules
- Monitor URL navigation
- Scan downloaded scripts
- Block malicious content

### OS Integration
- System call monitoring
- Registry modification tracking
- Process execution monitoring
- File access logging

### Application Integration
- Email client plugin
- Web browser extension
- Document viewer protection
- Download manager scanning

## Future Enhancements

### Phase 2 Implementation
- [ ] Browser extension development
- [ ] Advanced ML model training
- [ ] Enterprise dashboard
- [ ] Multi-device synchronization
- [ ] Threat intelligence feeds
- [ ] Machine learning model updates
- [ ] Performance benchmarking suite
- [ ] Comprehensive testing framework

### Phase 3 Features
- [ ] Zero-day threat detection
- [ ] Predictive threat modeling
- [ ] Behavioral learning
- [ ] Collaborative threat sharing
- [ ] Advanced visualization
- [ ] Mobile device support
