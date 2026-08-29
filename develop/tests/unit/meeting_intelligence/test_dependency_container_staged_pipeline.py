from application.dependency_container import (
    container,
    meeting_artifact_delivery_service,
    meeting_pipeline,
    meeting_report_docx_exporter,
    meeting_report_generator,
    meeting_report_pdf_exporter,
    meeting_report_projection_service,
    staged_chunk_knowledge_service,
    staged_meeting_report_consolidation_service,
)
from services.meeting_artifact_delivery_service import (
    MeetingArtifactDeliveryService,
)
from services.meeting_report_docx_exporter import (
    MeetingReportDocxExporter,
)
from services.meeting_report_pdf_exporter import (
    MeetingReportPdfExporter,
)
from services.meeting_report_projection_service import (
    MeetingReportProjectionService,
)
from services.staged_chunk_knowledge_service import (
    StagedChunkKnowledgeService,
)
from services.staged_meeting_report_consolidation_service import (
    StagedMeetingReportConsolidationService,
)


def test_container_registers_staged_chunk_knowledge_service() -> None:
    registered = container.get(
        "staged_chunk_knowledge_service"
    )

    assert (
        registered
        is staged_chunk_knowledge_service
    )

    assert isinstance(
        registered,
        StagedChunkKnowledgeService,
    )


def test_generator_uses_registered_staged_chunk_service() -> None:
    assert (
        meeting_report_generator
        .chunk_knowledge_service
        is staged_chunk_knowledge_service
    )


def test_container_does_not_register_legacy_chunk_service_alias() -> None:
    assert (
        container.get(
            "chunk_knowledge_service"
        )
        is None
    )


def test_container_does_not_register_legacy_chunk_formatter() -> None:
    assert (
        container.get(
            "chunk_prompt_formatter"
        )
        is None
    )


def test_container_registers_staged_global_consolidation_service() -> None:
    registered = container.get(
        "staged_meeting_report_consolidation_service"
    )

    assert (
        registered
        is staged_meeting_report_consolidation_service
    )

    assert isinstance(
        registered,
        StagedMeetingReportConsolidationService,
    )


def test_generator_uses_registered_staged_global_service() -> None:
    assert (
        meeting_report_generator
        .consolidation_service
        is staged_meeting_report_consolidation_service
    )


def test_container_does_not_register_legacy_global_service_alias() -> None:
    assert (
        container.get(
            "meeting_report_consolidation_service"
        )
        is None
    )


def test_container_does_not_register_legacy_global_formatter() -> None:
    assert (
        container.get(
            "meeting_knowledge_prompt_formatter"
        )
        is None
    )


def test_registered_global_service_uses_expected_contracts() -> None:
    service = (
        staged_meeting_report_consolidation_service
    )

    assert (
        service.SEMANTIC_CONSOLIDATION_CONTRACT
        == "meeting_semantic_consolidation_v1"
    )

    assert (
        service.NARRATIVE_CONTRACT
        == "meeting_report_narrative_v1"
    )

    assert (
        service.FINAL_PIPELINE_VERSION
        == "meeting_report_global_staged_v1"
    )


def test_container_does_not_register_legacy_summary_services() -> None:
    assert (
        container.get(
            "summary_service"
        )
        is None
    )

    assert (
        container.get(
            "summary_validator"
        )
        is None
    )

    assert (
        container.get(
            "summary_markdown_exporter"
        )
        is None
    )


def test_container_does_not_register_legacy_transcript_prompt_formatter() -> None:
    assert (
        container.get(
            "transcript_prompt_formatter"
        )
        is None
    )


def test_container_registers_report_projection_service() -> None:
    registered = container.get(
        "meeting_report_projection_service"
    )

    assert (
        registered
        is meeting_report_projection_service
    )

    assert isinstance(
        registered,
        MeetingReportProjectionService,
    )


def test_container_registers_docx_exporter() -> None:
    registered = container.get(
        "meeting_report_docx_exporter"
    )

    assert (
        registered
        is meeting_report_docx_exporter
    )

    assert isinstance(
        registered,
        MeetingReportDocxExporter,
    )


def test_container_registers_pdf_exporter() -> None:
    registered = container.get(
        "meeting_report_pdf_exporter"
    )

    assert (
        registered
        is meeting_report_pdf_exporter
    )

    assert isinstance(
        registered,
        MeetingReportPdfExporter,
    )


def test_container_registers_artifact_delivery_service() -> None:
    registered = container.get(
        "meeting_artifact_delivery_service"
    )

    assert (
        registered
        is meeting_artifact_delivery_service
    )

    assert isinstance(
        registered,
        MeetingArtifactDeliveryService,
    )


def test_pipeline_uses_registered_artifact_delivery_service() -> None:
    assert (
        meeting_pipeline
        .artifact_delivery_service
        is meeting_artifact_delivery_service
    )


def test_delivery_service_uses_registered_projection_service() -> None:
    assert (
        meeting_artifact_delivery_service
        .projection_service
        is meeting_report_projection_service
    )


def test_delivery_service_uses_registered_document_exporters() -> None:
    assert (
        meeting_artifact_delivery_service
        .docx_exporter
        is meeting_report_docx_exporter
    )

    assert (
        meeting_artifact_delivery_service
        .pdf_exporter
        is meeting_report_pdf_exporter
    )
