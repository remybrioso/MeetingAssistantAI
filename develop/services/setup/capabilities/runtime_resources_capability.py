"""
runtime_resources_capability.py

Representa la disponibilidad de los recursos internos que deben
acompañar al runtime de Meeting Assistant AI.
"""

from application.runtime_paths import RuntimePaths
from services.setup.capabilities.capability import (
    Capability,
)
from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)
from services.setup.task_result import TaskStatus
from services.setup.tasks.runtime_resources_task import (
    RuntimeResourcesTask,
)


class RuntimeResourcesCapability(Capability):

    capability_id = "runtime-resources"
    name = "Recursos internos"
    description = (
        "Comprueba los contratos internos necesarios "
        "para procesar reuniones."
    )

    def __init__(
        self,
        runtime_paths: RuntimePaths,
        schema_loader=None,
    ) -> None:
        if not isinstance(
            runtime_paths,
            RuntimePaths,
        ):
            raise TypeError(
                "runtime_paths debe ser una "
                "instancia de RuntimePaths."
            )

        self.runtime_paths = runtime_paths
        self.schema_loader = schema_loader

    def get_tasks(self) -> list:
        return [
            RuntimeResourcesTask(
                runtime_paths=(
                    self.runtime_paths
                ),
                schema_loader=(
                    self.schema_loader
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
                status=(
                    CapabilityStatus.UNAVAILABLE
                ),
                message=(
                    "No fue posible comprobar los "
                    "recursos internos de MAI."
                ),
                details={
                    "reason": (
                        "No se recibieron resultados."
                    ),
                },
                repairable=False,
                repair_action=None,
            )

        task_result = task_results[0]

        if (
            task_result.status
            == TaskStatus.SUCCESS
        ):
            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=(
                    CapabilityStatus.AVAILABLE
                ),
                message=(
                    "Los recursos internos de MAI "
                    "están disponibles."
                ),
                task_results=task_results,
                details=dict(
                    task_result.details
                ),
                repairable=False,
                repair_action=None,
            )

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=(
                CapabilityStatus.UNAVAILABLE
            ),
            message=(
                "La instalación de MAI no contiene "
                "todos los recursos requeridos."
            ),
            task_results=task_results,
            details=dict(
                task_result.details
            ),
            repairable=True,
            repair_action=(
                "REPAIR_APPLICATION_INSTALLATION"
            ),
        )
