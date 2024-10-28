import os
from typing import Any
import logging


def launch_logging(name: str, file_log: str) -> Any:
    """
    Функция, создающая логи и записывающая их в файл
    """
    os.makedirs('logs', exist_ok=True)
    logger = logging.getLogger(name)
    file_handler = logging.FileHandler(file_log, mode='w')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s')
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    return logger