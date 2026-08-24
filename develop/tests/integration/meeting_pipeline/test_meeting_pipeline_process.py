from pathlib import Path

import pytest
from requests.exceptions import ReadTimeout

from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from models.artifacts.meeting_report import MeetingReport
from models.recording_session import RecordingSession
from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.meeting_pipeline_service import (
    MeetingPipelineService,
)
from services.meeting_report_generator import (
    MeetingReportGenerator,
)
from services.meeting_report_markdown_exporter import (
    MeetingReportMarkdownExporter,
)
from services.workspace_service import WorkspaceService


@pytest.mark.integration
def test_meeting_pipeline_processes_latest_existing_meeting() -> None:
    session_dirs = sorted(
        Path("output").glob(
            "meeting_*"
        ),
        reverse=True,
    )

    if not session_dirs:
        pytest.skip(
            "No hay reuniones disponibles en "
            "output/meeting_*."
        )

    latest = next(
        (
            session_dir
            for session_dir in session_dirs
            if (
                session_dir
                / ".mai"
                / "transcript.json"
            ).exists()
        ),
        None,
    )

    if latest is None:
        pytest.skip(
            "No existe una reunión con "
            "transcript.json."
        )

    class ExistingRecordingSession(
        RecordingSession
    ):

        def __post_init__(
            self,
        ) -> None:
            self.session_dir = latest
            self.session_name = latest.name

            workspace = (
                WorkspaceService()
                .create(
                    latest
                )
            )

            self.attach_workspace(
                workspace
            )

    pipeline = MeetingPipelineService(
        artifact_generator=(
            MeetingReportGenerator()
        ),
        storage_service=(
            ArtifactStorageService()
        ),
        markdown_exporter=(
            MeetingReportMarkdownExporter()
        ),
    )

    session = ExistingRecordingSession()

    try:
        report = pipeline.process(
            session
        )

    except InsufficientTranscriptEvidenceError:
        pytest.skip(
            "La reunión existente no contiene "
            "evidencia suficiente para generar "
            "un MeetingReport."
        )

    except ReadTimeout:
        pytest.skip(
            "Ollama superó el tiempo máximo de "
            "respuesta durante la prueba real."
        )

    except ValueError as ex:
        if str(ex).startswith(
            "MeetingReport inválido:"
        ):
            pytest.skip(
                "El proveedor de IA devolvió un "
                "MeetingReport que no superó la "
                "validación semántica: "
                f"{ex}"
            )

        raise

    assert isinstance(
        report,
        MeetingReport,
    )

    assert (
        report.artifact_type
        == "meeting_report"
    )

    assert (
        report.prompt_version
        == "meeting_report_v1"
    )

    assert (
        session.workspace
        .meeting_report_json
        .exists()
    )

    assert (
        session.workspace
        .meeting_report_markdown
        .exists()
    )

    markdown = (
        session.workspace
        .meeting_report_markdown
        .read_text(
            encoding="utf-8"
        )
    )

    assert (
        f"# {report.title}"
        in markdown
    )

    assert (
        "## Resumen ejecutivo"
        in markdown
    )