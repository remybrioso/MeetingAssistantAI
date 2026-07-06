# M3 - Meeting Pipeline

## Versión

v0.8.0-alpha.1

## Objetivo del Milestone

Automatizar el flujo completo de una reunión desde la interfaz gráfica.

El usuario debe poder:

1. Iniciar una reunión.
2. Grabar micrófono y audio del sistema.
3. Finalizar la reunión.
4. Generar automáticamente transcript.json.
5. Recibir retroalimentación visual en la GUI.

---

## Historias previstas

### MAI-026 - MeetingWorkflowService

Crear un servicio de orquestación para coordinar el flujo de reunión.

### MAI-027 - Integración con AppController

Delegar el cierre de reunión al MeetingWorkflowService.

### MAI-028 - Transcripción automática

Generar Transcript al finalizar una reunión.

### MAI-029 - Persistencia automática

Guardar transcript.json automáticamente.

### MAI-030 - Actualización de GUI

Mostrar eventos del proceso en el ActivityPanel.

---

## Riesgos

- La transcripción puede bloquear la interfaz.
- Faster-Whisper puede tardar varios segundos.
- El usuario puede intentar iniciar otra reunión mientras se procesa la anterior.
- Se debe evitar que AppController crezca demasiado.

---

## Decisión arquitectónica

AppController no orquestará directamente el pipeline de reunión.

La orquestación se moverá a:

```text
MeetingWorkflowService