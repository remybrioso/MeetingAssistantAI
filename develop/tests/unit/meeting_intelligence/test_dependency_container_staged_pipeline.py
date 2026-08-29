from application.dependency_container import (
    chunk_knowledge_service,
    container,
    meeting_report_consolidation_service,
    meeting_report_generator,
    staged_chunk_knowledge_service,
    staged_meeting_report_consolidation_service,
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


def test_container_keeps_generic_chunk_service_alias() -> None:
    registered = container.get(
        "chunk_knowledge_service"
    )

    assert (
        registered
        is staged_chunk_knowledge_service
    )
    assert (
        chunk_knowledge_service
        is staged_chunk_knowledge_service
    )


def test_generator_uses_registered_staged_chunk_service() -> None:
    assert (
        meeting_report_generator
        .chunk_knowledge_service
        is staged_chunk_knowledge_service
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


def test_container_keeps_generic_global_consolidation_alias() -> None:
    registered = container.get(
        "meeting_report_consolidation_service"
    )

    assert (
        registered
        is staged_meeting_report_consolidation_service
    )
    assert (
        meeting_report_consolidation_service
        is staged_meeting_report_consolidation_service
    )


def test_generator_uses_registered_staged_global_service() -> None:
    assert (
        meeting_report_generator
        .consolidation_service
        is staged_meeting_report_consolidation_service
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
