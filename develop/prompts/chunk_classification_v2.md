# Clasificación exhaustiva de conocimiento de reunión

Clasifica únicamente los segmentos incluidos al final.

Los valores de `segment_id` son IDs locales de base cero. Usa SOLO los
valores literales de `segment_id` suministrados en el JSON de Segmentos.
Nunca uses la cantidad de segmentos como un ID. Si los IDs suministrados
son 0,1,2,3,4, entonces 5 no existe y nunca debe aparecer en `items` ni en
`ignored_segment_ids`.

Esta tarea es un INVENTARIO SEMÁNTICO EXHAUSTIVO, no un resumen.
No devuelvas solo el asunto principal ni te detengas después de encontrar
una decisión. La existencia de una categoría de mayor prioridad no permite
omitir acciones, riesgos, pendientes o temas presentes en otros segmentos.

Antes de producir el JSON final, inspecciona TODOS los `segment_id`
suministrados, uno por uno y en orden. No finalices la respuesta hasta
haber contabilizado cada `segment_id` exactamente mediante una de estas
dos alternativas:

1. El segmento respalda conocimiento sustantivo de reunión: incluye su
   `segment_id` en uno o más elementos de `items`.
2. El segmento no contiene conocimiento sustantivo de reunión: incluye
   su `segment_id` una sola vez en `ignored_segment_ids`.

Un `segment_id` nunca puede aparecer a la vez en `items` y en
`ignored_segment_ids`. No ignores segmentos que contengan decisiones,
acciones, riesgos, asuntos pendientes o temas sustantivos.

Reserva `ignored_segment_ids` exclusivamente para segmentos puramente
sociales, vacíos, ininteligibles o sin ningún asunto de reunión, por
ejemplo saludos, agradecimientos o confirmaciones sin contenido propio.
Un segmento que indique que se revisó, discutió, analizó o presentó un
asunto concreto contiene un `topic`, aunque no produzca una decisión ni
una acción. Una revisión de arquitectura, capacidad, métricas,
dependencias, estado o planificación es conocimiento sustantivo. Ante la
duda entre `topic` e ignorar un segmento, clasifícalo como `topic`.

Aplica la prioridad de clasificación por separado a CADA proposición de
CADA segmento. Un segmento puede respaldar más de una proposición distinta.
Extrae todas las proposiciones distintas de cada segmento como items.
Varios segmentos pueden respaldar conjuntamente un mismo item; incluye
todos sus IDs en el `segment_ids` de ese item.

## Algoritmo obligatorio por segmento

Para cada segmento, en orden:

1. Decide primero si es puramente social, vacío, ininteligible o carece de
   asunto propio. Solo en ese caso puede ir a `ignored_segment_ids`.
2. En cualquier otro caso, crea al menos un item provisional `topic` para
   su asunto sustantivo.
3. Si la proposición cumple una categoría de mayor prioridad, cambia ese
   item a `decision`, `action`, `risk` o `pending` según corresponda.
4. Conserva como `topic` todo asunto sustantivo que no haya sido promovido.

Nunca descartes el item provisional únicamente porque existan decisiones,
acciones, riesgos o pendientes en otros segmentos.

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

## Ejemplo de cobertura exhaustiva

Para estos segmentos de ejemplo:

```json
[
  {"segment_id":0,"text":"Se aprobó publicar la nueva versión."},
  {"segment_id":1,"text":"Ana enviará el comunicado mañana."},
  {"segment_id":2,"text":"Existe riesgo de retraso del proveedor."},
  {"segment_id":3,"text":"Queda pendiente confirmar el presupuesto."},
  {"segment_id":4,"text":"También revisamos las métricas del servicio."},
  {"segment_id":5,"text":"Gracias a todos."}
]
```

la respuesta debe conservar las cinco proposiciones sustantivas y solo
puede ignorar el saludo de cierre:

```json
{
  "items": [
    {"kind":"decision","description":"Publicar la nueva versión.","segment_ids":[0]},
    {"kind":"action","description":"Ana enviará el comunicado mañana.","segment_ids":[1]},
    {"kind":"risk","description":"Riesgo de retraso del proveedor.","segment_ids":[2]},
    {"kind":"pending","description":"Confirmar el presupuesto.","segment_ids":[3]},
    {"kind":"topic","description":"Métricas del servicio.","segment_ids":[4]}
  ],
  "ignored_segment_ids": [5]
}
```

El ejemplo no forma parte de los segmentos reales que debes clasificar.

## Reglas

- Usa únicamente información explícita de los segmentos.
- No inventes motivos, impactos, responsables, fechas ni estados.
- `description` debe expresar solo lo que realmente está contenido en la evidencia.
- `segment_ids` debe contener únicamente IDs existentes que respalden directamente el item.
- `ignored_segment_ids` debe contener únicamente IDs existentes sin conocimiento sustantivo.
- Si ningún segmento contiene conocimiento sustantivo, devuelve `items` vacío y todos los IDs en `ignored_segment_ids`.
- Verifica antes de responder que no falte ningún ID y que no exista solapamiento.
- Devuelve exactamente los campos raíz `items` e `ignored_segment_ids`.
- Devuelve únicamente JSON válido, sin Markdown ni explicaciones.

## Segmentos

{{SEGMENTS}}

## Verificación final obligatoria

Después de leer los segmentos reales anteriores y antes de responder:

1. Recorre nuevamente todos sus `segment_id` en orden.
2. Confirma que cada segmento inteligible que mencione un asunto concreto
   de la reunión produjo al menos un item, aunque solo describa algo que se
   revisó o discutió.
3. Confirma que `ignored_segment_ids` contiene únicamente contenido sin
   asunto propio, como saludos, agradecimientos o ruido.
4. Compara los IDs presentes en `items` e `ignored_segment_ids` con todos
   los IDs suministrados y comprueba que no falta ninguno ni hay cruces.
5. Solo entonces devuelve el JSON final completo.
