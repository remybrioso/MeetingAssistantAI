"""
setup_capability_card.py

Tarjeta visual utilizada por el Setup Wizard
para representar una capacidad de MAI.
"""

import customtkinter as ctk


STATUS_PRESENTATION = {
    "PENDING": {
        "symbol": "○",
        "label": "Pendiente",
        "color": "#8A94A6",
    },
    "RUNNING": {
        "symbol": "◌",
        "label": "Comprobando",
        "color": "#4EA1FF",
    },
    "AVAILABLE": {
        "symbol": "●",
        "label": "Disponible",
        "color": "#39C77F",
    },
    "DEGRADED": {
        "symbol": "●",
        "label": "Requiere atención",
        "color": "#F4B942",
    },
    "UNAVAILABLE": {
        "symbol": "●",
        "label": "No disponible",
        "color": "#EF6461",
    },
}


class SetupCapabilityCard(ctk.CTkFrame):

    def __init__(
        self,
        master,
        capability_id: str,
        name: str,
        description: str,
    ):

        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            border_color="#30394A",
        )

        self.capability_id = capability_id

        self.grid_columnconfigure(
            1,
            weight=1,
        )

        self.status_symbol = ctk.CTkLabel(
            self,
            text="○",
            font=ctk.CTkFont(
                size=22,
                weight="bold",
            ),
            text_color="#8A94A6",
            width=32,
        )

        self.status_symbol.grid(
            row=0,
            column=0,
            rowspan=2,
            padx=(16, 8),
            pady=16,
            sticky="n",
        )

        self.name_label = ctk.CTkLabel(
            self,
            text=name,
            font=ctk.CTkFont(
                size=15,
                weight="bold",
            ),
            anchor="w",
        )

        self.name_label.grid(
            row=0,
            column=1,
            padx=(0, 12),
            pady=(14, 2),
            sticky="ew",
        )

        self.description_label = ctk.CTkLabel(
            self,
            text=description,
            font=ctk.CTkFont(
                size=12,
            ),
            text_color="#AAB3C2",
            anchor="w",
            justify="left",
            wraplength=620,
        )

        self.description_label.grid(
            row=1,
            column=1,
            padx=(0, 12),
            pady=(0, 6),
            sticky="ew",
        )

        self.status_label = ctk.CTkLabel(
            self,
            text="Pendiente",
            font=ctk.CTkFont(
                size=12,
                weight="bold",
            ),
            text_color="#8A94A6",
        )

        self.status_label.grid(
            row=0,
            column=2,
            padx=16,
            pady=(14, 2),
            sticky="e",
        )

        self.message_label = ctk.CTkLabel(
            self,
            text="Esperando comprobación.",
            font=ctk.CTkFont(
                size=12,
            ),
            text_color="#D0D6E0",
            anchor="w",
            justify="left",
            wraplength=620,
        )

        self.message_label.grid(
            row=2,
            column=1,
            columnspan=2,
            padx=(0, 16),
            pady=(2, 14),
            sticky="ew",
        )

        self.repair_label = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(
                size=11,
            ),
            text_color="#F4B942",
            anchor="w",
        )

        self.repair_label.grid(
            row=3,
            column=1,
            columnspan=2,
            padx=(0, 16),
            pady=(0, 12),
            sticky="ew",
        )

        self.repair_label.grid_remove()

    def set_running(self) -> None:

        self._apply_status(
            status="RUNNING",
            message="Comprobando esta capacidad...",
            repair_action=None,
        )

    def set_result(self, result) -> None:

        self._apply_status(
            status=result.status.value,
            message=result.message,
            repair_action=result.repair_action,
        )

    def reset(self) -> None:

        self._apply_status(
            status="PENDING",
            message="Esperando comprobación.",
            repair_action=None,
        )

    def _apply_status(
        self,
        status: str,
        message: str,
        repair_action: str | None,
    ) -> None:

        presentation = STATUS_PRESENTATION.get(
            status,
            STATUS_PRESENTATION["PENDING"],
        )

        REPAIR_ACTION_PRESENTATION = {
        "CONFIGURE_SYSTEM_AUDIO": (
            "Configura la captura del audio del equipo "
            "para incluir las voces de los participantes."
        ),
        "CONFIGURE_MICROPHONE": (
            "Selecciona o conecta un micrófono disponible."
        ),
        "INSTALL_AI_PROVIDER": (
            "Instala o inicia el motor de inteligencia artificial."
        ),
        "DOWNLOAD_AI_MODEL": (
            "Descarga el modelo de inteligencia artificial requerido."
        ),
        "REPAIR_AI_CAPABILITY": (
            "Revisa la configuración del motor de inteligencia artificial."
        ),
        "REPAIR_AUDIO_DEVICES": (
            "Revisa los dispositivos y controladores de audio."
        ),
        "CREATE_OUTPUT_DIRECTORY": (
            "Permite que MAI cree la carpeta donde guardará las reuniones."
        ),
        "REPAIR_WORKSPACE": (
            "Revisa la carpeta de almacenamiento de reuniones."
        ),
        }

        self.status_symbol.configure(
            text=presentation["symbol"],
            text_color=presentation["color"],
        )

        self.status_label.configure(
            text=presentation["label"],
            text_color=presentation["color"],
        )

        self.message_label.configure(
            text=message,
        )

        if repair_action:

            repair_message = (
                REPAIR_ACTION_PRESENTATION.get(
                    repair_action,
                    "Revisa la configuración de esta función.",
                )
            )

            self.repair_label.configure(
                text=(
                    "Acción recomendada: "
                    f"{repair_message}"
                )
            )

            self.repair_label.grid()

        else:
            self.repair_label.grid_remove()