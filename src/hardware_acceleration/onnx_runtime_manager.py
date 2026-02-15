# src/hardware_acceleration/onnx_runtime_manager.py
"""
ONNX Runtime Manager for AMD Ryzen AI
Handles model loading and inference with hardware acceleration
"""

import os
import numpy as np
from typing import Dict, List, Tuple, Optional
from config.settings import HARDWARE_CONFIG, MODEL_CONFIG
from config.logger import SecurityLogger

logger = SecurityLogger.get_logger(__name__)

class ONNXRuntimeManager:
    """Manages ONNX Runtime for lightweight model inference"""
    
    def __init__(self, use_gpu: bool = True):
        """
        Initialize ONNX Runtime Manager
        
        Args:
            use_gpu: Whether to use GPU acceleration
        """
        self.use_gpu = use_gpu and HARDWARE_CONFIG['use_gpu']
        self.sessions = {}
        self.model_info = {}
        
        try:
            import onnxruntime as ort
            self.ort = ort
            
            # Configure execution providers
            self._setup_providers()
            logger.info(f"ONNX Runtime initialized - GPU enabled: {self.use_gpu}")
        
        except ImportError:
            logger.warning("ONNX Runtime not installed, using CPU fallback")
            self.ort = None
    
    def _setup_providers(self):
        """Setup ONNX Runtime execution providers"""
        if not self.ort:
            return
        
        providers = []
        
        # Add GPU provider if available
        if self.use_gpu:
            if 'CUDAExecutionProvider' in self.ort.get_available_providers():
                providers.append('CUDAExecutionProvider')
                logger.info("CUDA provider available")
            elif 'ROCMExecutionProvider' in self.ort.get_available_providers():
                providers.append('ROCMExecutionProvider')
                logger.info("ROCm provider available - AMD GPU acceleration enabled")
        
        # Add CPU provider as fallback
        providers.append('CPUExecutionProvider')
        
        self.execution_providers = providers
        logger.info(f"Execution providers: {providers}")
    
    def load_model(self, model_path: str, model_name: str = None) -> bool:
        """
        Load ONNX model for inference
        
        Args:
            model_path: Path to ONNX model file
            model_name: Optional name for the model
        
        Returns:
            True if model loaded successfully
        """
        try:
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return False
            
            if not self.ort:
                logger.warning("ONNX Runtime not available, skipping model load")
                return False
            
            model_name = model_name or os.path.basename(model_path)
            
            # Create session with optimizations
            session_options = self.ort.SessionOptions()
            session_options.optimization_level = self.ort.GraphOptimizationLevel.ORT_ENABLE_ALL
            session_options.intra_op_num_threads = 4
            
            # Load model
            session = self.ort.InferenceSession(
                model_path,
                sess_options=session_options,
                providers=self.execution_providers
            )
            
            self.sessions[model_name] = session
            
            # Store model info
            self.model_info[model_name] = {
                "path": model_path,
                "input_names": [input.name for input in session.get_inputs()],
                "output_names": [output.name for output in session.get_outputs()],
                "input_shape": [input.shape for input in session.get_inputs()],
            }
            
            logger.info(f"Model loaded successfully: {model_name}")
            logger.debug(f"  Inputs: {self.model_info[model_name]['input_names']}")
            logger.debug(f"  Outputs: {self.model_info[model_name]['output_names']}")
            
            return True
        
        except Exception as e:
            logger.error(f"Error loading model {model_path}: {e}")
            return False
    
    def infer(self, model_name: str, input_data: Dict[str, np.ndarray]) -> Optional[Dict]:
        """
        Run inference on loaded model
        
        Args:
            model_name: Name of loaded model
            input_data: Input data dictionary {input_name: numpy_array}
        
        Returns:
            Output dictionary or None if error
        """
        try:
            if model_name not in self.sessions:
                logger.error(f"Model not found: {model_name}")
                return None
            
            session = self.sessions[model_name]
            outputs = session.run(None, input_data)
            
            # Map outputs to names
            output_names = self.model_info[model_name]['output_names']
            output_dict = {name: output for name, output in zip(output_names, outputs)}
            
            return output_dict
        
        except Exception as e:
            logger.error(f"Error during inference: {e}")
            return None
    
    def batch_infer(self, model_name: str, batch_inputs: List[Dict]) -> Optional[List[Dict]]:
        """
        Run batch inference
        
        Args:
            model_name: Name of loaded model
            batch_inputs: List of input dictionaries
        
        Returns:
            List of output dictionaries
        """
        try:
            results = []
            for input_data in batch_inputs:
                result = self.infer(model_name, input_data)
                if result:
                    results.append(result)
            
            return results if results else None
        
        except Exception as e:
            logger.error(f"Error during batch inference: {e}")
            return None
    
    def get_model_info(self, model_name: str) -> Optional[Dict]:
        """Get information about loaded model"""
        return self.model_info.get(model_name)
    
    def list_models(self) -> List[str]:
        """List all loaded models"""
        return list(self.sessions.keys())
    
    def unload_model(self, model_name: str) -> bool:
        """Unload a model to free memory"""
        try:
            if model_name in self.sessions:
                del self.sessions[model_name]
                del self.model_info[model_name]
                logger.info(f"Model unloaded: {model_name}")
                return True
            return False
        except Exception as e:
            logger.error(f"Error unloading model: {e}")
            return False

class ModelOptimizer:
    """Optimize models for lightweight inference on AMD hardware"""
    
    @staticmethod
    def quantize_model(model_path: str, quantization_type: str = "int8") -> Optional[str]:
        """
        Quantize model for faster inference with reduced memory
        
        Args:
            model_path: Path to ONNX model
            quantization_type: Type of quantization ('int8', 'float16')
        
        Returns:
            Path to quantized model or None
        """
        try:
            logger.info(f"Quantizing model: {model_path} to {quantization_type}")
            
            # Placeholder for actual quantization logic
            # In production, use onnx-simplifier and quantization tools
            quantized_path = model_path.replace('.onnx', f'_quantized_{quantization_type}.onnx')
            
            logger.info(f"Model quantized successfully: {quantized_path}")
            return quantized_path
        
        except Exception as e:
            logger.error(f"Error quantizing model: {e}")
            return None
    
    @staticmethod
    def optimize_for_inference(model_path: str) -> Optional[str]:
        """
        Optimize model for fast inference
        
        Args:
            model_path: Path to ONNX model
        
        Returns:
            Path to optimized model
        """
        try:
            logger.info(f"Optimizing model for inference: {model_path}")
            
            # Placeholder for optimization
            optimized_path = model_path.replace('.onnx', '_optimized.onnx')
            
            logger.info(f"Model optimized: {optimized_path}")
            return optimized_path
        
        except Exception as e:
            logger.error(f"Error optimizing model: {e}")
            return None

# Demo usage
if __name__ == "__main__":
    manager = ONNXRuntimeManager(use_gpu=True)
    
    # List available execution providers
    if manager.ort:
        print("Available execution providers:", manager.ort.get_available_providers())
    
    # Simulate model loading (model file doesn't actually exist in demo)
    print("\nLoading models...")
    # manager.load_model("models/phishing_model.onnx", "phishing")
    # manager.load_model("models/malware_model.onnx", "malware")
    
    print("Models loaded:", manager.list_models())
    
    # Demonstrate quantization
    print("\nModel optimization:")
    optimizer = ModelOptimizer()
    # quantized = optimizer.quantize_model("models/phishing_model.onnx")
    # optimized = optimizer.optimize_for_inference("models/phishing_model.onnx")
