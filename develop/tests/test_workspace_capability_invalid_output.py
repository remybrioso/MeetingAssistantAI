from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.capabilities.workspace_capability import (
    WorkspaceCapability,
)
from services.setup.task_result import TaskStatus


with TemporaryDirectory() as temp_directory:

    invalid_output = (
        Path(temp_directory)
        / "output"
    )

    invalid_output.write_text(
        "Esta ruta está ocupada por un archivo.",
        encoding="utf-8",
    )

    capability = WorkspaceCapability(
        invalid_output
    )

    result = CapabilityRunner().run(
        capability
    )

    assert (
        result.status
        == CapabilityStatus.UNAVAILABLE
    )

    assert not result.is_available
    assert result.repairable

    assert (
        result.repair_action
        == "REPAIR_WORKSPACE"
    )

    # La primera tarea es crítica, por lo que
    # SetupEngine debe detener el flujo.
    assert len(result.task_results) == 1

    assert (
        result.task_results[0].status
        == TaskStatus.FAILED
    )

    assert (
        result.details[
            "failed_task"
        ]
        == "initialize-output-directory"
    )

    print(
        "[UNAVAILABLE] La ruta inválida "
        "fue detectada correctamente."
    )

    print(
        f"Acción propuesta: "
        f"{result.repair_action}"
    )

print()
print(
    "Escenario inválido de Workspace validado."
)