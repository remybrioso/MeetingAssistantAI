from pathlib import Path

import pytest
from requests.exceptions import ReadTimeout

from exceptions.insufficient_transcript_evidence_error import (
    InsufficientTranscriptEvidenceError,
)
from services.artifact_storage_service import (
    ArtifactStorageService,
)
from services.imported_meeting_service import (
    ImportedMeetingService,
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
from services.transcript_service import (
    TranscriptService,
)
from services.transcript_storage_service import (
    TranscriptStorageService,
)
from services.workspace_service import (
    WorkspaceService,
)


def find_test_wav() -> Path | None:
    candidates = list(
        Path("output").glob(
            "meeting_*/mic.wav"
        )
    )

    candidates.extend(
        Path("output").glob(
            "meeting_*/Audio/Reunion.wav"
        )
    )

    valid_candidates = [
        file
        for file in candidates
        if file.exists()
        and file.stat().st_size > 0
    ]

    if not valid_candidates:
        return None

    return max(
        valid_candidates,
        key=lambda file: (
            file.stat().st_mtime
        ),
    )


@pytest.mark.integration
def test_imported_meeting_service_imports_wav() -> None:
    source_file = find_test_wav()

    if source_file is None:
        pytest.skip(
            "No existe un archivo WAV válido "
            "para importar."
        )

    transcript_storage_service = (
        TranscriptStorageService()
    )

    meeting_pipeline = MeetingPipelineService(
        artifact_generator=(
            MeetingReportGenerator()
        ),
        transcript_storage_service=(
            transcript_storage_service
        ),
        storage_service=(
            ArtifactStorageService()
        ),
        markdown_exporter=(
            MeetingReportMarkdownExporter()
        ),
    )

    service = ImportedMeetingService(
        workspace_service=WorkspaceService(),
        transcript_service=TranscriptService(),
        transcript_storage_service=(
            transcript_storage_service
        ),
        meeting_pipeline=meeting_pipeline,
    )

    try:
        session = service.import_wav(
            source_file
        )

    except InsufficientTranscriptEvidenceError:
        pytest.skip(
            "El archivo WAV de integración no "
            "contiene evidencia suficiente para "
            "generar un MeetingReport."
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

    workspace = session.workspace

    assert workspace is not None

    assert (
        workspace.meeting_audio.exists()
    )

    assert (
        workspace.transcript_json.exists()
    )

    assert (
        workspace.processing_metrics_json.exists()
    )

    assert (
        workspace.meeting_report_json.exists()
    )

    assert (
        workspace.meeting_report_markdown.exists()
    )

    markdown = (
        workspace.meeting_report_markdown
        .read_text(
            encoding="utf-8"
        )
    )

    assert "# " in markdown

    assert (
        "## Resumen ejecutivo"
        in markdown
    )
