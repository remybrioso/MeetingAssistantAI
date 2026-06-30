import customtkinter as ctk


class MainWindow(ctk.CTk):

    def __init__(self, controller):
        super().__init__()

        self.controller = controller

        self.title("Meeting Assistant AI")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.build_ui()

    def build_ui(self):

        title = ctk.CTkLabel(
            self,
            text="Meeting Assistant AI",
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=(30, 20))

        self.status = ctk.CTkLabel(
            self,
            text="Estado: Detenido",
            font=("Segoe UI", 16)
        )

        self.status.pack(pady=10)

        start_button = ctk.CTkButton(
            self,
            text="Iniciar reunión",
            width=220,
            height=45,
            command=self.start_meeting
        )

        start_button.pack(pady=10)

        stop_button = ctk.CTkButton(
            self,
            text="Finalizar reunión",
            width=220,
            height=45,
            command=self.stop_meeting
        )

        stop_button.pack(pady=10)

    def start_meeting(self):

        self.controller.start_meeting()

        self.status.configure(
            text="Estado: Grabando"
        )

    def stop_meeting(self):

        self.controller.stop_meeting()

        self.status.configure(
            text="Estado: Detenido"
        )