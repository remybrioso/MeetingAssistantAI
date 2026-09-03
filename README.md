# Meeting Assistant AI (MAI)

Meeting Assistant AI es una aplicación de escritorio para Windows que captura o importa reuniones, genera transcripciones locales y transforma la conversación en artefactos estructurados de seguimiento.

La versión prerelease actual del código es **v0.9.0-alpha.3**.

## Qué hace MAI

MAI permite:

- capturar audio de micrófono y, cuando Windows lo permite, audio del sistema;
- importar reuniones grabadas;
- transcribir reuniones localmente con Faster-Whisper;
- analizar reuniones mediante un modelo local servido por Ollama;
- extraer temas, decisiones, acciones, pendientes y riesgos;
- generar un `MeetingReport` estructurado y grounded;
- producir artefactos JSON, Markdown, DOCX y PDF;
- validar dependencias mediante un Setup Wizard durante la primera ejecución.

## Privacidad y ejecución local

La transcripción y el procesamiento de IA se ejecutan localmente una vez instalados los modelos requeridos.

MAI utiliza:

- **Faster-Whisper** para transcripción local;
- **Ollama** como proveedor local de IA;
- **qwen2.5:3b** como modelo de IA configurado para esta release.

La primera preparación de los modelos requiere conexión a Internet.

## Instalación para usuarios de Windows

El instalador de esta versión tendrá el nombre:

```text
MeetingAssistantAI-Setup-v0.9.0-alpha.3.exe
```

La instalación es por usuario y no requiere permisos de administrador.

Durante la primera ejecución, el Setup Wizard comprueba:

1. recursos internos de MAI;
2. almacenamiento de reuniones;
3. modelo de transcripción;
4. Ollama y el modelo de IA;
5. dispositivos de audio.

Cuando falta una dependencia reparable, MAI ofrece la acción correspondiente desde el propio wizard.

Consulta la guía detallada en:

```text
develop/docs/INSTALLATION.md
```

## Artefactos generados

Cada reunión puede producir:

```text
.mai/
├── meeting_report.json
├── action_items.json
├── decisions.json
├── processing_metrics.json
├── transcript.json
└── workspace.json

Audio/
├── Microfono.wav
└── Sistema.wav

Documentos/
├── Meeting Report.md
├── minutes.docx
└── meeting.pdf
```

La presencia exacta de archivos de audio depende del origen y de las capacidades disponibles durante la reunión.

## Estado de la release

**v0.9.0-alpha.3** conserva la base instalable de alpha.2 y completa el hardening validado durante Corporate Acceptance:

- Meeting Pipeline;
- AI Pipeline staged;
- entrega determinista de artefactos;
- runtime empaquetado con PyInstaller;
- instalador de Windows con Inno Setup;
- onboarding de Faster-Whisper;
- onboarding de Ollama y `qwen2.5:3b`;
- configuración asistida de audio en Windows;
- integridad temporal para reuniones largas;
- preservación determinista del conocimiento y de su procedencia;
- almacenamiento canónico de reuniones importadas;
- experiencia controlada cuando una reunión no contiene evidencia suficiente.

Corporate Acceptance está completado.

La regresión global previa a publicación cerró con:

```text
1018 collected
1016 passed
2 skipped
0 failed
```

Además, el Meeting Pipeline fue validado con la reunión corporativa real de TSS y el runtime congelado fue validado para el almacenamiento canónico de importaciones y la experiencia de evidencia insuficiente.

## Desarrollo

El código productivo actual se encuentra bajo:

```text
develop/
```

Para instrucciones de desarrollo y build consulta:

```text
develop/README.md
```

## Release notes

Consulta:

```text
develop/docs/releases/v0.9.0-alpha.3.md
```

> Esta es una versión alpha. Puede contener limitaciones conocidas y cambios incompatibles antes de una versión estable.
