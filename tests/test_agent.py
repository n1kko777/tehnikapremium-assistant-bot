"""
Тесты для AI-агента
"""
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch


class TestSalesAgent:
    """Тесты для SalesAgent"""
    
    @pytest.fixture
    def mock_db_session(self):
        """Мок сессии базы данных"""
        session = AsyncMock()
        return session
    
    @pytest.fixture
    def mock_vector_store(self):
        """Мок векторного хранилища"""
        with patch('src.ai.agent.ProductVectorStore') as mock:
            store = MagicMock()
            store.search.return_value = [
                {
                    "id": 1,
                    "metadata": {
                        "product_id": 1,
                        "name": "Тестовый товар",
                        "price": 50000,
                    }
                }
            ]
            mock.return_value = store
            yield store
    
    @pytest.fixture
    def mock_openai(self):
        """Мок OpenAI клиента"""
        with patch('src.ai.agent.AsyncOpenAI') as mock:
            client = AsyncMock()
            
            # Мок ответа без вызова функций
            response = MagicMock()
            response.choices = [MagicMock()]
            response.choices[0].message.content = "Тестовый ответ"
            response.choices[0].message.tool_calls = None
            
            client.chat.completions.create = AsyncMock(return_value=response)
            mock.return_value = client
            yield client
    
    @pytest.mark.asyncio
    async def test_chat_simple_response(
        self, 
        mock_db_session, 
        mock_vector_store,
        mock_openai
    ):
        """Тест простого ответа без вызова функций"""
        from src.ai.agent import SalesAgent
        
        with patch.object(SalesAgent, '__init__', lambda self, db: None):
            agent = SalesAgent(mock_db_session)
            agent.client = mock_openai
            agent.db = mock_db_session
            agent.vector_store = mock_vector_store
            agent.model = "gpt-4o-mini"
            agent.system_prompt = "Тестовый промпт"
            
            response, history = await agent.chat("Привет!")
            
            assert response == "Тестовый ответ"
            assert len(history) == 2
            assert history[0]["role"] == "user"
            assert history[1]["role"] == "assistant"
    
    @pytest.mark.asyncio
    async def test_search_products(self, mock_db_session, mock_vector_store):
        """Тест поиска товаров"""
        from src.ai.agent import SalesAgent
        
        with patch.object(SalesAgent, '__init__', lambda self, db: None):
            agent = SalesAgent(mock_db_session)
            agent.db = mock_db_session
            agent.vector_store = mock_vector_store
            
            # Мокаем db.get
            mock_product = MagicMock()
            mock_product.to_dict.return_value = {
                "id": 1,
                "name": "Тестовый товар",
                "price": 50000,
            }
            mock_db_session.get = AsyncMock(return_value=mock_product)
            
            products = await agent._search_products("тест")
            
            assert len(products) == 1
            assert products[0]["name"] == "Тестовый товар"


class TestVectorStore:
    """Тесты для векторного хранилища"""
    
    def test_create_product_text(self):
        """Тест создания текста для индексации"""
        from src.ai.vector_store import ProductVectorStore
        
        # Создаём мок продукта
        product = MagicMock()
        product.name = "Духовой шкаф Bosch"
        product.brand = "Bosch"
        product.model = "HBG675BS1"
        product.description = "Отличный духовой шкаф"
        product.short_description = None
        product.category = MagicMock()
        product.category.name = "Духовые шкафы"
        product.specifications = {"Объем": "71 л"}
        
        with patch.object(ProductVectorStore, '__init__', lambda self: None):
            store = ProductVectorStore()
            text = store._create_product_text(product)
            
            assert "Духовой шкаф Bosch" in text
            assert "Bosch" in text
            assert "Духовые шкафы" in text


class TestHelpers:
    """Тесты для вспомогательных функций"""
    
    def test_format_price(self):
        """Тест форматирования цены"""
        from src.utils.helpers import format_price
        
        assert format_price(50000) == "50 000 ₽"
        assert format_price(1000000) == "1 000 000 ₽"
        assert format_price(None) == "Цена по запросу"
    
    def test_clean_html(self):
        """Тест очистки HTML"""
        from src.utils.helpers import clean_html
        
        assert clean_html("<p>Текст</p>") == "Текст"
        assert clean_html("<b>Bold</b> &amp; <i>Italic</i>") == "Bold & Italic"
        assert clean_html("") == ""
    
    def test_truncate_text(self):
        """Тест обрезки текста"""
        from src.utils.helpers import truncate_text
        
        long_text = "Это очень длинный текст, который нужно обрезать до определённой длины"
        result = truncate_text(long_text, max_length=30)
        
        assert len(result) <= 33  # 30 + "..."
        assert result.endswith("...")
    
    def test_slugify(self):
        """Тест создания slug"""
        from src.utils.helpers import slugify
        
        assert slugify("Духовые шкафы") == "duhovye-shkafy"
        assert slugify("Варочные панели Bosch") == "varochnye-paneli-bosch"
    
    def test_parse_price_from_text(self):
        """Тест извлечения цены из текста"""
        from src.utils.helpers import parse_price_from_text
        
        assert parse_price_from_text("до 50000 рублей") == 50000.0
        assert parse_price_from_text("в пределах 100 000 руб") == 100000.0
        assert parse_price_from_text("без цены") is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

