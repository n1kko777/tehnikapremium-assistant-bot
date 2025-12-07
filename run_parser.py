"""
Запуск парсера каталога
Используйте этот скрипт для первоначального наполнения базы данных
"""
import asyncio
import sys
from loguru import logger

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

from src.parser.catalog_parser import run_parser

if __name__ == "__main__":
    logger.info("Запуск парсера каталога...")
    try:
        asyncio.run(run_parser())
        logger.info("Парсинг завершён!")
    except KeyboardInterrupt:
        logger.info("Парсинг прерван")
    except Exception as e:
        logger.error(f"Ошибка парсинга: {e}")

