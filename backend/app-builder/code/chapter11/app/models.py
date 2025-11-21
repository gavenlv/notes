from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

class Category(AuditMixin, Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    
    # 预加载关系
    products = relationship("Product", back_populates="category")
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'), index=True)
    
    # 预加载关系
    category = relationship("Category", back_populates="products")
    
    # 复合索引
    __table_args__ = (Index('idx_category_price', 'category_id', 'price'),)
    
    def __repr__(self):
        return self.name