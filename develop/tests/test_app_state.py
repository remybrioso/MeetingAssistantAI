from application.app_state import AppState


def observer(key, value):
    print(f"{key} -> {value}")


state = AppState()
state.subscribe(observer)

state.set("meeting_active", True)
state.set("audio_status", "recording")