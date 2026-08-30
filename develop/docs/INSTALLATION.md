# Instalación de Meeting Assistant AI

Esta guía corresponde a:

```text
Meeting Assistant AI v0.9.0-alpha.2
```

## Plataforma soportada

La release actual está preparada para:

- Windows 10/11;
- arquitectura x64 compatible;
- instalación por usuario.

El instalador no requiere permisos administrativos.

## 1. Descargar el instalador

Descarga desde GitHub Releases:

```text
MeetingAssistantAI-Setup-v0.9.0-alpha.2.exe
```

La release de GitHub publica también el hash SHA256 del artefacto para verificar su integridad.

## 2. Ejecutar la instalación

Abre el instalador y completa el asistente.

La ubicación predeterminada es:

```text
%LOCALAPPDATA%\Programs\Meeting Assistant AI
```

El instalador puede crear:

- acceso directo en el menú Inicio;
- acceso directo opcional en el escritorio.

## 3. Primera ejecución

MAI abre un Setup Wizard que comprueba cinco capacidades:

```text
Recursos internos
Almacenamiento de reuniones
Transcripción
Inteligencia artificial
Audio
```

### Recursos internos

Comprueba que el ejecutable contiene los contratos y recursos necesarios.

Si estos recursos faltan, la instalación debe considerarse dañada y debe reinstalarse MAI.

### Almacenamiento de reuniones

MAI comprueba que puede crear y utilizar el workspace de reuniones dentro de las rutas de usuario.

### Transcripción

MAI utiliza Faster-Whisper localmente.

Si el modelo configurado no está disponible, el wizard muestra:

```text
Descargar modelo
```

La descarga solo comienza después de una acción explícita del usuario.

Cuando termina, MAI vuelve a comprobar automáticamente la capacidad.

### Inteligencia artificial

MAI utiliza Ollama como proveedor local.

Si Ollama no está disponible, el wizard muestra:

```text
Abrir descarga de Ollama
```

MAI abre la página oficial de Ollama, pero no instala software externo de forma silenciosa.

Después de instalar o iniciar Ollama, pulsa:

```text
Volver a comprobar
```

Si Ollama está disponible pero falta el modelo configurado, MAI muestra:

```text
Descargar modelo de IA
```

La release utiliza:

```text
qwen2.5:3b
```

La descarga se realiza mediante la API local de Ollama y MAI verifica el modelo al terminar.

### Audio

MAI necesita un micrófono utilizable para capturar una reunión.

La captura del audio del sistema utiliza loopback del dispositivo de salida de Windows. Si el micrófono está disponible pero el loopback no lo está, MAI puede continuar en estado degradado.

Cuando la configuración de audio necesita intervención, MAI puede abrir:

```text
Configuración > Sistema > Sonido
```

El usuario conserva el control sobre qué dispositivos utiliza Windows.

## 4. Uso offline

Después de instalar las dependencias y modelos necesarios:

- Faster-Whisper procesa la transcripción localmente;
- Ollama sirve el modelo de IA localmente;
- MAI genera los artefactos de reunión en el equipo local.

Las descargas iniciales de modelos requieren Internet.

## 5. Datos de reuniones

MAI almacena reuniones y artefactos en rutas de usuario, no dentro de la carpeta binaria de instalación.

La desinstalación elimina la aplicación, pero preserva los datos de reuniones del usuario.

## 6. Limitaciones conocidas de esta alpha

- Esta release está dirigida a Windows.
- El instalador todavía no está firmado digitalmente.
- Windows SmartScreen puede mostrar una advertencia al ejecutar una build alpha no firmada.
- Ollama es una dependencia externa y se instala por separado.
- La descarga inicial de modelos puede tardar según la conexión.
- La captura del audio del sistema depende del soporte de loopback del hardware/driver de Windows.
- Algunos entornos virtualizados pueden ofrecer solo audio degradado.
- No existe todavía un mecanismo automático de actualización de MAI.

## 7. Verificar integridad del instalador

En PowerShell:

```powershell
Get-FileHash `
    .\MeetingAssistantAI-Setup-v0.9.0-alpha.2.exe `
    -Algorithm SHA256
```

Compara el valor con el SHA256 publicado en la GitHub Release.

## 8. Desinstalación

Utiliza:

```text
Configuración de Windows > Aplicaciones > Aplicaciones instaladas
```

y selecciona **Meeting Assistant AI**.

La desinstalación no debe utilizarse para borrar reuniones o documentos creados por el usuario.
