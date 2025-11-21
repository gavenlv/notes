from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

class Category(AuditMixin, Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    products = relationship("Product", back_populates="category")
    
    def product_count(self):
        """获取该分类下的产品数量"""
        return len(self.products)
    
    def __repr__(self):
        return self.name

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    price = Column(Integer)
    category_id = Column(Integer, ForeignKey('category.id'))
    category = relationship("Category", back_populates="products")
    
    def is_expensive(self):
        """判断产品是否昂贵(价格大于1000)"""
        return self.price > 1000
    
    def __repr__(self):
        return self.name