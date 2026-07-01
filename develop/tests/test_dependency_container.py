from application.dependency_container import container

service1 = container.get("audio_capture_service")
service2 = container.get("audio_capture_service")

print("Objeto 1:", id(service1))
print("Objeto 2:", id(service2))

print()

print("¿Es la misma instancia?", service1 is service2)

assert service1 is service2

print()

print("Prueba satisfactoria.")