# MSRE-007 - Audio Capability

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Representar como una capacidad funcional la posibilidad
de capturar el micrófono y el audio reproducido por el equipo.

## Componentes

- AudioHealth
- AudioHealthService
- AudioHealthTask
- AudioCapability

## Estados

### AVAILABLE

Existe un micrófono utilizable y el loopback del altavoz
predeterminado está disponible.

### DEGRADED

El micrófono está disponible, pero no se puede capturar
el audio del sistema.

- repairable: true
- repair_action: CONFIGURE_SYSTEM_AUDIO

### UNAVAILABLE

No existe un micrófono utilizable.

- repairable: true
- repair_action: CONFIGURE_MICROPHONE

## Principios

- El diagnóstico no inicia grabaciones.
- El diagnóstico no crea archivos de audio.
- No se bloquean los dispositivos.
- No se encienden indicadores de captura.
- El micrófono es obligatorio.
- El audio del sistema admite estado degradado.
- La detección del loopback sigue el comportamiento real
  de SystemAudioEngine.
- DeviceManager continúa suministrando la enumeración
  de dispositivos para configuración y diagnóstico.

## Archivos

- models/audio_health.py
- services/audio_health_service.py
- services/setup/tasks/audio_health_task.py
- services/setup/capabilities/audio_capability.py
- tests/test_audio_health_service.py
- tests/test_audio_capability.py
- tests/test_audio_capability_degraded.py
- tests/test_audio_capability_no_microphone.py
- tests/test_audio_capability_service_failure.py
- tests/test_audio_capability_registry.py
- tests/test_real_audio_capability.py

## Criterios de aceptación

- Se detecta un micrófono disponible.
- Se detecta el loopback del altavoz predeterminado.
- No se inicia una grabación durante el diagnóstico.
- AVAILABLE requiere micrófono y audio del sistema.
- DEGRADED requiere al menos micrófono.
- UNAVAILABLE se utiliza cuando falta el micrófono.
- La capacidad propone la reparación adecuada.
- Los detalles técnicos permanecen disponibles.
- La capacidad puede registrarse.
- La prueba real no crea archivos de audio.