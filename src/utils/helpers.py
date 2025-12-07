"""
Вспомогательные функции
"""
import re
import uuid
import html
from typing import Optional


def format_price(price: float, currency: str = "₽") -> str:
    """
    Форматирование цены с разделителями тысяч
    
    Args:
        price: Цена
        currency: Символ валюты
    
    Returns:
        Отформатированная строка цены
    
    Example:
        >>> format_price(54990)
        '54 990 ₽'
    """
    if price is None:
        return "Цена по запросу"
    
    # Форматируем с пробелами как разделителями тысяч
    formatted = f"{price:,.0f}".replace(",", " ")
    return f"{formatted} {currency}"


def format_price_range(min_price: float, max_price: float, currency: str = "₽") -> str:
    """
    Форматирование диапазона цен
    
    Args:
        min_price: Минимальная цена
        max_price: Максимальная цена
        currency: Символ валюты
    
    Returns:
        Строка с диапазоном цен
    """
    if min_price == max_price:
        return format_price(min_price, currency)
    
    min_formatted = f"{min_price:,.0f}".replace(",", " ")
    max_formatted = f"{max_price:,.0f}".replace(",", " ")
    
    return f"{min_formatted} – {max_formatted} {currency}"


def clean_html(text: str) -> str:
    """
    Очистка текста от HTML-тегов
    
    Args:
        text: Исходный текст с HTML
    
    Returns:
        Очищенный текст
    """
    if not text:
        return ""
    
    # Удаляем HTML-теги
    clean = re.sub(r'<[^>]+>', '', text)
    
    # Декодируем HTML-сущности
    clean = html.unescape(clean)
    
    # Нормализуем пробелы
    clean = re.sub(r'\s+', ' ', clean)
    
    return clean.strip()


def truncate_text(text: str, max_length: int = 200, suffix: str = "...") -> str:
    """
    Обрезка текста до указанной длины
    
    Args:
        text: Исходный текст
        max_length: Максимальная длина
        suffix: Суффикс для обрезанного текста
    
    Returns:
        Обрезанный текст
    """
    if not text or len(text) <= max_length:
        return text or ""
    
    # Обрезаем по последнему пробелу
    truncated = text[:max_length]
    last_space = truncated.rfind(' ')
    
    if last_space > max_length * 0.7:
        truncated = truncated[:last_space]
    
    return truncated.rstrip('.,!?;:') + suffix


def generate_session_id() -> str:
    """
    Генерация уникального идентификатора сессии
    
    Returns:
        Уникальный ID сессии
    """
    return f"sess_{uuid.uuid4().hex[:16]}"


def normalize_phone(phone: str) -> str:
    """
    Нормализация номера телефона
    
    Args:
        phone: Номер телефона в любом формате
    
    Returns:
        Номер в формате +7XXXXXXXXXX
    """
    if not phone:
        return ""
    
    # Оставляем только цифры
    digits = re.sub(r'\D', '', phone)
    
    # Приводим к формату 7XXXXXXXXXX
    if len(digits) == 11 and digits.startswith('8'):
        digits = '7' + digits[1:]
    elif len(digits) == 10:
        digits = '7' + digits
    
    if len(digits) == 11 and digits.startswith('7'):
        return f"+{digits}"
    
    return phone


def slugify(text: str) -> str:
    """
    Создание slug из текста
    
    Args:
        text: Исходный текст
    
    Returns:
        Slug для URL
    """
    if not text:
        return ""
    
    # Транслитерация кириллицы
    translit_map = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'h', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'sch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
    }
    
    result = text.lower()
    
    for cyr, lat in translit_map.items():
        result = result.replace(cyr, lat)
    
    # Заменяем пробелы и спецсимволы на дефисы
    result = re.sub(r'[^a-z0-9]+', '-', result)
    result = result.strip('-')
    
    return result


def extract_numbers(text: str) -> list:
    """
    Извлечение чисел из текста
    
    Args:
        text: Текст с числами
    
    Returns:
        Список найденных чисел
    """
    if not text:
        return []
    
    # Ищем числа (целые и с плавающей точкой)
    numbers = re.findall(r'\d+(?:[.,]\d+)?', text)
    
    result = []
    for num in numbers:
        num = num.replace(',', '.')
        try:
            if '.' in num:
                result.append(float(num))
            else:
                result.append(int(num))
        except ValueError:
            continue
    
    return result


def parse_price_from_text(text: str) -> Optional[float]:
    """
    Извлечение цены из текста
    
    Args:
        text: Текст, содержащий цену
    
    Returns:
        Цена или None
    
    Example:
        >>> parse_price_from_text("до 50000 рублей")
        50000.0
    """
    if not text:
        return None
    
    # Убираем пробелы между цифрами
    text = re.sub(r'(\d)\s+(\d)', r'\1\2', text)
    
    # Ищем числа
    numbers = extract_numbers(text)
    
    # Берём самое большое число (вероятнее всего это цена)
    if numbers:
        # Фильтруем нереальные цены
        valid_prices = [n for n in numbers if 100 <= n <= 10_000_000]
        if valid_prices:
            return float(max(valid_prices))
    
    return None


def format_specifications(specs: dict) -> str:
    """
    Форматирование характеристик для отображения
    
    Args:
        specs: Словарь характеристик
    
    Returns:
        Отформатированная строка
    """
    if not specs:
        return ""
    
    lines = []
    for key, value in specs.items():
        lines.append(f"• {key}: {value}")
    
    return "\n".join(lines)

