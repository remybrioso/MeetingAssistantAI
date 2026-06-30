import customtkinter as ctk

from gui.theme.colors import TEXT
from gui.theme.fonts import TITLE


class Header(ctk.CTkFrame):

    def __init__(self, master):
        super().__init__(master, fg_color="transparent")

        title = ctk.CTkLabel(
            self,
            text="Meeting Assistant AI",
            font=TITLE,
            text_color=TEXT
        )

        title.pack(side="left", padx=20, pady=15)