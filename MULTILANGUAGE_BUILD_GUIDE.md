# MULTILANGUAGE_BUILD_GUIDE.md
# AMD Ryzen AI Security Layer - Multi-Language Build Guide

## 🎯 Quick Start (5 Minutes)

### Option 1: Docker Compose (Recommended)

```bash
# Clone/extract project
cd amd_security_layer

# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

### Option 2: Individual Components

Jump to the section below for your preferred language.

---

## 🐍 Python Setup (Main Orchestrator)

### Prerequisites
- Python 3.9+
- pip/venv

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run demos
python demos/demo_phishing_detection.py
python demos/threat_alert_demo.py
```

### Verify Installation

```bash
python -c "from src.security_core.threat_engine import ThreatEngine; print('✅ Python setup OK')"
```

---

## 🚀 C++ Setup (Performance Engine)

### Prerequisites
- GCC 9+ or Clang 11+
- CMake 3.15+
- OpenSSL development files
- OpenMP

### Installation (Linux/macOS)

```bash
# Install dependencies
# Ubuntu/Debian
sudo apt-get install build-essential cmake libssl-dev libomp-dev

# macOS
brew install cmake openssl libomp

# Build C++ components
cd cpp
mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release \
      -DCMAKE_CXX_FLAGS="-march=znver3" ..
make -j$(nproc)
cd ../..
```

### Installation (Windows)

```bash
# Install Visual Studio 2022 (with C++ tools)
# Install CMake from cmake.org
# Install OpenSSL from slproweb.com

cd cpp
mkdir build
cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
cmake --build . --config Release --parallel
```

### Verify Installation

```bash
cd cpp/build
ctest --output-on-failure
```

### Test C++ Directly

```cpp
// cpp/test_phishing.cpp
#include "threat_engine/phishing_detector.hpp"
#include <iostream>

int main() {
    amd_security::threat_detection::PhishingDetector detector;
    auto result = detector.detect("https://paypa1.com");
    std::cout << "Phishing: " << result.is_phishing << std::endl;
    std::cout << "Confidence: " << result.confidence << std::endl;
    return 0;
}
```

---

## ☕ Java Setup (Enterprise Service)

### Prerequisites
- Java 17+
- Maven 3.8+

### Installation

```bash
# Check Java version
java -version  # Should be 17+
mvn -version   # Should be 3.8+

# Build Java service
cd java/enterprise
mvn clean package

# Create uber JAR with dependencies
mvn assembly:assembly -DdescriptorId=jar-with-dependencies
```

### Run Java Service

```bash
cd java/enterprise

# Run directly
mvn exec:java -Dexec.mainClass="com.amd.security.ThreatDetectionService"

# Run compiled JAR
java -jar target/security-layer-java-1.0.0-jar-with-dependencies.jar
```

### Verify Installation

```bash
# Run tests
mvn test

# Should see output like:
# [INFO] -------------------------------------------------------
# [INFO]  T E S T S
# [INFO] -------------------------------------------------------
# [INFO] Running com.amd.security.ThreatDetectionServiceTest
# [INFO] Tests run: 10, Failures: 0, Errors: 0, Skipped: 0
```

---

## 🦀 Rust Setup (API Backend)

### Prerequisites
- Rust 1.70+
- Cargo

### Installation

```bash
# Install Rust (if not already installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
source $HOME/.cargo/env

# Build Rust API
cd rust/api
cargo build --release

# Output: target/release/amd-security-api
```

### Run Rust API

```bash
cd rust/api
RUST_LOG=info cargo run --release

# Server running at http://localhost:8080
```

### Verify Installation

```bash
# In another terminal
curl http://localhost:8080/api/health

# Should return:
# {"status":"healthy","version":"1.0.0","timestamp":"..."}
```

### Test Rust API

```bash
# Single detection
curl -X POST http://localhost:8080/api/detect \
  -H "Content-Type: application/json" \
  -d '{"threat_type":"url","content":"https://example.com"}'

# Batch detection
curl -X POST http://localhost:8080/api/detect/batch \
  -H "Content-Type: application/json" \
  -d '{
    "threats": [
      {"threat_type":"url","content":"https://url1.com"},
      {"threat_type":"code","content":"eval(...)"}
    ]
  }'

# Statistics
curl http://localhost:8080/api/stats
```

---

## 🐳 Docker Setup

### Build All Images

```bash
# Build with docker-compose (automatic)
docker-compose build

# Or manually build individual images
docker build -t amd-security:python -f Dockerfile.python .
docker build -t amd-security:rust rust/api/
docker build -t amd-security:java java/enterprise/
docker build -t amd-security:cpp cpp/
```

### Run Services

```bash
# Start all services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f rust-api
docker-compose logs -f python-service
docker-compose logs -f java-service

# Stop all services
docker-compose down
```

### Test Services

```bash
# Test API
curl http://localhost:8080/api/health

# Test Python service
curl http://localhost:5000/health

# Test Java service
curl http://localhost:9090/health
```

---

## 🔄 Integration Testing

### Test All Components Together

```python
# test_integration.py
import requests
import time

def test_integration():
    # Test Rust API
    response = requests.post('http://localhost:8080/api/detect',
        json={'threat_type': 'url', 'content': 'https://example.com'})
    assert response.status_code == 200
    print("✅ Rust API OK")
    
    # Test Python service
    response = requests.get('http://localhost:5000/health')
    assert response.status_code == 200
    print("✅ Python service OK")
    
    # Test Java service
    response = requests.get('http://localhost:9090/health')
    assert response.status_code == 200
    print("✅ Java service OK")
    
    print("\n✅ All services healthy!")

if __name__ == '__main__':
    test_integration()
```

Run it:
```bash
python test_integration.py
```

---

## 📊 Performance Benchmarking

### Benchmark All Components

```bash
# Python benchmark
python -m pytest tests/benchmark_python.py -v

# C++ benchmark
cd cpp/build && ./benchmark_cpp

# Java benchmark
cd java/enterprise && mvn test -Dtest=*Benchmark

# Rust benchmark
cd rust/api && cargo bench
```

### Expected Results

```
Component | Single    | Batch (10) | Throughput
───────────────────────────────────────────────
Python    | 120ms     | 1.2s       | 8 ops/sec
C++       | 50ms      | 500ms      | 20 ops/sec
Java      | 100ms     | 1s         | 10 ops/sec
Rust API  | <10ms     | <100ms     | 100+ ops/sec
```

---

## 🔧 Development Workflow

### Making Changes to C++

1. Edit `cpp/threat_engine/phishing_detector.cpp`
2. Rebuild:
   ```bash
   cd cpp/build
   make
   ```
3. Test: `ctest`
4. Python will use updated library automatically

### Making Changes to Java

1. Edit `java/enterprise/src/main/java/com/amd/security/*.java`
2. Rebuild:
   ```bash
   mvn clean package
   ```
3. Test: `mvn test`
4. Deploy: `docker-compose up --build java-service`

### Making Changes to Rust

1. Edit `rust/api/src/main.rs`
2. Rebuild:
   ```bash
   cargo build --release
   ```
3. Test: `cargo test`
4. Deploy: `docker-compose up --build rust-api`

### Making Changes to Python

1. Edit Python files in `src/`
2. Restart Python service:
   ```bash
   python demos/demo_phishing_detection.py
   ```
   Or:
   ```bash
   docker-compose restart python-service
   ```

---

## 📈 Scaling

### Single Machine

Run docker-compose as-is. Scales to ~100 requests/sec.

### Multiple Machines (Kubernetes)

```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: amd-security
spec:
  replicas: 3
  selector:
    matchLabels:
      app: amd-security
  template:
    metadata:
      labels:
        app: amd-security
    spec:
      containers:
      - name: rust-api
        image: amd-security:rust-latest
        ports:
        - containerPort: 8080
        resources:
          limits:
            cpu: "2"
            memory: "1Gi"
```

Deploy:
```bash
kubectl apply -f k8s/deployment.yaml
```

---

## 🚨 Troubleshooting

### C++ Build Fails

```bash
# Check compiler
g++ --version  # Should be 9+

# Check CMake
cmake --version  # Should be 3.15+

# Check OpenSSL
pkg-config --modversion openssl

# Clean and rebuild
rm -rf cpp/build
cd cpp && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release ..
make -j$(nproc)
```

### Java Build Fails

```bash
# Check Java
java -version  # Should be 17+

# Check Maven
mvn -version  # Should be 3.8+

# Clear Maven cache
rm -rf ~/.m2/repository/com/amd

# Rebuild
mvn clean package -X
```

### Rust Build Fails

```bash
# Update Rust
rustup update

# Clean build
cd rust/api
cargo clean
cargo build --release
```

### Docker Issues

```bash
# Check Docker
docker --version
docker-compose --version

# Rebuild images
docker-compose build --no-cache

# View logs
docker-compose logs --tail=100
```

---

## 📝 Configuration

### C++ (CMAKE)

```bash
# Optimization level
-DCMAKE_BUILD_TYPE=Release  # Or Debug

# CPU target
-DCMAKE_CXX_FLAGS="-march=znver3"  # For Ryzen 5000

# Compiler
-DCMAKE_CXX_COMPILER=clang++
```

### Java (pom.xml)

```xml
<maven.compiler.source>17</maven.compiler.source>
<maven.compiler.target>17</maven.compiler.target>
```

### Rust (Cargo.toml)

```toml
[profile.release]
opt-level = 3
lto = true
codegen-units = 1
```

### Python (config/settings.py)

```python
DETECTION_CONFIG = {
    "phishing": {
        "confidence_threshold": 0.7,
    },
    ...
}
```

---

## ✅ Verification Checklist

- [ ] Python installation: `python -c "from src.security_core.threat_engine import ThreatEngine"`
- [ ] C++ build: `cd cpp/build && ctest`
- [ ] Java build: `mvn test -DskipIntegrationTests`
- [ ] Rust build: `cargo test`
- [ ] Docker: `docker-compose up -d && docker-compose ps`
- [ ] All services healthy: Run `test_integration.py`
- [ ] Demo: `python demos/demo_phishing_detection.py`

---

## 📚 Additional Resources

- **C++ Guide**: See `docs/MULTILANG_ARCHITECTURE.md` (C++ section)
- **Java Guide**: See `java/enterprise/README.md`
- **Rust Guide**: See `rust/api/README.md`
- **Architecture**: See `docs/MULTILANG_ARCHITECTURE.md`
- **Docker**: See `docker-compose.yml`

---

## 🎉 You're Ready!

All components are now set up. Start with:

```bash
# Option 1: Docker (easiest)
docker-compose up -d

# Option 2: Individual components
python demos/demo_phishing_detection.py  # Terminal 1
cd rust/api && cargo run --release        # Terminal 2
cd java/enterprise && mvn exec:java       # Terminal 3
```

**Next Steps**:
1. Read `docs/MULTILANG_ARCHITECTURE.md` for system design
2. Review individual language guides for development
3. Run integration tests
4. Deploy to your environment

Good luck! 🚀
