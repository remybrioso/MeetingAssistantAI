from pathlib import Path

from application.app_info import (
    BUILD,
    MILESTONE,
    VERSION,
)


PROJECT_ROOT = Path(
    __file__
).resolve().parents[3]


def test_runtime_version_matches_version_file() -> None:
    release_version = (
        PROJECT_ROOT
        / "VERSION"
    ).read_text(
        encoding="utf-8"
    ).strip()

    assert release_version == f"v{VERSION}"


def test_runtime_version_is_current_release() -> None:
    assert VERSION == "0.9.0-alpha.4"


def test_runtime_milestone_is_ai_pipeline() -> None:
    assert MILESTONE == "AI Pipeline"


def test_build_identifies_current_release_cycle() -> None:
    assert BUILD == "2026-09"
