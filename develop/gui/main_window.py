import customtkinter as ctk

from application.dependency_container import container

from gui.components.header import Header
from gui.components.status_panel import StatusPanel
from gui.components.activity_panel import ActivityPanel
from gui.components.action_panel import ActionPanel
from gui.components.setup_wizard_frame import (
    SetupWizardFrame,
)

from gui.theme.colors import BACKGROUND


class MainWindow(ctk.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.bus = container.get("event_bus")
        self.timer = container.get("meeting_timer")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Meeting Assistant AI")
        self.geometry("1300x800")

        self.configure(fg_color=BACKGROUND)
  
        # Status
        self.grid_rowconfigure(1, weight=0)

        # Activity (única fila que crecerá)
        self.grid_rowconfigure(2, weight=1)

        # Actions
        self.grid_rowconfigure(3, weight=0)

        self.build_ui()
        self.build_setup_wizard()
        self.subscribe_setup_wizard_events()

        # Suscripción a eventos
        self.bus.subscribe("activity", self.activity.add)
        self.bus.subscribe("meeting_started", self.on_meeting_started)
        self.bus.subscribe("meeting_finished", self.on_meeting_finished)
        self.bus.subscribe(
            "meeting_processing_started",
            lambda: self.activity.add("Procesando reunión...")
        )

        self.bus.subscribe(
            "meeting_transcribing",
            lambda: self.activity.add("Transcribiendo audio...")
        )

        self.bus.subscribe(
            "meeting_saving",
            lambda: self.activity.add("Guardando transcripción...")
        )

        self.bus.subscribe(
            "meeting_processing_completed",
            lambda session: self.activity.add(
                f"Procesamiento completado: {session.session_name}"
            )
        )

        self.bus.subscribe(
            "meeting_processing_started",
            lambda: self.status_panel.set_status(
                "processing",
                True
            )
        )

        self.bus.subscribe(
            "meeting_processing_completed",
            lambda session: self.status_panel.set_status(
                "processing",
                False
            )
        )

        self.bus.subscribe(
            "meeting_processing_failed",
            lambda error: self.activity.add(
                f"❌ Error durante el procesamiento: {error}"
            )
        )

        self.bus.subscribe(
            "meeting_processing_failed",
            lambda error: self.status_panel.set_status(
                "processing",
                False
            )
        )

        self.update_timer()

        self.after(
            200,
            self.controller.start_setup_wizard,
        )

    def build_setup_wizard(self):

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

    def subscribe_setup_wizard_events(
        self
    ):

        self.bus.subscribe(
            "setup_wizard_ui_started",
            lambda: self.after(
                0,
                self.setup_wizard.begin,
            ),
        )

        self.bus.subscribe(
            "setup_wizard_capability_started",
            lambda capability_id,
            name,
            index,
            total: self.after(
                0,
                self.setup_wizard
                .capability_started,
                capability_id,
                name,
                index,
                total,
            ),
        )

        self.bus.subscribe(
            "setup_wizard_capability_completed",
            lambda result,
            index,
            total: self.after(
                0,
                self.setup_wizard
                .capability_completed,
                result,
                index,
                total,
            ),
        )

        self.bus.subscribe(
            "setup_wizard_ui_completed",
            lambda result: self.after(
                0,
                self._on_setup_wizard_completed,
                result,
            ),
        )

        self.bus.subscribe(
            "setup_wizard_ui_failed",
            lambda error: self.after(
                0,
                self._on_setup_wizard_failed,
                error,
            ),
        )

        self.bus.subscribe(
            "setup_wizard_continue_requested",
            lambda: self.after(
                0,
                self.hide_setup_wizard,
            ),
        )

    def _on_setup_wizard_completed(
        self,
        result,
    ):

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

    def _on_setup_wizard_failed(
        self,
        error,
    ):

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

    def hide_setup_wizard(self):

        if not self.controller.state.get(
            "application_ready"
        ):

            return

        self.setup_wizard.place_forget()

    def build_ui(self):

        # Header
        self.header = Header(self)

        self.header.pack(
            fill="x",
            padx=20,
            pady=(20, 10)
        )

        # Estado
        self.status_panel = StatusPanel(self)

        self.status_panel.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

        # Actividad
        self.activity = ActivityPanel(self)

        self.activity.pack(
        fill="both",
        expand=True,
        padx=20,
        pady=(0, 20)
        )

        self.activity.add("Aplicación iniciada correctamente.")
        
        # Panel de acciones
        self.action_panel = ActionPanel(
        self,
        self.controller
        )

        self.action_panel.pack(
            fill="x",
            padx=20,
            pady=(0, 20)
        )

    def update_timer(self):

        if self.timer.running:
            value = self.timer.tick()
            self.bus.emit("timer_tick", value)

        self.after(1000, self.update_timer)
        
    def on_meeting_started(self):
        self.status_panel.set_status("meeting", True)

    def on_meeting_finished(self):
        self.status_panel.set_status("meeting", False)