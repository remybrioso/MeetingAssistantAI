"""
Footer y diálogo de atribución del producto.
"""

from __future__ import annotations

import application.app_info as app_info
import customtkinter as ctk

from gui.theme.colors import (
    BORDER,
    SURFACE,
    TEXT,
    TEXT_SECONDARY,
)
from gui.theme.fonts import SMALL, SUBTITLE


DEVELOPER_ATTRIBUTION = (
    "Diseñado y desarrollado por Remy Brioso"
)


def build_attribution_text() -> str:
    """Devuelve el texto visible del footer con la versión actual."""

    return (
        f"{app_info.APP_NAME} • "
        f"{DEVELOPER_ATTRIBUTION} • "
        f"v{app_info.VERSION}"
    )


def build_about_metadata() -> dict[str, str]:
    """Devuelve los metadatos mostrados por el diálogo Acerca de."""

    return {
        "app_name": app_info.APP_NAME,
        "version": f"v{app_info.VERSION}",
        "developer": DEVELOPER_ATTRIBUTION,
        "milestone": app_info.MILESTONE,
        "build": app_info.BUILD,
    }


class AboutDialog(ctk.CTkToplevel):

    WIDTH = 380
    HEIGHT = 300

    def __init__(
        self,
        parent,
        on_close=None,
    ) -> None:
        super().__init__(parent)

        self._on_close_callback = on_close

        self.title("Acerca de")
        self.geometry(
            f"{self.WIDTH}x{self.HEIGHT}"
        )
        self.resizable(False, False)
        self.configure(fg_color=SURFACE)

        self.transient(parent)
        self.protocol(
            "WM_DELETE_WINDOW",
            self.close,
        )

        self._build_ui()
        self.after_idle(self._center_over_parent)

    def _build_ui(self) -> None:
        content = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )
        content.pack(
            fill="both",
            expand=True,
            padx=24,
            pady=20,
        )

        metadata = build_about_metadata()

        ctk.CTkLabel(
            content,
            text=metadata["app_name"],
            font=SUBTITLE,
            text_color=TEXT,
        ).pack(
            pady=(0, 14),
        )

        ctk.CTkLabel(
            content,
            text=f"Versión: {metadata['version']}",
            font=SMALL,
            text_color=TEXT_SECONDARY,
        ).pack()

        ctk.CTkLabel(
            content,
            text="Diseñado y desarrollado por",
            font=SMALL,
            text_color=TEXT_SECONDARY,
        ).pack(
            pady=(16, 0),
        )

        ctk.CTkLabel(
            content,
            text="Remy Brioso",
            font=SMALL,
            text_color=TEXT,
        ).pack()

        ctk.CTkLabel(
            content,
            text=(
                f"Milestone: {metadata['milestone']}\n"
                f"Build: {metadata['build']}"
            ),
            font=SMALL,
            text_color=TEXT_SECONDARY,
            justify="center",
        ).pack(
            pady=(16, 12),
        )

        ctk.CTkButton(
            content,
            text="Cerrar",
            width=90,
            height=28,
            command=self.close,
        ).pack()

    def _center_over_parent(self) -> None:
        try:
            parent = self.master
            parent.update_idletasks()
            self.update_idletasks()

            x = parent.winfo_rootx() + max(
                0,
                (parent.winfo_width() - self.WIDTH) // 2,
            )
            y = parent.winfo_rooty() + max(
                0,
                (parent.winfo_height() - self.HEIGHT) // 2,
            )
            self.geometry(
                f"{self.WIDTH}x{self.HEIGHT}+{x}+{y}"
            )
        except Exception:
            return

    def close(self) -> None:
        callback = self._on_close_callback
        self._on_close_callback = None

        if callable(callback):
            callback()

        if self.winfo_exists():
            self.destroy()


class Footer(ctk.CTkFrame):

    def __init__(self, master) -> None:
        super().__init__(
            master,
            fg_color="transparent",
            border_width=1,
            border_color=BORDER,
            corner_radius=8,
            height=36,
        )

        self._about_window = None
        self._build_ui()

    def _build_ui(self) -> None:
        self.grid_columnconfigure(0, weight=1)

        self.attribution_label = ctk.CTkLabel(
            self,
            text=build_attribution_text(),
            font=SMALL,
            text_color=TEXT_SECONDARY,
            anchor="w",
        )
        self.attribution_label.grid(
            row=0,
            column=0,
            sticky="w",
            padx=(12, 8),
            pady=5,
        )

        self.about_button = ctk.CTkButton(
            self,
            text="Acerca de",
            width=84,
            height=25,
            font=SMALL,
            command=self.show_about,
        )
        self.about_button.grid(
            row=0,
            column=1,
            sticky="e",
            padx=(8, 12),
            pady=5,
        )

    def show_about(self) -> None:
        if (
            self._about_window is not None
            and self._about_window.winfo_exists()
        ):
            self._about_window.deiconify()
            self._about_window.lift()
            self._about_window.focus_force()
            return

        self._about_window = AboutDialog(
            self.winfo_toplevel(),
            on_close=self._clear_about_window,
        )
        self._about_window.focus_force()

    def _clear_about_window(self) -> None:
        self._about_window = None
