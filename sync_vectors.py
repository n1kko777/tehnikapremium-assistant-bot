"""
Синхронизация товаров из БД в векторное хранилище
Запустите после парсинга каталога
"""
import asyncio
import sys
from loguru import logger
from sqlalchemy import select

# Настройка логирования
logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


async def sync_to_vectors():
    """Синхронизация товаров в векторное хранилище"""
    from src.database.session import AsyncSessionLocal, init_db
    from src.database.models import Product
    from src.ai.vector_store import ProductVectorStore
    from sqlalchemy.orm import selectinload
    
    logger.info("Инициализация базы данных...")
    await init_db()
    
    logger.info("Инициализация векторного хранилища...")
    vector_store = ProductVectorStore()
    
    logger.info("Загрузка товаров из базы данных...")
    
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Product).options(selectinload(Product.category))
        )
        products = result.scalars().all()
        
        if not products:
            logger.warning("Товары не найдены в базе данных!")
            logger.info("Сначала запустите парсер: python run_parser.py")
            return
        
        logger.info(f"Найдено товаров: {len(products)}")
        
        # Добавляем товары в векторное хранилище
        vector_store.add_products(list(products))
        
        logger.info(f"Товаров в векторном хранилище: {vector_store.count}")
        
        # Показываем категории и бренды
        categories = vector_store.get_categories()
        brands = vector_store.get_brands()
        
        logger.info(f"Категории: {categories}")
        logger.info(f"Бренды: {brands}")


if __name__ == "__main__":
    logger.info("Синхронизация товаров в векторное хранилище...")
    try:
        asyncio.run(sync_to_vectors())
        logger.info("Синхронизация завершена!")
    except Exception as e:
        logger.error(f"Ошибка: {e}")

