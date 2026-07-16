# MSRE-002 - Output Directory Initialization Task

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Preparar y validar automáticamente la carpeta base donde
MAI almacena los Workspaces de las reuniones.

## Comportamiento

- Crea la carpeta cuando no existe.
- Comprueba que la ruta sea un directorio.
- Valida permisos efectivos de escritura y lectura.
- Elimina los archivos temporales de validación.
- Devuelve SUCCESS cuando realiza la reparación.
- Devuelve SKIPPED cuando la carpeta ya está disponible.
- Devuelve FAILED cuando no puede utilizarse.

## Archivos

- services/setup/tasks/initialize_output_directory_task.py
- tests/test_initialize_output_directory_task.py
- tests/test_initialize_output_directory_invalid_path.py
- tests/test_setup_real_output_directory.py

## Criterios de aceptación

- La tarea crea la carpeta ausente.
- La tarea reconoce una carpeta existente.
- La tarea detecta una ruta ocupada por un archivo.
- La tarea comprueba lectura y escritura reales.
- No deja archivos temporales.
- Los errores se convierten en TaskResult.
- Una carpeta válida no se recrea.
- No se crea un MeetingWorkspace en la raíz de output.