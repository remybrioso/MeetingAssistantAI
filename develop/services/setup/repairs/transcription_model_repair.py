"""
transcription_model_repair.py

Descarga de forma explícita el modelo Faster-Whisper
configurado para Meeting Assistant AI.
"""

from pathlib import Path

from faster_whisper import download_model

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionResult,
    RepairExecutionStatus,
)


class TranscriptionModelRepair:

    def __init__(
        self,
        model_name: str,
        model_downloader=None,
    ) -> None:

        if not isinstance(
            model_name,
            str,
        ):
            raise TypeError(
                "model_name debe ser una cadena."
            )

        normalized_model = (
            model_name.strip()
        )

        if not normalized_model:
            raise ValueError(
                "model_name no puede estar vacío."
            )

        self.model_name = normalized_model

        self.model_downloader = (
            model_downloader
            if model_downloader is not None
            else download_model
        )

    def __call__(
        self,
        context: dict,
    ) -> RepairExecutionResult:

        repair_context = dict(
            context or {}
        )

        try:
            model_path = self.model_downloader(
                self.model_name,
                local_files_only=False,
            )

            resolved_path = Path(
                model_path
            )

            if not resolved_path.exists():
                return RepairExecutionResult(
                    action=(
                        RepairAction
                        .DOWNLOAD_TRANSCRIPTION_MODEL
                    ),
                    status=(
                        RepairExecutionStatus.FAILED
                    ),
                    message=(
                        "La descarga terminó, pero MAI "
                        "no pudo localizar el modelo."
                    ),
                    details={
                        "reason": "model-path-not-found",
                        "model": self.model_name,
                        "model_path": str(
                            resolved_path
                        ),
                        "local_files_only": False,
                        "capability_id": (
                            repair_context.get(
                                "capability_id"
                            )
                        ),
                    },
                )

            return RepairExecutionResult(
                action=(
                    RepairAction
                    .DOWNLOAD_TRANSCRIPTION_MODEL
                ),
                status=RepairExecutionStatus.SUCCESS,
                message=(
                    "El modelo de transcripción "
                    "se descargó correctamente."
                ),
                details={
                    "model": self.model_name,
                    "model_path": str(
                        resolved_path
                    ),
                    "local_files_only": False,
                    "capability_id": (
                        repair_context.get(
                            "capability_id"
                        )
                    ),
                },
            )

        except Exception as ex:
            return RepairExecutionResult(
                action=(
                    RepairAction
                    .DOWNLOAD_TRANSCRIPTION_MODEL
                ),
                status=RepairExecutionStatus.FAILED,
                message=(
                    "No fue posible descargar el "
                    "modelo de transcripción."
                ),
                details={
                    "reason": "download-failed",
                    "model": self.model_name,
                    "local_files_only": False,
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
