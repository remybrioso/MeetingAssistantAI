from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)


with TemporaryDirectory() as temp_directory:

    test_output = (
        Path(temp_directory)
        / "mai-output"
    )

    task = InitializeOutputDirectoryTask(
        test_output
    )

    engine = SetupEngine(
        tasks=[task]
    )

    first_result = engine.run()

    assert len(first_result.task_results) == 1

    first_task_result = (
        first_result.task_results[0]
    )

    assert (
        first_task_result.status
        == TaskStatus.SUCCESS
    )

    assert test_output.exists()
    assert test_output.is_dir()
    assert first_result.successful

    temporary_files = list(
        test_output.glob(
            ".mai_write_test_*.tmp"
        )
    )

    assert temporary_files == []

    print(
        "[SUCCESS] La carpeta fue creada "
        "y validada correctamente."
    )

    second_result = engine.run()

    second_task_result = (
        second_result.task_results[0]
    )

    assert (
        second_task_result.status
        == TaskStatus.SKIPPED
    )

    assert second_result.successful

    temporary_files = list(
        test_output.glob(
            ".mai_write_test_*.tmp"
        )
    )

    assert temporary_files == []

    print(
        "[SKIPPED] La carpeta existente "
        "fue reconocida correctamente."
    )

print()
print(
    "InitializeOutputDirectoryTask validada."
)