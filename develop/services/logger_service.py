"""
logger_service.py

Servicio centralizado de logging.
"""

import logging
from pathlib import Path

from application.runtime_paths import RuntimePaths


class LoggerService:

    LOGGER_NAME = "MeetingAssistantAI"
    LOG_FILENAME = "meeting_assistant.log"

    def __init__(
        self,
        runtime_paths: RuntimePaths | None = None,
    ):
        if (
            runtime_paths is not None
            and not isinstance(
                runtime_paths,
                RuntimePaths,
            )
        ):
            raise TypeError(
                "runtime_paths debe ser una "
                "instancia de RuntimePaths o None."
            )

        self.runtime_paths = (
            runtime_paths
            if runtime_paths is not None
            else RuntimePaths.resolve()
        )

        self.log_directory = (
            self.runtime_paths.logs_root
        )

        self.log_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.log_file = (
            self.log_directory
            / self.LOG_FILENAME
        )

        self.logger = logging.getLogger(
            self.LOGGER_NAME
        )

        self.logger.setLevel(
            logging.INFO
        )

        self.logger.propagate = False

        self._ensure_file_handler()

    def _ensure_file_handler(self) -> None:
        """
        Registra un FileHandler para la ruta de runtime
        únicamente cuando todavía no existe uno equivalente.
        """

        target_file = (
            self.log_file
            .resolve()
        )

        for handler in self.logger.handlers:
            if not isinstance(
                handler,
                logging.FileHandler,
            ):
                continue

            handler_file = Path(
                handler.baseFilename
            ).resolve()

            if (
                handler_file
                == target_file
            ):
                return

        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s"
        )

        file_handler = logging.FileHandler(
            self.log_file,
            encoding="utf-8",
        )

        file_handler.setFormatter(
            formatter
        )

        self.logger.addHandler(
            file_handler
        )

    def info(self, message: str):
        self.logger.info(message)

    def warning(self, message: str):
        self.logger.warning(message)

    def error(self, message: str):
        self.logger.error(message)
