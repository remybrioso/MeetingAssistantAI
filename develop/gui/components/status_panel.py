import customtkinter as ctk

from gui.theme.colors import (
    SURFACE,
    TEXT,
    SUCCESS,
    ERROR,
    BORDER,
)
from gui.theme.fonts import SUBTITLE, NORMAL


class StatusPanel(ctk.CTkFrame):

    def __init__(self, master, ui_events):
        super().__init__(
            master,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=10
        )

        self._build_ui()
        self.ui_events = ui_events
        

        self.ui_events.subscribe("meeting_started", self.on_meeting_started)
        self.ui_events.subscribe("meeting_finished", self.on_meeting_finished)

        self.ui_events.subscribe(
            "timer_tick",
            self.on_timer_tick
        )

    def _build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Estado del Sistema",
            font=SUBTITLE,
            text_color=TEXT
        )

        title.pack(anchor="w", padx=20, pady=(15, 10))

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="x", padx=20, pady=(0, 20))
        timer_frame = ctk.CTkFrame(content, fg_color="transparent")
        timer_frame.pack(anchor="e", padx=20, pady=(0, 15))
        timer_title = ctk.CTkLabel(timer_frame, text="Duración", font=NORMAL, text_color=TEXT)
        timer_title.pack()
        self.timer_value = ctk.CTkLabel(timer_frame, text="00:00:00", font=("Consolas", 22, "bold"), text_color=TEXT)
        self.timer_value.pack()

        self.meeting = self._create_status(content, "Reunión", ERROR)
        self.audio = self._create_status(content, "Audio", ERROR)
        self.ai = self._create_status(content, "IA", ERROR)
        self.document = self._create_status(content, "Documento", ERROR)
        self.processing = self._create_status(content, "Procesando", ERROR)
        self.rec_label = ctk.CTkLabel(self, text="", font=("segoe UI", 18, "bold"), text_color=ERROR)

        self.rec_label.pack(anchor="e", padx=20)

    def _create_status(self, master, text, color):

        frame = ctk.CTkFrame(master, fg_color="transparent")
        frame.pack(side="left", padx=25)

        dot = ctk.CTkLabel(
            frame,
            text="●",
            text_color=color,
            font=("Segoe UI", 20)
        )

        dot.pack(side="left")

        label = ctk.CTkLabel(
            frame,
            text=text,
            font=NORMAL,
            text_color=TEXT
        )

        label.pack(side="left", padx=6)

        return dot

    def set_status(self, service: str, active: bool):

        color = SUCCESS if active else ERROR

        controls = {
        "meeting": self.meeting,
        "audio": self.audio,
        "ai": self.ai,
        "document": self.document,
        "processing": self.processing,
    }
        if service in controls:
            controls[service].configure(text_color=color)

    def on_timer_tick(self, value):
        self.timer_value.configure(text=value)

    def on_meeting_started(self):
        self.rec_label.configure(text="🔴 REC")


    def on_meeting_finished(self):
        self.rec_label.configure(text="")

    
            