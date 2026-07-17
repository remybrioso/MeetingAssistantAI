from application.dependency_container import (
    container,
)
from services.setup.wizard.setup_wizard_result import (
    SetupWizardStatus,
)


service = container.get(
    "setup_wizard_service"
)

assert service is not None

result = service.run()

print("=" * 60)
print("MEETING ASSISTANT AI — SETUP WIZARD")
print("=" * 60)

print()
print(f"Estado global: {result.status.value}")
print(f"Mensaje: {result.message}")

print()

for capability in result.capability_results:

    print(
        f"[{capability.status.value}] "
        f"{capability.name}"
    )

    print(
        f"  {capability.message}"
    )

    if capability.repair_action:

        print(
            "  Acción: "
            f"{capability.repair_action}"
        )

    print()

print("-" * 60)

print(
    "Disponibles: "
    f"{result.details['available_count']}"
)

print(
    "Degradadas: "
    f"{result.details['degraded_count']}"
)

print(
    "No disponibles: "
    f"{result.details['unavailable_count']}"
)

print(
    "Puede continuar: "
    f"{result.can_continue}"
)

assert len(
    result.capability_results
) == 3

assert result.status in {
    SetupWizardStatus.READY,
    SetupWizardStatus.ATTENTION,
    SetupWizardStatus.BLOCKED,
}

assert (
    result.get_capability(
        "workspace"
    )
    is not None
)

assert (
    result.get_capability(
        "artificial-intelligence"
    )
    is not None
)

assert (
    result.get_capability(
        "audio"
    )
    is not None
)

print()
print(
    "El Setup Wizard real fue ejecutado."
)