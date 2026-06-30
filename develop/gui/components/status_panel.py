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

    def __init__(self, master):
        super().__init__(
            master,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=10
        )

        self._build_ui()

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

        self.meeting = self._create_status(content, "Reunión", ERROR)
        self.audio = self._create_status(content, "Audio", ERROR)
        self.ai = self._create_status(content, "IA", ERROR)
        self.document = self._create_status(content, "Documento", ERROR)

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
        }

        if service in controls:
            controls[service].configure(text_color=color)