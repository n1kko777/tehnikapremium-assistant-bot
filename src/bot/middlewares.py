"""
Middleware для Telegram бота
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from loguru import logger
from datetime import datetime


class LoggingMiddleware(BaseMiddleware):
    """Middleware для логирования всех сообщений"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            logger.info(
                f"Message | User: {user.id} (@{user.username}) | "
                f"Text: {event.text[:50] if event.text else 'N/A'}..."
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.info(
                f"Callback | User: {user.id} (@{user.username}) | "
                f"Data: {event.data}"
            )
        
        return await handler(event, data)


class ThrottlingMiddleware(BaseMiddleware):
    """Middleware для ограничения частоты запросов"""
    
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.user_last_message: Dict[int, datetime] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id
            now = datetime.now()
            
            if user_id in self.user_last_message:
                diff = (now - self.user_last_message[user_id]).total_seconds()
                if diff < self.rate_limit:
                    logger.warning(f"Throttling user {user_id}: {diff:.2f}s since last message")
                    return None  # Игнорируем слишком частые сообщения
            
            self.user_last_message[user_id] = now
        
        return await handler(event, data)


class UserTrackingMiddleware(BaseMiddleware):
    """Middleware для отслеживания пользователей"""
    
    def __init__(self):
        self.users: Dict[int, Dict[str, Any]] = {}
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
            user_id = user.id
            
            # Обновляем информацию о пользователе
            if user_id not in self.users:
                logger.info(f"New user: {user_id} (@{user.username})")
            
            self.users[user_id] = {
                "id": user_id,
                "username": user.username,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "last_active": datetime.now(),
            }
            
            # Добавляем информацию о пользователе в data
            data["user_info"] = self.users[user_id]
        
        return await handler(event, data)


class ErrorHandlingMiddleware(BaseMiddleware):
    """Middleware для обработки ошибок"""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        try:
            return await handler(event, data)
        except Exception as e:
            logger.error(f"Error in handler: {e}", exc_info=True)
            
            # Отправляем сообщение об ошибке пользователю
            if isinstance(event, Message):
                await event.answer(
                    "😔 Произошла ошибка при обработке запроса. "
                    "Пожалуйста, попробуйте позже или свяжитесь с нами напрямую."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    "Произошла ошибка. Попробуйте ещё раз.",
                    show_alert=True
                )
            
            return None

