"""
logger_service.py

Servicio centralizado de logging.
"""

import logging
from pathlib import Path


class LoggerService:

    def __init__(self):

        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)

        self.logger = logging.getLogger("MeetingAssistantAI")
        self.logger.setLevel(logging.INFO)

        if not self.logger.handlers:

            formatter = logging.Formatter(
                "%(asctime)s | %(levelname)s | %(message)s"
            )

            file_handler = logging.FileHandler(
                log_dir / "meeting_assistant.log",
                encoding="utf-8"
            )

            file_handler.setFormatter(formatter)

            self.logger.addHandler(file_handler)

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)