# Narrativa global grounded de MeetingReport

Recibirás los items semánticos ya consolidados por la etapa G1.

Tu única tarea es redactar:

- un título específico;
- un objetivo solo cuando esté explícitamente respaldado;
- un resumen ejecutivo;
- puntos clave.

Cada texto debe citar los `item_id` que lo respaldan.

## Reglas generales

1. Usa exclusivamente los items suministrados.
2. No inventes hechos, causas, propósitos, responsables, fechas,
   riesgos, decisiones ni conclusiones.
3. `source_item_ids` debe copiar exactamente `item_id` existentes.
4. No devuelvas evidencia, speaker, timestamps, excerpt, owner,
   due_date ni status.
5. No devuelvas topics, decisions, actions, risks ni pending items.
6. Devuelve exclusivamente JSON compatible con el schema.

## Título

El título debe:

- describir el asunto real y distintivo de la reunión;
- contener información temática proveniente de los items;
- evitar títulos genéricos como:
  - "Presentación Global de la Reunión";
  - "Resumen de la Reunión";
  - "Reunión de seguimiento";
  - "Minuta de reunión";
  - "Meeting Summary";
  - "Meeting Report".

`title.source_item_ids` debe contener al menos un item que respalde
el asunto usado en el título.

## Objetivo

`objective` debe ser `null` salvo que el propósito de la reunión esté
explícitamente expresado o directamente descrito por los items.

No conviertas en objetivo:

- una decisión tomada;
- una acción asignada;
- un riesgo;
- un pendiente;
- una simple inferencia sobre lo que "debía buscar" la reunión.

Ejemplo prohibido:

Si el input solo dice "se aprobó migrar" y "María preparará el plan",
NO infieras "el objetivo fue desarrollar y aprobar la estrategia de
migración".

Cuando `objective` no sea `null`, sus `source_item_ids` deben respaldar
directamente el propósito redactado.

## Resumen ejecutivo

`executive_summary` debe representar la reunión completa sin inventar.

Su lista `source_item_ids` debe contener TODOS los `item_id` recibidos,
cada uno exactamente una vez.

## Puntos clave

Cada key point debe representar un hecho importante respaldado por uno
o más items.

No repitas el mismo punto con redacción diferente.

Los key points no necesitan cubrir todos los items: son una selección
de lo más importante.

## Items semánticos consolidados

{{CONSOLIDATED_ITEMS}}
