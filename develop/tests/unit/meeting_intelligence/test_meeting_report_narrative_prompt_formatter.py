import json
from pathlib import Path

import pytest

from application.runtime_paths import RuntimePaths
from models.chunk_classification import (
    ChunkKnowledgeKind,
)
from models.meeting_semantic_consolidation import (
    ConsolidatedMeetingKnowledgeItem,
    MeetingKnowledgeItemReference,
    MeetingSemanticConsolidation,
)
from models.prompt import Prompt
from services.meeting_report_narrative_prompt_formatter import (
    MeetingReportNarrativePromptFormatter,
)


def reference(
    chunk_index: int,
    item_index: int,
) -> MeetingKnowledgeItemReference:
    return MeetingKnowledgeItemReference(
        chunk_index=chunk_index,
        item_index=item_index,
    )


def build_consolidation() -> MeetingSemanticConsolidation:
    return MeetingSemanticConsolidation(
        items=[
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.TOPIC,
                description=(
                    "Arquitectura actual del servicio."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.DECISION,
                description=(
                    "Se aprobó migrar la base de datos."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
            ConsolidatedMeetingKnowledgeItem(
                kind=ChunkKnowledgeKind.ACTION,
                description=(
                    "María preparará el plan de migración."
                ),
                source_refs=[
                    reference(
                        0,
                        0,
                    )
                ],
            ),
        ]
    )


def create_template(
    tmp_path: Path,
    content: str = (
        "Narrativa:\n"
        "{{CONSOLIDATED_ITEMS}}"
    ),
) -> Path:
    path = (
        tmp_path
        / "meeting_report_narrative_v1.md"
    )

    path.write_text(
        content,
        encoding="utf-8",
    )

    return path


def extract_catalog(
    prompt: Prompt,
) -> list[dict]:
    marker = "Narrativa:\n"

    assert prompt.content.startswith(
        marker
    )

    return json.loads(
        prompt.content[
            len(marker):
        ]
    )


def test_formatter_returns_versioned_prompt(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    result = formatter.format(
        build_consolidation()
    )

    assert isinstance(
        result,
        Prompt,
    )
    assert (
        result.version
        == "meeting_report_narrative_v1"
    )
    assert (
        "{{CONSOLIDATED_ITEMS}}"
        not in result.content
    )


def test_formatter_builds_compact_catalog(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    catalog = extract_catalog(
        formatter.format(
            build_consolidation()
        )
    )

    assert catalog == [
        {
            "item_id": 0,
            "kind": "topic",
            "description": (
                "Arquitectura actual del servicio."
            ),
        },
        {
            "item_id": 1,
            "kind": "decision",
            "description": (
                "Se aprobó migrar la base de datos."
            ),
        },
        {
            "item_id": 2,
            "kind": "action",
            "description": (
                "María preparará el plan de migración."
            ),
        },
    ]


def test_formatter_does_not_serialize_g1_source_refs(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    catalog = extract_catalog(
        formatter.format(
            build_consolidation()
        )
    )

    for item in catalog:
        assert set(
            item.keys()
        ) == {
            "item_id",
            "kind",
            "description",
        }


def test_formatter_preserves_unicode(
    tmp_path: Path,
) -> None:
    consolidation = (
        build_consolidation()
    )

    consolidation.items[
        2
    ] = ConsolidatedMeetingKnowledgeItem(
        kind=ChunkKnowledgeKind.ACTION,
        description=(
            "María preparará el plan."
        ),
        source_refs=[
            reference(
                0,
                0,
            )
        ],
    )

    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    result = formatter.format(
        consolidation
    )

    assert "María" in result.content
    assert "\\u00ed" not in result.content


def test_formatter_rejects_empty_consolidation(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="no contiene items suficientes",
    ):
        formatter.format(
            MeetingSemanticConsolidation()
        )


def test_formatter_rejects_invalid_input(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    with pytest.raises(
        TypeError,
        match="MeetingSemanticConsolidation",
    ):
        formatter.format(
            object()
        )


def test_formatter_does_not_mutate_input(
    tmp_path: Path,
) -> None:
    consolidation = (
        build_consolidation()
    )

    original = (
        consolidation.as_dict()
    )

    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path
            )
        )
    )

    formatter.format(
        consolidation
    )

    assert (
        consolidation.as_dict()
        == original
    )


def test_formatter_rejects_missing_placeholder(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path,
                content="Sin marcador.",
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="no contiene el marcador",
    ):
        formatter.format(
            build_consolidation()
        )


def test_formatter_rejects_duplicate_placeholder(
    tmp_path: Path,
) -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter(
            template_file=create_template(
                tmp_path,
                content=(
                    "{{CONSOLIDATED_ITEMS}}\n"
                    "{{CONSOLIDATED_ITEMS}}"
                ),
            )
        )
    )

    with pytest.raises(
        ValueError,
        match="más de una ocurrencia",
    ):
        formatter.format(
            build_consolidation()
        )


def test_formatter_resolves_default_contract_template() -> None:
    formatter = (
        MeetingReportNarrativePromptFormatter()
    )

    expected_template = (
        RuntimePaths.resolve()
        .prompts_directory
        / "meeting_report_narrative_v1.md"
    )

    assert (
        formatter.template_file
        == expected_template
    )

    result = formatter.format(
        build_consolidation()
    )

    assert (
        result.version
        == "meeting_report_narrative_v1"
    )
    assert (
        "No conviertas en objetivo"
        in result.content
    )
    assert (
        "Presentación Global de la Reunión"
        in result.content
    )
