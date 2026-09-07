# Auditoría semántica de segmentos marcados como ignorados

Revisa únicamente los segmentos candidatos incluidos en el JSON final.
La clasificación J1 anterior no es autoritativa: debes desafiarla.

Para cada candidato, devuelve una o más proposiciones semánticas si el
segmento contiene conocimiento sustantivo de reunión. Usa la prioridad:
`decision`, `action`, `risk`, `pending`, `topic`.

Solo devuelve un ID en `confirmed_ignored_segment_ids` cuando el segmento
no contenga ningún conocimiento sustantivo: debe ser social, vacío o
ininteligible. Nunca marques como ignorado un segmento que revise, discuta,
analice o presente un asunto concreto.

Cada candidato debe aparecer en al menos un `segment_ids` de `items` o en
`confirmed_ignored_segment_ids`, nunca en ambos. Usa únicamente los IDs
locales suministrados en `candidate_segment_ids`. No inventes información.

Devuelve el objeto JSON completo con exactamente `items` y
`confirmed_ignored_segment_ids`. Solo JSON, sin explicaciones ni Markdown.

## Segmentos candidatos (JSON)

{{CANDIDATE_SEGMENTS}}
