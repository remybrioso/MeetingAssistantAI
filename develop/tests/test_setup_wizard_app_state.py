from application.app_state import AppState


state = AppState()

assert (
    state.setup_wizard_status
    == "pending"
)

assert (
    state.setup_wizard_completed
    is False
)

assert (
    state.application_ready
    is False
)

state.set(
    "setup_wizard_status",
    "ready",
)

state.set(
    "setup_wizard_completed",
    True,
)

state.set(
    "application_ready",
    True,
)

assert (
    state.get("setup_wizard_status")
    == "ready"
)

assert (
    state.get("setup_wizard_completed")
    is True
)

assert (
    state.get("application_ready")
    is True
)

print(
    "Estado del Setup Wizard "
    "validado correctamente."
)