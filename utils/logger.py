# book_app/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os

LOG_DIR = "logs"
LOG_FILE = os.path.join(LOG_DIR, "app.log")

def setup_logger() -> logging.Logger:
    """Configura el logger para registrar eventos de la aplicación."""
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Crear el logger
    logger = logging.getLogger('BookAppLogger')
    logger.setLevel(logging.INFO)

    # Evitar añadir manejadores múltiples si el logger ya está configurado
    if logger.hasHandlers():
        return logger

    # Crear un manejador que rota los logs (1MB por archivo, mantiene 5 backups)
    handler = RotatingFileHandler(LOG_FILE, maxBytes=1*1024*1024, backupCount=5, encoding='utf-8')

    # Crear un formato para los logs
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - User: %(user)s - Operation: %(operation)s - Book: "%(book)s" - Result: %(result)s'
    )
    handler.setFormatter(formatter)

    # Añadir el manejador al logger
    logger.addHandler(handler)

    return logger

def log_operation(user: str, operation: str, book_title: str = "N/A", result: str = "Success") -> None:
    """
    Registra una operación en el log.
    
    Args:
        user (str): El usuario que realiza la operación.
        operation (str): El tipo de operación (e.g., 'ADD_BOOK', 'LOGIN').
        book_title (str): El título del libro afectado.
        result (str): El resultado de la operación.
    """
    logger = logging.getLogger('BookAppLogger')
    extra_info = {
        'user': user,
        'operation': operation,
        'book': book_title,
        'result': result
    }
    logger.info("", extra=extra_info)

# Configurar el logger al importar el módulo
setup_logger()