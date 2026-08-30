"""
repair_action.py

Contrato central de acciones de reparación utilizadas por
el Setup Wizard de Meeting Assistant AI.
"""


class RepairAction:

    REPAIR_APPLICATION_INSTALLATION = (
        "REPAIR_APPLICATION_INSTALLATION"
    )
    REPAIR_WORKSPACE = "REPAIR_WORKSPACE"
    DOWNLOAD_TRANSCRIPTION_MODEL = (
        "DOWNLOAD_TRANSCRIPTION_MODEL"
    )
    INSTALL_AI_PROVIDER = "INSTALL_AI_PROVIDER"
    DOWNLOAD_AI_MODEL = "DOWNLOAD_AI_MODEL"
    REPAIR_AI_CAPABILITY = "REPAIR_AI_CAPABILITY"
    CONFIGURE_MICROPHONE = "CONFIGURE_MICROPHONE"
    CONFIGURE_SYSTEM_AUDIO = "CONFIGURE_SYSTEM_AUDIO"
    REPAIR_AUDIO_DEVICES = "REPAIR_AUDIO_DEVICES"

    ALL = frozenset(
        {
            REPAIR_APPLICATION_INSTALLATION,
            REPAIR_WORKSPACE,
            DOWNLOAD_TRANSCRIPTION_MODEL,
            INSTALL_AI_PROVIDER,
            DOWNLOAD_AI_MODEL,
            REPAIR_AI_CAPABILITY,
            CONFIGURE_MICROPHONE,
            CONFIGURE_SYSTEM_AUDIO,
            REPAIR_AUDIO_DEVICES,
        }
    )


REPAIR_ACTION_PRESENTATION = {
    RepairAction.REPAIR_APPLICATION_INSTALLATION: (
        "Reinstala Meeting Assistant AI para restaurar "
        "los recursos internos requeridos."
    ),
    RepairAction.REPAIR_WORKSPACE: (
        "Revisa la carpeta de almacenamiento de reuniones "
        "y los permisos de escritura."
    ),
    RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL: (
        "Descarga el modelo local de transcripción "
        "requerido por MAI."
    ),
    RepairAction.INSTALL_AI_PROVIDER: (
        "Instala Ollama desde su sitio oficial o inicia "
        "la aplicación si ya está instalada."
    ),
    RepairAction.DOWNLOAD_AI_MODEL: (
        "Descarga el modelo de inteligencia artificial requerido."
    ),
    RepairAction.REPAIR_AI_CAPABILITY: (
        "Revisa la configuración del motor de inteligencia artificial."
    ),
    RepairAction.CONFIGURE_MICROPHONE: (
        "Abre la configuración de sonido de Windows para "
        "conectar o seleccionar un micrófono utilizable."
    ),
    RepairAction.CONFIGURE_SYSTEM_AUDIO: (
        "Abre la configuración de sonido de Windows para "
        "comprobar el dispositivo de salida predeterminado."
    ),
    RepairAction.REPAIR_AUDIO_DEVICES: (
        "Abre la configuración de sonido de Windows para "
        "revisar los dispositivos de entrada y salida."
    ),
}


REPAIR_ACTION_BUTTON_LABELS = {
    RepairAction.REPAIR_APPLICATION_INSTALLATION: (
        "Reparar instalación"
    ),
    RepairAction.REPAIR_WORKSPACE: (
        "Reparar carpeta"
    ),
    RepairAction.DOWNLOAD_TRANSCRIPTION_MODEL: (
        "Descargar modelo"
    ),
    RepairAction.INSTALL_AI_PROVIDER: (
        "Abrir descarga de Ollama"
    ),
    RepairAction.DOWNLOAD_AI_MODEL: (
        "Descargar modelo de IA"
    ),
    RepairAction.REPAIR_AI_CAPABILITY: (
        "Reparar IA"
    ),
    RepairAction.CONFIGURE_MICROPHONE: (
        "Abrir configuración de sonido"
    ),
    RepairAction.CONFIGURE_SYSTEM_AUDIO: (
        "Abrir configuración de sonido"
    ),
    RepairAction.REPAIR_AUDIO_DEVICES: (
        "Abrir configuración de sonido"
    ),
}
