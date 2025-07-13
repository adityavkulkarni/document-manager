import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from sys import prefix

from ..config import Config


class AppLogger:
    def __init__(self, name='AppLogger', log_dir=Config.LOG_DIRECTORY, log_file='app.log', level=logging.INFO, prefix=""):
        """
        Initialize the logger.
        :param name: Name of the logger.
        :param log_dir: Directory where log files will be stored.
        :param log_file: Name of the log file.
        :param level: Logging level.
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        self._setup_handlers(log_dir, log_file, level, prefix)

    def _setup_handlers(self, log_dir, log_file, level, prefix):
        # Ensure log directory exists
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(message)s'+prefix)

        # File handler with rotation
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, log_file),
            maxBytes=1_048_576,
            backupCount=5
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(level)
        self.logger.addHandler(file_handler)

        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        console_handler.setLevel(level)
        self.logger.addHandler(console_handler)

    def get_logger(self):
        return self.logger

# Example usage
if __name__ == "__main__":
    logger = AppLogger().get_logger()
    logger.info("This is an info message.")
    logger.error("This is an error message.")
