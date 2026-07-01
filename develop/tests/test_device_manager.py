from engines.audio.device_manager import DeviceManager


manager = DeviceManager()

print()
print("===== MICRÓFONOS =====")
print()

for device in manager.get_microphones():
    print(f"{device.id:2} | {device.name}")

print()
print("===== AUDIO DEL SISTEMA =====")
print()

for device in manager.get_system_devices():
    print(f"{device.id:2} | {device.name}")