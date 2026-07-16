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

    output_directory.mkdir(
        parents=True
    )

    capability = WorkspaceCapability(
        output_directory
    )

    result = CapabilityRunner().run(
        capability
    )

    assert (
        result.status
        == CapabilityStatus.AVAILABLE
    )

    assert len(result.task_results) == 2

    assert (
        result.task_results[0].status
        == TaskStatus.SKIPPED
    )

    assert (
        result.task_results[1].status
        == TaskStatus.SUCCESS
    )

    assert (
        result.details[
            "output_created"
        ]
        is False
    )

    assert (
        result.details[
            "workspace_verified"
        ]
        is True
    )

    residual_workspaces = list(
        output_directory.glob(
            ".mai_workspace_test_*"
        )
    )

    assert residual_workspaces == []

    print(
        "[AVAILABLE] La carpeta existente "
        "y el Workspace fueron validados."
    )

print()
print(
    "Escenario con output existente validado."
)