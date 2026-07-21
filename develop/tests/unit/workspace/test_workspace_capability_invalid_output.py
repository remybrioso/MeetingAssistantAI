from pathlib import Path

from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.capabilities.workspace_capability import WorkspaceCapability
from services.setup.task_result import TaskStatus


def test_workspace_capability_fails_with_invalid_output_path(
    tmp_path: Path,
) -> None:
    invalid_output = tmp_path / "output"

    invalid_output.write_text(
        "Esta ruta está ocupada por un archivo.",
        encoding="utf-8",
    )

    result = CapabilityRunner().run(
        WorkspaceCapability(
            invalid_output
        )
    )

    assert result.status == CapabilityStatus.UNAVAILABLE
    assert result.is_available is False
    assert result.repairable is True
    assert result.repair_action == "REPAIR_WORKSPACE"

    # La primera tarea es crítica, por lo que
    # SetupEngine debe detener el flujo.
    assert len(result.task_results) == 1
    assert result.task_results[0].status == TaskStatus.FAILED

    assert (
        result.details["failed_task"]
        == "initialize-output-directory"
    )