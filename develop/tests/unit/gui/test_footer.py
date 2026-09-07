import application.app_info as app_info

from gui.components.footer import (
    DEVELOPER_ATTRIBUTION,
    build_about_metadata,
    build_attribution_text,
)


def test_attribution_text_uses_application_name_and_exact_developer() -> None:
    text = build_attribution_text()

    assert app_info.APP_NAME in text
    assert DEVELOPER_ATTRIBUTION in text
    assert "Remy Brioso" in text


def test_attribution_text_uses_current_version_dynamically(monkeypatch) -> None:
    monkeypatch.setattr(
        app_info,
        "VERSION",
        "test-version",
    )

    assert build_attribution_text().endswith(
        "vtest-version"
    )
    assert "0.9.0-alpha.3" not in build_attribution_text()


def test_about_metadata_uses_all_application_metadata(monkeypatch) -> None:
    monkeypatch.setattr(
        app_info,
        "APP_NAME",
        "Test Product",
    )
    monkeypatch.setattr(
        app_info,
        "VERSION",
        "test-version",
    )
    monkeypatch.setattr(
        app_info,
        "MILESTONE",
        "Test Milestone",
    )
    monkeypatch.setattr(
        app_info,
        "BUILD",
        "Test Build",
    )

    metadata = build_about_metadata()

    assert metadata == {
        "app_name": "Test Product",
        "version": "vtest-version",
        "developer": DEVELOPER_ATTRIBUTION,
        "milestone": "Test Milestone",
        "build": "Test Build",
    }
