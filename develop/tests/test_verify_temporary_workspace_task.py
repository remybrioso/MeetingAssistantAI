from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)
from services.setup.tasks.verify_temporary_workspace_task import (
    VerifyTemporaryWorkspaceTask,
)


with TemporaryDirectory() as temp_directory:

    output_directory = (
        Path(temp_directory)
        / "output"
    )

    engine = SetupEngine(
        tasks=[
            InitializeOutputDirectoryTask(
                output_directory
            ),
            VerifyTemporaryWorkspaceTask(
                output_directory
            ),
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 2

    output_result = result.task_results[0]
    workspace_result = result.task_results[1]

    assert output_result.status in {
        TaskStatus.SUCCESS,
        TaskStatus.SKIPPED,
    }

    assert (
        workspace_result.status
        == TaskStatus.SUCCESS
    )

    assert result.successful

    assert (
        workspace_result.details[
            "cleanup_completed"
        ]
        is True
    )

    residual_directories = list(
        output_directory.glob(
            ".mai_workspace_test_*"
        )
    )

    assert residual_directories == []

    print(
        "[SUCCESS] Workspace temporal creado, "
        "validado y eliminado correctamente."
    )

print()
print(
    "VerifyTemporaryWorkspaceTask validada."
)