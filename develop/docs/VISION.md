# Meeting Assistant AI (MAI)

> "La mejor tecnología es aquella que desaparece para el usuario y solo deja visible el resultado."

---

# Nuestra Visión

Meeting Assistant AI (MAI) nace con un objetivo muy claro:

Permitir que cualquier persona pueda grabar una reunión y obtener una minuta profesional sin conocimientos técnicos.

El usuario nunca debería preocuparse por inteligencia artificial, modelos, configuraciones, dependencias o comandos de consola.

Toda la complejidad técnica debe permanecer dentro de MAI.

---

# Nuestra Misión

Crear el asistente de reuniones más sencillo, confiable y profesional posible.

MAI debe permitir que una persona instale la aplicación y comience a trabajar en pocos minutos, sin conocimientos técnicos.

---

# Filosofía del Producto

MAI no es solamente una aplicación.

MAI es un producto.

Cada decisión de arquitectura debe mejorar alguno de estos aspectos:

- Simplicidad
- Confiabilidad
- Automatización
- Escalabilidad
- Mantenibilidad

Si una nueva funcionalidad aumenta la complejidad sin aportar valor al usuario, probablemente no pertenece al producto.

---

# Principios Fundamentales

## 1. Invisible Complexity

Toda la complejidad debe permanecer dentro de MAI.

El usuario solamente debe ver resultados.

Nunca debería preocuparse por:

- Ollama
- Whisper
- JSON
- Python
- Dependencias
- Consola
- Modelos de IA

---

## 2. Automatización primero

Si MAI puede realizar una tarea automáticamente, debe hacerlo.

Ejemplos:

- Crear carpetas.
- Instalar componentes.
- Descargar modelos.
- Reparar configuraciones.
- Validar el sistema.

El usuario únicamente interviene cuando la decisión depende de él.

---

## 3. Detectar no es suficiente

Encontrar un problema no es el objetivo.

Resolverlo sí.

Siempre que sea posible, MAI intentará reparar automáticamente cualquier componente que impida su funcionamiento.

---

## 4. Un servicio, una responsabilidad

Cada componente del sistema debe tener un único propósito.

La simplicidad arquitectónica es una inversión para el futuro.

---

## 5. Workspace único

Cada reunión vive dentro de su propio Workspace.

Toda la información relacionada con una reunión debe permanecer organizada dentro de esa estructura.

El Workspace es la única fuente oficial de información de una reunión.

---

## 6. El usuario nunca debería abrir una consola

Durante el uso normal de MAI no debe ser necesario ejecutar comandos manuales.

Las tareas técnicas deben ser ejecutadas automáticamente por el sistema.

---

## 7. Los errores deben ayudar

Todo mensaje debe explicar:

- Qué ocurrió.
- Cómo solucionarlo.
- O mejor aún:

Permitir que MAI lo repare automáticamente.

---

## 8. Pensar como producto

Antes de implementar cualquier funcionalidad debemos preguntarnos:

¿Hace que MAI sea más sencillo?

¿Hace que MAI sea más útil?

¿Hace que MAI sea más profesional?

Si la respuesta es no, debemos reconsiderarla.

---

# Arquitectura General

Meeting Assistant AI está compuesto por varios motores independientes.

## Meeting Engine

Gestiona el ciclo de vida de las reuniones.

---

## AI Pipeline

Procesa la transcripción y genera el conocimiento.

---

## Workspace Manager

Organiza todos los artefactos generados por una reunión.

---

## Health Engine

Detecta el estado del sistema.

Nunca modifica el entorno.

---

## Setup & Recovery Engine

Prepara el entorno.

Instala componentes.

Repara problemas.

Verifica nuevamente.

---

## UI Engine

Presenta toda la complejidad mediante una interfaz simple y comprensible.

---

# Regla de Oro

Toda nueva funcionalidad debe responder esta pregunta:

"¿Hace que la experiencia del usuario sea mejor?"

Si la respuesta es no, probablemente no pertenece al producto.

---

# Nuestra Promesa

Queremos que cualquier persona pueda instalar MAI y comenzar a trabajar sin conocimientos técnicos.

Nuestro objetivo no es mostrar tecnología.

Nuestro objetivo es ocultarla.

Cuando el usuario termine una reunión debería recordar la calidad de la minuta.

No la complejidad que hubo para generarla.

---

# Este documento está vivo.

La arquitectura evolucionará.

La tecnología cambiará.

Los modelos de IA cambiarán.

Los proveedores cambiarán.

La visión no.

Cada decisión futura debe respetar los principios definidos en este documento.