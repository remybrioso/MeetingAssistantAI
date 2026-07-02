import customtkinter as ctk

from application.dependency_container import container

from gui.components.header import Header
from gui.components.status_panel import StatusPanel
from gui.components.activity_panel import ActivityPanel
from gui.components.action_panel import ActionPanel

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

        # Suscripción a eventos
        self.bus.subscribe("activity", self.activity.add)
        self.bus.subscribe("meeting_started", self.on_meeting_started)
        self.bus.subscribe("meeting_finished", self.on_meeting_finished)

        self.update_timer()

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