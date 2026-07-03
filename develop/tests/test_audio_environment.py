import sounddevice as sd


def print_section(title):
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


print_section("Meeting Assistant AI - Audio Environment Report")

hostapis = sd.query_hostapis()
devices = sd.query_devices()

print_section("HOST APIs")

wasapi_available = False

for index, api in enumerate(hostapis):
    name = api["name"]

    if "WASAPI" in name.upper():
        wasapi_available = True

    print(f"[{index}] {name}")
    print(f"    Default Input : {api['default_input_device']}")
    print(f"    Default Output: {api['default_output_device']}")
    print(f"    Devices       : {api['devices']}")

print_section("INPUT DEVICES")

for index, device in enumerate(devices):
    if device["max_input_channels"] > 0:
        print(f"[{index}] {device['name']}")
        print(f"    Input Channels : {device['max_input_channels']}")
        print(f"    Sample Rate    : {device['default_samplerate']}")
        print(f"    Host API       : {hostapis[device['hostapi']]['name']}")

print_section("OUTPUT DEVICES")

for index, device in enumerate(devices):
    if device["max_output_channels"] > 0:
        print(f"[{index}] {device['name']}")
        print(f"    Output Channels: {device['max_output_channels']}")
        print(f"    Sample Rate    : {device['default_samplerate']}")
        print(f"    Host API       : {hostapis[device['hostapi']]['name']}")

print_section("LOOPBACK CANDIDATES")

for index, device in enumerate(devices):
    hostapi_name = hostapis[device["hostapi"]]["name"]

    if "WASAPI" in hostapi_name.upper() and device["max_output_channels"] > 0:
        print(f"[{index}] {device['name']}")
        print(f"    Host API       : {hostapi_name}")
        print(f"    Output Channels: {device['max_output_channels']}")
        print(f"    Sample Rate    : {device['default_samplerate']}")

print_section("ENVIRONMENT STATUS")

if wasapi_available:
    print("WASAPI: AVAILABLE")
    print("Status: READY FOR LOOPBACK TESTING")
else:
    print("WASAPI: NOT AVAILABLE")
    print("Status: LOOPBACK MAY REQUIRE STEREO MIX OR VB-CABLE")