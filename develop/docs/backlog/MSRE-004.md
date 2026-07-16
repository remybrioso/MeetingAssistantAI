# MSRE-004 - Capability Framework

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Representar el estado de MAI mediante capacidades
funcionales comprensibles para el usuario, agrupando
las tareas técnicas internas.

## Componentes

- Capability
- CapabilityResult
- CapabilityStatus
- CapabilityRunner
- CapabilityRegistry

## Estados

- AVAILABLE
- DEGRADED
- UNAVAILABLE

## Principios

- El usuario ve capacidades, no tareas técnicas.
- Una capacidad declara sus tareas.
- Una capacidad interpreta los resultados.
- CapabilityRunner coordina la ejecución.
- CapabilityRegistry permite descubrir capacidades.
- Las capacidades no conocen la GUI.
- Las excepciones se convierten en UNAVAILABLE.

## Criterios de aceptación

- Una capacidad puede registrar sus tareas.
- Las tareas se ejecutan mediante SetupEngine.
- Los resultados se convierten en CapabilityResult.
- El registro rechaza identificadores duplicados.
- Una excepción no se propaga a la aplicación.
- El diseño permite añadir nuevas capacidades sin modificar el motor.