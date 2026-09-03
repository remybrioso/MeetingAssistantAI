import customtkinter as ctk


from gui.theme.colors import SURFACE, BORDER
from gui.theme.fonts import SUBTITLE


class ActionPanel(ctk.CTkFrame):

    def __init__(self, master, controller, ui_events):
        super().__init__(
            master,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=10
        )

        self.controller = controller
        self.ui_events = ui_events


        self._build_ui()
        self._bind_events()
        self._set_initial_state()

    def _build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Acciones",
            font=SUBTITLE
        )
        title.pack(anchor="w", padx=20, pady=(15, 10))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(fill="x", padx=20, pady=(0, 20))

        self.btn_start = ctk.CTkButton(
            buttons,
            text="▶ Iniciar",
            width=150,
            command=self.controller.start_meeting
        )
        self.btn_start.pack(side="left", padx=8)

        self.btn_pause = ctk.CTkButton(
            buttons,
            text="⏸ Pausar",
            width=150,
            command=self.controller.pause_meeting
        )
        self.btn_pause.pack(side="left", padx=8)

        self.btn_resume = ctk.CTkButton(
            buttons,
            text="▶ Reanudar",
            width=150,
            command=self.controller.resume_meeting
        )
        self.btn_resume.pack(side="left", padx=8)

        self.btn_stop = ctk.CTkButton(
            buttons,
            text="⏹ Finalizar",
            width=150,
            command=self.controller.stop_meeting
        )
        self.btn_stop.pack(side="left", padx=8)

        self.btn_import = ctk.CTkButton(
            buttons,
            text="📂 Importar grabación",
            width=170,
            command=self.controller.import_recording
        )

        self.btn_import.pack(
            side="left",
            padx=8
        )

        self.btn_export = ctk.CTkButton(
            buttons,
            text="📄 Exportar",
            width=150,
            state="disabled"
        )
        self.btn_export.pack(side="left", padx=8)

    def _bind_events(self):

        self.ui_events.subscribe("meeting_started", self.on_meeting_started)
        self.ui_events.subscribe("meeting_paused", self.on_meeting_paused)
        self.ui_events.subscribe("meeting_resumed", self.on_meeting_resumed)
        self.ui_events.subscribe("meeting_finished", self.on_meeting_finished)
        self.ui_events.subscribe(
            "meeting_import_started",
            self.on_import_started
        )

        self.ui_events.subscribe(
            "meeting_import_completed",
            self.on_import_completed
        )

        self.ui_events.subscribe(
            "meeting_import_failed",
            self.on_import_failed
        )

        self.ui_events.subscribe(
            "meeting_import_insufficient_evidence",
            self.on_import_insufficient_evidence,
        )

        self.ui_events.subscribe(
            "meeting_processing_completed",
            self.on_processing_completed,
        )

        self.ui_events.subscribe(
            "meeting_processing_failed",
            self.on_processing_failed,
        )

        self.ui_events.subscribe(
            "meeting_processing_insufficient_evidence",
            self.on_processing_insufficient_evidence,
        )

    def _set_initial_state(self):

        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.btn_export.configure(state="disabled")
        self.btn_import.configure(
            state="normal"
        )

    def on_meeting_started(self):

        self.btn_start.configure(state="disabled")
        self.btn_pause.configure(state="normal")
        self.btn_resume.configure(state="disabled")
        self.btn_stop.configure(state="normal")
        self.btn_export.configure(state="disabled")
        self.btn_import.configure(
            state="normal"
        )

    def on_meeting_paused(self):

        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="normal")

    def on_meeting_resumed(self):

        self.btn_pause.configure(state="normal")
        self.btn_resume.configure(state="disabled")

    def on_meeting_finished(self):

        self.btn_start.configure(state="normal")
        self.btn_pause.configure(state="disabled")
        self.btn_resume.configure(state="disabled")
        self.btn_stop.configure(state="disabled")
        self.btn_export.configure(state="disabled")

    def on_processing_completed(self, session):

        self.btn_export.configure(
            state="normal"
        )

    def on_processing_failed(self, error):

        self.btn_export.configure(
            state="disabled"
        )

    def on_processing_insufficient_evidence(self, error):

        self.btn_export.configure(
            state="disabled"
        )

    def on_import_started(self, filename):

        self.btn_start.configure(
            state="disabled"
        )

        self.btn_import.configure(
            state="disabled"
        )

        self.btn_export.configure(
            state="disabled"
        )


    def on_import_completed(self, session):

        self.btn_start.configure(
            state="normal"
        )

        self.btn_import.configure(
            state="normal"
        )

        self.btn_export.configure(
            state="normal"
        )


    def on_import_failed(self, error):

        self.btn_start.configure(
            state="normal"
        )

        self.btn_import.configure(
            state="normal"
        )

        self.btn_export.configure(
            state="disabled"
        )

    def on_import_insufficient_evidence(self, error):

        self.btn_start.configure(
            state="normal"
        )

        self.btn_import.configure(
            state="normal"
        )

        self.btn_export.configure(
            state="disabled"
        )
