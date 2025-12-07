"""
Модели базы данных для хранения товаров
"""
from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Text, Float, 
    DateTime, ForeignKey, Boolean, JSON
)
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()


class Category(Base):
    """Категория товаров"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    slug = Column(String(255), unique=True, nullable=False)
    url = Column(String(500), nullable=True)
    parent_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    parent = relationship("Category", remote_side=[id], backref="children")
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return f"<Category(id={self.id}, name='{self.name}')>"


class Product(Base):
    """Товар"""
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    external_id = Column(String(100), unique=True, nullable=True)  # ID с сайта
    name = Column(String(500), nullable=False)
    slug = Column(String(500), nullable=True)
    url = Column(String(1000), nullable=True)
    
    # Цены
    price = Column(Float, nullable=True)
    old_price = Column(Float, nullable=True)  # Старая цена (для скидок)
    currency = Column(String(10), default="RUB")
    
    # Описание и характеристики
    description = Column(Text, nullable=True)
    short_description = Column(Text, nullable=True)
    brand = Column(String(255), nullable=True)
    model = Column(String(255), nullable=True)
    article = Column(String(100), nullable=True)  # Артикул
    
    # Изображения
    image_url = Column(String(1000), nullable=True)
    images = Column(JSON, nullable=True)  # Список URL изображений
    
    # Наличие
    in_stock = Column(Boolean, default=True)
    stock_quantity = Column(Integer, nullable=True)
    
    # Категория
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    category = relationship("Category", back_populates="products")
    
    # Дополнительные данные
    specifications = Column(JSON, nullable=True)  # Характеристики в JSON
    features = Column(JSON, nullable=True)  # Особенности
    
    # Метаданные
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Связи
    specs = relationship("ProductSpecification", back_populates="product", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Product(id={self.id}, name='{self.name}', price={self.price})>"
    
    def to_dict(self) -> dict:
        """Преобразовать в словарь для AI"""
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "model": self.model,
            "article": self.article,
            "price": self.price,
            "old_price": self.old_price,
            "description": self.description,
            "short_description": self.short_description,
            "url": self.url,
            "image_url": self.image_url,
            "in_stock": self.in_stock,
            "category": self.category.name if self.category else None,
            "specifications": self.specifications,
            "features": self.features,
        }
    
    def format_for_user(self) -> str:
        """Форматированное описание для пользователя"""
        parts = [f"📦 **{self.name}**"]
        
        if self.brand:
            parts.append(f"🏷️ Бренд: {self.brand}")
        if self.model:
            parts.append(f"📋 Модель: {self.model}")
        if self.article:
            parts.append(f"🔢 Артикул: {self.article}")
        
        if self.price:
            price_str = f"💰 Цена: {self.price:,.0f} ₽".replace(",", " ")
            if self.old_price and self.old_price > self.price:
                old_price_str = f"{self.old_price:,.0f} ₽".replace(",", " ")
                price_str += f" (было {old_price_str})"
            parts.append(price_str)
        
        if self.in_stock:
            parts.append("✅ В наличии")
        else:
            parts.append("❌ Нет в наличии")
        
        if self.short_description:
            parts.append(f"\n📝 {self.short_description}")
        
        if self.url:
            parts.append(f"\n🔗 Подробнее: {self.url}")
        
        return "\n".join(parts)


class ProductSpecification(Base):
    """Характеристика товара"""
    __tablename__ = "product_specifications"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    name = Column(String(255), nullable=False)
    value = Column(String(500), nullable=True)
    unit = Column(String(50), nullable=True)  # Единица измерения
    group = Column(String(255), nullable=True)  # Группа характеристик
    
    product = relationship("Product", back_populates="specs")
    
    def __repr__(self):
        return f"<ProductSpecification(name='{self.name}', value='{self.value}')>"

