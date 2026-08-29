"""
setup_wizard_frame.py

Interfaz inicial de diagnóstico y preparación
de Meeting Assistant AI.
"""

import customtkinter as ctk

from gui.components.setup_capability_card import (
    SetupCapabilityCard,
)


CAPABILITY_PRESENTATION = {
    "runtime-resources": {
        "name": "Recursos internos",
        "description": (
            "Comprueba que MAI incluya los recursos internos "
            "necesarios para procesar reuniones."
        ),
    },
    "workspace": {
        "name": "Almacenamiento de reuniones",
        "description": (
            "Comprueba que MAI pueda crear y guardar "
            "las reuniones correctamente."
        ),
    },
    "transcription": {
        "name": "Transcripción",
        "description": (
            "Comprueba que el modelo local necesario para "
            "transcribir reuniones esté disponible."
        ),
    },
    "artificial-intelligence": {
        "name": "Inteligencia artificial",
        "description": (
            "Comprueba la conexión con el motor de IA "
            "y la disponibilidad del modelo."
        ),
    },
    "audio": {
        "name": "Audio de reuniones",
        "description": (
            "Comprueba el micrófono y la captura del "
            "audio reproducido por el equipo."
        ),
    },
}


class SetupWizardFrame(ctk.CTkFrame):

    def __init__(
        self,
        master,
        controller,
    ):

        super().__init__(
            master,
            corner_radius=0,
            fg_color="#10141D",
        )

        self.controller = controller
        self.cards = {}
        self.last_result = None

        self.grid_columnconfigure(
            0,
            weight=1,
        )

        self.grid_rowconfigure(
            1,
            weight=1,
        )

        self._build_ui()
        self._build_capability_cards()

    def _build_ui(self) -> None:

        header_frame = ctk.CTkFrame(
            self,
            fg_color="transparent",
        )

        header_frame.grid(
            row=0,
            column=0,
            padx=50,
            pady=(40, 16),
            sticky="ew",
        )

        title = ctk.CTkLabel(
            header_frame,
            text="Preparando Meeting Assistant AI",
            font=ctk.CTkFont(
                size=28,
                weight="bold",
            ),
        )

        title.pack(
            anchor="w",
        )

        subtitle = ctk.CTkLabel(
            header_frame,
            text=(
                "MAI está comprobando los componentes "
                "necesarios para trabajar correctamente."
            ),
            font=ctk.CTkFont(
                size=14,
            ),
            text_color="#AAB3C2",
        )

        subtitle.pack(
            anchor="w",
            pady=(6, 0),
        )

        self.cards_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
        )

        self.cards_frame.grid(
            row=1,
            column=0,
            padx=50,
            pady=10,
            sticky="nsew",
        )

        self.cards_frame.grid_columnconfigure(
            0,
            weight=1,
        )

        footer = ctk.CTkFrame(
            self,
            fg_color="#171C27",
            corner_radius=0,
        )

        footer.grid(
            row=2,
            column=0,
            sticky="ew",
        )

        footer.grid_columnconfigure(
            0,
            weight=1,
        )

        self.global_status_label = ctk.CTkLabel(
            footer,
            text="Iniciando comprobación...",
            font=ctk.CTkFont(
                size=14,
                weight="bold",
            ),
            anchor="w",
        )

        self.global_status_label.grid(
            row=0,
            column=0,
            padx=50,
            pady=(18, 4),
            sticky="ew",
        )

        self.progress_bar = ctk.CTkProgressBar(
            footer,
            height=8,
        )

        self.progress_bar.grid(
            row=1,
            column=0,
            columnspan=3,
            padx=50,
            pady=(4, 18),
            sticky="ew",
        )

        self.progress_bar.set(0)

        self.retry_button = ctk.CTkButton(
            footer,
            text="Volver a comprobar",
            command=self._retry,
            state="disabled",
        )

        self.retry_button.grid(
            row=0,
            column=1,
            rowspan=2,
            padx=(12, 8),
            pady=16,
        )

        self.continue_button = ctk.CTkButton(
            footer,
            text="Continuar",
            command=self._continue,
            state="disabled",
        )

        self.continue_button.grid(
            row=0,
            column=2,
            rowspan=2,
            padx=(8, 50),
            pady=16,
        )

    def _build_capability_cards(self) -> None:

        for row, (
            capability_id,
            presentation,
        ) in enumerate(
            CAPABILITY_PRESENTATION.items()
        ):

            card = SetupCapabilityCard(
                self.cards_frame,
                capability_id=capability_id,
                name=presentation["name"],
                description=(
                    presentation["description"]
                ),
            )

            card.grid(
                row=row,
                column=0,
                padx=4,
                pady=8,
                sticky="ew",
            )

            self.cards[
                capability_id
            ] = card

    def begin(self) -> None:

        self.last_result = None

        self.retry_button.configure(
            state="disabled"
        )

        self.continue_button.configure(
            state="disabled"
        )

        self.global_status_label.configure(
            text="Comprobando el entorno de MAI..."
        )

        self.progress_bar.set(0)

        for card in self.cards.values():
            card.reset()

    def capability_started(
        self,
        capability_id: str,
        name: str,
        index: int,
        total: int,
    ) -> None:

        card = self.cards.get(
            capability_id
        )

        if card:
            card.set_running()

        if total:

            self.progress_bar.set(
                (index - 1) / total
            )

        self.global_status_label.configure(
            text=f"Comprobando: {name}"
        )

    def capability_completed(
        self,
        result,
        index: int,
        total: int,
    ) -> None:

        card = self.cards.get(
            result.capability_id
        )

        if card:
            card.set_result(result)

        if total:

            self.progress_bar.set(
                index / total
            )

    def show_result(
        self,
        result,
    ) -> None:

        self.last_result = result

        self.progress_bar.set(1)

        for capability_result in (
            result.capability_results
        ):

            card = self.cards.get(
                capability_result.capability_id
            )

            if card:
                card.set_result(
                    capability_result
                )

        self.global_status_label.configure(
            text=result.message
        )

        self.retry_button.configure(
            state="normal"
        )

        if result.can_continue:

            self.continue_button.configure(
                state="normal"
            )

        else:

            self.continue_button.configure(
                state="disabled"
            )

    def show_failure(
        self,
        error: str,
    ) -> None:

        self.global_status_label.configure(
            text=(
                "No fue posible completar la "
                f"comprobación: {error}"
            )
        )

        self.retry_button.configure(
            state="normal"
        )

        self.continue_button.configure(
            state="disabled"
        )

    def _retry(self) -> None:

        self.controller.retry_setup_wizard()

    def _continue(self) -> None:

        self.controller.continue_with_attention()
