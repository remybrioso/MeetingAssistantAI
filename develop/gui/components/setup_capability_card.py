"""
setup_capability_card.py

Tarjeta visual utilizada por el Setup Wizard
para representar una capacidad de MAI.
"""

import customtkinter as ctk

from services.setup.repair_action import (
    REPAIR_ACTION_BUTTON_LABELS,
    REPAIR_ACTION_PRESENTATION,
)


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
    "REPAIRING": {
        "symbol": "◌",
        "label": "Preparando",
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
        on_repair=None,
        can_repair=None,
    ):

        super().__init__(
            master,
            corner_radius=12,
            border_width=1,
            border_color="#30394A",
        )

        self.capability_id = capability_id
        self.on_repair = on_repair
        self.can_repair = can_repair
        self.repair_action = None

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
            padx=(0, 12),
            pady=(0, 12),
            sticky="ew",
        )

        self.repair_button = ctk.CTkButton(
            self,
            text="Resolver",
            width=150,
            command=self._request_repair,
        )

        self.repair_button.grid(
            row=3,
            column=2,
            padx=(0, 16),
            pady=(0, 12),
            sticky="e",
        )

        self.repair_label.grid_remove()
        self.repair_button.grid_remove()

    def set_running(self) -> None:

        self.repair_action = None

        self._apply_status(
            status="RUNNING",
            message="Comprobando esta capacidad...",
            repair_action=None,
        )

    def set_result(self, result) -> None:

        self.repair_action = (
            result.repair_action
        )

        self._apply_status(
            status=result.status.value,
            message=result.message,
            repair_action=result.repair_action,
        )

    def set_repair_running(
        self,
        repair_action: str,
    ) -> None:

        self.repair_action = repair_action

        self._apply_status(
            status="REPAIRING",
            message=(
                "Preparando esta capacidad. "
                "No cierres MAI."
            ),
            repair_action=repair_action,
        )

        self.repair_button.configure(
            state="disabled",
            text="Procesando...",
        )

    def set_repair_result(
        self,
        result,
    ) -> None:

        self.repair_action = result.action

        if result.succeeded:
            self._apply_status(
                status="REPAIRING",
                message=(
                    f"{result.message} "
                    "MAI está verificando el resultado."
                ),
                repair_action=result.action,
            )

            self.repair_button.configure(
                state="disabled",
                text="Verificando...",
            )

            return

        self._apply_status(
            status="UNAVAILABLE",
            message=result.message,
            repair_action=result.action,
        )

    def set_repair_unavailable(
        self,
        repair_action: str,
    ) -> None:

        self.repair_action = repair_action

        self._apply_status(
            status="UNAVAILABLE",
            message=(
                "Esta reparación todavía no está "
                "disponible en MAI."
            ),
            repair_action=repair_action,
        )

    def set_repair_failure(
        self,
        repair_action: str,
        error: str,
    ) -> None:

        self.repair_action = repair_action

        self._apply_status(
            status="UNAVAILABLE",
            message=(
                "No fue posible completar la reparación: "
                f"{error}"
            ),
            repair_action=repair_action,
        )

    def reset(self) -> None:

        self.repair_action = None

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

            if self._can_execute_repair(
                repair_action
            ):

                self.repair_button.configure(
                    text=(
                        REPAIR_ACTION_BUTTON_LABELS.get(
                            repair_action,
                            "Resolver",
                        )
                    ),
                    state="normal",
                )

                self.repair_button.grid()

            else:
                self.repair_button.grid_remove()

        else:
            self.repair_label.grid_remove()
            self.repair_button.grid_remove()

    def _can_execute_repair(
        self,
        repair_action: str,
    ) -> bool:

        if self.on_repair is None:
            return False

        if self.can_repair is None:
            return False

        return bool(
            self.can_repair(
                repair_action
            )
        )

    def _request_repair(self) -> None:

        if (
            self.repair_action is None
            or self.on_repair is None
        ):
            return

        self.on_repair(
            self.capability_id,
            self.repair_action,
        )
