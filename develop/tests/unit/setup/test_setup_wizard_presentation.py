from gui.components.setup_wizard_frame import (
    CAPABILITY_PRESENTATION,
)
from services.setup.wizard.setup_wizard_policy import (
    SetupWizardPolicy,
)


EXPECTED_CAPABILITY_ORDER = (
    "runtime-resources",
    "workspace",
    "transcription",
    "artificial-intelligence",
    "audio",
)


def test_setup_wizard_presents_all_required_capabilities() -> None:
    policy = SetupWizardPolicy()

    assert (
        set(CAPABILITY_PRESENTATION)
        == policy.required_capability_ids
    )


def test_setup_wizard_presentation_matches_diagnostic_order() -> None:
    assert (
        tuple(CAPABILITY_PRESENTATION)
        == EXPECTED_CAPABILITY_ORDER
    )


def test_setup_wizard_presentation_has_visible_content() -> None:
    for presentation in CAPABILITY_PRESENTATION.values():
        assert presentation["name"].strip()
        assert presentation["description"].strip()
