"""
meeting_pipeline_service.py

Orquestador del Knowledge Pipeline.
"""

from pathlib import Path


class MeetingPipelineService:

    def __init__(
        self,
        summary_service,
        validator,
        storage_service,
        markdown_exporter
    ):

        self.summary_service = summary_service
        self.validator = validator
        self.storage_service = storage_service
        self.markdown_exporter = markdown_exporter

    def process(
        self,
        recording_session
    ):
        """
        Ejecuta el Knowledge Pipeline completo.

        Devuelve Summary.
        """

        workspace = recording_session.workspace

        summary = self.summary_service.generate_from_transcript(
            workspace.transcript_json
        )

        valid, errors = self.validator.validate(summary)

        if not valid:
            raise ValueError(
                "Summary inválido: " + "; ".join(errors)
            )

        self.storage_service.save(
            summary,
            workspace.summary_json
        )

        self.markdown_exporter.export(
            summary,
            workspace.summary_markdown
        )

        return summary
