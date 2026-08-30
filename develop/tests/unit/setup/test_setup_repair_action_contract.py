from services.setup.repair_action import (
    REPAIR_ACTION_PRESENTATION,
    RepairAction,
)


def test_repair_action_catalog_contains_expected_actions() -> None:
    assert RepairAction.ALL == {
        "REPAIR_APPLICATION_INSTALLATION",
        "REPAIR_WORKSPACE",
        "DOWNLOAD_TRANSCRIPTION_MODEL",
        "INSTALL_AI_PROVIDER",
        "DOWNLOAD_AI_MODEL",
        "REPAIR_AI_CAPABILITY",
        "CONFIGURE_MICROPHONE",
        "CONFIGURE_SYSTEM_AUDIO",
        "REPAIR_AUDIO_DEVICES",
    }


def test_every_repair_action_has_ui_presentation() -> None:
    assert (
        set(REPAIR_ACTION_PRESENTATION)
        == RepairAction.ALL
    )


def test_repair_action_presentations_are_non_empty() -> None:
    for action, message in (
        REPAIR_ACTION_PRESENTATION.items()
    ):
        assert action in RepairAction.ALL
        assert isinstance(message, str)
        assert message.strip()


def test_transcription_model_action_has_specific_guidance() -> None:
    message = REPAIR_ACTION_PRESENTATION[
        RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL
    ]

    assert "modelo" in message.lower()
    assert "transcripción" in message.lower()


def test_application_repair_action_has_specific_guidance() -> None:
    message = REPAIR_ACTION_PRESENTATION[
        RepairAction.REPAIR_APPLICATION_INSTALLATION
    ]

    assert "reinstala" in message.lower()
    assert "meeting assistant ai" in message.lower()
