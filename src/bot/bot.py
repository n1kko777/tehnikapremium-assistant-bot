"""
Telegram бот на aiogram 3.x
"""
import asyncio
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from loguru import logger

from src.config import get_settings
from src.bot.handlers import router
from src.database.session import init_db

settings = get_settings()


class TelegramBot:
    """Telegram бот"""
    
    def __init__(self):
        self.bot = Bot(
            token=settings.telegram_bot_token,
            default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN)
        )
        self.dp = Dispatcher()
        self.dp.include_router(router)
    
    async def start(self):
        """Запуск бота"""
        logger.info("Инициализация базы данных...")
        await init_db()
        
        logger.info("Запуск Telegram бота...")
        
        try:
            # Удаляем webhook если был
            await self.bot.delete_webhook(drop_pending_updates=True)
            
            # Запускаем polling
            await self.dp.start_polling(
                self.bot,
                allowed_updates=["message", "callback_query"]
            )
        finally:
            await self.bot.session.close()
    
    async def stop(self):
        """Остановка бота"""
        logger.info("Остановка Telegram бота...")
        await self.dp.stop_polling()
        await self.bot.session.close()


async def run_bot():
    """Запустить бота"""
    bot = TelegramBot()
    await bot.start()


if __name__ == "__main__":
    asyncio.run(run_bot())

