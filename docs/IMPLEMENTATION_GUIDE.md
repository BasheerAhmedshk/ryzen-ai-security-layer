# docs/IMPLEMENTATION_GUIDE.md
# Implementation Guide - Phase 2: Completing the Security Layer

## Overview

This guide covers the remaining implementation tasks to complete the AMD Ryzen AI Security Layer. Phase 1 has completed approximately 50% of the project, focusing on core threat detection and explanation systems. Phase 2 will focus on UI, integration, testing, and optimization.

## Phase 2 Tasks

### 1. User Interface Development [20% Effort]

#### 1.1 Desktop Alert UI (`src/ui/alert_ui.py`)

**Objective**: Create cross-platform desktop alert notifications

**Implementation Steps**:

```python
# Use PyQt5 or tkinter for cross-platform compatibility
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer

class AlertWindow:
    def __init__(self, alert):
        # Create alert popup window
        # Display threat type, confidence, message
        # Show action buttons (Block, Details, Dismiss)
        # Auto-dismiss after timeout
        pass
```

**Features to Implement**:
- [ ] Multi-monitor support
- [ ] Always-on-top alerts
- [ ] Customizable severity colors
- [ ] Sound notifications
- [ ] Action button callbacks
- [ ] Detailed threat view
- [ ] History panel

#### 1.2 Settings UI (`src/ui/settings_ui.py`)

**Objective**: Create settings and configuration panel

**Features**:
- [ ] Enable/disable detectors
- [ ] Adjust confidence thresholds
- [ ] Configure alert behavior
- [ ] Review threat history
- [ ] Export/import settings
- [ ] Theme customization

### 2. Model Integration [25% Effort]

#### 2.1 Real ONNX Model Implementation

**Objective**: Integrate actual trained ML models

**Tasks**:
- [ ] Download/train phishing detection models
- [ ] Download/train malware detection models
- [ ] Convert to ONNX format
- [ ] Test model accuracy
- [ ] Optimize for inference
- [ ] Create model versioning system

**Models to Integrate**:
```python
# In src/hardware_acceleration/model_manager.py
class ModelManager:
    def __init__(self):
        self.models = {
            'phishing': load_phishing_model(),
            'malware': load_malware_model(),
            'behavior': load_behavior_model()
        }
    
    def predict(self, model_name, input_data):
        # Use actual ML models instead of heuristics
        pass
```

#### 2.2 Model Training Pipeline

**Objective**: Set up model training infrastructure

**Components**:
- [ ] Dataset preparation
- [ ] Feature engineering
- [ ] Model training scripts
- [ ] Validation pipeline
- [ ] Performance metrics
- [ ] Model versioning

### 3. Testing & Validation [20% Effort]

#### 3.1 Unit Tests

**Location**: `tests/test_threat_detection.py`

```python
import unittest
from src.threat_detection.phishing_detector import PhishingDetector

class TestPhishingDetector(unittest.TestCase):
    def test_legitimate_url(self):
        # Test legitimate URLs
        pass
    
    def test_phishing_url(self):
        # Test phishing URLs
        pass
    
    def test_confidence_scores(self):
        # Validate confidence score ranges
        pass
```

**Test Categories**:
- [ ] Unit tests for each detector
- [ ] Integration tests
- [ ] Performance tests
- [ ] Edge case handling
- [ ] Error recovery

#### 3.2 Performance Benchmarking

**Location**: `tests/test_hardware_acceleration.py`

```python
def benchmark_latency():
    # Measure detection latency
    # Verify < 500ms target
    pass

def benchmark_throughput():
    # Measure detections per second
    pass

def benchmark_memory():
    # Track memory usage
    pass
```

### 4. Browser Integration [15% Effort]

#### 4.1 Browser Extension Development

**Objective**: Create Chromium-based extension

**Structure**:
```
browser_extension/
├── manifest.json
├── popup.html
├── popup.css
├── popup.js
├── content_script.js
├── background.js
└── images/
```

**Features**:
- [ ] URL scanning on navigation
- [ ] Real-time threat detection
- [ ] Alert popups
- [ ] Block dangerous URLs
- [ ] Settings panel
- [ ] History view

#### 4.2 Browser Hook Integration

**In `src/security_core/browser_integration.py`**:
```python
class BrowserIntegration:
    def scan_url(self, url):
        # Scan URL before navigation
        pass
    
    def scan_downloaded_file(self, file_path):
        # Scan downloaded files
        pass
    
    def monitor_scripts(self, script_content):
        # Monitor injected scripts
        pass
```

### 5. Database & Logging [10% Effort]

#### 5.1 Threat Database

**Objective**: Implement local threat database

**Location**: `src/security_core/threat_database.py`

```python
class ThreatDatabase:
    def __init__(self):
        self.db = sqlite3.connect('threats.db')
        self.create_tables()
    
    def log_threat(self, threat_data):
        # Store threat information
        pass
    
    def query_threats(self, filters):
        # Query threat history
        pass
    
    def update_threat_status(self, threat_id, status):
        # Update threat handling status
        pass
```

**Tables to Create**:
- [ ] threats (id, type, confidence, timestamp, details)
- [ ] alerts (id, threat_id, user_action, timestamp)
- [ ] actions (id, alert_id, action_type, timestamp)
- [ ] statistics (date, detection_count, threat_types)

#### 5.2 Analytics & Reporting

**Location**: `src/security_core/analytics.py`

```python
class Analytics:
    def generate_daily_report(self):
        # Create daily threat summary
        pass
    
    def generate_weekly_report(self):
        # Create weekly analysis
        pass
    
    def export_statistics(self):
        # Export threat statistics
        pass
```

### 6. System Integration [10% Effort]

#### 6.1 Service Installation

**Windows**: `install_windows.py`
- [ ] Register as Windows Defender antimalware service
- [ ] Add to startup
- [ ] System tray integration
- [ ] Driver installation if needed

**Linux**: `install_linux.py`
- [ ] Systemd service registration
- [ ] Startup scripts
- [ ] File permissions
- [ ] User/group setup

**macOS**: `install_macos.py`
- [ ] Launchd plist creation
- [ ] Code signing
- [ ] System Extension registration
- [ ] Privacy permissions

## Development Roadmap

### Week 1: UI Development
- [ ] Create alert window UI
- [ ] Implement settings panel
- [ ] Add system tray integration
- [ ] Test on multiple platforms

### Week 2: Model Integration
- [ ] Download pre-trained models
- [ ] Convert to ONNX format
- [ ] Integration testing
- [ ] Performance validation

### Week 3: Testing
- [ ] Write unit tests
- [ ] Benchmark performance
- [ ] Test edge cases
- [ ] Documentation

### Week 4: Browser Extension
- [ ] Create extension structure
- [ ] Implement content scripts
- [ ] Add detection logic
- [ ] Store submission

### Week 5: Database & Analytics
- [ ] Set up SQLite database
- [ ] Implement logging
- [ ] Create report generation
- [ ] Export functionality

### Week 6: System Integration & Polish
- [ ] OS-specific installers
- [ ] Service registration
- [ ] Final testing
- [ ] Documentation completion

## Code Examples for Phase 2

### Example 1: Real Model Integration

```python
# In src/hardware_acceleration/model_manager.py
import onnxruntime as ort
import numpy as np

class ModelManager:
    def __init__(self):
        # Load actual ML models
        self.session_phishing = ort.InferenceSession('models/phishing_model.onnx')
        self.session_malware = ort.InferenceSession('models/malware_model.onnx')
    
    def predict_phishing(self, url_features):
        input_name = self.session_phishing.get_inputs()[0].name
        results = self.session_phishing.run(None, {input_name: url_features})
        return results[0][0]  # Confidence score
```

### Example 2: Browser Extension Content Script

```javascript
// In browser_extension/content_script.js
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === 'scanURL') {
        scanUrl(request.url).then(result => {
            sendResponse({threat: result});
        });
    }
});

function scanUrl(url) {
    return fetch(`http://localhost:5000/scan`, {
        method: 'POST',
        body: JSON.stringify({url: url})
    }).then(r => r.json());
}
```

### Example 3: Threat Database Schema

```python
# In src/security_core/threat_database.py
import sqlite3

def create_tables(db):
    cursor = db.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS threats (
            id INTEGER PRIMARY KEY,
            threat_type TEXT,
            confidence REAL,
            timestamp DATETIME,
            details TEXT,
            user_action TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS statistics (
            date DATE,
            detection_count INTEGER,
            phishing_count INTEGER,
            malware_count INTEGER,
            anomaly_count INTEGER
        )
    ''')
    
    db.commit()
```

## Testing Checklist

- [ ] All unit tests pass
- [ ] Integration tests pass
- [ ] Performance tests meet < 500ms target
- [ ] Memory usage < 200MB
- [ ] CPU usage < 20% under load
- [ ] Browser extension works on Chrome/Firefox/Edge
- [ ] Settings persist across restarts
- [ ] Alerts display correctly on multiple monitors
- [ ] Database exports are valid
- [ ] All platforms (Windows/Linux/macOS) supported

## Success Criteria

✅ **Core Functionality**
- Sub-500ms threat detection latency
- 90%+ phishing detection accuracy
- 85%+ malware detection accuracy

✅ **User Experience**
- Clear threat alerts
- Easy settings configuration
- Intuitive action buttons

✅ **Performance**
- < 200MB memory usage
- < 5% CPU idle
- < 20% CPU active

✅ **Reliability**
- 99.9% uptime
- Automatic error recovery
- Comprehensive logging

## Resources

- **ONNX Model Zoo**: https://github.com/onnx/models
- **PyQt5 Documentation**: https://www.riverbankcomputing.com/software/pyqt/
- **Chrome Extension Dev**: https://developer.chrome.com/docs/extensions/
- **ROCm Documentation**: https://rocmdocs.amd.com/

## Conclusion

Completing Phase 2 will result in a production-ready security layer that can be deployed to end-users. The focus is on real-world usability, performance, and integration with existing systems.
