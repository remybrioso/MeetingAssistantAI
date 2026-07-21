import pytest

from services.configuration_service import ConfigurationService
from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)


@pytest.mark.integration
def test_real_output_directory_can_be_initialized() -> None:
    configuration = ConfigurationService()

    engine = SetupEngine(
        tasks=[
            InitializeOutputDirectoryTask(
                configuration.output_directory
            )
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 1

    task_result = result.task_results[0]

    if task_result.status == TaskStatus.SKIPPED:
        pytest.skip(task_result.message)

    assert result.successful is True