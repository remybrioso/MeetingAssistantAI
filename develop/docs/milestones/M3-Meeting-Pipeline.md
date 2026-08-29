# M3 - Meeting Pipeline

## Versión

v0.8.0-alpha.1

## Estado

✅ Completado

## Objetivo del Milestone

Automatizar el flujo completo de una reunión desde la interfaz
gráfica sin convertir a los controladores en orquestadores de
procesamiento.

El usuario puede:

1. Iniciar una reunión.
2. Grabar micrófono y audio del sistema.
3. Finalizar la reunión.
4. Generar automáticamente `transcript.json`.
5. Recibir retroalimentación visual del procesamiento.
6. Importar una reunión para procesarla con el mismo pipeline.

## Resultado implementado

La arquitectura productiva separa:

```text
GUI / Controllers
        |
        v
MeetingFinalizationService / ImportedMeetingService
        |
        v
Transcript Service + Storage
        |
        v
MeetingPipelineService
```

El procesamiento que puede tardar no debe bloquear el hilo
principal de la interfaz.

## Capacidades consolidadas

- Captura dual de audio.
- `RecordingSession` y `MeetingWorkspace`.
- Transcripción automática.
- Persistencia de `transcript.json`.
- Procesamiento asíncrono respecto de la GUI.
- Flujo de reuniones grabadas.
- Flujo de reuniones importadas.
- Setup Wizard para validar capacidades del entorno.

## Riesgos mitigados

- El controlador no concentra la lógica del pipeline.
- El trabajo pesado no debe ejecutarse en el hilo de la GUI.
- La persistencia del transcript pertenece a servicios dedicados.
- La sesión y el workspace mantienen rutas explícitas de artefactos.

## Cierre

M3 dejó preparado el dominio de reunión y el transcript como
fuente confiable para el milestone M4.
