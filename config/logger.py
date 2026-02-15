# config/logger.py
"""
Logging setup for AMD Ryzen AI Security Layer
"""

import logging
import logging.handlers
from config.settings import LOGGING_CONFIG

class SecurityLogger:
    """Custom logger for the security layer"""
    
    _loggers = {}
    
    @staticmethod
    def get_logger(name):
        """Get or create a logger with the given name"""
        if name not in SecurityLogger._loggers:
            logger = logging.getLogger(name)
            logger.setLevel(getattr(logging, LOGGING_CONFIG['level']))
            
            # File handler with rotation
            file_handler = logging.handlers.RotatingFileHandler(
                LOGGING_CONFIG['log_file'],
                maxBytes=LOGGING_CONFIG['max_bytes'],
                backupCount=LOGGING_CONFIG['backup_count']
            )
            
            # Console handler
            console_handler = logging.StreamHandler()
            
            # Formatter
            formatter = logging.Formatter(LOGGING_CONFIG['format'])
            file_handler.setFormatter(formatter)
            console_handler.setFormatter(formatter)
            
            logger.addHandler(file_handler)
            logger.addHandler(console_handler)
            
            SecurityLogger._loggers[name] = logger
        
        return SecurityLogger._loggers[name]

# Initialize default logger
logger = SecurityLogger.get_logger("amd_security_layer")

if __name__ == "__main__":
    test_logger = SecurityLogger.get_logger("test")
    test_logger.info("Logger initialized successfully")
    test_logger.warning("This is a warning")
    test_logger.error("This is an error")
