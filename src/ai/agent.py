"""
AI-агент продавец бытовой техники
"""
import json
from typing import List, Optional, Dict, Any, Tuple
from loguru import logger
from openai import AsyncOpenAI
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.config import get_settings
from src.database.models import Product, Category
from src.ai.vector_store import ProductVectorStore

settings = get_settings()


class SalesAgent:
    """AI-продавец бытовой техники"""
    
    SYSTEM_PROMPT = """Ты — профессиональный консультант интернет-магазина "{company_name}".

## Твоя роль
Ты помогаешь клиентам:
- Подобрать бытовую технику под их потребности
- Рассказать о характеристиках и преимуществах товаров
- Сравнить товары между собой
- Подобрать комплекты техники (например, для кухни)
- Ответить на вопросы о доставке, гарантии и сервисе

## Информация о компании
{company_description}

📞 Телефон: {company_phone}
📧 Email: {company_email}
📍 Адрес: {company_address}
🌐 Сайт: {website_url}

## Правила общения
1. Всегда отвечай на русском языке
2. Будь вежливым, профессиональным и дружелюбным
3. Давай конкретные рекомендации на основе запроса клиента
4. Если не знаешь ответ — честно скажи об этом
5. При подборе техники учитывай бюджет клиента
6. Подчёркивай преимущества товаров
7. Предлагай дополнительные товары, которые могут пригодиться
8. Используй эмодзи для наглядности, но умеренно

## Формат ответов о товарах
Когда рассказываешь о товаре, используй формат:
📦 **Название товара**
🏷️ Бренд: ...
💰 Цена: ... ₽
✅/❌ Наличие
📝 Краткое описание
🔗 Ссылка на товар

## Доступные функции
Ты можешь использовать следующие функции для работы с каталогом:
- search_products: поиск товаров по запросу
- get_product_details: детальная информация о товаре
- get_categories: список категорий товаров
- get_product_recommendations: рекомендации товаров
- create_product_set: подбор комплекта техники

Всегда используй эти функции для получения актуальной информации о товарах."""

    TOOLS = [
        {
            "type": "function",
            "function": {
                "name": "search_products",
                "description": "Поиск товаров по запросу. Используй для поиска конкретных товаров или товаров по критериям.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Поисковый запрос (например: 'варочная панель индукционная', 'холодильник Samsung', 'духовой шкаф встраиваемый')"
                        },
                        "category": {
                            "type": "string",
                            "description": "Категория товаров (опционально)"
                        },
                        "brand": {
                            "type": "string",
                            "description": "Бренд (опционально)"
                        },
                        "min_price": {
                            "type": "number",
                            "description": "Минимальная цена в рублях (опционально)"
                        },
                        "max_price": {
                            "type": "number",
                            "description": "Максимальная цена в рублях (опционально)"
                        },
                        "in_stock_only": {
                            "type": "boolean",
                            "description": "Только товары в наличии",
                            "default": True
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_details",
                "description": "Получить детальную информацию о конкретном товаре по его ID",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "ID товара"
                        }
                    },
                    "required": ["product_id"]
                }
            }
        },
        {
            "type": "function", 
            "function": {
                "name": "get_categories",
                "description": "Получить список всех категорий товаров",
                "parameters": {
                    "type": "object",
                    "properties": {}
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_product_recommendations",
                "description": "Получить рекомендации похожих или сопутствующих товаров",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "product_id": {
                            "type": "integer",
                            "description": "ID товара, для которого нужны рекомендации"
                        },
                        "count": {
                            "type": "integer",
                            "description": "Количество рекомендаций",
                            "default": 3
                        }
                    },
                    "required": ["product_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "create_product_set",
                "description": "Подобрать комплект техники. Используй когда клиент хочет укомплектовать кухню, ванную или другое помещение.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "purpose": {
                            "type": "string",
                            "description": "Назначение комплекта (например: 'кухня', 'ванная', 'стирка и сушка')"
                        },
                        "budget": {
                            "type": "number",
                            "description": "Общий бюджет в рублях (опционально)"
                        },
                        "preferences": {
                            "type": "string", 
                            "description": "Дополнительные пожелания клиента"
                        }
                    },
                    "required": ["purpose"]
                }
            }
        }
    ]

    def __init__(self, db_session: AsyncSession):
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.db = db_session
        self.vector_store = ProductVectorStore()
        self.model = settings.openai_model
        
        # Подготавливаем системный промпт
        self.system_prompt = self.SYSTEM_PROMPT.format(
            company_name=settings.company_name,
            company_description=settings.company_description,
            company_phone=settings.company_phone,
            company_email=settings.company_email,
            company_address=settings.company_address,
            website_url=settings.website_url,
        )
    
    async def _search_products(
        self,
        query: str,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        in_stock_only: bool = True,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Поиск товаров через векторное хранилище"""
        results = self.vector_store.search(
            query=query,
            n_results=limit,
            category=category,
            brand=brand,
            min_price=min_price,
            max_price=max_price,
            in_stock_only=in_stock_only,
        )
        
        # Получаем полные данные из БД
        products = []
        for result in results:
            product_id = result.get("id") or result.get("metadata", {}).get("product_id")
            if product_id:
                product = await self.db.get(Product, product_id)
                if product:
                    products.append(product.to_dict())
        
        return products
    
    async def _get_product_details(self, product_id: int) -> Optional[Dict[str, Any]]:
        """Получить детали товара"""
        result = await self.db.execute(
            select(Product)
            .options(selectinload(Product.category))
            .where(Product.id == product_id)
        )
        product = result.scalar_one_or_none()
        return product.to_dict() if product else None
    
    async def _get_categories(self) -> List[str]:
        """Получить список категорий"""
        result = await self.db.execute(select(Category.name).distinct())
        categories = result.scalars().all()
        return list(categories)
    
    async def _get_recommendations(
        self, 
        product_id: int, 
        count: int = 3
    ) -> List[Dict[str, Any]]:
        """Получить рекомендации для товара"""
        product = await self.db.get(Product, product_id)
        if not product:
            return []
        
        # Ищем похожие товары через векторный поиск
        query = f"{product.name} {product.brand or ''} {product.category.name if product.category else ''}"
        results = self.vector_store.search(
            query=query,
            n_results=count + 1,  # +1 потому что найдём сам товар
            in_stock_only=True,
        )
        
        recommendations = []
        for result in results:
            rec_id = result.get("id") or result.get("metadata", {}).get("product_id")
            if rec_id and rec_id != product_id:
                rec_product = await self.db.get(Product, rec_id)
                if rec_product:
                    recommendations.append(rec_product.to_dict())
                    if len(recommendations) >= count:
                        break
        
        return recommendations
    
    async def _create_product_set(
        self,
        purpose: str,
        budget: Optional[float] = None,
        preferences: Optional[str] = None
    ) -> Dict[str, Any]:
        """Подобрать комплект техники"""
        # Определяем что искать по назначению
        search_queries = {
            "кухня": [
                "варочная панель",
                "духовой шкаф",
                "вытяжка",
                "холодильник",
                "посудомоечная машина",
            ],
            "ванная": [
                "стиральная машина",
                "сушильная машина",
            ],
            "стирка": [
                "стиральная машина",
                "сушильная машина",
            ],
        }
        
        # Находим подходящие категории
        queries = []
        for key, items in search_queries.items():
            if key in purpose.lower():
                queries.extend(items)
        
        if not queries:
            # Если не определили назначение, ищем по тексту
            queries = [purpose]
        
        # Ищем товары для каждой позиции комплекта
        product_set = {
            "purpose": purpose,
            "items": [],
            "total_price": 0,
        }
        
        max_price_per_item = budget / len(queries) if budget else None
        
        for query in queries:
            products = await self._search_products(
                query=query,
                max_price=max_price_per_item,
                in_stock_only=True,
                limit=1
            )
            
            if products:
                product = products[0]
                product_set["items"].append({
                    "category": query,
                    "product": product
                })
                if product.get("price"):
                    product_set["total_price"] += product["price"]
        
        return product_set
    
    async def _execute_function(
        self, 
        function_name: str, 
        arguments: Dict[str, Any]
    ) -> Any:
        """Выполнить функцию по имени"""
        if function_name == "search_products":
            return await self._search_products(**arguments)
        elif function_name == "get_product_details":
            return await self._get_product_details(**arguments)
        elif function_name == "get_categories":
            return await self._get_categories()
        elif function_name == "get_product_recommendations":
            return await self._get_recommendations(**arguments)
        elif function_name == "create_product_set":
            return await self._create_product_set(**arguments)
        else:
            return {"error": f"Неизвестная функция: {function_name}"}
    
    async def chat(
        self, 
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[str, List[Dict[str, str]]]:
        """
        Обработать сообщение пользователя
        
        Args:
            user_message: Сообщение от пользователя
            conversation_history: История разговора
        
        Returns:
            Tuple[ответ агента, обновлённая история]
        """
        # Инициализируем историю если её нет
        if conversation_history is None:
            conversation_history = []
        
        # Добавляем системное сообщение если его нет
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        try:
            # Первый запрос к модели
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=self.TOOLS,
                tool_choice="auto",
                temperature=0.7,
                max_tokens=2000,
            )
            
            assistant_message = response.choices[0].message
            
            # Обрабатываем вызовы функций
            while assistant_message.tool_calls:
                # Добавляем ответ ассистента
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": tc.type,
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })
                
                # Выполняем каждый вызов функции
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    arguments = json.loads(tool_call.function.arguments)
                    
                    logger.info(f"Вызов функции: {function_name}({arguments})")
                    
                    result = await self._execute_function(function_name, arguments)
                    
                    # Добавляем результат функции
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result, ensure_ascii=False, default=str)
                    })
                
                # Получаем следующий ответ
                response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    tools=self.TOOLS,
                    tool_choice="auto",
                    temperature=0.7,
                    max_tokens=2000,
                )
                
                assistant_message = response.choices[0].message
            
            # Финальный ответ
            final_response = assistant_message.content or "Извините, не могу ответить на этот вопрос."
            
            # Обновляем историю (без системного промпта)
            updated_history = conversation_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": final_response}
            ]
            
            # Ограничиваем историю последними 20 сообщениями
            if len(updated_history) > 20:
                updated_history = updated_history[-20:]
            
            return final_response, updated_history
            
        except Exception as e:
            logger.error(f"Ошибка при обработке сообщения: {e}")
            error_response = "Извините, произошла техническая ошибка. Пожалуйста, попробуйте ещё раз или свяжитесь с нами по телефону."
            
            updated_history = conversation_history + [
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": error_response}
            ]
            
            return error_response, updated_history

