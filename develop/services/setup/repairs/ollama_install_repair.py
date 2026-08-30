"""
ollama_install_repair.py

Abre de forma explícita la página oficial de descarga
de Ollama para que el usuario complete la instalación.
"""

import webbrowser

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


OLLAMA_WINDOWS_DOWNLOAD_URL = (
    "https://ollama.com/download/windows"
)


class OllamaInstallRepair:

    def __init__(
        self,
        download_url: str = OLLAMA_WINDOWS_DOWNLOAD_URL,
        browser_opener=None,
    ) -> None:

        if not isinstance(
            download_url,
            str,
        ):
            raise TypeError(
                "download_url debe ser una cadena."
            )

        normalized_url = (
            download_url.strip()
        )

        if not normalized_url:
            raise ValueError(
                "download_url no puede estar vacío."
            )

        self.download_url = normalized_url
        self.browser_opener = (
            browser_opener
            if browser_opener is not None
            else webbrowser.open
        )

    def __call__(
        self,
        context: dict,
    ) -> RepairExecutionResult:

        repair_context = dict(
            context or {}
        )

        try:
            opened = self.browser_opener(
                self.download_url
            )
        except Exception as ex:
            return RepairExecutionResult(
                action=RepairAction.INSTALL_AI_PROVIDER,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "No fue posible abrir la página "
                    "oficial de descarga de Ollama."
                ),
                details={
                    "reason": "browser-open-failed",
                    "download_url": self.download_url,
                    "error_type": (
                        ex.__class__.__name__
                    ),
                    "error": str(ex),
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        if opened is False:
            return RepairExecutionResult(
                action=RepairAction.INSTALL_AI_PROVIDER,
                status=RepairExecutionStatus.FAILED,
                message=(
                    "El navegador no pudo abrir la página "
                    "oficial de descarga de Ollama."
                ),
                details={
                    "reason": "browser-open-returned-false",
                    "download_url": self.download_url,
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        return RepairExecutionResult(
            action=RepairAction.INSTALL_AI_PROVIDER,
            status=(
                RepairExecutionStatus
                .USER_ACTION_REQUIRED
            ),
            message=(
                "Se abrió la página oficial de Ollama. "
                "Instala o inicia Ollama y después pulsa "
                "«Volver a comprobar»."
            ),
            details={
                "download_url": self.download_url,
                "capability_id": (
                    repair_context.get(
                        "capability_id"
                    )
                ),
            },
        )
