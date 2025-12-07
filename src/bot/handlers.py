"""
Обработчики сообщений Telegram бота
"""
from typing import Dict, List
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from loguru import logger

from src.database.session import AsyncSessionLocal
from src.ai.agent import SalesAgent
from src.config import get_settings

settings = get_settings()
router = Router()

# Хранилище историй разговоров (в продакшене использовать Redis)
conversation_histories: Dict[int, List[Dict[str, str]]] = {}


class ChatStates(StatesGroup):
    """Состояния чата"""
    chatting = State()


def escape_markdown(text: str) -> str:
    """Экранирование специальных символов Markdown"""
    # Для MarkdownV2 нужно экранировать больше символов
    # Но мы используем обычный Markdown, поэтому минимальное экранирование
    return text


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """Обработчик команды /start"""
    user = message.from_user
    logger.info(f"Новый пользователь: {user.id} (@{user.username})")
    
    # Очищаем историю для нового пользователя
    conversation_histories[user.id] = []
    
    await state.set_state(ChatStates.chatting)
    
    welcome_text = f"""
👋 Здравствуйте, {user.first_name}!

Добро пожаловать в **{settings.company_name}** — ваш помощник по выбору бытовой техники!

🛒 Я могу помочь вам:
• Подобрать технику под ваши потребности
• Рассказать о характеристиках товаров
• Сравнить разные модели
• Собрать комплект техники для кухни или дома
• Ответить на вопросы о доставке и гарантии

💡 Просто напишите, что вас интересует!

Например:
• "Помоги выбрать варочную панель"
• "Какие есть холодильники Samsung?"
• "Собери комплект для кухни за 300000 рублей"
"""
    
    await message.answer(welcome_text)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработчик команды /help"""
    help_text = """
🔍 **Как пользоваться ботом**

Просто напишите мне, что вас интересует, и я помогу подобрать подходящую технику!

**Примеры запросов:**
• "Покажи духовые шкафы Bosch"
• "Нужна индукционная варочная панель до 50000"
• "Расскажи о холодильнике Samsung RB37A5470SA"
• "Какие есть посудомоечные машины шириной 45 см?"
• "Собери мне кухню с бюджетом 500000 рублей"

**Команды:**
/start — начать заново
/help — показать эту справку
/clear — очистить историю диалога
/catalog — категории товаров
/contacts — контакты магазина
"""
    
    await message.answer(help_text)


@router.message(Command("clear"))
async def cmd_clear(message: Message):
    """Очистка истории разговора"""
    user_id = message.from_user.id
    conversation_histories[user_id] = []
    
    await message.answer("🔄 История диалога очищена. Можем начать заново!")


@router.message(Command("catalog"))
async def cmd_catalog(message: Message):
    """Показать категории каталога"""
    async with AsyncSessionLocal() as session:
        agent = SalesAgent(session)
        categories = agent.vector_store.get_categories()
    
    if categories:
        categories_text = "\n".join([f"• {cat}" for cat in categories])
        text = f"📂 **Категории товаров:**\n\n{categories_text}\n\nНапишите название категории, чтобы посмотреть товары."
    else:
        text = "📂 Каталог пока пуст. Напишите, что вас интересует, и я постараюсь помочь!"
    
    await message.answer(text)


@router.message(Command("contacts"))
async def cmd_contacts(message: Message):
    """Показать контакты"""
    contacts_text = f"""
📞 **Контакты {settings.company_name}**

🌐 Сайт: {settings.website_url}
📧 Email: {settings.company_email}
📱 Телефон: {settings.company_phone}
📍 Адрес: {settings.company_address}

Мы всегда рады помочь с выбором техники!
"""
    
    await message.answer(contacts_text)


@router.message(F.text)
async def handle_message(message: Message, state: FSMContext):
    """Обработка текстовых сообщений"""
    user_id = message.from_user.id
    user_message = message.text.strip()
    
    if not user_message:
        return
    
    logger.info(f"Сообщение от {user_id}: {user_message[:50]}...")
    
    # Показываем индикатор набора текста
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Получаем историю разговора
    history = conversation_histories.get(user_id, [])
    
    try:
        async with AsyncSessionLocal() as session:
            agent = SalesAgent(session)
            response, updated_history = await agent.chat(user_message, history)
        
        # Сохраняем обновлённую историю
        conversation_histories[user_id] = updated_history
        
        # Отправляем ответ (разбиваем на части если слишком длинный)
        if len(response) > 4000:
            # Разбиваем на части
            parts = []
            current_part = ""
            
            for line in response.split("\n"):
                if len(current_part) + len(line) + 1 > 4000:
                    parts.append(current_part)
                    current_part = line
                else:
                    current_part += "\n" + line if current_part else line
            
            if current_part:
                parts.append(current_part)
            
            for part in parts:
                await message.answer(part)
        else:
            await message.answer(response)
            
    except Exception as e:
        logger.error(f"Ошибка обработки сообщения: {e}")
        await message.answer(
            "😔 Извините, произошла ошибка. Попробуйте ещё раз или свяжитесь с нами по телефону."
        )


@router.callback_query()
async def handle_callback(callback: CallbackQuery):
    """Обработка callback-запросов от inline кнопок"""
    data = callback.data
    
    if data.startswith("product_"):
        product_id = int(data.replace("product_", ""))
        
        async with AsyncSessionLocal() as session:
            agent = SalesAgent(session)
            product = await agent._get_product_details(product_id)
        
        if product:
            text = f"""
📦 **{product['name']}**

🏷️ Бренд: {product.get('brand', 'Не указан')}
💰 Цена: {product.get('price', 'По запросу'):,.0f} ₽
✅ В наличии: {'Да' if product.get('in_stock') else 'Нет'}

📝 {product.get('description', 'Описание не доступно')}

🔗 Подробнее: {product.get('url', settings.website_url)}
"""
        else:
            text = "Товар не найден"
        
        await callback.message.answer(text)
    
    await callback.answer()

