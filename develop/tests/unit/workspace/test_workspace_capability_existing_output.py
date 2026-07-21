from pathlib import Path

from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.capabilities.workspace_capability import WorkspaceCapability
from services.setup.task_result import TaskStatus


def test_workspace_capability_uses_existing_output_directory(
    tmp_path: Path,
) -> None:
    output_directory = tmp_path / "output"
    output_directory.mkdir(parents=True)

    result = CapabilityRunner().run(
        WorkspaceCapability(
            output_directory
        )
    )

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True

    assert len(result.task_results) == 2
    assert result.task_results[0].status == TaskStatus.SKIPPED
    assert result.task_results[1].status == TaskStatus.SUCCESS

    assert result.details["output_created"] is False
    assert result.details["workspace_verified"] is True

    residual_workspaces = list(
        output_directory.glob(
            ".mai_workspace_test_*"
        )
    )

    assert residual_workspaces == []