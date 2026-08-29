"""
runtime_paths.py

Resuelve las rutas de ejecución de Meeting Assistant AI sin
depender del current working directory.
"""

from dataclasses import dataclass
from pathlib import Path
import sys

from platformdirs import (
    user_data_path,
    user_documents_path,
    user_log_path,
)

from application.app_info import APP_NAME


@dataclass(frozen=True)
class RuntimePaths:
    """
    Rutas canónicas utilizadas durante la ejecución de MAI.
    """

    resource_root: Path
    user_data_root: Path
    meetings_root: Path
    logs_root: Path
    frozen: bool

    @classmethod
    def resolve(
        cls,
        *,
        resource_root: Path | None = None,
        user_data_root: Path | None = None,
        meetings_root: Path | None = None,
        logs_root: Path | None = None,
    ) -> "RuntimePaths":
        resolved_resource_root = (
            cls._normalize_override(
                resource_root,
                "resource_root",
            )
            if resource_root is not None
            else cls._default_resource_root()
        )

        resolved_user_data_root = (
            cls._normalize_override(
                user_data_root,
                "user_data_root",
            )
            if user_data_root is not None
            else Path(
                user_data_path(
                    APP_NAME,
                    appauthor=False,
                )
            ).resolve()
        )

        resolved_meetings_root = (
            cls._normalize_override(
                meetings_root,
                "meetings_root",
            )
            if meetings_root is not None
            else (
                Path(
                    user_documents_path()
                )
                / APP_NAME
                / "Meetings"
            ).resolve()
        )

        resolved_logs_root = (
            cls._normalize_override(
                logs_root,
                "logs_root",
            )
            if logs_root is not None
            else Path(
                user_log_path(
                    APP_NAME,
                    appauthor=False,
                )
            ).resolve()
        )

        return cls(
            resource_root=resolved_resource_root,
            user_data_root=resolved_user_data_root,
            meetings_root=resolved_meetings_root,
            logs_root=resolved_logs_root,
            frozen=bool(
                getattr(
                    sys,
                    "frozen",
                    False,
                )
            ),
        )

    @property
    def prompts_directory(self) -> Path:
        """
        Directorio de plantillas de prompt incluidas con MAI.
        """
        return (
            self.resource_root
            / "prompts"
        )

    @property
    def schemas_directory(self) -> Path:
        """
        Directorio de contratos JSON Schema incluidos con MAI.
        """
        return (
            self.prompts_directory
            / "schemas"
        )

    @property
    def models_directory(self) -> Path:
        return (
            self.user_data_root
            / "models"
        )

    def ensure_user_directories(self) -> None:
        for directory in (
            self.user_data_root,
            self.meetings_root,
            self.logs_root,
            self.models_directory,
        ):
            directory.mkdir(
                parents=True,
                exist_ok=True,
            )

    @staticmethod
    def _default_resource_root() -> Path:
        return (
            Path(__file__)
            .resolve()
            .parents[1]
        )

    @staticmethod
    def _normalize_override(
        value: Path,
        name: str,
    ) -> Path:
        if not isinstance(
            value,
            Path,
        ):
            raise TypeError(
                f"{name} debe ser una instancia de Path."
            )

        return value.resolve()
