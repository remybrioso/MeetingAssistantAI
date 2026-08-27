# Consolidación global de una reunión

Recibirás conocimiento estructurado extraído previamente de TODOS los bloques de una reunión.

Tu tarea es producir un único MeetingReport formal, coherente y global.

NO estás analizando la transcripción original. Trabaja únicamente con el conocimiento y las evidencias incluidas en `MeetingKnowledge`.

## Principio de cobertura total

1. Considera todos los elementos de `chunks`, desde `chunk_index = 0` hasta el último.
2. No favorezcas los últimos chunks por aparecer al final del contexto.
3. Un chunk vacío es válido y no debe provocar contenido inventado.
4. El resumen ejecutivo debe representar la reunión completa, no solo una parte temporal.
5. Los puntos importantes del inicio, mitad y final deben conservarse cuando sean sustantivos.

## Principio de fidelidad

- No inventes hechos, decisiones, acciones, riesgos, responsables, fechas, participantes ni conclusiones.
- No uses conocimiento externo.
- No conviertas posibilidades, sugerencias o frases de cortesía en decisiones o compromisos.
- No conviertas conversaciones exploratorias en asuntos pendientes si no quedaron realmente abiertos.
- Si la evidencia disponible no permite sostener un elemento, no lo incluyas.

## Consolidación y deduplicación

El conocimiento puede repetir un mismo hecho en chunks distintos.

Debes:

- fusionar duplicados semánticos reales;
- conservar hechos distintos aunque sean parecidos;
- evitar repetir el mismo punto con redacciones diferentes;
- combinar evidencias compatibles cuando respaldan el mismo elemento;
- preservar diferencias importantes de contexto, responsable, fecha, estado o alcance.

No elimines información únicamente porque apareció una sola vez: una decisión o acción importante puede existir en un único chunk.

## Evidencia

Los elementos de:

- `topics`
- `decisions`
- `action_items`
- `risks`
- `pending_items`

deben conservar evidencia proveniente del `MeetingKnowledge`.

Para cada referencia de evidencia:

- copia `speaker` sin modificarlo;
- copia `start` sin modificarlo;
- copia `end` sin modificarlo;
- copia `excerpt` sin modificarlo;
- no inventes nuevas referencias;
- no parafrasees `excerpt`;
- no combines fragmentos diferentes para crear una cita nueva.

Si fusionas dos elementos equivalentes de chunks distintos, puedes conservar varias referencias de evidencia originales.

## Título

Genera un título profesional y específico que represente los asuntos centrales de toda la reunión.

No uses títulos genéricos como:

- "Reunión"
- "Reunión técnica"
- "Reunión de seguimiento"

cuando el conocimiento permita un título más descriptivo.

## Objetivo

`objective` debe ser:

- una cadena cuando el propósito principal de la reunión esté claramente respaldado por el conocimiento global;
- `null` cuando no exista evidencia suficiente para establecerlo con seguridad.

No inventes un objetivo únicamente para completar el campo.

## Resumen ejecutivo

Redacta un resumen ejecutivo profesional que:

- represente el contenido global;
- destaque los asuntos realmente importantes;
- refleje decisiones, acciones, riesgos y pendientes cuando existan;
- no introduzca hechos ausentes del conocimiento;
- evite centrarse únicamente en los últimos chunks.

## Puntos clave

`key_points` debe contener los hechos globales más importantes y estar respaldado por el conocimiento recibido.

Deduplica puntos equivalentes.

Debe existir al menos un punto clave en el MeetingReport final.

## Temas

Consolida temas equivalentes cuando pertenezcan al mismo asunto.

Cada tema final debe:

- tener título descriptivo;
- resumir únicamente información respaldada;
- conservar una o más evidencias originales.

## Decisiones

Incluye únicamente decisiones realmente identificadas en los chunks.

Al consolidar:

- fusiona decisiones equivalentes;
- conserva rationale solo cuando esté respaldado;
- conserva evidencias originales.

## Acciones y compromisos

Incluye únicamente tareas o compromisos presentes en el conocimiento.

- No inventes `owner`.
- No inventes `due_date`.
- No cambies `status` sin evidencia.
- Si dos acciones parecen similares pero tienen responsables, fechas o alcance distintos, mantenlas separadas.

## Riesgos y bloqueos

Incluye únicamente riesgos o bloqueos presentes en el conocimiento.

Fusiona duplicados únicamente cuando representen realmente el mismo riesgo.

## Asuntos pendientes

Incluye únicamente asuntos que el conocimiento identifique como abiertos, sin resolver o pendientes.

No conviertas una posibilidad futura en pendiente.

## Participantes

Deduplica participantes únicamente cuando exista identidad suficiente para afirmar que representan a la misma persona.

Una etiqueta como `LOCAL`, `REMOTE`, `USER` o `IMPORTED` es un speaker, no necesariamente el nombre real de una persona.

No inventes nombres ni roles.

## Conclusiones

Incluye únicamente conclusiones respaldadas por el conocimiento global.

Deduplica conclusiones equivalentes.

## Formato de respuesta

Devuelve únicamente JSON válido compatible con el schema solicitado.

No incluyas Markdown.

No incluyas explicaciones antes o después del JSON.

## MeetingKnowledge completo

{{MEETING_KNOWLEDGE}}
