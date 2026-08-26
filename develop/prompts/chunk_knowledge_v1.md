# Extracción estructurada de conocimiento de un bloque de reunión

Analiza ÚNICAMENTE el bloque de transcripción incluido al final.

Tu tarea no es redactar el informe final de la reunión. Extrae conocimiento estructurado y verificable que será consolidado posteriormente con el conocimiento de otros bloques.

## Reglas de fidelidad

1. No inventes información.
2. No completes información implícita como si hubiera sido expresada explícitamente.
3. Si una sección no contiene información suficiente, devuelve una lista vacía `[]`.
4. No generes objetos vacíos, cadenas vacías ni placeholders para completar el esquema.
5. No incluyas `chunk_index`, `index`, `start` o `end` como campos raíz de la respuesta.
6. Devuelve únicamente el objeto JSON solicitado, sin Markdown ni explicaciones.

## Reglas semánticas

- `key_points`: solo hechos relevantes presentes en este bloque; puede ser `[]`.
- `conclusions`: solo conclusiones realmente expresadas o inequívocamente establecidas en este bloque; puede ser `[]`.
- `topics`: solo temas sustantivos tratados en el bloque.
- `decisions`: solo decisiones realmente adoptadas, acordadas, aprobadas, rechazadas o seleccionadas. No conviertas sugerencias, posibilidades, preguntas u opiniones en decisiones.
- `action_items`: solo tareas o compromisos concretos. No conviertas posibilidades futuras, despedidas, frases de cortesía o intenciones vagas en acciones.
- `owner`: solo cuando el responsable esté explícitamente identificado; en caso contrario, `null`.
- `due_date`: solo cuando la fecha pueda normalizarse sin asumir el año, la fecha de la reunión ni el calendario actual; si existe ambigüedad, `null`.
- `status`: usa únicamente `unknown`, `pending`, `completed` o `cancelled`. Si no fue expresado claramente, usa `unknown`.
- `risks`: solo riesgos, bloqueos, problemas o impedimentos realmente expresados.
- `pending_items`: solo asuntos explícitamente abiertos, sin resolver, por confirmar o pendientes.
- `participants`: no inventes nombres ni roles. `name` y `role` deben ser `null` si no pueden identificarse. No generes un participante con todos sus campos en `null`.

## Evidencia obligatoria

Cada elemento de `topics`, `decisions`, `action_items`, `risks` y `pending_items` debe contener al menos una referencia de `evidence`.

Para cada referencia:

- `evidence.excerpt` debe copiar LITERALMENTE una frase o fragmento del campo `text` de UN SOLO segmento. No parafrasees.
- `evidence.speaker` debe ser exactamente el `speaker` de ese mismo segmento.
- Usa como `evidence.start` y `evidence.end` exactamente los valores `start` y `end` de ese segmento.
- No combines texto de segmentos diferentes dentro de un mismo `excerpt`.
- Si una afirmación no tiene evidencia textual verificable, no la incluyas.

## Bloque de transcripción

{{CHUNK}}
