import logging
from logging.handlers import RotatingFileHandler
import sys
import os

# Ensure logs directory exists
LOG_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
os.makedirs(LOG_DIR, exist_ok=True)

# Path to the log file
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logger(name: str) -> logging.Logger:
    """
    Sets up a custom logger configured to output to both the terminal and a file.
    """
    logger = logging.getLogger(name)
    
    # Set base level for the logger
    logger.setLevel(logging.INFO)
    
    # Prevent this logger from propagating logs to the root logger.
    # Uvicorn configures the root logger in an aggressive way which often
    # hides custom formatting or prevents terminal output when running via `python -m uvicorn`.
    logger.propagate = False
    
    # Avoid adding handlers multiple times if `setup_logger` is called more than once
    if not logger.handlers:
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

        # 1. File Handler (Rotating to avoid massive log files)
        # Keeps up to 5 backups of 10MB each
        file_handler = RotatingFileHandler(
            LOG_FILE, maxBytes=10*1024*1024, backupCount=5, encoding="utf-8"
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        # 2. Terminal (Stream) Handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
