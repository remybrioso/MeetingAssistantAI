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
        Ejecuta el pipeline completo.

        Devuelve Summary.
        """

        transcript_file = (
        recording_session.session_dir /
        "transcript.json"
        )
        summary = self.summary_service.generate_from_transcript(
        transcript_file
        )
        valid, errors = self.validator.validate(summary)

        artifacts_dir = (
        recording_session.session_dir /
        "artifacts"
        )
        summary_json = artifacts_dir / "summary.json"
        summary_md = artifacts_dir / "summary.md"

        self.storage_service.save(
        summary,
        summary_json
        )

        self.markdown_exporter.export(
        summary,
        summary_md
        )

        return summary
