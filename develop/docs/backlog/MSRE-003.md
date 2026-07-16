# MSRE-003 - Temporary Workspace Verification Task

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Comprobar que MAI puede crear, utilizar y eliminar
un MeetingWorkspace temporal dentro de la carpeta
de salida configurada.

## Comportamiento

- Crea un Workspace temporal.
- Valida las carpetas Audio, Documentos y .mai.
- Valida el archivo workspace.json.
- Comprueba lectura y escritura en cada área.
- Elimina archivos temporales.
- Elimina completamente el Workspace de prueba.
- Devuelve FAILED si la carpeta base no existe.
- No modifica reuniones reales.

## Archivos

- services/setup/tasks/verify_temporary_workspace_task.py
- tests/test_verify_temporary_workspace_task.py
- tests/test_verify_temporary_workspace_missing_output.py
- tests/test_setup_real_temporary_workspace.py

## Criterios de aceptación

- Se crea un Workspace completo.
- Se valida la estructura física.
- Se valida el manifiesto.
- Se comprueba escritura en las tres áreas.
- La carpeta temporal se elimina.
- No quedan residuos.
- Los fallos se convierten en TaskResult.
- La tarea funciona dentro de SetupEngine.