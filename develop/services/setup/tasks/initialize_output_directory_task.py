"""
initialize_output_directory_task.py

Prepara y valida la carpeta base donde MAI
almacenará los Workspaces de las reuniones.
"""

from pathlib import Path
from uuid import uuid4

from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)


class InitializeOutputDirectoryTask(SetupTask):

    task_id = "initialize-output-directory"
    name = "Preparar carpeta de reuniones"
    critical = True

    def __init__(self, output_directory):

        self.output_directory = Path(
            output_directory
        ).expanduser()

    def should_run(self) -> bool:
        """
        Siempre se ejecuta para comprobar que la carpeta
        continúa disponible y admite escritura.

        La propia tarea devuelve SKIPPED cuando no necesita
        realizar ninguna reparación.
        """

        return True

    def run(self) -> TaskResult:

        try:
            if (
                self.output_directory.exists()
                and not self.output_directory.is_dir()
            ):

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "La ruta de salida existe, "
                        "pero no es una carpeta."
                    ),
                    details={
                        "path": str(
                            self.output_directory.resolve()
                        ),
                    },
                    error=(
                        "La ruta está ocupada por un archivo."
                    ),
                )

            directory_created = False

            if not self.output_directory.exists():

                self.output_directory.mkdir(
                    parents=True,
                    exist_ok=True,
                )

                directory_created = True

            self._verify_read_write_access()

            if directory_created:

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.SUCCESS,
                    message=(
                        "La carpeta de reuniones fue creada "
                        "y validada correctamente."
                    ),
                    details={
                        "path": str(
                            self.output_directory.resolve()
                        ),
                        "created": True,
                        "writable": True,
                    },
                    verification_required=True,
                )

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SKIPPED,
                message=(
                    "La carpeta de reuniones ya existe "
                    "y está disponible."
                ),
                details={
                    "path": str(
                        self.output_directory.resolve()
                    ),
                    "created": False,
                    "writable": True,
                },
            )

        except Exception as ex:

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "No fue posible preparar la carpeta "
                    "de reuniones."
                ),
                details={
                    "path": str(
                        self.output_directory.absolute()
                    ),
                },
                error=str(ex),
            )

    def verify(self) -> bool:

        try:
            if not self.output_directory.is_dir():
                return False

            self._verify_read_write_access()

            return True

        except Exception:
            return False

    def _verify_read_write_access(self) -> None:

        temporary_file = (
            self.output_directory
            / f".mai_write_test_{uuid4().hex}.tmp"
        )

        expected_content = (
            "Meeting Assistant AI write test"
        )

        try:
            temporary_file.write_text(
                expected_content,
                encoding="utf-8",
            )

            actual_content = temporary_file.read_text(
                encoding="utf-8",
            )

            if actual_content != expected_content:

                raise OSError(
                    "La validación de lectura devolvió "
                    "un contenido inesperado."
                )

        finally:
            if temporary_file.exists():
                temporary_file.unlink()