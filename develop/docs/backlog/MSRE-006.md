# MSRE-006 - AI Capability

## Versión

v0.9.2-alpha.1

## Sprint

S-04 - Deployment & Self-Healing

## Objetivo

Representar como una capacidad funcional la posibilidad
de generar resúmenes y conocimiento mediante el proveedor
de inteligencia artificial configurado.

## Componentes

- AIProviderHealthTask
- AICapability

## Estados

### AVAILABLE

El proveedor responde y el modelo configurado está instalado.

### UNAVAILABLE — proveedor ausente

- repairable: true
- repair_action: INSTALL_AI_PROVIDER

### UNAVAILABLE — modelo ausente

- repairable: true
- repair_action: DOWNLOAD_AI_MODEL

### UNAVAILABLE — fallo desconocido

- repairable: true
- repair_action: REPAIR_AI_CAPABILITY

## Principios

- AICapability no depende directamente de Ollama.
- La tarea utiliza el contrato health() del proveedor.
- Health Engine y Setup Engine permanecen separados.
- El usuario ve una capacidad funcional, no detalles técnicos.
- Los detalles técnicos siguen disponibles para diagnóstico avanzado.

## Archivos

- services/setup/tasks/ai_provider_health_task.py
- services/setup/capabilities/ai_capability.py
- tests/test_ai_capability.py
- tests/test_ai_capability_provider_unavailable.py
- tests/test_ai_capability_missing_model.py
- tests/test_ai_capability_broken_provider.py
- tests/test_ai_capability_registry.py
- tests/test_real_ai_capability.py

## Criterios de aceptación

- Se detecta un proveedor disponible.
- Se detecta un proveedor desconectado.
- Se detecta un modelo ausente.
- Se capturan errores inesperados.
- La capacidad se registra correctamente.
- Se propone la acción de reparación adecuada.
- El proveedor real puede validarse.
- No se duplica la lógica de OllamaProvider.health().