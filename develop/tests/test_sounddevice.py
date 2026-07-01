import sounddevice as sd

print("\n===== DISPOSITIVOS DE AUDIO =====\n")

for index, device in enumerate(sd.query_devices()):
    print(f"[{index}] {device['name']}")