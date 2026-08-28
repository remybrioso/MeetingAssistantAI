# Clasificación de conocimiento de reunión

Clasifica únicamente los segmentos incluidos al final.

Devuelve cada proposición relevante UNA SOLA VEZ dentro de `items`.

## Tipos permitidos

- `decision`: decisión explícitamente aprobada, adoptada, rechazada o elegida.
- `action`: tarea o compromiso concreto que alguien debe ejecutar.
- `risk`: riesgo, problema, bloqueo o impedimento explícito.
- `pending`: asunto explícitamente pendiente, abierto o por confirmar.
- `topic`: asunto sustantivo tratado que no pertenece a las clases anteriores.

## Prioridad de clasificación

1. Decisión explícita → `decision`.
2. Tarea concreta asignada → `action`.
3. Riesgo, problema, bloqueo o impedimento → `risk`.
4. Asunto pendiente, abierto o por confirmar → `pending`.
5. Otro asunto sustantivo → `topic`.

No dupliques una misma proposición entre tipos.

## Reglas

- Usa únicamente información explícita de los segmentos.
- No inventes motivos, impactos, responsables, fechas ni estados.
- `description` debe expresar solo lo que realmente está contenido en la evidencia.
- `segment_ids` debe contener únicamente IDs existentes que respalden directamente el item.
- Si no existe conocimiento sustantivo, devuelve `{"items":[]}`.
- Devuelve únicamente JSON válido, sin Markdown ni explicaciones.

## Segmentos

{{SEGMENTS}}
