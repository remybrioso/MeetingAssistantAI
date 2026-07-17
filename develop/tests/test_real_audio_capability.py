from services.setup.capabilities.audio_capability import (
    AudioCapability,
)
from services.setup.capabilities.capability_result import (
    CapabilityStatus,
)
from services.setup.capabilities.capability_runner import (
    CapabilityRunner,
)


result = CapabilityRunner().run(
    AudioCapability()
)

print("=" * 60)
print("MAI REAL AUDIO CAPABILITY")
print("=" * 60)

print()
print(f"Estado: {result.status.value}")
print(f"Mensaje: {result.message}")

print()

for key, value in result.details.items():

    print(f"{key}: {value}")

print()

for task_result in result.task_results:

    print(
        f"[{task_result.status.value}] "
        f"{task_result.name}"
    )

    print(
        f"  {task_result.message}"
    )

    if task_result.error:
        print(
            f"  Error: {task_result.error}"
        )

assert result.status in {
    CapabilityStatus.AVAILABLE,
    CapabilityStatus.DEGRADED,
}

assert (
    result.details[
        "microphone_available"
    ]
    is True
)

print()
print(
    "La capacidad real de audio "
    "es utilizable."
)