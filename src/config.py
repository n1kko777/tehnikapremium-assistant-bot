"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from functools import lru_cache


class Settings(BaseSettings):
    """Настройки приложения"""
    
    # Telegram
    telegram_bot_token: str = Field(..., env="TELEGRAM_BOT_TOKEN")
    
    # OpenAI
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", env="OPENAI_MODEL")
    
    # Database
    database_url: str = Field(
        default="sqlite+aiosqlite:///./data/products.db",
        env="DATABASE_URL"
    )
    
    # ChromaDB
    chroma_db_path: str = Field(default="./data/chroma_db", env="CHROMA_DB_PATH")
    
    # API Server
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    
    # Website
    website_url: str = Field(
        default="https://tehnikapremium.ru",
        env="WEBSITE_URL"
    )
    
    # Debug
    debug: bool = Field(default=False, env="DEBUG")
    
    # Информация об организации
    company_name: str = "ТехникаПремиум"
    company_description: str = """
    ТехникаПремиум - это интернет-магазин премиальной встраиваемой бытовой техники.
    Мы предлагаем широкий ассортимент техники ведущих мировых брендов:
    варочные панели, духовые шкафы, вытяжки, холодильники, посудомоечные машины,
    стиральные машины и многое другое.
    
    Преимущества работы с нами:
    - Только оригинальная техника от официальных поставщиков
    - Гарантия от производителя
    - Профессиональная консультация
    - Доставка по всей России
    - Установка и подключение техники
    """
    company_phone: str = "+7 (XXX) XXX-XX-XX"
    company_email: str = "info@tehnikapremium.ru"
    company_address: str = "Россия"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Получить настройки приложения (с кэшированием)"""
    return Settings()

