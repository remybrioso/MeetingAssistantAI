from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.verify_temporary_workspace_task import (
    VerifyTemporaryWorkspaceTask,
)


with TemporaryDirectory() as temp_directory:

    missing_output = (
        Path(temp_directory)
        / "output-inexistente"
    )

    engine = SetupEngine(
        tasks=[
            VerifyTemporaryWorkspaceTask(
                missing_output
            )
        ]
    )

    result = engine.run()

    assert len(result.task_results) == 1

    task_result = result.task_results[0]

    assert (
        task_result.status
        == TaskStatus.FAILED
    )

    assert not result.successful

    assert (
        "no existe"
        in task_result.message.lower()
    )

    assert not missing_output.exists()

    print(
        "[FAILED controlado] "
        "La carpeta de salida inexistente "
        "fue detectada correctamente."
    )

print()
print(
    "Escenario sin carpeta de salida validado."
)