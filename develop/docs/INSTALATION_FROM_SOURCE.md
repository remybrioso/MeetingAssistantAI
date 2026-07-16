# Instalar Meeting Assistant AI desde el repositorio

> **La tecnología trabaja. Tú solo reúnete.**

Este documento explica cómo preparar un entorno de desarrollo y ejecutar Meeting Assistant AI (MAI) directamente desde el código fuente.

Estas instrucciones están dirigidas a:

* desarrolladores;
* colaboradores;
* evaluadores técnicos;
* personas interesadas en probar MAI desde el repositorio.

El usuario final no necesitará realizar estos pasos cuando exista el instalador oficial.

---

## 1. Requisitos del sistema

### Sistema operativo

Actualmente, MAI está desarrollado y validado principalmente en:

* Windows 10 de 64 bits;
* Windows 11 de 64 bits.

### Hardware recomendado

* Procesador Intel Core i5, AMD Ryzen 5 o superior.
* 16 GB de memoria RAM recomendados.
* Al menos 15 GB de espacio libre.
* Micrófono funcional.
* Dispositivo de audio compatible con captura del sonido del sistema.
* Conexión a Internet para descargar dependencias y modelos.

### Software requerido

* Git.
* Python de 64 bits.
* Ollama.
* Controladores de audio correctamente instalados.

La versión de Python utilizada durante el desarrollo actual de MAI es Python 3.14 de 64 bits.

---

## 2. Clonar el repositorio

Abre PowerShell y ejecuta:

```powershell
git clone <URL-DEL-REPOSITORIO>
cd MeetingAssistantAI
```

Si el desarrollo se realiza en la rama `develop`:

```powershell
git checkout develop
```

Comprueba el estado del repositorio:

```powershell
git status
```

---

## 3. Crear el entorno virtual

Desde la raíz del repositorio:

```powershell
python -m venv .venv
```

Activa el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

El prompt de PowerShell debería mostrar:

```text
(.venv)
```

Si PowerShell bloquea la activación de scripts, ejecuta temporalmente:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

Luego activa nuevamente el entorno:

```powershell
.\.venv\Scripts\Activate.ps1
```

---

## 4. Actualizar las herramientas de instalación

Con el entorno virtual activo:

```powershell
python -m pip install --upgrade pip setuptools wheel
```

---

## 5. Instalar las dependencias de MAI

Ejecuta:

```powershell
pip install -r requirements.txt
```

Las dependencias principales incluyen componentes como:

* CustomTkinter;
* SoundCard;
* SoundFile;
* NumPy;
* Faster-Whisper;
* Requests;
* python-docx;
* Pydantic;
* Pillow.

No instales las dependencias individualmente salvo que estés investigando un problema específico.

---

## 6. Verificar Python y las dependencias

Ejecuta el Health Check:

```powershell
python -m tests.test_health_service
```

El resultado esperado debe incluir:

```text
[OK] Python
[OK] Dependencies
```

Si alguna dependencia aparece como ausente, ejecuta nuevamente:

```powershell
pip install -r requirements.txt
```

Comprueba también que estés utilizando el Python del entorno virtual:

```powershell
Get-Command python
```

La ruta debería apuntar a:

```text
MeetingAssistantAI\.venv\Scripts\python.exe
```

---

## 7. Instalar Ollama

Descarga e instala Ollama para Windows desde su sitio oficial.

Después de instalarlo, abre una terminal nueva y verifica:

```powershell
ollama --version
```

También puedes comprobar los modelos disponibles:

```powershell
ollama list
```

---

## 8. Descargar el modelo de inteligencia artificial

MAI utiliza actualmente:

```text
qwen2.5:3b
```

Descárgalo con:

```powershell
ollama pull qwen2.5:3b
```

Verifica nuevamente:

```powershell
ollama list
```

Debe aparecer `qwen2.5:3b` en la lista.

---

## 9. Verificar el proveedor de IA

Ejecuta:

```powershell
python -m tests.test_ollama_provider_health
```

El resultado esperado debe indicar:

```text
Conectado: True
Modelo encontrado: True
```

Después ejecuta el diagnóstico integrado:

```powershell
python -m tests.test_health_service
```

El informe debería terminar con:

```text
READY FOR USE
```

---

## 10. Modelos de transcripción

MAI utiliza Faster-Whisper para la transcripción local.

La primera ejecución puede descargar automáticamente el modelo configurado de Whisper. Este proceso puede tomar varios minutos dependiendo de la conexión a Internet.

El modelo utilizado actualmente es:

```text
base
```

Los archivos descargados se almacenan en la caché local del usuario y no deben agregarse al repositorio.

---

## 11. Configuración de audio

Antes de iniciar una reunión, confirma:

* que Windows reconoce el micrófono;
* que el micrófono tiene permisos;
* que existe un dispositivo de salida activo;
* que el audio del sistema puede ser capturado;
* que ninguna otra aplicación está bloqueando los dispositivos.

Puedes revisar los dispositivos desde:

```text
Configuración de Windows
→ Sistema
→ Sonido
```

En equipos virtuales, la captura del audio del sistema puede no estar disponible o comportarse de manera diferente a un equipo físico.

---

## 12. Ejecutar MAI

Con el entorno virtual activo y Ollama funcionando:

```powershell
python app.py
```

Si el punto de entrada del proyecto cambia, consulta el archivo `README.md` o la documentación de la versión correspondiente.

---

## 13. Prueba básica de funcionamiento

Realiza una reunión de prueba de entre 30 y 60 segundos:

1. Inicia MAI.
2. Pulsa **Iniciar**.
3. Habla mediante el micrófono.
4. Reproduce algún audio en el equipo, si deseas probar la captura del sistema.
5. Pulsa **Finalizar**.
6. Espera a que termine el procesamiento.

Debe crearse una carpeta similar a:

```text
output/
└── meeting_YYYYMMDD_HHMMSS/
    ├── Audio/
    │   ├── Microfono.wav
    │   └── Sistema.wav
    ├── Documentos/
    │   └── Resumen.md
    └── .mai/
        ├── transcript.json
        ├── processing_metrics.json
        ├── summary.json
        └── workspace.json
```

Comprueba que:

* `Microfono.wav` contenga sonido;
* `transcript.json` contenga la transcripción;
* `summary.json` contenga un resumen válido;
* `Resumen.md` pueda abrirse correctamente.

---

## 14. Probar la importación de una reunión

MAI permite procesar un archivo WAV existente desde la interfaz.

También puede validarse mediante:

```powershell
python -m tests.test_imported_meeting_service
```

La prueba debe generar un Workspace independiente con:

```text
Audio/Reunion.wav
.mai/transcript.json
.mai/summary.json
.mai/processing_metrics.json
Documentos/Resumen.md
```

---

## 15. Pruebas recomendadas

Ejecuta al menos:

```powershell
python -m tests.test_health_service
python -m tests.test_ollama_provider_health
python -m tests.test_missing_ollama_model
python -m tests.test_imported_meeting_service
```

Todas deben terminar sin errores no controlados.

---

## 16. Problemas frecuentes

### `ModuleNotFoundError`

Comprueba que:

* estás en la raíz del repositorio;
* el entorno virtual está activo;
* las dependencias fueron instaladas;
* ejecutas las pruebas con `python -m`;
* las carpetas Python contienen su archivo `__init__.py` cuando corresponda.

Ejemplo correcto:

```powershell
cd C:\Proyectos\MeetingAssistantAI\develop
python -m tests.test_health_service
```

### Ollama no responde

Verifica:

```powershell
ollama list
```

Si el comando no funciona, inicia Ollama y vuelve a ejecutar el diagnóstico.

### Modelo no encontrado

Ejecuta:

```powershell
ollama pull qwen2.5:3b
```

### El audio está vacío

Revisa:

* dispositivo de entrada configurado;
* permisos del micrófono;
* volumen de entrada;
* dispositivo de audio del sistema;
* aplicaciones que estén usando el dispositivo en modo exclusivo.

### La interfaz se congela durante el primer procesamiento

La primera transcripción puede tardar más debido a la descarga y carga inicial del modelo. Si la aplicación deja de responder permanentemente, revisa los logs y ejecuta las pruebas individuales.

---

## 17. Actualizar el repositorio

Antes de comenzar una nueva sesión de desarrollo:

```powershell
git checkout develop
git pull
```

Después de actualizar, conviene ejecutar:

```powershell
pip install -r requirements.txt
python -m tests.test_health_service
```

---

## 18. Reglas para colaboradores

Antes de enviar cambios:

* utiliza una rama independiente;
* no agregues modelos ni archivos de audio al repositorio;
* no incluyas la carpeta `.venv`;
* no incluyas carpetas `output`;
* actualiza o agrega pruebas;
* verifica que no existan regresiones;
* documenta cualquier cambio arquitectónico importante;
* respeta `docs/VISION.md`.

Ejemplo de rama:

```powershell
git checkout -b feature/descripcion-del-cambio
```

---

## 19. Desactivar el entorno virtual

Al terminar:

```powershell
deactivate
```

---

## 20. Estado del instalador final

Este procedimiento es exclusivo para ejecutar MAI desde el repositorio.

La versión destinada al usuario final tendrá un instalador y un asistente de configuración que se encargarán de:

* instalar MAI;
* preparar sus dependencias;
* instalar el motor de IA;
* descargar los modelos;
* crear la configuración inicial;
* verificar el audio;
* reparar automáticamente los componentes compatibles.

El usuario final no necesitará seguir este documento ni utilizar una consola.
