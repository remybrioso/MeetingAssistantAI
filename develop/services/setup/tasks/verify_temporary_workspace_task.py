"""
verify_temporary_workspace_task.py

Comprueba que MAI puede crear, utilizar y eliminar
un MeetingWorkspace temporal.
"""

import json
import shutil
from pathlib import Path
from uuid import uuid4

from services.setup.setup_task import SetupTask
from services.setup.task_result import (
    TaskResult,
    TaskStatus,
)
from services.workspace_service import WorkspaceService


class VerifyTemporaryWorkspaceTask(SetupTask):

    task_id = "verify-temporary-workspace"
    name = "Verificar Workspace"
    critical = True

    def __init__(
        self,
        output_directory,
        workspace_service=None
    ):

        self.output_directory = Path(
            output_directory
        ).expanduser()

        self.workspace_service = (
            workspace_service or WorkspaceService()
        )

        self.temporary_root = None

    def should_run(self) -> bool:
        """
        La comprobación debe ejecutarse cada vez que se
        valide o repare el entorno.
        """
        return True

    def run(self) -> TaskResult:

        workspace = None

        self.temporary_root = (
            self.output_directory
            / f".mai_workspace_test_{uuid4().hex}"
        )

        try:
            if not self.output_directory.exists():

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "La carpeta de reuniones no existe."
                    ),
                    details={
                        "output_directory": str(
                            self.output_directory.absolute()
                        ),
                    },
                    error=(
                        "Ejecute primero la tarea de "
                        "inicialización de la carpeta de salida."
                    ),
                )

            if not self.output_directory.is_dir():

                return TaskResult(
                    task_id=self.task_id,
                    name=self.name,
                    status=TaskStatus.FAILED,
                    message=(
                        "La ruta de salida no es una carpeta."
                    ),
                    details={
                        "output_directory": str(
                            self.output_directory.absolute()
                        ),
                    },
                )

            workspace = self.workspace_service.create(
                self.temporary_root
            )

            self._validate_structure(workspace)
            self._validate_manifest(workspace)
            self._validate_workspace_write_access(
                workspace
            )

            details = {
                "output_directory": str(
                    self.output_directory.resolve()
                ),
                "temporary_workspace": str(
                    self.temporary_root.resolve()
                ),
                "audio_directory": str(
                    workspace.audio_dir.resolve()
                ),
                "documents_directory": str(
                    workspace.documents_dir.resolve()
                ),
                "internal_directory": str(
                    workspace.internal_dir.resolve()
                ),
                "manifest": str(
                    workspace.workspace_manifest.resolve()
                ),
                "cleanup_completed": False,
            }

            self._cleanup()

            details["cleanup_completed"] = True

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.SUCCESS,
                message=(
                    "El Workspace fue creado, validado "
                    "y eliminado correctamente."
                ),
                details=details,
                verification_required=True,
            )

        except Exception as ex:

            self._cleanup()

            return TaskResult(
                task_id=self.task_id,
                name=self.name,
                status=TaskStatus.FAILED,
                message=(
                    "No fue posible validar el Workspace."
                ),
                details={
                    "output_directory": str(
                        self.output_directory.absolute()
                    ),
                    "temporary_workspace": (
                        str(self.temporary_root.absolute())
                        if self.temporary_root
                        else None
                    ),
                    "cleanup_completed": (
                        not self._temporary_root_exists()
                    ),
                },
                error=str(ex),
            )

    def verify(self) -> bool:
        """
        Confirma que la carpeta temporal ya no existe.
        """

        return not self._temporary_root_exists()

    def _validate_structure(self, workspace) -> None:

        required_directories = [
            workspace.root_dir,
            workspace.audio_dir,
            workspace.documents_dir,
            workspace.internal_dir,
        ]

        for directory in required_directories:

            if not directory.exists():

                raise FileNotFoundError(
                    f"No se creó la carpeta requerida: "
                    f"{directory}"
                )

            if not directory.is_dir():

                raise NotADirectoryError(
                    f"La ruta no es una carpeta: "
                    f"{directory}"
                )

    def _validate_manifest(self, workspace) -> None:

        manifest = workspace.workspace_manifest

        if not manifest.exists():

            raise FileNotFoundError(
                "No se creó workspace.json."
            )

        if not manifest.is_file():

            raise ValueError(
                "workspace.json no es un archivo válido."
            )

        with open(
            manifest,
            "r",
            encoding="utf-8"
        ) as file:

            data = json.load(file)

        if data.get("version") != workspace.version:

            raise ValueError(
                "La versión del manifiesto no coincide "
                "con la versión del Workspace."
            )

        structure = data.get(
            "structure",
            {}
        )

        expected_paths = {
            "audio": str(workspace.audio_dir),
            "documents": str(
                workspace.documents_dir
            ),
            "internal": str(
                workspace.internal_dir
            ),
        }

        for key, expected_value in (
            expected_paths.items()
        ):

            if structure.get(key) != expected_value:

                raise ValueError(
                    "El manifiesto contiene una ruta "
                    f"incorrecta para '{key}'."
                )

    def _validate_workspace_write_access(
        self,
        workspace
    ) -> None:

        test_targets = [
            workspace.audio_dir,
            workspace.documents_dir,
            workspace.internal_dir,
        ]

        for target_directory in test_targets:

            test_file = (
                target_directory
                / f".mai_test_{uuid4().hex}.tmp"
            )

            expected_content = (
                "Meeting Assistant AI workspace test"
            )

            try:
                test_file.write_text(
                    expected_content,
                    encoding="utf-8",
                )

                actual_content = (
                    test_file.read_text(
                        encoding="utf-8",
                    )
                )

                if actual_content != expected_content:

                    raise OSError(
                        "La lectura del archivo temporal "
                        "no devolvió el contenido esperado."
                    )

            finally:
                if test_file.exists():
                    test_file.unlink()

    def _cleanup(self) -> None:

        if (
            self.temporary_root
            and self.temporary_root.exists()
        ):

            shutil.rmtree(
                self.temporary_root
            )

    def _temporary_root_exists(self) -> bool:

        return bool(
            self.temporary_root
            and self.temporary_root.exists()
        )