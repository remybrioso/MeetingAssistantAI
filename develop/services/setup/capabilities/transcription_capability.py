"""
transcription_capability.py

Representa la capacidad de MAI para transcribir reuniones
mediante Faster-Whisper y el modelo configurado.
"""

from services.setup.capabilities.capability import (
    Capability,
)
from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)
from services.setup.repair_action import RepairAction
from services.setup.task_result import TaskStatus
from services.setup.tasks.transcription_model_task import (
    TranscriptionModelTask,
)


class TranscriptionCapability(Capability):

    capability_id = "transcription"
    name = "Transcripción"
    description = (
        "Comprueba que el modelo local necesario "
        "para transcribir reuniones esté disponible."
    )

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
        self.model_resolver = model_resolver

    def get_tasks(self) -> list:
        return [
            TranscriptionModelTask(
                model_name=self.model_name,
                model_resolver=(
                    self.model_resolver
                ),
            )
        ]

    def evaluate(
        self,
        task_results,
    ) -> CapabilityResult:
        if not task_results:
            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "No fue posible comprobar "
                    "la transcripción."
                ),
                details={
                    "model": self.model_name,
                    "reason": (
                        "No se recibieron resultados."
                    ),
                },
                repairable=True,
                repair_action=(
                    RepairAction
                    .DOWNLOAD_TRANSCRIPTION_MODEL
                ),
            )

        task_result = task_results[0]
        details = dict(
            task_result.details
        )

        if (
            task_result.status
            == TaskStatus.SUCCESS
        ):
            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.AVAILABLE,
                message=(
                    "MAI puede transcribir reuniones "
                    "con el modelo configurado."
                ),
                task_results=task_results,
                details=details,
                repairable=False,
                repair_action=None,
            )

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.UNAVAILABLE,
            message=(
                "El modelo de transcripción "
                "necesario no está instalado."
            ),
            task_results=task_results,
            details=details,
            repairable=True,
            repair_action=(
                RepairAction
                .DOWNLOAD_TRANSCRIPTION_MODEL
            ),
        )
