// cpp/CMakeLists.txt
cmake_minimum_required(VERSION 3.15)
project(AMD_Security_Layer_CPP)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Find required packages
find_package(OpenSSL REQUIRED)
find_package(OpenMP REQUIRED)

# Add threat engine library
add_library(threat_engine_cpp SHARED
    threat_engine/phishing_detector.cpp
    threat_engine/malware_detector.cpp
    threat_engine/behavior_monitor.cpp
)

target_include_directories(threat_engine_cpp PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${OPENSSL_INCLUDE_DIR}
)

target_link_libraries(threat_engine_cpp
    ${OPENSSL_LIBRARIES}
    OpenMP::OpenMP_CXX
)

# Optimization flags for AMD Ryzen
if(CMAKE_CXX_COMPILER_ID MATCHES "GNU|Clang")
    target_compile_options(threat_engine_cpp PRIVATE
        -march=znver3  # Ryzen 5000 series optimization
        -mtune=znver3
        -O3
        -ffast-math
        -mavx2
        -mfma
    )
elseif(MSVC)
    target_compile_options(threat_engine_cpp PRIVATE
        /O2
        /arch:AVX2
    )
endif()

# Add hardware acceleration module
add_library(hardware_accel_cpp SHARED
    hardware/rocm_interface.cpp
    hardware/gpu_accelerator.cpp
    hardware/npu_optimizer.cpp
)

target_link_libraries(hardware_accel_cpp PUBLIC threat_engine_cpp)

# Enable testing
enable_testing()

# Add tests
add_executable(threat_detection_tests 
    tests/test_phishing.cpp
    tests/test_malware.cpp
)

target_link_libraries(threat_detection_tests threat_engine_cpp)
add_test(NAME ThreatDetectionTests COMMAND threat_detection_tests)

# Export library
export(TARGETS threat_engine_cpp hardware_accel_cpp
    FILE AMDSecurityLayerTargets.cmake)
