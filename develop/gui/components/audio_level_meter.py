"""
Componente compacto para mostrar el nivel de una fuente de audio.
"""

import math

import customtkinter as ctk

from gui.theme.colors import (
    BORDER,
    PRIMARY,
    SURFACE_ALT,
    TEXT,
)
from gui.theme.fonts import SMALL


class AudioLevelMeter(ctk.CTkFrame):

    def __init__(
        self,
        master,
        source_name: str,
    ) -> None:
        super().__init__(
            master,
            fg_color="transparent",
        )

        self.level = 0.0

        self.source_label = ctk.CTkLabel(
            self,
            text=source_name,
            font=SMALL,
            text_color=TEXT,
        )
        self.source_label.pack(
            anchor="w",
            pady=(0, 4),
        )

        self.progress_bar = ctk.CTkProgressBar(
            self,
            height=10,
            fg_color=SURFACE_ALT,
            progress_color=PRIMARY,
            border_width=1,
            border_color=BORDER,
        )
        self.progress_bar.pack(
            fill="x",
        )
        self.progress_bar.set(0.0)

    def set_level(self, level: float) -> None:
        try:
            value = float(level)
        except (TypeError, ValueError):
            value = 0.0

        if not math.isfinite(value):
            value = 0.0

        self.level = max(
            0.0,
            min(1.0, value),
        )
        self.progress_bar.set(self.level)
