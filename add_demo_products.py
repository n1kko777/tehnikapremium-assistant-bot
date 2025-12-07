"""
Добавление демонстрационных товаров в базу данных
Используйте для тестирования без парсинга реального сайта
"""
import asyncio
import sys
from loguru import logger

# Настройка логирования
logger.remove()
logger.add(sys.stdout, format="{time:HH:mm:ss} | {level} | {message}", level="INFO")

DEMO_PRODUCTS = [
    # Варочные панели
    {
        "name": "Варочная панель Bosch PIE631FB1E",
        "brand": "Bosch",
        "model": "PIE631FB1E",
        "article": "PIE631FB1E",
        "price": 54990,
        "old_price": 64990,
        "description": "Индукционная варочная панель с 4 зонами нагрева. Функция PowerBoost, таймер, защита от детей.",
        "short_description": "Индукционная, 4 конфорки, 60 см, черная",
        "category_name": "Варочные панели",
        "in_stock": True,
        "specifications": {
            "Тип": "Индукционная",
            "Количество конфорок": "4",
            "Ширина": "60 см",
            "Цвет": "Черный",
            "Мощность": "7400 Вт",
            "Таймер": "Да",
            "Защита от детей": "Да"
        }
    },
    {
        "name": "Варочная панель Electrolux EHH96340FK",
        "brand": "Electrolux",
        "model": "EHH96340FK",
        "article": "EHH96340FK",
        "price": 42990,
        "description": "Индукционная варочная панель с функцией Bridge. Сенсорное управление, 4 зоны нагрева.",
        "short_description": "Индукционная, 4 конфорки, 60 см",
        "category_name": "Варочные панели",
        "in_stock": True,
        "specifications": {
            "Тип": "Индукционная",
            "Количество конфорок": "4",
            "Ширина": "60 см",
            "Функция Bridge": "Да"
        }
    },
    {
        "name": "Варочная панель Samsung NZ64H37070K",
        "brand": "Samsung",
        "model": "NZ64H37070K",
        "article": "NZ64H37070K",
        "price": 38990,
        "description": "Индукционная варочная панель с технологией Virtual Flame. Плавная регулировка мощности.",
        "short_description": "Индукционная, 4 конфорки, Virtual Flame",
        "category_name": "Варочные панели",
        "in_stock": True,
        "specifications": {
            "Тип": "Индукционная",
            "Количество конфорок": "4",
            "Технология": "Virtual Flame"
        }
    },
    
    # Духовые шкафы
    {
        "name": "Духовой шкаф Bosch HBG675BS1",
        "brand": "Bosch",
        "model": "HBG675BS1",
        "article": "HBG675BS1",
        "price": 89990,
        "old_price": 99990,
        "description": "Встраиваемый духовой шкаф с функцией пароварки. 13 режимов нагрева, пиролитическая очистка.",
        "short_description": "Электрический, 71 л, пиролиз, нержавейка",
        "category_name": "Духовые шкафы",
        "in_stock": True,
        "specifications": {
            "Тип": "Электрический",
            "Объем": "71 л",
            "Очистка": "Пиролитическая",
            "Режимов нагрева": "13",
            "Гриль": "Да",
            "Конвекция": "Да"
        }
    },
    {
        "name": "Духовой шкаф Electrolux EOD5C71X",
        "brand": "Electrolux",
        "model": "EOD5C71X",
        "article": "EOD5C71X",
        "price": 64990,
        "description": "Встраиваемый духовой шкаф с каталитической очисткой. SurroundCook для равномерного запекания.",
        "short_description": "Электрический, 72 л, каталитическая очистка",
        "category_name": "Духовые шкафы",
        "in_stock": True,
        "specifications": {
            "Тип": "Электрический",
            "Объем": "72 л",
            "Очистка": "Каталитическая",
            "Технология": "SurroundCook"
        }
    },
    
    # Холодильники
    {
        "name": "Холодильник Samsung RB37A5470SA",
        "brand": "Samsung",
        "model": "RB37A5470SA",
        "article": "RB37A5470SA",
        "price": 74990,
        "old_price": 84990,
        "description": "Двухкамерный холодильник с технологией No Frost. Инверторный компрессор, зона свежести.",
        "short_description": "No Frost, 367 л, инвертор, серебристый",
        "category_name": "Холодильники",
        "in_stock": True,
        "specifications": {
            "Тип": "Двухкамерный",
            "Общий объем": "367 л",
            "Морозильная камера": "114 л",
            "Холодильная камера": "253 л",
            "Система разморозки": "No Frost",
            "Компрессор": "Инверторный",
            "Класс энергопотребления": "A+"
        }
    },
    {
        "name": "Холодильник LG GA-B509CLWL",
        "brand": "LG",
        "model": "GA-B509CLWL",
        "article": "GA-B509CLWL",
        "price": 69990,
        "description": "Холодильник с технологией DoorCooling+ и линейным инверторным компрессором. Зона FRESHConverter.",
        "short_description": "No Frost, 384 л, DoorCooling+, белый",
        "category_name": "Холодильники",
        "in_stock": True,
        "specifications": {
            "Тип": "Двухкамерный",
            "Общий объем": "384 л",
            "Система разморозки": "No Frost",
            "Технология": "DoorCooling+",
            "Компрессор": "Линейный инверторный"
        }
    },
    
    # Вытяжки
    {
        "name": "Вытяжка Elica HIDDEN IXGL/A/60",
        "brand": "Elica",
        "model": "HIDDEN IXGL/A/60",
        "article": "HIDDEN-IXGL-60",
        "price": 45990,
        "description": "Встраиваемая вытяжка с выдвижным экраном. Производительность 1200 м³/ч, сенсорное управление.",
        "short_description": "Встраиваемая, 60 см, 1200 м³/ч",
        "category_name": "Вытяжки",
        "in_stock": True,
        "specifications": {
            "Тип": "Встраиваемая",
            "Ширина": "60 см",
            "Производительность": "1200 м³/ч",
            "Уровень шума": "54 дБ",
            "Управление": "Сенсорное"
        }
    },
    {
        "name": "Вытяжка Falmec MOVE 90",
        "brand": "Falmec",
        "model": "MOVE 90",
        "article": "MOVE-90-BK",
        "price": 89990,
        "description": "Наклонная вытяжка премиум-класса. Периметральное всасывание, мощность 800 м³/ч.",
        "short_description": "Наклонная, 90 см, черное стекло",
        "category_name": "Вытяжки",
        "in_stock": True,
        "specifications": {
            "Тип": "Наклонная",
            "Ширина": "90 см",
            "Производительность": "800 м³/ч",
            "Материал": "Черное стекло"
        }
    },
    
    # Посудомоечные машины
    {
        "name": "Посудомоечная машина Bosch SMV4HCX48E",
        "brand": "Bosch",
        "model": "SMV4HCX48E",
        "article": "SMV4HCX48E",
        "price": 69990,
        "description": "Полноразмерная встраиваемая посудомоечная машина. 14 комплектов, система сушки Zeolith.",
        "short_description": "Встраиваемая, 60 см, 14 комплектов",
        "category_name": "Посудомоечные машины",
        "in_stock": True,
        "specifications": {
            "Тип": "Встраиваемая",
            "Ширина": "60 см",
            "Вместимость": "14 комплектов",
            "Расход воды": "9.5 л",
            "Уровень шума": "44 дБ",
            "Сушка": "Zeolith"
        }
    },
    {
        "name": "Посудомоечная машина Miele G 7160 SCVi",
        "brand": "Miele",
        "model": "G 7160 SCVi",
        "article": "G7160SCVI",
        "price": 189990,
        "description": "Премиальная посудомоечная машина с технологией AutoDos. Автоматическое дозирование моющего средства.",
        "short_description": "Встраиваемая, AutoDos, 14 комплектов",
        "category_name": "Посудомоечные машины",
        "in_stock": True,
        "specifications": {
            "Тип": "Встраиваемая",
            "Ширина": "60 см",
            "Вместимость": "14 комплектов",
            "Технология": "AutoDos",
            "Класс": "Премиум"
        }
    },
    
    # Стиральные машины
    {
        "name": "Стиральная машина Bosch WAX32DH1OE",
        "brand": "Bosch",
        "model": "WAX32DH1OE",
        "article": "WAX32DH1OE",
        "price": 94990,
        "description": "Отдельностоящая стиральная машина с функцией Home Connect. Загрузка 10 кг, отжим 1600 об/мин.",
        "short_description": "10 кг, 1600 об/мин, Home Connect",
        "category_name": "Стиральные машины",
        "in_stock": True,
        "specifications": {
            "Тип": "Отдельностоящая",
            "Загрузка": "10 кг",
            "Отжим": "1600 об/мин",
            "Технология": "Home Connect",
            "Класс энергопотребления": "A+++"
        }
    },
    {
        "name": "Стиральная машина LG F4V5TG0W",
        "brand": "LG",
        "model": "F4V5TG0W",
        "article": "F4V5TG0W",
        "price": 54990,
        "description": "Стиральная машина с технологией AI DD. Распознавание типа ткани, паровая обработка Steam.",
        "short_description": "8 кг, AI DD, Steam, белая",
        "category_name": "Стиральные машины",
        "in_stock": True,
        "specifications": {
            "Тип": "Отдельностоящая",
            "Загрузка": "8 кг",
            "Отжим": "1400 об/мин",
            "Технология": "AI DD, Steam"
        }
    },
]


async def add_demo_products():
    """Добавление демонстрационных товаров"""
    from src.database.session import AsyncSessionLocal, init_db
    from src.database.models import Product, Category
    from src.ai.vector_store import ProductVectorStore
    from sqlalchemy import select
    
    logger.info("Инициализация базы данных...")
    await init_db()
    
    async with AsyncSessionLocal() as session:
        # Создаём категории
        categories = {}
        category_names = set(p["category_name"] for p in DEMO_PRODUCTS)
        
        for cat_name in category_names:
            result = await session.execute(
                select(Category).where(Category.name == cat_name)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                category = Category(
                    name=cat_name,
                    slug=cat_name.lower().replace(" ", "-")
                )
                session.add(category)
                await session.flush()
            
            categories[cat_name] = category
        
        # Добавляем товары
        products = []
        for p_data in DEMO_PRODUCTS:
            # Проверяем существует ли товар
            result = await session.execute(
                select(Product).where(Product.article == p_data["article"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                logger.info(f"Товар уже существует: {p_data['name']}")
                products.append(existing)
                continue
            
            product = Product(
                name=p_data["name"],
                brand=p_data["brand"],
                model=p_data["model"],
                article=p_data["article"],
                price=p_data["price"],
                old_price=p_data.get("old_price"),
                description=p_data["description"],
                short_description=p_data.get("short_description"),
                category_id=categories[p_data["category_name"]].id,
                in_stock=p_data.get("in_stock", True),
                specifications=p_data.get("specifications"),
                url=f"https://tehnikapremium.ru/product/{p_data['article'].lower()}"
            )
            session.add(product)
            products.append(product)
            logger.info(f"Добавлен товар: {p_data['name']}")
        
        await session.commit()
        
        # Обновляем товары с ID
        for product in products:
            await session.refresh(product)
        
        logger.info(f"Всего товаров: {len(products)}")
        
        # Синхронизируем в векторное хранилище
        logger.info("Синхронизация в векторное хранилище...")
        vector_store = ProductVectorStore()
        
        # Загружаем категории для товаров
        for product in products:
            await session.refresh(product, ["category"])
        
        vector_store.add_products(products)
        logger.info(f"Товаров в векторном хранилище: {vector_store.count}")


if __name__ == "__main__":
    logger.info("Добавление демонстрационных товаров...")
    try:
        asyncio.run(add_demo_products())
        logger.info("Готово! Теперь можно запустить бота: python run_bot.py")
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        raise

