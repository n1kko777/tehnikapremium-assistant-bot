"""
Парсер каталога сайта tehnikapremium.ru
"""
import asyncio
import re
from typing import List, Optional, Dict, Any
from urllib.parse import urljoin, urlparse
from loguru import logger
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from src.database.models import Product, Category
from src.config import get_settings

settings = get_settings()


class CatalogParser:
    """Парсер каталога сайта"""
    
    def __init__(self, base_url: str = None):
        self.base_url = base_url or settings.website_url
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
        }
        self.client: Optional[httpx.AsyncClient] = None
    
    async def __aenter__(self):
        self.client = httpx.AsyncClient(
            headers=self.headers,
            timeout=30.0,
            follow_redirects=True
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.aclose()
    
    async def fetch_page(self, url: str) -> Optional[str]:
        """Загрузить страницу"""
        try:
            response = await self.client.get(url)
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"Ошибка загрузки страницы {url}: {e}")
            return None
    
    async def parse_categories(self) -> List[Dict[str, Any]]:
        """Парсинг категорий с главной страницы"""
        categories = []
        html = await self.fetch_page(self.base_url)
        
        if not html:
            logger.error("Не удалось загрузить главную страницу")
            return categories
        
        soup = BeautifulSoup(html, "lxml")
        
        # Ищем навигационное меню с категориями
        # Это базовая логика, которую нужно адаптировать под реальную структуру сайта
        nav_selectors = [
            "nav.catalog-menu a",
            ".menu-catalog a",
            ".category-menu a",
            ".main-menu a",
            "nav a[href*='catalog']",
            ".catalog a",
            "a[href*='/category/']",
            "a[href*='/catalog/']",
        ]
        
        for selector in nav_selectors:
            links = soup.select(selector)
            if links:
                for link in links:
                    href = link.get("href", "")
                    name = link.get_text(strip=True)
                    
                    if name and href:
                        full_url = urljoin(self.base_url, href)
                        slug = self._extract_slug(href)
                        
                        if slug and name:
                            categories.append({
                                "name": name,
                                "slug": slug,
                                "url": full_url
                            })
                break
        
        logger.info(f"Найдено категорий: {len(categories)}")
        return categories
    
    async def parse_category_products(
        self, 
        category_url: str,
        max_pages: int = 10
    ) -> List[Dict[str, Any]]:
        """Парсинг товаров из категории"""
        products = []
        page = 1
        
        while page <= max_pages:
            # Формируем URL с пагинацией
            if "?" in category_url:
                url = f"{category_url}&page={page}"
            else:
                url = f"{category_url}?page={page}" if page > 1 else category_url
            
            html = await self.fetch_page(url)
            if not html:
                break
            
            soup = BeautifulSoup(html, "lxml")
            
            # Ищем карточки товаров - адаптировать под реальную структуру
            product_selectors = [
                ".product-card",
                ".product-item",
                ".catalog-item",
                ".goods-item",
                "[data-product]",
                ".product",
            ]
            
            found_products = []
            for selector in product_selectors:
                items = soup.select(selector)
                if items:
                    found_products = items
                    break
            
            if not found_products:
                logger.info(f"Товары не найдены на странице {page}")
                break
            
            for item in found_products:
                product_data = await self._parse_product_card(item)
                if product_data:
                    products.append(product_data)
            
            logger.info(f"Страница {page}: найдено {len(found_products)} товаров")
            
            # Проверяем наличие следующей страницы
            next_page = soup.select_one(
                ".pagination .next, .pager .next, a[rel='next'], .page-next"
            )
            if not next_page:
                break
            
            page += 1
            await asyncio.sleep(0.5)  # Задержка между запросами
        
        return products
    
    async def _parse_product_card(self, item: BeautifulSoup) -> Optional[Dict[str, Any]]:
        """Парсинг карточки товара"""
        try:
            # Название
            name_el = item.select_one(
                ".product-name, .product-title, .item-name, .name, h3, h4, a[title]"
            )
            name = name_el.get_text(strip=True) if name_el else None
            
            if not name:
                return None
            
            # Ссылка на товар
            link_el = item.select_one("a[href]")
            url = urljoin(self.base_url, link_el.get("href", "")) if link_el else None
            
            # Цена
            price = None
            price_el = item.select_one(
                ".price, .product-price, .price-current, .current-price, [data-price]"
            )
            if price_el:
                price_text = price_el.get_text(strip=True)
                price = self._extract_price(price_text)
            
            # Старая цена
            old_price = None
            old_price_el = item.select_one(
                ".old-price, .price-old, .original-price, .was-price"
            )
            if old_price_el:
                old_price_text = old_price_el.get_text(strip=True)
                old_price = self._extract_price(old_price_text)
            
            # Изображение
            image_url = None
            img_el = item.select_one("img")
            if img_el:
                image_url = img_el.get("src") or img_el.get("data-src") or img_el.get("data-lazy")
                if image_url:
                    image_url = urljoin(self.base_url, image_url)
            
            # Артикул
            article = None
            article_el = item.select_one(
                ".article, .sku, [data-article], .product-article"
            )
            if article_el:
                article = article_el.get_text(strip=True).replace("Артикул:", "").strip()
            
            # Наличие
            in_stock = True
            stock_el = item.select_one(".out-of-stock, .not-available, .sold-out")
            if stock_el:
                in_stock = False
            
            return {
                "name": name,
                "url": url,
                "price": price,
                "old_price": old_price,
                "image_url": image_url,
                "article": article,
                "in_stock": in_stock,
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга карточки товара: {e}")
            return None
    
    async def parse_product_details(self, url: str) -> Optional[Dict[str, Any]]:
        """Парсинг детальной страницы товара"""
        html = await self.fetch_page(url)
        if not html:
            return None
        
        soup = BeautifulSoup(html, "lxml")
        
        try:
            # Название
            name_el = soup.select_one("h1, .product-name, .product-title")
            name = name_el.get_text(strip=True) if name_el else None
            
            # Описание
            desc_el = soup.select_one(
                ".product-description, .description, .product-text, [itemprop='description']"
            )
            description = desc_el.get_text(strip=True) if desc_el else None
            
            # Бренд
            brand = None
            brand_el = soup.select_one(
                ".brand, .manufacturer, [itemprop='brand']"
            )
            if brand_el:
                brand = brand_el.get_text(strip=True)
            
            # Характеристики
            specifications = {}
            specs_container = soup.select_one(
                ".specifications, .characteristics, .params, .product-specs"
            )
            if specs_container:
                rows = specs_container.select("tr, .spec-row, .param-row, li")
                for row in rows:
                    cells = row.select("td, .spec-name, .spec-value, span")
                    if len(cells) >= 2:
                        spec_name = cells[0].get_text(strip=True)
                        spec_value = cells[1].get_text(strip=True)
                        if spec_name and spec_value:
                            specifications[spec_name] = spec_value
            
            # Все изображения
            images = []
            img_elements = soup.select(
                ".product-images img, .gallery img, .product-gallery img"
            )
            for img in img_elements:
                src = img.get("src") or img.get("data-src") or img.get("data-large")
                if src:
                    images.append(urljoin(self.base_url, src))
            
            return {
                "name": name,
                "description": description,
                "brand": brand,
                "specifications": specifications,
                "images": images,
            }
            
        except Exception as e:
            logger.error(f"Ошибка парсинга страницы товара {url}: {e}")
            return None
    
    def _extract_slug(self, url: str) -> str:
        """Извлечь slug из URL"""
        parsed = urlparse(url)
        path = parsed.path.strip("/")
        parts = path.split("/")
        return parts[-1] if parts else ""
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Извлечь цену из текста"""
        if not price_text:
            return None
        # Убираем всё кроме цифр и точки/запятой
        price_clean = re.sub(r"[^\d.,]", "", price_text)
        price_clean = price_clean.replace(",", ".")
        # Если есть несколько точек, оставляем только последнюю
        parts = price_clean.split(".")
        if len(parts) > 2:
            price_clean = "".join(parts[:-1]) + "." + parts[-1]
        try:
            return float(price_clean) if price_clean else None
        except ValueError:
            return None
    
    async def sync_to_database(
        self, 
        session: AsyncSession,
        products_data: List[Dict[str, Any]],
        category_name: str = None
    ) -> int:
        """Синхронизация товаров в базу данных"""
        count = 0
        
        # Получаем или создаём категорию
        category = None
        if category_name:
            result = await session.execute(
                select(Category).where(Category.name == category_name)
            )
            category = result.scalar_one_or_none()
            
            if not category:
                category = Category(
                    name=category_name,
                    slug=category_name.lower().replace(" ", "-")
                )
                session.add(category)
                await session.flush()
        
        for data in products_data:
            try:
                # Проверяем существует ли товар
                existing = None
                if data.get("url"):
                    result = await session.execute(
                        select(Product).where(Product.url == data["url"])
                    )
                    existing = result.scalar_one_or_none()
                
                if existing:
                    # Обновляем существующий товар
                    for key, value in data.items():
                        if value is not None and hasattr(existing, key):
                            setattr(existing, key, value)
                else:
                    # Создаём новый товар
                    product = Product(
                        name=data.get("name"),
                        url=data.get("url"),
                        price=data.get("price"),
                        old_price=data.get("old_price"),
                        image_url=data.get("image_url"),
                        article=data.get("article"),
                        description=data.get("description"),
                        brand=data.get("brand"),
                        in_stock=data.get("in_stock", True),
                        specifications=data.get("specifications"),
                        images=data.get("images"),
                        category_id=category.id if category else None,
                    )
                    session.add(product)
                    count += 1
                    
            except Exception as e:
                logger.error(f"Ошибка сохранения товара: {e}")
                continue
        
        await session.commit()
        logger.info(f"Добавлено новых товаров: {count}")
        return count


async def run_parser():
    """Запуск полного парсинга каталога"""
    from src.database.session import AsyncSessionLocal, init_db
    
    await init_db()
    
    async with CatalogParser() as parser:
        # Парсим категории
        categories = await parser.parse_categories()
        
        async with AsyncSessionLocal() as session:
            for cat_data in categories:
                # Парсим товары из каждой категории
                products = await parser.parse_category_products(
                    cat_data["url"], 
                    max_pages=5
                )
                
                # Сохраняем в базу
                await parser.sync_to_database(
                    session, 
                    products, 
                    category_name=cat_data["name"]
                )
                
                await asyncio.sleep(1)  # Пауза между категориями


if __name__ == "__main__":
    asyncio.run(run_parser())

