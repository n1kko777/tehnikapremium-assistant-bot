"""
Клавиатуры для Telegram бота
"""
from typing import List, Optional
from aiogram.types import (
    ReplyKeyboardMarkup, 
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


def get_main_menu() -> ReplyKeyboardMarkup:
    """Главное меню бота"""
    builder = ReplyKeyboardBuilder()
    
    builder.row(
        KeyboardButton(text="🔍 Поиск товаров"),
        KeyboardButton(text="📂 Каталог"),
    )
    builder.row(
        KeyboardButton(text="🛒 Собрать комплект"),
        KeyboardButton(text="💬 Консультация"),
    )
    builder.row(
        KeyboardButton(text="📞 Контакты"),
        KeyboardButton(text="❓ Помощь"),
    )
    
    return builder.as_markup(resize_keyboard=True)


def get_categories_keyboard(categories: List[str]) -> InlineKeyboardMarkup:
    """Клавиатура с категориями"""
    builder = InlineKeyboardBuilder()
    
    for category in categories:
        builder.row(InlineKeyboardButton(
            text=f"📦 {category}",
            callback_data=f"category:{category}"
        ))
    
    return builder.as_markup()


def get_product_keyboard(
    product_id: int, 
    product_url: Optional[str] = None
) -> InlineKeyboardMarkup:
    """Клавиатура для товара"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="📋 Подробнее",
            callback_data=f"product:{product_id}"
        ),
        InlineKeyboardButton(
            text="🔄 Похожие товары",
            callback_data=f"similar:{product_id}"
        ),
    )
    
    if product_url:
        builder.row(InlineKeyboardButton(
            text="🌐 Открыть на сайте",
            url=product_url
        ))
    
    return builder.as_markup()


def get_products_list_keyboard(
    products: List[dict],
    page: int = 1,
    total_pages: int = 1,
) -> InlineKeyboardMarkup:
    """Клавиатура со списком товаров и пагинацией"""
    builder = InlineKeyboardBuilder()
    
    # Кнопки товаров
    for product in products:
        name = product.get("name", "Товар")
        if len(name) > 40:
            name = name[:37] + "..."
        
        price = product.get("price")
        price_str = f" • {price:,.0f}₽".replace(",", " ") if price else ""
        
        builder.row(InlineKeyboardButton(
            text=f"{name}{price_str}",
            callback_data=f"product:{product['id']}"
        ))
    
    # Пагинация
    if total_pages > 1:
        pagination_buttons = []
        
        if page > 1:
            pagination_buttons.append(InlineKeyboardButton(
                text="◀️ Назад",
                callback_data=f"page:{page-1}"
            ))
        
        pagination_buttons.append(InlineKeyboardButton(
            text=f"{page}/{total_pages}",
            callback_data="noop"
        ))
        
        if page < total_pages:
            pagination_buttons.append(InlineKeyboardButton(
                text="Вперёд ▶️",
                callback_data=f"page:{page+1}"
            ))
        
        builder.row(*pagination_buttons)
    
    return builder.as_markup()


def get_set_options_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора типа комплекта"""
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(
        text="🍳 Комплект для кухни",
        callback_data="set:kitchen"
    ))
    builder.row(InlineKeyboardButton(
        text="🚿 Комплект для ванной",
        callback_data="set:bathroom"
    ))
    builder.row(InlineKeyboardButton(
        text="👔 Стирка и сушка",
        callback_data="set:laundry"
    ))
    builder.row(InlineKeyboardButton(
        text="🏠 Полный комплект для дома",
        callback_data="set:full"
    ))
    
    return builder.as_markup()


def get_budget_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для выбора бюджета"""
    builder = InlineKeyboardBuilder()
    
    budgets = [
        ("До 100 000 ₽", "budget:100000"),
        ("До 200 000 ₽", "budget:200000"),
        ("До 300 000 ₽", "budget:300000"),
        ("До 500 000 ₽", "budget:500000"),
        ("Без ограничений", "budget:0"),
    ]
    
    for text, callback in budgets:
        builder.row(InlineKeyboardButton(text=text, callback_data=callback))
    
    return builder.as_markup()


def get_confirmation_keyboard(action: str) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения"""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Да", callback_data=f"confirm:{action}:yes"),
        InlineKeyboardButton(text="❌ Нет", callback_data=f"confirm:{action}:no"),
    )
    
    return builder.as_markup()


def get_back_keyboard(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Кнопка "Назад" """
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="◀️ Назад", callback_data=callback_data))
    return builder.as_markup()


def get_contact_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура с контактами"""
    builder = InlineKeyboardBuilder()
    
    builder.row(InlineKeyboardButton(
        text="📞 Позвонить",
        url="tel:+7XXXXXXXXXX"  # Замените на реальный номер
    ))
    builder.row(InlineKeyboardButton(
        text="💬 Написать в WhatsApp",
        url="https://wa.me/7XXXXXXXXXX"  # Замените на реальный номер
    ))
    builder.row(InlineKeyboardButton(
        text="🌐 Открыть сайт",
        url="https://tehnikapremium.ru"
    ))
    
    return builder.as_markup()

