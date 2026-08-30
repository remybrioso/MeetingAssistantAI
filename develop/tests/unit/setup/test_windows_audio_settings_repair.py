import pytest

from services.setup.repair_action import RepairAction
from services.setup.repairs.windows_audio_settings_repair import (
    WINDOWS_SOUND_SETTINGS_URI,
    WindowsAudioSettingsRepair,
)


@pytest.mark.parametrize(
    "action",
    [
        RepairAction.CONFIGURE_MICROPHONE,
        RepairAction.CONFIGURE_SYSTEM_AUDIO,
        RepairAction.REPAIR_AUDIO_DEVICES,
    ],
)
def test_audio_settings_repair_opens_windows_sound_settings(
    action,
) -> None:
    opened = []

    repair = WindowsAudioSettingsRepair(
        action=action,
        settings_opener=(
            lambda uri: (
                opened.append(uri)
                or True
            )
        ),
    )

    result = repair(
        {
            "capability_id": "audio",
        }
    )

    assert opened == [
        WINDOWS_SOUND_SETTINGS_URI
    ]
    assert result.user_action_required is True
    assert result.action == action
    assert (
        result.details["settings_uri"]
        == WINDOWS_SOUND_SETTINGS_URI
    )
    assert (
        result.details["capability_id"]
        == "audio"
    )


def test_audio_settings_repair_reports_false_result() -> None:
    repair = WindowsAudioSettingsRepair(
        action=RepairAction.CONFIGURE_MICROPHONE,
        settings_opener=lambda uri: False,
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "settings-open-returned-false"
    )


def test_audio_settings_repair_reports_exception() -> None:
    def failing_opener(uri):
        raise RuntimeError(
            "settings unavailable"
        )

    repair = WindowsAudioSettingsRepair(
        action=(
            RepairAction.CONFIGURE_SYSTEM_AUDIO
        ),
        settings_opener=failing_opener,
    )

    result = repair({})

    assert result.failed is True
    assert (
        result.details["reason"]
        == "settings-open-failed"
    )
    assert (
        result.details["error"]
        == "settings unavailable"
    )


def test_audio_settings_repair_rejects_unsupported_action() -> None:
    with pytest.raises(
        ValueError,
        match="acciones de reparación de audio",
    ):
        WindowsAudioSettingsRepair(
            action=RepairAction.REPAIR_WORKSPACE
        )


def test_audio_settings_repair_rejects_empty_uri() -> None:
    with pytest.raises(
        ValueError,
        match="settings_uri no puede estar vacío",
    ):
        WindowsAudioSettingsRepair(
            action=RepairAction.REPAIR_AUDIO_DEVICES,
            settings_uri="   ",
        )
