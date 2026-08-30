from pathlib import Path

import pytest

from services.setup.repair_action import RepairAction
from services.setup.repair_result import (
    RepairExecutionStatus,
)
from services.setup.repairs.transcription_model_repair import (
    TranscriptionModelRepair,
)


def test_transcription_repair_downloads_model_online(
    tmp_path: Path,
) -> None:
    calls = []

    model_path = tmp_path / "model"
    model_path.mkdir()

    def downloader(
        model_name,
        *,
        local_files_only,
    ):
        calls.append(
            (
                model_name,
                local_files_only,
            )
        )
        return model_path

    repair = TranscriptionModelRepair(
        model_name="base",
        model_downloader=downloader,
    )

    result = repair(
        {
            "capability_id": "transcription",
        }
    )

    assert calls == [
        (
            "base",
            False,
        )
    ]

    assert result.succeeded is True
    assert (
        result.action
        == RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
    )
    assert (
        result.status
        == RepairExecutionStatus.SUCCESS
    )
    assert result.details["model"] == "base"
    assert (
        result.details["local_files_only"]
        is False
    )
    assert (
        result.details["capability_id"]
        == "transcription"
    )
    assert (
        result.details["model_path"]
        == str(model_path)
    )


def test_transcription_repair_fails_when_path_is_missing(
    tmp_path: Path,
) -> None:
    missing_path = (
        tmp_path / "missing-model"
    )

    repair = TranscriptionModelRepair(
        model_name="base",
        model_downloader=(
            lambda *args, **kwargs: missing_path
        ),
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "model-path-not-found"
    )


def test_transcription_repair_reports_download_error() -> None:
    def downloader(
        model_name,
        *,
        local_files_only,
    ):
        raise RuntimeError(
            "network unavailable"
        )

    repair = TranscriptionModelRepair(
        model_name="base",
        model_downloader=downloader,
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "download-failed"
    )
    assert (
        result.details["error_type"]
        == "RuntimeError"
    )
    assert (
        result.details["error"]
        == "network unavailable"
    )


@pytest.mark.parametrize(
    "model_name",
    [
        "",
        "   ",
    ],
)
def test_transcription_repair_rejects_empty_model(
    model_name,
) -> None:
    with pytest.raises(ValueError):
        TranscriptionModelRepair(
            model_name=model_name
        )


def test_transcription_repair_rejects_non_string_model() -> None:
    with pytest.raises(TypeError):
        TranscriptionModelRepair(
            model_name=None
        )
