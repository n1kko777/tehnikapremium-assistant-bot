"""
Векторное хранилище для поиска товаров
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
from loguru import logger

import chromadb
from chromadb.config import Settings as ChromaSettings
from sentence_transformers import SentenceTransformer

from src.config import get_settings
from src.database.models import Product

settings = get_settings()


class ProductVectorStore:
    """Векторное хранилище товаров для семантического поиска"""
    
    def __init__(self):
        self.chroma_path = Path(settings.chroma_db_path)
        self.chroma_path.mkdir(parents=True, exist_ok=True)
        
        # Инициализация ChromaDB
        self.client = chromadb.PersistentClient(
            path=str(self.chroma_path),
            settings=ChromaSettings(
                anonymized_telemetry=False,
                allow_reset=True,
            )
        )
        
        # Коллекция для товаров
        self.collection = self.client.get_or_create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )
        
        # Модель для эмбеддингов (многоязычная, хорошо работает с русским)
        self.embedder = SentenceTransformer(
            "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
        )
        
        logger.info(f"Векторное хранилище инициализировано: {self.chroma_path}")
    
    def _create_product_text(self, product: Product) -> str:
        """Создать текстовое представление товара для индексации"""
        parts = [product.name]
        
        if product.brand:
            parts.append(f"Бренд: {product.brand}")
        if product.model:
            parts.append(f"Модель: {product.model}")
        if product.category:
            parts.append(f"Категория: {product.category.name}")
        if product.description:
            parts.append(product.description)
        if product.short_description:
            parts.append(product.short_description)
        
        # Добавляем характеристики
        if product.specifications:
            for key, value in product.specifications.items():
                parts.append(f"{key}: {value}")
        
        return " | ".join(parts)
    
    def add_product(self, product: Product) -> None:
        """Добавить товар в векторное хранилище"""
        text = self._create_product_text(product)
        embedding = self.embedder.encode(text).tolist()
        
        metadata = {
            "product_id": product.id,
            "name": product.name,
            "brand": product.brand or "",
            "price": product.price or 0,
            "in_stock": product.in_stock,
            "category": product.category.name if product.category else "",
        }
        
        self.collection.upsert(
            ids=[str(product.id)],
            embeddings=[embedding],
            documents=[text],
            metadatas=[metadata]
        )
    
    def add_products(self, products: List[Product]) -> None:
        """Добавить несколько товаров"""
        if not products:
            return
        
        ids = []
        embeddings = []
        documents = []
        metadatas = []
        
        for product in products:
            text = self._create_product_text(product)
            embedding = self.embedder.encode(text).tolist()
            
            ids.append(str(product.id))
            embeddings.append(embedding)
            documents.append(text)
            metadatas.append({
                "product_id": product.id,
                "name": product.name,
                "brand": product.brand or "",
                "price": product.price or 0,
                "in_stock": product.in_stock,
                "category": product.category.name if product.category else "",
            })
        
        self.collection.upsert(
            ids=ids,
            embeddings=embeddings,
            documents=documents,
            metadatas=metadatas
        )
        
        logger.info(f"Добавлено товаров в векторное хранилище: {len(products)}")
    
    def search(
        self, 
        query: str, 
        n_results: int = 5,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
        category: Optional[str] = None,
        brand: Optional[str] = None,
        in_stock_only: bool = False,
    ) -> List[Dict[str, Any]]:
        """
        Семантический поиск товаров
        
        Args:
            query: Поисковый запрос
            n_results: Количество результатов
            min_price: Минимальная цена
            max_price: Максимальная цена
            category: Фильтр по категории
            brand: Фильтр по бренду
            in_stock_only: Только товары в наличии
        
        Returns:
            Список найденных товаров с метаданными
        """
        # Создаём эмбеддинг запроса
        query_embedding = self.embedder.encode(query).tolist()
        
        # Формируем фильтры
        where_filters = []
        
        if in_stock_only:
            where_filters.append({"in_stock": True})
        if category:
            where_filters.append({"category": {"$eq": category}})
        if brand:
            where_filters.append({"brand": {"$eq": brand}})
        if min_price is not None:
            where_filters.append({"price": {"$gte": min_price}})
        if max_price is not None:
            where_filters.append({"price": {"$lte": max_price}})
        
        where = None
        if len(where_filters) == 1:
            where = where_filters[0]
        elif len(where_filters) > 1:
            where = {"$and": where_filters}
        
        # Выполняем поиск
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            where=where,
            include=["documents", "metadatas", "distances"]
        )
        
        # Форматируем результаты
        found_products = []
        if results["ids"] and results["ids"][0]:
            for i, id_ in enumerate(results["ids"][0]):
                found_products.append({
                    "id": int(id_),
                    "document": results["documents"][0][i] if results["documents"] else None,
                    "metadata": results["metadatas"][0][i] if results["metadatas"] else None,
                    "distance": results["distances"][0][i] if results["distances"] else None,
                })
        
        return found_products
    
    def get_categories(self) -> List[str]:
        """Получить список всех категорий"""
        results = self.collection.get(include=["metadatas"])
        categories = set()
        
        for metadata in results.get("metadatas", []):
            if metadata and metadata.get("category"):
                categories.add(metadata["category"])
        
        return sorted(list(categories))
    
    def get_brands(self) -> List[str]:
        """Получить список всех брендов"""
        results = self.collection.get(include=["metadatas"])
        brands = set()
        
        for metadata in results.get("metadatas", []):
            if metadata and metadata.get("brand"):
                brands.add(metadata["brand"])
        
        return sorted(list(brands))
    
    def clear(self) -> None:
        """Очистить хранилище"""
        self.client.delete_collection("products")
        self.collection = self.client.create_collection(
            name="products",
            metadata={"hnsw:space": "cosine"}
        )
        logger.info("Векторное хранилище очищено")
    
    @property
    def count(self) -> int:
        """Количество товаров в хранилище"""
        return self.collection.count()

