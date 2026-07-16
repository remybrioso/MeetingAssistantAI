# MSRE-005 - Workspace Capability

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Representar como una capacidad funcional la posibilidad
de crear, escribir y organizar los Workspaces de reuniones.

## Tareas agrupadas

- InitializeOutputDirectoryTask
- VerifyTemporaryWorkspaceTask

## Estados

### AVAILABLE

La carpeta base está disponible y MAI puede crear,
escribir, validar y eliminar un Workspace temporal.

### UNAVAILABLE

La carpeta base o la estructura del Workspace no pueden
utilizarse correctamente.

## Reparación

Cuando la capacidad no está disponible:

- repairable: true
- repair_action: REPAIR_WORKSPACE

## Archivos

- services/setup/capabilities/workspace_capability.py
- tests/test_workspace_capability.py
- tests/test_workspace_capability_existing_output.py
- tests/test_workspace_capability_invalid_output.py
- tests/test_workspace_capability_registry.py
- tests/test_real_workspace_capability.py

## Criterios de aceptación

- La capacidad agrupa las dos tareas del Workspace.
- Una carpeta ausente se crea automáticamente.
- Una carpeta existente se valida sin recrearse.
- El Workspace temporal se crea y elimina.
- Una ruta inválida devuelve UNAVAILABLE.
- Los resultados técnicos permanecen disponibles.
- El usuario recibe un estado funcional comprensible.
- La capacidad puede registrarse en CapabilityRegistry.
- No quedan archivos ni carpetas temporales.