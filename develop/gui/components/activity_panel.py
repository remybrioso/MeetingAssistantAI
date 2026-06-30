import customtkinter as ctk

from datetime import datetime

from gui.theme.colors import (
    SURFACE,
    BORDER,
    TEXT,
)

from gui.theme.fonts import SUBTITLE


class ActivityPanel(ctk.CTkFrame):

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
            text="Actividad",
            font=SUBTITLE,
            text_color=TEXT
        )

        title.pack(anchor="w", padx=20, pady=(15, 10))

        self.log = ctk.CTkTextbox(
            self,
            height=350
        )

        self.log.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.log.configure(state="disabled")

    def add(self, message: str):

        now = datetime.now().strftime("%H:%M:%S")

        self.log.configure(state="normal")

        self.log.insert(
            "end",
            f"[{now}] {message}\n"
        )

        self.log.see("end")

        self.log.configure(state="disabled")