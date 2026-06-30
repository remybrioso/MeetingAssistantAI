import customtkinter as ctk

from gui.components.header import Header
from gui.theme.colors import BACKGROUND
from gui.components.status_panel import StatusPanel
from gui.components.activity_panel import ActivityPanel


class MainWindow(ctk.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Meeting Assistant AI")

        self.geometry("1300x800")

        self.configure(
            fg_color=BACKGROUND
        )

        Header(self).pack(fill="x", padx=20, pady=(20, 10))

        self.status_panel = StatusPanel(self)

        self.status_panel.pack(
        fill="x",
        padx=20,
        pady=(0, 20)
        )
        self.activity = ActivityPanel(self)

        self.activity.pack(
            fill="both",
            expand=True,
            padx=20,
            pady=(0, 20)
        )

        self.activity.add("Aplicación iniciada correctamente.")