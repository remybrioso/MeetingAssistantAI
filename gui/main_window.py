import customtkinter as ctk

from config import (
    APP_NAME,
    APP_VERSION,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
    APPEARANCE_MODE,
    COLOR_THEME
)

ctk.set_appearance_mode(APPEARANCE_MODE)
ctk.set_default_color_theme(COLOR_THEME)


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title(APP_NAME)

        self.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.resizable(False, False)

        self.create_widgets()

    def create_widgets(self):

        title = ctk.CTkLabel(
            self,
            text=APP_NAME,
            font=("Segoe UI", 28, "bold")
        )

        title.pack(pady=30)

        version = ctk.CTkLabel(
            self,
            text=APP_VERSION,
            font=("Segoe UI", 14)
        )

        version.pack()