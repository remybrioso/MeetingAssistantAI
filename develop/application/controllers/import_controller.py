"""
import_controller.py

Responsable de seleccionar, importar y procesar
grabaciones externas de reuniones.
"""

from pathlib import Path
from tkinter import filedialog


class ImportController:
    """
    Controlador del flujo de importación de grabaciones.
    """

    def __init__(
        self,
        state,
        bus,
        logger,
        task_runner,
        imported_meeting_service,
    ):
        self.state = state
        self.bus = bus
        self.logger = logger
        self.task_runner = task_runner
        self.imported_meeting_service = (
            imported_meeting_service
        )

    def import_recording(self):

        if not self.state.get(
            "application_ready"
        ):

            self.bus.emit(
                "activity",
                "❌ Complete primero la "
                "configuración inicial de MAI.",
            )

            return

        if self.state.get(
            "meeting_active"
        ):

            self.bus.emit(
                "activity",
                "❌ Finalice la reunión actual "
                "antes de importar un archivo.",
            )

            return

        selected_file = filedialog.askopenfilename(
            title="Seleccionar grabación WAV",
            filetypes=[
                (
                    "Archivos WAV",
                    "*.wav",
                )
            ],
        )

        if not selected_file:
            return

        source_file = Path(
            selected_file
        )

        self.logger.info(
            f"Importación iniciada: {source_file}"
        )

        self.bus.emit(
            "meeting_import_started",
            source_file.name,
        )

        self.bus.emit(
            "activity",
            f"Importando grabación: {source_file.name}",
        )

        self.task_runner.run(
            self._process_imported_recording,
            source_file,
        )

    def _process_imported_recording(
        self,
        source_file: Path,
    ):

        try:

            session = (
                self.imported_meeting_service
                .import_wav(source_file)
            )

            self.logger.info(
                "Grabación importada correctamente: "
                f"{session.session_dir}"
            )

            self.bus.emit(
                "meeting_import_completed",
                session,
            )

            self.bus.emit(
                "activity",
                "✅ Grabación importada y "
                "procesada correctamente.",
            )

        except Exception as ex:

            self.logger.error(
                f"Error importando grabación: {ex}"
            )

            self.bus.emit(
                "meeting_import_failed",
                str(ex),
            )

            self.bus.emit(
                "activity",
                f"❌ Error importando grabación: {ex}",
            )