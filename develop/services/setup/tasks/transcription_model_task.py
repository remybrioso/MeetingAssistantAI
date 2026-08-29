"""
transcription_model_task.py

Comprueba offline que el modelo Faster-Whisper requerido por
MAI ya exista en el cache local utilizado por el proveedor.
"""

from pathlib import Path

from faster_whisper import download_model

from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class TranscriptionModelTask(SetupTask):

    task_id = "verify-transcription-model"
    name = "Verificar modelo de transcripción"
    critical = True

    def __init__(
        self,
        model_name: str,
        model_resolver=None,
    ) -> None:
        if not isinstance(
            model_name,
            str,
        ):
            raise TypeError(
                "model_name debe ser una cadena."
            )

        normalized_model = (
            model_name.strip()
        )

        if not normalized_model:
            raise ValueError(
                "model_name no puede estar vacío."
            )

        self.model_name = normalized_model

        self.model_resolver = (
            model_resolver
            if model_resolver is not None
            else download_model
        )

    def should_run(self) -> bool:
        return True

    def run(self) -> TaskResult:
        try:
            model_path = (
                self.model_resolver(
                    self.model_name,
                    local_files_only=True,
                )
            )

            resolved_path = Path(
                model_path
            )

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SUCCESS,
                message=(
                    "El modelo de transcripción "
                    "está disponible localmente."
                ),
                details={
                    "model": self.model_name,
                    "model_path": str(
                        resolved_path
                    ),
                    "local_files_only": True,
                },
            )

        except Exception as ex:
            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "El modelo de transcripción "
                    "no está disponible localmente."
                ),
                details={
                    "model": self.model_name,
                    "local_files_only": True,
                    "error_type": (
                        ex.__class__.__name__
                    ),
                },
                error=str(ex),
            )

    def verify(self) -> bool:
        return (
            self.run().status
            == TaskStatus.SUCCESS
        )
