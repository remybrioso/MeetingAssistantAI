"""
meeting_workspace.py

Representa la estructura física de una reunión.
"""

import json
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path


@dataclass
class MeetingWorkspace:
    """
    Define las ubicaciones oficiales utilizadas por una
    reunión dentro del Workspace de MAI.

    Las propiedades representan rutas conocidas del
    sistema, pero no crean los artefactos por sí mismas.
    """

    root_dir: Path

    audio_dir: Path

    documents_dir: Path

    internal_dir: Path

    version: str = "1.0"

    def initialize(self) -> None:
        """
        Crea la estructura física base del Workspace y
        escribe su manifiesto.
        """

        self.audio_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.documents_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self.internal_dir.mkdir(
            parents=True,
            exist_ok=True,
        )

        self._write_manifest()

    def _write_manifest(self) -> None:
        """
        Persiste la descripción de la estructura física
        del Workspace.
        """

        data = {
            "version": self.version,
            "created_at": (
                datetime.now(
                    UTC
                ).isoformat()
            ),
            "structure": {
                "audio": str(
                    self.audio_dir
                ),
                "documents": str(
                    self.documents_dir
                ),
                "internal": str(
                    self.internal_dir
                ),
            },
        }

        with open(
            self.workspace_manifest,
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4,
            )

    @property
    def workspace_manifest(
        self,
    ) -> Path:
        return (
            self.internal_dir
            / "workspace.json"
        )

    @property
    def microphone_audio(
        self,
    ) -> Path:
        return (
            self.audio_dir
            / "Microfono.wav"
        )

    @property
    def system_audio(
        self,
    ) -> Path:
        return (
            self.audio_dir
            / "Sistema.wav"
        )

    @property
    def meeting_audio(
        self,
    ) -> Path:
        return (
            self.audio_dir
            / "Reunion.wav"
        )

    @property
    def transcript_json(
        self,
    ) -> Path:
        return (
            self.internal_dir
            / "transcript.json"
        )

    @property
    def summary_json(
        self,
    ) -> Path:
        """
        Ruta histórica del artefacto Summary.

        Se conserva temporalmente mientras MeetingReport
        completa su integración con el pipeline.
        """

        return (
            self.internal_dir
            / "summary.json"
        )

    @property
    def meeting_report_json(
        self,
    ) -> Path:
        """
        Representación estructurada persistente del
        MeetingReport.
        """

        return (
            self.internal_dir
            / "meeting_report.json"
        )

    @property
    def processing_metrics_json(
        self,
    ) -> Path:
        return (
            self.internal_dir
            / "processing_metrics.json"
        )

    @property
    def metadata_json(
        self,
    ) -> Path:
        return (
            self.internal_dir
            / "metadata.json"
        )

    @property
    def summary_markdown(
        self,
    ) -> Path:
        """
        Documento histórico generado desde Summary.
        """

        return (
            self.documents_dir
            / "Resumen.md"
        )

    @property
    def meeting_report_markdown(
        self,
    ) -> Path:
        """
        Documento formal generado desde MeetingReport.
        """

        return (
            self.documents_dir
            / "Meeting Report.md"
        )
