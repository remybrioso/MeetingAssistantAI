import customtkinter as ctk

from gui.theme.colors import SURFACE, BORDER
from gui.theme.fonts import SUBTITLE


class ActionPanel(ctk.CTkFrame):

    def __init__(self, master, controller):
        super().__init__(
            master,
            fg_color=SURFACE,
            border_width=1,
            border_color=BORDER,
            corner_radius=10
        )

        self.controller = controller

        self._build_ui()

    def _build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Acciones",
            font=SUBTITLE
        )

        title.pack(anchor="w", padx=20, pady=(15, 10))

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=(0, 20))

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

        self.btn_export = ctk.CTkButton(
            buttons,
            text="📄 Exportar",
            width=150,
            state="disabled"
        )

        self.btn_export.pack(side="left", padx=8)