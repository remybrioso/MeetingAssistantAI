import pytest

from services.meeting_report_parser import MeetingReportParser


def build_parser() -> MeetingReportParser:
    return MeetingReportParser()


def parse_report(response: str):
    return build_parser().parse(
        response=response,
        provider="ollama",
        model="qwen2.5:3b",
        prompt_version="meeting_report_v1",
    )


def base_response(section: str) -> str:
    return f"""
    {{
        \"title\": \"Reunión técnica\",
        \"executive_summary\": \"Se revisó el estado general del proyecto.\",
        \"key_points\": [
            \"Se revisó el estado actual del proyecto.\"
        ],
        {section}
    }}
    """


def test_parser_ignores_empty_decision_placeholder() -> None:
    response = base_response(
        '"decisions": [{"description": "", "rationale": "", "evidence": []}]'
    )

    report = parse_report(response)

    assert report.decisions == []


def test_parser_rejects_partially_empty_decision() -> None:
    response = base_response(
        '"decisions": [{"description": "", "rationale": "Existe una justificación real.", "evidence": []}]'
    )

    with pytest.raises(
        ValueError,
        match="Decision description no puede estar vacío",
    ):
        parse_report(response)


def test_parser_ignores_empty_risk_placeholder() -> None:
    response = base_response(
        '"risks": [{"description": "", "impact": "", "evidence": []}]'
    )

    report = parse_report(response)

    assert report.risks == []


def test_parser_rejects_partially_empty_risk() -> None:
    response = base_response(
        '"risks": [{"description": "", "impact": "Puede afectar el despliegue.", "evidence": []}]'
    )

    with pytest.raises(
        ValueError,
        match="MeetingRisk description no puede estar vacío",
    ):
        parse_report(response)


def test_parser_ignores_empty_pending_item_placeholder() -> None:
    response = base_response(
        '"pending_items": [{"description": "", "evidence": []}]'
    )

    report = parse_report(response)

    assert report.pending_items == []


def test_parser_ignores_empty_action_item_placeholder() -> None:
    response = base_response(
        '"action_items": [{"description": "", "owner": null, "due_date": null, "status": "unknown", "evidence": []}]'
    )

    report = parse_report(response)

    assert report.action_items == []


def test_parser_rejects_partially_empty_action_item() -> None:
    response = base_response(
        '"action_items": [{"description": "", "owner": {"display_name": "Equipo DBA"}, "due_date": null, "status": "pending", "evidence": []}]'
    )

    with pytest.raises(
        ValueError,
        match="ActionItem description no puede estar vacío",
    ):
        parse_report(response)
