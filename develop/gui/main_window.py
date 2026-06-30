import customtkinter as ctk

from gui.components.header import Header
from gui.theme.colors import BACKGROUND


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

        self.build_ui()

    def build_ui(self):

        Header(self).pack(fill="x")