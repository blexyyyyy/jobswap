import logging
import sys
import os

def check_logging():
    """Confirms logging is working."""
    logger = logging.getLogger("jobswap")
    logger.info("Logging initialized.")

def get_logger(name: str) -> logging.Logger:
    """Returns a configured logger instance."""
    logger = logging.getLogger(name)
    
    # If logger is already configured, don't reconfigure
    if logger.handlers:
        return logger
        
    logger.setLevel(logging.INFO)
    
    # JSON formatter could be added here later as per checklist, but standard is requested for now.
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console Handler
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(formatter)
    ch.setLevel(logging.INFO)
    
    logger.addHandler(ch)
    
    return logger

# Create main application logger
logger = get_logger("jobswap")
