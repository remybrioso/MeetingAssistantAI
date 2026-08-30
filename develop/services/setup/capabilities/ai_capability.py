"""
ai_capability.py

Representa la capacidad de MAI para procesar
reuniones mediante inteligencia artificial.
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
from services.setup.tasks.ai_provider_health_task import (
    AIProviderHealthTask,
)


class AICapability(Capability):

    capability_id = "artificial-intelligence"
    name = "Inteligencia artificial"
    description = (
        "Permite generar resúmenes y conocimiento "
        "a partir de las reuniones."
    )

    def __init__(self, provider):

        self.provider = provider

    def get_tasks(self) -> list:

        return [
            AIProviderHealthTask(
                self.provider
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
                    "No fue posible comprobar la "
                    "inteligencia artificial."
                ),
                details={
                    "reason": (
                        "No se recibieron resultados."
                    ),
                },
                repairable=True,
                repair_action=RepairAction.REPAIR_AI_CAPABILITY,
            )

        task_result = task_results[0]
        details = dict(
            task_result.details
        )

        if task_result.status in {
            TaskStatus.SUCCESS,
            TaskStatus.SKIPPED,
        }:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.AVAILABLE,
                message=(
                    "MAI puede generar resúmenes "
                    "y conocimiento correctamente."
                ),
                task_results=task_results,
                details=details,
                repairable=False,
                repair_action=None,
            )

        connected = details.get(
            "connected",
            False
        )

        model_found = details.get(
            "model_found",
            False
        )

        if not connected:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "El motor de inteligencia artificial "
                    "necesita instalarse o iniciarse."
                ),
                task_results=task_results,
                details=details,
                repairable=True,
                repair_action=RepairAction.INSTALL_AI_PROVIDER,
            )

        if not model_found:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "El modelo de inteligencia artificial "
                    "necesario no está instalado."
                ),
                task_results=task_results,
                details=details,
                repairable=True,
                repair_action=RepairAction.DOWNLOAD_AI_MODEL,
            )

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.UNAVAILABLE,
            message=(
                "La inteligencia artificial requiere "
                "atención."
            ),
            task_results=task_results,
            details=details,
            repairable=True,
            repair_action=RepairAction.REPAIR_AI_CAPABILITY,
        )
