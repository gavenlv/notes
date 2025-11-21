import pytest
from app.models import Category, Product

def test_category_creation(db_session):
    """测试分类创建"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    assert category.id is not None
    assert category.name == "Electronics"

def test_product_creation(db_session):
    """测试产品创建"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    product = Product(
        name="Laptop",
        description="High performance laptop",
        price=1200,
        category_id=category.id
    )
    db_session.add(product)
    db_session.commit()
    
    assert product.id is not None
    assert product.name == "Laptop"
    assert product.category.name == "Electronics"

def test_category_product_count(db_session):
    """测试分类产品计数"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    product1 = Product(name="Laptop", price=1200, category_id=category.id)
    product2 = Product(name="Mouse", price=25, category_id=category.id)
    db_session.add_all([product1, product2])
    db_session.commit()
    
    assert category.product_count() == 2

def test_product_is_expensive(db_session):
    """测试产品昂贵判断"""
    category = Category(name="Electronics")
    db_session.add(category)
    db_session.commit()
    
    expensive_product = Product(name="Laptop", price=1200, category_id=category.id)
    cheap_product = Product(name="Mouse", price=25, category_id=category.id)
    db_session.add_all([expensive_product, cheap_product])
    db_session.commit()
    
    assert expensive_product.is_expensive() is True
    assert cheap_product.is_expensive() is False