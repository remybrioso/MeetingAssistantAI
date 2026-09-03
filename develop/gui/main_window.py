import customtkinter as ctk

from application.dependency_container import container
from exceptions.insufficient_meeting_evidence_error import (
    InsufficientMeetingEvidenceError,
)
from exceptions.insufficient_meeting_semantic_evidence_error import (
    InsufficientMeetingSemanticEvidenceError,
)
from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from gui.ui_event_dispatcher import UIEventDispatcher
from gui.components.header import Header
from gui.components.status_panel import StatusPanel
from gui.components.activity_panel import ActivityPanel
from gui.components.action_panel import ActionPanel
from gui.components.setup_wizard_frame import SetupWizardFrame
from gui.theme.colors import BACKGROUND


class MainWindow(ctk.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.bus = container.get("event_bus")
        self.timer = container.get("meeting_timer")

        # El dispatcher debe existir antes de construir los paneles,
        # porque StatusPanel y ActionPanel lo reciben en su constructor.
        self.ui_events = UIEventDispatcher(
            widget=self,
            event_bus=self.bus,
        )

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Meeting Assistant AI")
        self.geometry("1300x800")
        self.configure(fg_color=BACKGROUND)

        self.build_ui()
        self.build_setup_wizard()
        self.subscribe_events()
        self.subscribe_setup_wizard_events()

        # El procesamiento de la cola comienza después de crear
        # todos los widgets y registrar todas las suscripciones.
        self.ui_events.start()

        self.protocol(
            "WM_DELETE_WINDOW",
            self.on_close,
        )

        self.update_timer()

        self.after(
            200,
            self.controller.start_setup_wizard,
        )

    def subscribe_events(self) -> None:

        self.ui_events.subscribe(
            "activity",
            self.activity.add,
        )

        self.ui_events.subscribe(
            "meeting_started",
            self.on_meeting_started,
        )

        self.ui_events.subscribe(
            "meeting_finished",
            self.on_meeting_finished,
        )

        self.ui_events.subscribe(
            "meeting_processing_started",
            lambda: self.activity.add(
                "Procesando reunión..."
            ),
        )

        self.ui_events.subscribe(
            "meeting_transcribing",
            lambda: self.activity.add(
                "Transcribiendo audio..."
            ),
        )

        self.ui_events.subscribe(
            "meeting_saving",
            lambda: self.activity.add(
                "Guardando transcripción..."
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_completed",
            lambda session: self.activity.add(
                "Procesamiento completado: "
                f"{session.session_name}"
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_started",
            lambda: self.status_panel.set_status(
                "processing",
                True,
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_completed",
            lambda session: self.status_panel.set_status(
                "processing",
                False,
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_failed",
            lambda error: self.activity.add(
                "❌ Error durante el procesamiento: "
                f"{error}"
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_failed",
            lambda error: self.status_panel.set_status(
                "processing",
                False,
            ),
        )

        self.ui_events.subscribe(
            "meeting_processing_insufficient_evidence",
            self._on_meeting_processing_insufficient_evidence,
        )

        self.ui_events.subscribe(
            "meeting_import_insufficient_evidence",
            self._on_meeting_import_insufficient_evidence,
        )

    def _on_meeting_processing_insufficient_evidence(
        self,
        error: InsufficientMeetingEvidenceError,
    ) -> None:
        self._show_insufficient_evidence_warning(
            error
        )
        self.status_panel.set_status(
            "processing",
            False,
        )

    def _on_meeting_import_insufficient_evidence(
        self,
        error: InsufficientMeetingEvidenceError,
    ) -> None:
        self._show_insufficient_evidence_warning(
            error
        )

    def _show_insufficient_evidence_warning(
        self,
        error: InsufficientMeetingEvidenceError,
    ) -> None:
        self.activity.add(
            self._insufficient_evidence_message(
                error
            )
        )

    @staticmethod
    def _insufficient_evidence_message(
        error: InsufficientMeetingEvidenceError,
    ) -> str:
        if not isinstance(
            error,
            InsufficientMeetingEvidenceError,
        ):
            raise TypeError(
                "error debe ser una instancia de "
                "InsufficientMeetingEvidenceError."
            )

        if isinstance(
            error,
            InsufficientTranscriptEvidenceError,
        ):
            return (
                "⚠️ Audio y transcripción guardados. "
                "No se generó una minuta porque la "
                "transcripción no contiene suficiente "
                "contenido utilizable."
            )

        if isinstance(
            error,
            InsufficientMeetingSemanticEvidenceError,
        ):
            return (
                "⚠️ Audio y transcripción guardados. "
                "No se generó una minuta porque el "
                "contenido no contiene suficiente evidencia "
                "de una reunión."
            )

        return (
            "⚠️ Audio y transcripción guardados. "
            "No se generó una minuta porque no existe "
            "evidencia suficiente para producir un reporte útil."
        )

    def build_setup_wizard(self) -> None:

        self.setup_wizard = SetupWizardFrame(
            self,
            self.controller,
        )

        self.setup_wizard.place(
            relx=0,
            rely=0,
            relwidth=1,
            relheight=1,
        )

        self.setup_wizard.lift()

    def subscribe_setup_wizard_events(self) -> None:

        self.ui_events.subscribe(
            "setup_wizard_ui_started",
            self.setup_wizard.begin,
        )

        self.ui_events.subscribe(
            "setup_wizard_capability_started",
            self.setup_wizard.capability_started,
        )

        self.ui_events.subscribe(
            "setup_wizard_capability_completed",
            self.setup_wizard.capability_completed,
        )

        self.ui_events.subscribe(
            "setup_wizard_ui_completed",
            self._on_setup_wizard_completed,
        )

        self.ui_events.subscribe(
            "setup_wizard_ui_failed",
            self._on_setup_wizard_failed,
        )

        self.ui_events.subscribe(
            "setup_wizard_continue_requested",
            self.hide_setup_wizard,
        )

        self.ui_events.subscribe(
            "setup_repair_ui_started",
            self.setup_wizard.repair_started,
        )

        self.ui_events.subscribe(
            "setup_repair_ui_completed",
            self.setup_wizard.repair_completed,
        )

        self.ui_events.subscribe(
            "setup_repair_ui_unavailable",
            self.setup_wizard.repair_unavailable,
        )

        self.ui_events.subscribe(
            "setup_repair_ui_failed",
            self.setup_wizard.repair_failed,
        )

    def _on_setup_wizard_completed(self, result) -> None:

        self.controller.accept_setup_wizard_result(
            result
        )

        self.setup_wizard.show_result(
            result
        )

        if result.is_ready:

            self.after(
                600,
                self.hide_setup_wizard,
            )

            self.activity.add(
                "✅ MAI está configurado "
                "y listo para trabajar."
            )

        elif result.has_attention_items:

            self.activity.add(
                "⚠️ MAI puede funcionar, pero "
                "algunas capacidades requieren atención."
            )

        else:

            self.activity.add(
                "❌ MAI requiere configuración "
                "antes de iniciar una reunión."
            )

    def _on_setup_wizard_failed(self, error) -> None:

        self.controller.state.set(
            "setup_wizard_status",
            "failed",
        )

        self.controller.state.set(
            "setup_wizard_completed",
            True,
        )

        self.controller.state.set(
            "application_ready",
            False,
        )

        self.setup_wizard.show_failure(
            error
        )

        self.activity.add(
            "❌ Error en la comprobación "
            f"inicial: {error}"
        )

    def hide_setup_wizard(self) -> None:

        if not self.controller.state.get(
            "application_ready"
        ):
            return

        self.setup_wizard.place_forget()

    def build_ui(self) -> None:

        # Header
        self.header = Header(self)

        self.header.pack(
            fill="x",
            padx=20,
            pady=(20, 10),
        )

        # Estado
        self.status_panel = StatusPanel(
            self,
            self.ui_events,
        )

        self.status_panel.pack(
            fill="x",
            padx=20,
            pady=(0, 20),
        )

        # Actividad
        self.activity = ActivityPanel(self)

        self.activity.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20),
        )

        self.activity.add(
            "Aplicación iniciada correctamente."
        )

        # Panel de acciones
        self.action_panel = ActionPanel(
            self,
            self.controller,
            self.ui_events,
        )

        self.action_panel.pack(
            fill="x",
            padx=20,
            pady=(0, 20),
        )

    def update_timer(self) -> None:

        if self.timer.running:
            value = self.timer.tick()
            self.bus.emit(
                "timer_tick",
                value,
            )

        self.after(
            1000,
            self.update_timer,
        )

    def on_meeting_started(self) -> None:
        self.status_panel.set_status(
            "meeting",
            True,
        )

    def on_meeting_finished(self) -> None:
        self.status_panel.set_status(
            "meeting",
            False,
        )

    def on_close(self) -> None:
        self.ui_events.stop()
        self.destroy()
