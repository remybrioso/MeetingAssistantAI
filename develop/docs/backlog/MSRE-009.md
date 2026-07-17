# MSRE-009 - Setup Wizard UI

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Presentar visualmente el estado de las capacidades de MAI
antes de permitir el acceso a las funciones principales.

## Componentes

- SetupWizardFrame
- SetupCapabilityCard
- Integración con MainWindow
- Integración con AppController
- Estado de preparación en AppState

## Flujo

1. MainWindow construye la interfaz principal.
2. SetupWizardFrame se muestra como overlay.
3. AppController ejecuta SetupWizardService mediante TaskRunner.
4. SetupWizardService emite eventos de progreso.
5. MainWindow redirige los eventos al hilo gráfico con after().
6. Las tarjetas muestran el estado de cada capacidad.
7. READY permite el acceso automáticamente.
8. ATTENTION permite continuar manualmente.
9. BLOCKED impide el acceso.

## Estados visuales

### Pendiente

La capacidad todavía no ha sido comprobada.

### Comprobando

La capacidad está siendo evaluada.

### Disponible

La capacidad funciona correctamente.

### Requiere atención

La capacidad funciona parcialmente.

### No disponible

La capacidad requerida impide continuar.

## Seguridad de hilos

- Los diagnósticos se ejecutan mediante TaskRunner.
- Los widgets no se actualizan desde el worker thread.
- MainWindow utiliza after() para todas las actualizaciones
  relacionadas con el Setup Wizard.
- EventBus continúa siendo síncrono.
- La mejora global del EventBus queda fuera de alcance.

## Protección funcional

- start_meeting() requiere application_ready.
- import_recording() requiere application_ready.
- El overlay visual no es la única protección.
- AppState conserva el estado global del asistente.

## Archivos

- application/app_state.py
- application/app_controller.py
- gui/main_window.py
- gui/components/setup_capability_card.py
- gui/components/setup_wizard_frame.py
- tests/test_setup_wizard_app_state.py
- tests/test_setup_wizard_controller_flow.py

## Criterios de aceptación

- El asistente aparece al iniciar MAI.
- No se crea una segunda ventana raíz.
- No se crea un segundo mainloop.
- Las capacidades muestran progreso.
- READY abre la aplicación automáticamente.
- ATTENTION permite continuar manualmente.
- BLOCKED impide continuar.
- El diagnóstico no congela la interfaz.
- Las actualizaciones del wizard se ejecutan con after().
- El usuario puede repetir el diagnóstico.
- Las reuniones no pueden comenzar si MAI está bloqueado.
- Las importaciones no pueden comenzar si MAI está bloqueado.
- AppState conserva el resultado global.
- Los errores del asistente se muestran sin cerrar MAI.

## Fuera de alcance

- Reparaciones automáticas.
- Instalación de Ollama.
- Descarga del modelo.
- Configuración automática de audio.
- Persistencia entre ejecuciones.
- Traducción de repair_action a comandos ejecutables.
- Corrección global de eventos UI multihilo.

## Deuda técnica registrada

CORE-UI-001 - Thread-safe UI event dispatching.