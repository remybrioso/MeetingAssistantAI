# Meeting Assistant AI — Development

Meeting Assistant AI (MAI) es una aplicación de escritorio para Windows orientada a captura, transcripción y análisis local de reuniones.

Versión actual:

```text
v0.9.0-alpha.2
```

## Arquitectura actual

El flujo productivo principal es:

```text
GUI / Import
    ↓
Meeting Pipeline
    ↓
Transcript Pipeline
    ↓
Meeting Intelligence staged
    ↓
Global Consolidation
    ↓
MeetingReport
    ↓
Artifact Delivery
```

El Setup Wizard valida las capacidades necesarias antes de continuar:

```text
runtime-resources
workspace
transcription
artificial-intelligence
audio
```

## Requisitos de desarrollo

- Windows 10/11 x64
- Python 3.14
- entorno virtual recomendado
- Ollama para el procesamiento local de IA
- acceso a Internet para descargar modelos por primera vez

El modelo de IA configurado para esta release es:

```text
qwen2.5:3b
```

## Preparar el entorno

Desde `develop/`:

```powershell
py -3.14 -m venv .venv
.\.venv\Scripts\Activate.ps1

python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Ejecutar MAI desde código fuente

```powershell
python app.py
```

El Setup Wizard permite preparar las dependencias reparables de forma explícita.

## Ejecutar tests

Suite completa:

```powershell
python -m pytest -q
```

Tests de release:

```powershell
python -m pytest .\tests\unit\release -q
```

Baseline de publicación:

```text
941 passed
2 skipped
0 failed
```

## Build de Windows

Las dependencias de build están fijadas en:

```text
requirements-build.txt
```

Para construir ejecutable e instalador desde cero:

```powershell
.\scripts\build_windows_installer.ps1 -Clean
```

Si la política de ejecución de PowerShell bloquea scripts locales, puede ejecutarse el build en un proceso aislado:

```powershell
powershell.exe `
    -NoProfile `
    -ExecutionPolicy Bypass `
    -File .\scripts\build_windows_installer.ps1 `
    -Clean
```

El resultado esperado es:

```text
dist/
├── MeetingAssistantAI/
│   └── MeetingAssistantAI.exe
└── installer/
    └── MeetingAssistantAI-Setup-v0.9.0-alpha.2.exe
```

## Instalación y first-run

Consulta:

```text
docs/INSTALLATION.md
```

## Release notes

Consulta:

```text
docs/releases/v0.9.0-alpha.2.md
```

## Contratos de release

La identidad de versión debe permanecer sincronizada entre:

```text
VERSION
application/app_info.py
```

La suite `tests/unit/release/` protege este contrato junto con los contratos de PyInstaller e Inno Setup.

## Nota de desarrollo

Los scripts `probe_*` son herramientas diagnósticas de investigación y no forman parte automáticamente de una release productiva.
