import pytest
from app.utils import calculate_total_price, validate_product_data
from app.models import Product

def test_calculate_total_price():
    """测试计算总价函数"""
    products = [
        Product(name="Product 1", price=100),
        Product(name="Product 2", price=200),
        Product(name="Product 3", price=300)
    ]
    
    total = calculate_total_price(products)
    assert total == 600

def test_validate_product_data_decorator():
    """测试产品数据验证装饰器"""
    @validate_product_data
    def create_product(name, price):
        return {"name": name, "price": price}
    
    # 正常情况
    result = create_product("Test Product", 100)
    assert result["price"] == 100
    
    # 异常情况
    with pytest.raises(ValueError):
        create_product("Test Product", -50)