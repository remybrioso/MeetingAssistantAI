from application.dependency_container import container

logger = container.get("logger")

logger.info("Aplicación iniciada.")
logger.warning("Prueba de advertencia.")
logger.error("Prueba de error.")

print("Logger OK")