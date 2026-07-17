# MSRE-008 - Setup Wizard Orchestrator

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Orquestar todas las capacidades funcionales de MAI
y producir un resultado global comprensible para el usuario.

## Componentes

- SetupWizardStatus
- SetupWizardResult
- SetupWizardPolicy
- SetupWizardService
- DefaultCapabilityRegistry

## Capacidades iniciales

- workspace
- artificial-intelligence
- audio

## Estados globales

### READY

Todas las capacidades requeridas están disponibles.

### ATTENTION

MAI puede continuar, pero existe al menos una capacidad
degradada o una capacidad opcional no disponible.

### BLOCKED

Existe al menos una capacidad requerida no disponible.

## Reglas

- AVAILABLE permite continuar.
- DEGRADED permite continuar cuando la política lo autoriza.
- UNAVAILABLE bloquea cuando la capacidad es requerida.
- Las capacidades opcionales no bloquean el sistema.
- La política determina qué capacidades son requeridas.
- El asistente no ejecuta tareas directamente.
- CapabilityRunner continúa siendo el único ejecutor
  funcional de capacidades.
- SetupEngine continúa siendo el único ejecutor de tareas.
- El resultado global conserva todos los diagnósticos
  y acciones de reparación.

## Eventos

- setup_wizard_started
- setup_wizard_capability_started
- setup_wizard_capability_completed
- setup_wizard_completed
- setup_wizard_capability_retry_started
- setup_wizard_capability_retry_completed

## Funciones

- run()
- refresh()
- rerun_capability()
- get_capability()
- get_unavailable()
- get_degraded()
- get_repairable()

## Archivos

- services/setup/wizard/__init__.py
- services/setup/wizard/setup_wizard_result.py
- services/setup/wizard/setup_wizard_policy.py
- services/setup/wizard/setup_wizard_service.py
- services/setup/default_capability_registry.py
- application/dependency_container.py
- tests/test_setup_wizard_ready.py
- tests/test_setup_wizard_attention.py
- tests/test_setup_wizard_blocked.py
- tests/test_setup_wizard_rerun_capability.py
- tests/test_setup_wizard_events.py
- tests/test_setup_wizard_container.py
- tests/test_real_setup_wizard.py

## Criterios de aceptación

- Todas las capacidades registradas se ejecutan.
- Se genera un resultado global READY.
- Se genera un resultado global ATTENTION.
- Se genera un resultado global BLOCKED.
- DEGRADED puede continuar según la política.
- UNAVAILABLE requerido bloquea.
- Las capacidades pueden repetirse individualmente.
- Se emiten eventos de progreso.
- El último resultado queda disponible.
- El servicio está registrado en DependencyContainer.
- Las reglas de negocio no dependen de la GUI.
- No se crean ciclos de eventos gráficos adicionales.

## Fuera de alcance

- Ejecución automática de reparaciones.
- Descarga real de Ollama.
- Descarga real del modelo.
- Configuración automática de dispositivos.
- Implementación visual del Setup Wizard.
- Persistencia de la finalización del asistente.