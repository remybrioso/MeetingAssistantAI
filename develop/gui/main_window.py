import customtkinter as ctk


class MainWindow(ctk.CTk):

    def __init__(self):
        super().__init__()

        self.title("Meeting Assistant AI")
        self.geometry("1200x750")
        self.minsize(1000, 650)

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")