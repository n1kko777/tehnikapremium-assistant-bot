"""
FastAPI сервер для веб-виджета
"""
import uuid
from typing import Dict, List, Optional
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from loguru import logger
from pathlib import Path

from src.config import get_settings
from src.database.session import init_db, AsyncSessionLocal
from src.ai.agent import SalesAgent

settings = get_settings()

# Хранилище сессий (в продакшене использовать Redis)
chat_sessions: Dict[str, List[Dict[str, str]]] = {}


class ChatRequest(BaseModel):
    """Запрос к чату"""
    session_id: Optional[str] = None
    message: str


class ChatResponse(BaseModel):
    """Ответ чата"""
    session_id: str
    message: str
    products: Optional[List[dict]] = None


class ProductSearchRequest(BaseModel):
    """Запрос на поиск товаров"""
    query: str
    category: Optional[str] = None
    brand: Optional[str] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    limit: int = 10


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Жизненный цикл приложения"""
    logger.info("Инициализация API сервера...")
    await init_db()
    yield
    logger.info("Остановка API сервера...")


app = FastAPI(
    title="TehnikaPremium Assistant API",
    description="AI-продавец бытовой техники",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS для виджета
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене указать конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "name": "TehnikaPremium Assistant API",
        "version": "1.0.0",
        "status": "running",
    }


@app.get("/health")
async def health_check():
    """Проверка состояния сервиса"""
    return {"status": "healthy"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Отправить сообщение AI-ассистенту
    """
    # Создаём или получаем сессию
    session_id = request.session_id or str(uuid.uuid4())
    history = chat_sessions.get(session_id, [])
    
    try:
        async with AsyncSessionLocal() as db_session:
            agent = SalesAgent(db_session)
            response, updated_history = await agent.chat(request.message, history)
        
        # Сохраняем историю
        chat_sessions[session_id] = updated_history
        
        return ChatResponse(
            session_id=session_id,
            message=response
        )
        
    except Exception as e:
        logger.error(f"Ошибка в chat API: {e}")
        raise HTTPException(status_code=500, detail="Внутренняя ошибка сервера")


@app.post("/api/search")
async def search_products(request: ProductSearchRequest):
    """
    Поиск товаров
    """
    try:
        async with AsyncSessionLocal() as db_session:
            agent = SalesAgent(db_session)
            products = await agent._search_products(
                query=request.query,
                category=request.category,
                brand=request.brand,
                min_price=request.min_price,
                max_price=request.max_price,
                limit=request.limit,
            )
        
        return {"products": products, "count": len(products)}
        
    except Exception as e:
        logger.error(f"Ошибка в search API: {e}")
        raise HTTPException(status_code=500, detail="Ошибка поиска")


@app.get("/api/product/{product_id}")
async def get_product(product_id: int):
    """
    Получить информацию о товаре
    """
    try:
        async with AsyncSessionLocal() as db_session:
            agent = SalesAgent(db_session)
            product = await agent._get_product_details(product_id)
        
        if not product:
            raise HTTPException(status_code=404, detail="Товар не найден")
        
        return product
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Ошибка получения товара: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.get("/api/categories")
async def get_categories():
    """
    Получить список категорий
    """
    try:
        async with AsyncSessionLocal() as db_session:
            agent = SalesAgent(db_session)
            categories = await agent._get_categories()
        
        return {"categories": categories}
        
    except Exception as e:
        logger.error(f"Ошибка получения категорий: {e}")
        raise HTTPException(status_code=500, detail="Ошибка сервера")


@app.delete("/api/session/{session_id}")
async def clear_session(session_id: str):
    """
    Очистить сессию чата
    """
    if session_id in chat_sessions:
        del chat_sessions[session_id]
    
    return {"status": "cleared"}


# Статические файлы для виджета
static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")


@app.get("/widget", response_class=HTMLResponse)
async def get_widget():
    """
    Страница с виджетом для встраивания
    """
    widget_html = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Чат-виджет ТехникаПремиум</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=Nunito:wght@400;500;600;700&display=swap" rel="stylesheet">
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Nunito', sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
        }
        .demo-container {
            text-align: center;
            color: #fff;
            padding: 2rem;
        }
        .demo-container h1 {
            font-size: 2.5rem;
            margin-bottom: 1rem;
            background: linear-gradient(90deg, #00d9ff, #00ff88);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }
        .demo-container p {
            opacity: 0.8;
            margin-bottom: 2rem;
        }
    </style>
</head>
<body>
    <div class="demo-container">
        <h1>🏠 ТехникаПремиум</h1>
        <p>AI-ассистент по подбору бытовой техники</p>
        <p>Нажмите на иконку в правом нижнем углу, чтобы начать диалог</p>
    </div>
    
    <!-- Виджет чата -->
    <script src="/static/widget.js"></script>
    <script>
        TehnikaPremiumWidget.init({
            apiUrl: window.location.origin,
            position: 'right',
            primaryColor: '#00d9ff',
            title: 'Консультант ТехникаПремиум'
        });
    </script>
</body>
</html>
"""
    return widget_html


def run_server():
    """Запуск сервера"""
    import uvicorn
    uvicorn.run(
        "src.api.server:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.debug,
    )


if __name__ == "__main__":
    run_server()

