from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Numeric
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    is_active = Column(Boolean, default=True)
    
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Numeric(precision=10, scale=2))
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="products")
    
    order_items = relationship("OrderItem", back_populates="product")
    
    def __repr__(self):
        return self.name

class Order(Model):
    __tablename__ = 'order'
    
    id = Column(Integer, primary_key=True)
    order_number = Column(String(50), unique=True, nullable=False)
    customer_name = Column(String(100), nullable=False)
    customer_email = Column(String(100))
    total_amount = Column(Numeric(precision=10, scale=2))
    status = Column(String(20), default='pending')  # pending, confirmed, shipped, delivered, cancelled
    created_on = Column(DateTime, default=func.now())
    
    items = relationship("OrderItem", back_populates="order")
    
    def __repr__(self):
        return f"Order {self.order_number}"

class OrderItem(Model):
    __tablename__ = 'order_item'
    
    id = Column(Integer, primary_key=True)
    quantity = Column(Integer, nullable=False)
    unit_price = Column(Numeric(precision=10, scale=2))
    total_price = Column(Numeric(precision=10, scale=2))
    
    order_id = Column(Integer, ForeignKey('order.id'))
    product_id = Column(Integer, ForeignKey('product.id'))
    
    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")