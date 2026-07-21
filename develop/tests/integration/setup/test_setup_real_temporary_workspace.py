from pathlib import Path

import pytest

from services.configuration_service import ConfigurationService
from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)
from services.setup.tasks.verify_temporary_workspace_task import (
    VerifyTemporaryWorkspaceTask,
)


@pytest.mark.integration
def test_real_temporary_workspace_is_verified_without_residue() -> None:
    configuration = ConfigurationService()

    output_directory = Path(configuration.output_directory)

    engine = SetupEngine(
        tasks=[
            InitializeOutputDirectoryTask(output_directory),
            VerifyTemporaryWorkspaceTask(output_directory),
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 2

    initialize_result = result.task_results[0]
    workspace_result = result.task_results[1]

    assert initialize_result.status in {
        TaskStatus.SUCCESS,
        TaskStatus.SKIPPED,
    }

    assert workspace_result.status == TaskStatus.SUCCESS
    assert result.successful is True

    residual_directories = list(
        output_directory.glob(".mai_workspace_test_*")
    )

    assert residual_directories == []