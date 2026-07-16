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

    output_directory = (
        Path(temp_directory)
        / "output"
    )

    capability = WorkspaceCapability(
        output_directory
    )

    runner = CapabilityRunner()

    result = runner.run(
        capability
    )

    print("=" * 60)
    print("MAI WORKSPACE CAPABILITY")
    print("=" * 60)

    print(f"Capacidad: {result.name}")
    print(f"Estado: {result.status.value}")
    print(f"Mensaje: {result.message}")

    print()

    for task_result in result.task_results:

        print(
            f"[{task_result.status.value}] "
            f"{task_result.name}"
        )

        print(
            f"  {task_result.message}"
        )

        if task_result.error:
            print(
                f"  Error: {task_result.error}"
            )

    assert (
        result.status
        == CapabilityStatus.AVAILABLE
    )

    assert result.is_available

    assert len(result.task_results) == 2

    assert (
        result.task_results[0].status
        == TaskStatus.SUCCESS
    )

    assert (
        result.task_results[1].status
        == TaskStatus.SUCCESS
    )

    assert output_directory.exists()
    assert output_directory.is_dir()

    residual_workspaces = list(
        output_directory.glob(
            ".mai_workspace_test_*"
        )
    )

    assert residual_workspaces == []

    assert (
        result.details[
            "workspace_verified"
        ]
        is True
    )

    assert (
        result.details[
            "cleanup_completed"
        ]
        is True
    )

print()
print(
    "WorkspaceCapability validada correctamente."
)