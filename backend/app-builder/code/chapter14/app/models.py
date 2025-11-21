from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    
    # 关系
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer)  # 以分为单位存储价格
    stock_quantity = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    
    # 外键
    category_id = Column(Integer, ForeignKey('category.id'))
    
    # 关系
    category = relationship("Category", back_populates="products")
    
    def __repr__(self):
        return self.name