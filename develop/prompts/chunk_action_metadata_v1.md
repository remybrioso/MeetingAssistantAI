# Metadatos de acciones de reunión

Recibirás una lista de acciones YA CLASIFICADAS.
No reclasifiques, no agregues ni elimines acciones.

Devuelve EXACTAMENTE una entrada dentro de `actions` por cada
acción recibida y conserva exactamente su `item_index`.

## owner

- Identifica únicamente a la persona, equipo, área o entidad
  explícitamente responsable de ejecutar la acción.
- El valor debe aparecer literalmente dentro del texto de alguno
  de los segmentos de esa acción.
- No uses etiquetas técnicas o de canal como `LOCAL`, `REMOTE`,
  `USER`, `SYSTEM` o similares como responsable.
- Ejemplo:
  `María debe preparar el plan` → `"owner":"María"`.
- Si no existe un responsable explícito → `"owner":null`.

## due_date

- Usa formato `YYYY-MM-DD` únicamente cuando la fecha completa
  pueda obtenerse del texto sin asumir año, calendario actual ni
  fecha de la reunión.
- Ejemplo:
  `antes del 30 de agosto de 2026` → `"2026-08-30"`.
- Si falta información o existe ambigüedad → `null`.

## status

Usa únicamente:

- `pending`: la tarea debe ejecutarse o sigue pendiente.
- `completed`: se afirma explícitamente que la tarea ya fue completada.
- `cancelled`: se afirma explícitamente que fue cancelada.
- `unknown`: el estado no puede determinarse con seguridad.

## Fidelidad

- No inventes responsables, fechas ni estados.
- No cambies `item_index`.
- No devuelvas descripciones ni segment_ids.
- No agregues acciones que no estén en la entrada.
- No omitas acciones.
- Devuelve únicamente JSON válido, sin Markdown ni explicaciones.

## Acciones

{{ACTIONS}}
