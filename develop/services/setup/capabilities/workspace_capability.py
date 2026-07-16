"""
workspace_capability.py

Representa la capacidad de MAI para crear,
escribir y organizar reuniones.
"""

from pathlib import Path

from services.setup.capabilities.capability import (
    Capability,
)
from services.setup.capabilities.capability_result import (
    CapabilityResult,
    CapabilityStatus,
)
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)
from services.setup.tasks.verify_temporary_workspace_task import (
    VerifyTemporaryWorkspaceTask,
)


class WorkspaceCapability(Capability):

    capability_id = "workspace"
    name = "Almacenamiento de reuniones"
    description = (
        "Permite crear, escribir y organizar "
        "los archivos de las reuniones."
    )

    def __init__(
        self,
        output_directory,
        workspace_service=None
    ):

        self.output_directory = Path(
            output_directory
        ).expanduser()

        self.workspace_service = workspace_service

    def get_tasks(self) -> list:

        return [
            InitializeOutputDirectoryTask(
                self.output_directory
            ),
            VerifyTemporaryWorkspaceTask(
                output_directory=self.output_directory,
                workspace_service=self.workspace_service,
            ),
        ]

    def evaluate(
        self,
        task_results
    ) -> CapabilityResult:

        details = {
            "output_directory": str(
                self.output_directory.absolute()
            ),
            "tasks_executed": len(task_results),
        }

        if not task_results:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "No fue posible comprobar el "
                    "almacenamiento de reuniones."
                ),
                task_results=[],
                details={
                    **details,
                    "reason": (
                        "No se recibieron resultados "
                        "de las tareas."
                    ),
                },
                repairable=True,
                repair_action=(
                    "REPAIR_WORKSPACE"
                ),
            )

        failed_results = [
            result
            for result in task_results
            if result.status == TaskStatus.FAILED
        ]

        if failed_results:

            failed_task = failed_results[0]

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "MAI no puede utilizar correctamente "
                    "la carpeta de reuniones."
                ),
                task_results=task_results,
                details={
                    **details,
                    "failed_task": (
                        failed_task.task_id
                    ),
                    "error": failed_task.error,
                },
                repairable=True,
                repair_action=(
                    "REPAIR_WORKSPACE"
                ),
            )

        workspace_verified = any(
            result.task_id
            == "verify-temporary-workspace"
            and result.status
            == TaskStatus.SUCCESS
            for result in task_results
        )

        if not workspace_verified:

            return CapabilityResult(
                capability_id=self.capability_id,
                name=self.name,
                status=CapabilityStatus.UNAVAILABLE,
                message=(
                    "La carpeta de reuniones está disponible, "
                    "pero no se pudo verificar el Workspace."
                ),
                task_results=task_results,
                details={
                    **details,
                    "workspace_verified": False,
                },
                repairable=True,
                repair_action=(
                    "REPAIR_WORKSPACE"
                ),
            )

        output_task = next(
            (
                result
                for result in task_results
                if result.task_id
                == "initialize-output-directory"
            ),
            None,
        )

        output_created = bool(
            output_task
            and output_task.details.get(
                "created",
                False
            )
        )

        return CapabilityResult(
            capability_id=self.capability_id,
            name=self.name,
            status=CapabilityStatus.AVAILABLE,
            message=(
                "MAI puede crear, escribir y organizar "
                "reuniones correctamente."
            ),
            task_results=task_results,
            details={
                **details,
                "output_created": output_created,
                "workspace_verified": True,
                "cleanup_completed": True,
            },
            repairable=False,
            repair_action=None,
        )