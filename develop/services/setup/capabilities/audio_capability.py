"""
audio_capability.py

Representa la capacidad de MAI para capturar
el audio necesario durante una reunión.
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
from services.setup.tasks.audio_health_task import (
    AudioHealthTask,
)


class AudioCapability(Capability):

    capability_id = "audio"
    name = "Audio de reuniones"
    description = (
        "Permite capturar la voz del usuario y "
        "el audio reproducido por el equipo."
    )

    def __init__(
        self,
        audio_health_service=None
    ):

        self.audio_health_service = (
            audio_health_service
        )

    def get_tasks(self) -> list:

        return [
            AudioHealthTask(
                self.audio_health_service
            )
        ]

    def evaluate(
        self,
        task_results
    ) -> CapabilityResult:

        if not task_results:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "No fue posible comprobar "
                    "los dispositivos de audio."
                ),
                details={
                    "reason": (
                        "No se recibieron resultados."
                    ),
                },
                repairable=True,
                repair_action=RepairAction.REPAIR_AUDIO_DEVICES,
            )

        task_result = task_results[0]
        details = dict(
            task_result.details
        )

        microphone_available = details.get(
            "microphone_available",
            False,
        )

        system_audio_available = details.get(
            "system_audio_available",
            False,
        )

        if not microphone_available:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "MAI necesita un micrófono "
                    "para capturar la reunión."
                ),
                task_results=task_results,
                details=details,
                repairable=True,
                repair_action=RepairAction.CONFIGURE_MICROPHONE,
            )

        if not system_audio_available:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.DEGRADED,
                message=(
                    "El micrófono está disponible, "
                    "pero MAI no puede capturar el "
                    "audio del sistema."
                ),
                task_results=task_results,
                details=details,
                repairable=True,
                repair_action=RepairAction.CONFIGURE_SYSTEM_AUDIO,
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
                    "MAI puede capturar el micrófono "
                    "y el audio del sistema."
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
                "La configuración de audio "
                "requiere atención."
            ),
            task_results=task_results,
            details=details,
            repairable=True,
            repair_action=RepairAction.REPAIR_AUDIO_DEVICES,
        )
