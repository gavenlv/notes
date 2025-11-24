from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, ForeignKey, Index
from sqlalchemy.orm import relationship

class Category(Model):
    __tablename__ = 'category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False, index=True)
    products = relationship("Product", back_populates="category")
    
    __table_args__ = (
        Index('idx_category_name', 'name'),
    )
    
    def __repr__(self):
        return self.name

class Product(Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False, index=True)
    description = Column(Text)
    price = Column(Integer, index=True)
    category_id = Column(Integer, ForeignKey('category.id'), index=True)
    category = relationship("Category", back_populates="products")
    
    __table_args__ = (
        Index('idx_product_category_price', 'category_id', 'price'),
        Index('idx_product_name_category', 'name', 'category_id'),
    )
    
    def __repr__(self):
        return self.name