# config/settings.py
"""
Configuration and constants for AMD Ryzen AI Security Layer
"""

import os
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
SRC_DIR = PROJECT_ROOT / "src"
MODELS_DIR = PROJECT_ROOT / "models"
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create logs directory if it doesn't exist
LOGS_DIR.mkdir(exist_ok=True)

# ============ THREAT DETECTION SETTINGS ============
DETECTION_CONFIG = {
    "phishing": {
        "model_path": str(MODELS_DIR / "phishing_model.onnx"),
        "confidence_threshold": 0.7,
        "timeout_ms": 500,
    },
    "malware": {
        "model_path": str(MODELS_DIR / "malware_model.onnx"),
        "confidence_threshold": 0.75,
        "timeout_ms": 500,
    },
    "behavior": {
        "anomaly_threshold": 0.8,
        "window_size": 100,  # number of actions to monitor
    }
}

# ============ HARDWARE ACCELERATION SETTINGS ============
HARDWARE_CONFIG = {
    "use_gpu": True,
    "use_npu": True,
    "device": "cuda",  # "cuda" for GPU, "cpu" for CPU
    "optimization_level": "O2",  # Optimization level
}

# ============ EXPLAINABILITY SETTINGS ============
EXPLAINABILITY_CONFIG = {
    "model_name": "distilbert-base-uncased",  # For NLP explanations
    "max_explanation_length": 150,
    "threat_categories": {
        "phishing": "Phishing Site",
        "malware": "Malicious Script",
        "behavioral": "Suspicious Behavior",
        "unknown": "Potential Threat"
    }
}

# ============ PRIVACY SETTINGS ============
PRIVACY_CONFIG = {
    "log_threats_locally": True,
    "encrypt_local_logs": True,
    "data_retention_days": 30,
    "cloud_sync": False,  # No cloud sync - privacy-first
}

# ============ UI/ALERT SETTINGS ============
ALERT_CONFIG = {
    "alert_timeout_seconds": 10,
    "auto_dismiss": True,
    "show_details": True,
    "alert_sound": True,
    "log_alerts": True,
}

# ============ LOGGING SETTINGS ============
LOGGING_CONFIG = {
    "level": "INFO",
    "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    "log_file": str(LOGS_DIR / "security_layer.log"),
    "max_bytes": 10485760,  # 10MB
    "backup_count": 5,
}

# ============ MODEL SETTINGS ============
MODEL_CONFIG = {
    "quantization_enabled": True,
    "quantization_type": "int8",  # int8, float16
    "batch_size": 1,
    "input_shape": (1, 384),  # Standard BERT input
}

# ============ PERFORMANCE MONITORING ============
MONITORING_CONFIG = {
    "track_latency": True,
    "track_memory": True,
    "track_gpu_usage": True,
    "sampling_interval_ms": 100,
}

# ============ DATABASE SETTINGS ============
DATABASE_CONFIG = {
    "threat_db_path": str(DATA_DIR / "threats.db"),
    "patterns_db_path": str(DATA_DIR / "phishing_patterns.json"),
    "signatures_db_path": str(DATA_DIR / "malware_signatures.json"),
}

def print_config():
    """Print all configuration settings"""
    print("=" * 60)
    print("AMD RYZEN AI SECURITY LAYER - CONFIGURATION")
    print("=" * 60)
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Models Directory: {MODELS_DIR}")
    print(f"Data Directory: {DATA_DIR}")
    print(f"Logs Directory: {LOGS_DIR}")
    print("\nDetection Thresholds:")
    print(f"  Phishing: {DETECTION_CONFIG['phishing']['confidence_threshold']}")
    print(f"  Malware: {DETECTION_CONFIG['malware']['confidence_threshold']}")
    print("\nHardware Acceleration:")
    print(f"  GPU Enabled: {HARDWARE_CONFIG['use_gpu']}")
    print(f"  NPU Enabled: {HARDWARE_CONFIG['use_npu']}")
    print(f"  Device: {HARDWARE_CONFIG['device']}")
    print("\nPrivacy Settings:")
    print(f"  Cloud Sync: {PRIVACY_CONFIG['cloud_sync']}")
    print(f"  Local Encryption: {PRIVACY_CONFIG['encrypt_local_logs']}")
    print("=" * 60)

if __name__ == "__main__":
    print_config()
