from application.dependency_container import container
from services.setup.capabilities.capability_registry import (
    CapabilityRegistry,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)
from services.setup.wizard.setup_wizard_service import (
    SetupWizardService,
)


def test_setup_wizard_dependencies_are_registered() -> None:
    registry = container.get(
        "capability_registry"
    )

    runner = container.get(
        "capability_runner"
    )

    wizard = container.get(
        "setup_wizard_service"
    )

    assert isinstance(
        registry,
        CapabilityRegistry,
    )

    assert isinstance(
        runner,
        CapabilityRunner,
    )

    assert isinstance(
        wizard,
        SetupWizardService,
    )

    registered_capability_ids = {
        capability.capability_id
        for capability in registry.get_all()
    }

    assert registered_capability_ids == {
        "runtime-resources",
        "workspace",
        "transcription",
        "artificial-intelligence",
        "audio",
    }

    assert len(registry) == 5

    for capability_id in (
        "runtime-resources",
        "workspace",
        "transcription",
        "artificial-intelligence",
        "audio",
    ):
        assert (
            registry.get(
                capability_id
            )
            is not None
        )
