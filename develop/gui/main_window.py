import customtkinter as ctk

from application.dependency_container import container

from gui.components.header import Header
from gui.components.status_panel import StatusPanel
from gui.components.activity_panel import ActivityPanel

from gui.theme.colors import BACKGROUND


class MainWindow(ctk.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller
        self.bus = container.get("event_bus")

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.title("Meeting Assistant AI")
        self.geometry("1300x800")

        self.configure(
            fg_color=BACKGROUND
        )

        self.build_ui()

        # Suscripción a eventos
        self.bus.subscribe("activity", self.activity.add)
        self.bus.subscribe("meeting_started", self.on_meeting_started)
        self.bus.subscribe("meeting_finished", self.on_meeting_finished)

    def build_ui(self):

        self.header = Header(self)
        self.header.pack(fill="x", padx=20, pady=(20, 10))

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

        buttons = ctk.CTkFrame(self, fg_color="transparent")
        buttons.pack(pady=20)

        ctk.CTkButton(
            buttons,
            text="Iniciar reunión",
            width=180,
            command=self.start_meeting
        ).pack(side="left", padx=10)

        ctk.CTkButton(
            buttons,
            text="Finalizar reunión",
            width=180,
            command=self.stop_meeting
        ).pack(side="left", padx=10)

    def start_meeting(self):
        self.controller.start_meeting()

    def stop_meeting(self):
        self.controller.stop_meeting()

    def on_meeting_started(self):
        self.status_panel.set_status("meeting", True)

    def on_meeting_finished(self):
        self.status_panel.set_status("meeting", False)