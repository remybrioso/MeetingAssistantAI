# ADR-006 - Versionado del Desarrollo

## Estado

Aceptado

## Fecha

2026-07-06

## Contexto

El proyecto necesita trazabilidad entre historias, versiones y commits.

## Decisión

Toda historia deberá indicar:

- Versión
- Milestone
- Identificador

Toda versión será inmutable una vez publicada.

Los commits incluirán el identificador de la historia.

## Consecuencias

### Positivas

- Mejor auditoría.
- Mejor mantenimiento.
- Release Notes automáticas.
- Historial claro.

### Negativas

- Ligero aumento en la documentación.