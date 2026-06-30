from application.dependency_container import container

state = container.get("app_state")
bus = container.get("event_bus")

print(type(state).__name__)
print(type(bus).__name__)