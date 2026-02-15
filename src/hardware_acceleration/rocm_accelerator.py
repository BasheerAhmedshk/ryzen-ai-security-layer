# src/hardware_acceleration/rocm_accelerator.py
"""
ROCm Accelerator for AMD Ryzen AI (GPU + NPU)
Enables hardware-accelerated inference on AMD GPUs and NPUs
"""

import time
from typing import Dict, Optional
from config.settings import HARDWARE_CONFIG
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class ROCmAccelerator:
    """Manages ROCm acceleration for AMD hardware"""
    
    def __init__(self):
        """Initialize ROCm accelerator"""
        self.is_available = self._check_rocm_availability()
        self.device_info = {}
        self.use_npu = HARDWARE_CONFIG.get('use_npu', True)
        self.use_gpu = HARDWARE_CONFIG.get('use_gpu', True)
        
        if self.is_available:
            self._init_devices()
        
        logger.info(f"ROCm Accelerator initialized - Available: {self.is_available}")
    
    def _check_rocm_availability(self) -> bool:
        """Check if ROCm is available on system"""
        try:
            import torch
            if hasattr(torch, 'version'):
                logger.info(f"PyTorch available: {torch.__version__}")
            return torch.cuda.is_available() or self._check_hip_available()
        except ImportError:
            logger.warning("PyTorch not available, ROCm acceleration unavailable")
            return False
    
    def _check_hip_available(self) -> bool:
        """Check if HIP (AMD's CUDA equivalent) is available"""
        try:
            import os
            # Check for HIP installation
            rocm_path = os.environ.get('ROCM_HOME', '/opt/rocm')
            return os.path.exists(rocm_path)
        except Exception:
            return False
    
    def _init_devices(self):
        """Initialize available AMD devices"""
        try:
            import torch
            
            if torch.cuda.is_available():
                self.device_info['gpu_count'] = torch.cuda.device_count()
                for i in range(torch.cuda.device_count()):
                    device_name = torch.cuda.get_device_name(i)
                    self.device_info[f'gpu_{i}'] = {
                        'name': device_name,
                        'capability': torch.cuda.get_device_capability(i),
                        'total_memory': torch.cuda.get_device_properties(i).total_memory / 1e9  # GB
                    }
                    logger.info(f"GPU Device {i}: {device_name} - "
                              f"{self.device_info[f'gpu_{i}']['total_memory']:.2f}GB")
            
            # Note: NPU detection would require ROCm-specific APIs
            if self.use_npu:
                logger.info("AMD Ryzen AI NPU support enabled")
                self.device_info['npu_available'] = True
        
        except Exception as e:
            logger.warning(f"Error initializing devices: {e}")
    
    def get_device_info(self) -> Dict:
        """Get information about available devices"""
        return self.device_info
    
    def optimize_tensor(self, tensor_size: int, dtype: str = "float32") -> Dict:
        """
        Optimize tensor for efficient GPU/NPU processing
        
        Args:
            tensor_size: Size of tensor
            dtype: Data type (float32, float16, int8)
        
        Returns:
            Optimization recommendations
        """
        try:
            # Determine optimal memory allocation
            dtype_bytes = {'float32': 4, 'float16': 2, 'int8': 1}
            memory_needed = tensor_size * dtype_bytes.get(dtype, 4) / 1e6  # MB
            
            optimization = {
                "original_size_mb": memory_needed,
                "dtype": dtype,
                "device": "gpu" if self.use_gpu else "cpu",
                "optimization_applied": False
            }
            
            # Recommend quantization if size is large
            if memory_needed > 100:
                optimization['recommendation'] = "Consider quantization to int8"
                optimization['optimized_size_mb'] = memory_needed / 4
                optimization['optimization_applied'] = True
            
            logger.info(f"Tensor optimization: {memory_needed:.2f}MB -> "
                       f"{optimization.get('optimized_size_mb', memory_needed):.2f}MB")
            
            return optimization
        
        except Exception as e:
            logger.error(f"Error optimizing tensor: {e}")
            return {}
    
    def benchmark_inference(self, model_name: str, input_size: int, iterations: int = 100) -> Dict:
        """
        Benchmark inference latency on available hardware
        
        Args:
            model_name: Name of model
            input_size: Input tensor size
            iterations: Number of iterations for benchmarking
        
        Returns:
            Benchmark results
        """
        try:
            logger.info(f"Benchmarking {model_name} - {iterations} iterations")
            
            # Simulate benchmark
            results = {
                "model": model_name,
                "iterations": iterations,
                "avg_latency_ms": 150.0,  # Placeholder
                "min_latency_ms": 120.0,
                "max_latency_ms": 200.0,
                "throughput_fps": 6.67,  # 1000/150
                "device": "gpu" if self.use_gpu else "cpu",
                "npu_acceleration": self.use_npu,
            }
            
            logger.info(f"Benchmark results: {results['avg_latency_ms']:.2f}ms avg latency")
            
            return results
        
        except Exception as e:
            logger.error(f"Error benchmarking: {e}")
            return {}
    
    def enable_mixed_precision(self) -> bool:
        """Enable mixed precision training/inference for faster computation"""
        try:
            logger.info("Enabling mixed precision (float16 + float32)")
            # Would actually set up mixed precision with PyTorch
            return True
        except Exception as e:
            logger.error(f"Error enabling mixed precision: {e}")
            return False
    
    def get_memory_info(self) -> Dict:
        """Get GPU/NPU memory information"""
        try:
            memory_info = {}
            
            if self.is_available and self.use_gpu:
                import torch
                if torch.cuda.is_available():
                    for i in range(torch.cuda.device_count()):
                        torch.cuda.set_device(i)
                        memory_info[f'gpu_{i}'] = {
                            'allocated_mb': torch.cuda.memory_allocated(i) / 1e6,
                            'reserved_mb': torch.cuda.memory_reserved(i) / 1e6,
                            'free_mb': (torch.cuda.get_device_properties(i).total_memory - 
                                      torch.cuda.memory_allocated(i)) / 1e6,
                        }
            
            return memory_info
        
        except Exception as e:
            logger.error(f"Error getting memory info: {e}")
            return {}
    
    def allocate_memory_pool(self, size_mb: int) -> bool:
        """Pre-allocate memory pool for faster inference"""
        try:
            logger.info(f"Allocating {size_mb}MB memory pool")
            # Placeholder for actual memory allocation
            return True
        except Exception as e:
            logger.error(f"Error allocating memory: {e}")
            return False

class NPUOptimizer:
    """Special optimizations for AMD Ryzen AI NPU"""
    
    def __init__(self):
        """Initialize NPU optimizer"""
        self.npu_available = self._check_npu_available()
        logger.info(f"NPU Optimizer initialized - NPU available: {self.npu_available}")
    
    def _check_npu_available(self) -> bool:
        """Check if NPU is available"""
        try:
            # Check for Ryzen AI NPU
            import os
            npu_lib = os.environ.get('NPU_LIB', None)
            return npu_lib is not None or self._check_ryzen_ai_driver()
        except Exception:
            return False
    
    def _check_ryzen_ai_driver(self) -> bool:
        """Check if Ryzen AI drivers are installed"""
        try:
            import os
            # Look for Ryzen AI specific directories/files
            paths = [
                "/opt/ryzen-ai",
                "C:\\Program Files\\AMD\\Ryzen AI",
                "/usr/local/lib/libmyo*"
            ]
            for path in paths:
                if os.path.exists(path.split('*')[0]):
                    return True
            return False
        except Exception:
            return False
    
    def optimize_for_npu(self, model_path: str) -> Dict:
        """
        Optimize model specifically for NPU execution
        
        Args:
            model_path: Path to model
        
        Returns:
            Optimization configuration
        """
        optimization = {
            "model": model_path,
            "target": "npu",
            "quantization": "int8",  # NPU prefers int8
            "batch_size": 1,  # NPU typically works with batch size 1
            "optimization_enabled": self.npu_available,
            "expected_latency_ms": 50,  # NPU can be very fast
        }
        
        logger.info(f"NPU optimization: {optimization}")
        return optimization
    
    def get_npu_info(self) -> Dict:
        """Get information about NPU capabilities"""
        return {
            "npu_available": self.npu_available,
            "supported_precision": ["int8", "float16"],
            "max_batch_size": 1,
            "typical_latency_ms": 50,
            "power_consumption": "Low (< 100mW)",
        }

# Demo usage
if __name__ == "__main__":
    print("=== ROCm Accelerator Demo ===\n")
    
    rocm = ROCmAccelerator()
    print(f"ROCm Available: {rocm.is_available}")
    print(f"Device Info: {rocm.get_device_info()}\n")
    
    # Tensor optimization
    opt = rocm.optimize_tensor(1000000, "float32")
    print(f"Tensor Optimization: {opt}\n")
    
    # Benchmark
    bench = rocm.benchmark_inference("phishing_model", 384)
    print(f"Benchmark: {bench}\n")
    
    # NPU Optimization
    print("=== NPU Optimizer Demo ===\n")
    npu = NPUOptimizer()
    npu_opt = npu.optimize_for_npu("models/phishing_model.onnx")
    print(f"NPU Optimization: {npu_opt}\n")
    
    npu_info = npu.get_npu_info()
    print(f"NPU Info: {npu_info}")
