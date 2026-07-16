from pathlib import Path
from tempfile import TemporaryDirectory

from services.setup.setup_engine import SetupEngine
from services.setup.task_result import TaskStatus
from services.setup.tasks.initialize_output_directory_task import (
    InitializeOutputDirectoryTask,
)


with TemporaryDirectory() as temp_directory:

    occupied_path = (
        Path(temp_directory)
        / "output"
    )

    occupied_path.write_text(
        "Esta ruta es un archivo.",
        encoding="utf-8",
    )

    task = InitializeOutputDirectoryTask(
        occupied_path
    )

    engine = SetupEngine(
        tasks=[task]
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
        "no es una carpeta"
        in task_result.message
    )

    print(
        "[FAILED controlado] "
        "La ruta ocupada por un archivo "
        "fue detectada correctamente."
    )

print()
print(
    "Escenario de ruta inválida validado."
)