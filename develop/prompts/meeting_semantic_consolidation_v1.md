# Consolidación semántica global por referencias

Recibirás un catálogo compacto de conocimiento ya extraído de todos
los chunks de una reunión.

Tu única tarea es consolidar semánticamente los items del catálogo.

No redactes todavía el título, objetivo, resumen ejecutivo ni puntos
clave del MeetingReport.

## Regla de cobertura exacta

Cada item del catálogo fuente debe aparecer en exactamente una
`source_ref` de la respuesta.

Por tanto:

- no omitas ningún item fuente;
- no reutilices un item fuente en más de un item consolidado;
- no inventes referencias;
- copia exactamente `chunk_index` e `item_index`;
- una referencia pertenece al mismo `kind` del item consolidado.

## Consolidación

Los `kind` permitidos son únicamente:

- `topic`
- `decision`
- `action`
- `risk`
- `pending`

Solo puedes fusionar items que:

1. tengan el mismo `kind`; y
2. representen realmente el mismo hecho semántico.

Si dos items son parecidos pero expresan hechos distintos, deben
permanecer separados.

No conviertas un `topic` en `decision`, `action`, `risk` o `pending`.

No cambies la categoría semántica de ningún item fuente.

## Acciones

El catálogo puede incluir `owner`, `due_date` y `status` únicamente
para ayudarte a distinguir acciones.

No devuelvas esos campos.

No fusiones acciones cuando su responsable, fecha, estado o alcance
sean incompatibles.

## Descripción consolidada

`description` debe representar fielmente todas las referencias fuente
del item consolidado.

No inventes hechos ausentes del catálogo.

## Campos prohibidos

No devuelvas:

- evidencia;
- speaker;
- timestamps;
- excerpt;
- owner;
- due_date;
- status;
- title global;
- objective;
- executive_summary;
- key_points;
- participants;
- conclusions.

El sistema reconstruirá determinísticamente la evidencia y la metadata
estructurada a partir de `source_refs`.

## Formato

Devuelve únicamente JSON válido compatible con el schema solicitado.

No incluyas Markdown ni explicaciones.

## Catálogo fuente

{{SOURCE_CATALOG}}
