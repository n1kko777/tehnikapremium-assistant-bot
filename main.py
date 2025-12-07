"""
Главный файл запуска приложения
Запускает Telegram бота и API сервер одновременно
"""
import asyncio
import signal
import sys
from loguru import logger

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)
logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="1 day",
    retention="30 days",
    level="DEBUG"
)


async def run_telegram_bot():
    """Запуск Telegram бота"""
    from src.bot.bot import TelegramBot
    
    bot = TelegramBot()
    await bot.start()


async def run_api_server():
    """Запуск API сервера"""
    import uvicorn
    from src.config import get_settings
    
    settings = get_settings()
    
    config = uvicorn.Config(
        "src.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        log_level="info",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def main():
    """Главная функция"""
    logger.info("=" * 50)
    logger.info("Запуск TehnikaPremium Assistant")
    logger.info("=" * 50)
    
    # Создаём задачи для бота и сервера
    tasks = [
        asyncio.create_task(run_telegram_bot()),
        asyncio.create_task(run_api_server()),
    ]
    
    # Обработка сигналов завершения
    def signal_handler():
        logger.info("Получен сигнал завершения...")
        for task in tasks:
            task.cancel()
    
    loop = asyncio.get_event_loop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, signal_handler)
        except NotImplementedError:
            # Windows не поддерживает add_signal_handler
            pass
    
    try:
        await asyncio.gather(*tasks)
    except asyncio.CancelledError:
        logger.info("Задачи отменены")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
    finally:
        logger.info("Приложение остановлено")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Приложение остановлено пользователем")

