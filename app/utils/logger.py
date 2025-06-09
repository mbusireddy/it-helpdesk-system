from loguru import logger
import sys
from app.utils.config import settings  # Import application settings

# First, remove the default Loguru logger to fully customize the configuration
logger.remove()

# Add a new log handler to output logs to the console (stdout)
logger.add(
    sys.stdout,  # Stream output to standard console
    level=settings.log_level,  # Use the logging level from settings (e.g., INFO, DEBUG)
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>"
    # This colorful and structured format includes:
    # - Timestamp in green
    # - Log level padded to 8 characters
    # - Source filename, function, and line number in cyan
    # - The log message itself in level-dependent color
)

# Add another handler to write logs into a file
logger.add(
    "logs/helpdesk.log",  # File path where logs will be saved
    rotation="1 day",     # Automatically create a new log file every day
    retention="30 days",  # Keep log files for 30 days, delete older ones
    level=settings.log_level,  # Use log level from settings
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}"
    # This is a file-friendly format (no colors), with structured info:
    # - Timestamp
    # - Log level
    # - File name, function, line number
    # - Message
)
