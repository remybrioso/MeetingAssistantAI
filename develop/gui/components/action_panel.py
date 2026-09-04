import customtkinter as ctk


from gui.theme.colors import SURFACE, BORDER
from gui.theme.fonts import SUBTITLE
from gui.layout_policy import (
    ACTION_LAYOUT_NORMAL_COLUMNS,
    action_column_count,
)


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

        self._buttons_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        self._buttons_frame.pack(
            fill="x",
            padx=20,
            pady=(0, 20),
        )

        self.btn_start = ctk.CTkButton(
            self._buttons_frame,
            text="▶ Iniciar",
            command=self.controller.start_meeting
        )

        self.btn_pause = ctk.CTkButton(
            self._buttons_frame,
            text="⏸ Pausar",
            command=self.controller.pause_meeting
        )

        self.btn_resume = ctk.CTkButton(
            self._buttons_frame,
            text="▶ Reanudar",
            command=self.controller.resume_meeting
        )

        self.btn_stop = ctk.CTkButton(
            self._buttons_frame,
            text="⏹ Finalizar",
            command=self.controller.stop_meeting
        )

        self.btn_import = ctk.CTkButton(
            self._buttons_frame,
            text="📂 Importar grabación",
            command=self.controller.import_recording
        )

        self.btn_export = ctk.CTkButton(
            self._buttons_frame,
            text="📄 Exportar",
            state="disabled"
        )

        self._buttons = (
            self.btn_start,
            self.btn_pause,
            self.btn_resume,
            self.btn_stop,
            self.btn_import,
            self.btn_export,
        )
        self._action_columns = None
        self._apply_action_layout(
            ACTION_LAYOUT_NORMAL_COLUMNS
        )
        self._buttons_frame.bind(
            "<Configure>",
            self._on_buttons_configure,
        )

    def _on_buttons_configure(self, event):
        self._apply_action_layout(
            action_column_count(event.width)
        )

    def _apply_action_layout(self, column_count: int) -> None:
        if self._action_columns == column_count:
            return

        for column in range(ACTION_LAYOUT_NORMAL_COLUMNS):
            self._buttons_frame.grid_columnconfigure(
                column,
                weight=1 if column < column_count else 0,
            )

        vertical_padding = 4 if column_count < len(self._buttons) else 0

        for index, button in enumerate(self._buttons):
            row, column = divmod(index, column_count)
            button.grid(
                row=row,
                column=column,
                sticky="ew",
                padx=8,
                pady=vertical_padding,
            )

        self._action_columns = column_count

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
