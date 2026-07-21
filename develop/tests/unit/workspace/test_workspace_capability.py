from pathlib import Path

from services.setup.capabilities.capability_result import CapabilityStatus
from services.setup.capabilities.capability_runner import CapabilityRunner
from services.setup.capabilities.workspace_capability import WorkspaceCapability
from services.setup.task_result import TaskStatus


def test_workspace_capability_creates_and_cleans_workspace(
    tmp_path: Path,
) -> None:
    output_directory = tmp_path / "output"

    capability = WorkspaceCapability(
        output_directory
    )

    result = CapabilityRunner().run(
        capability
    )

    assert result.status == CapabilityStatus.AVAILABLE
    assert result.is_available is True

    assert len(result.task_results) == 2
    assert result.task_results[0].status == TaskStatus.SUCCESS
    assert result.task_results[1].status == TaskStatus.SUCCESS

    assert output_directory.exists()
    assert output_directory.is_dir()

    residual_workspaces = list(
        output_directory.glob(
            ".mai_workspace_test_*"
        )
    )

    assert residual_workspaces == []

    assert result.details["workspace_verified"] is True
    assert result.details["cleanup_completed"] is True