import pytest
import json

def test_api_get_products(client):
    """测试获取产品列表API"""
    response = client.get('/api/v1/products/')
    assert response.status_code == 200
    
    data = json.loads(response.data)
    assert 'result' in data

def test_api_get_single_product(client):
    """测试获取单个产品API"""
    # 先获取一个产品的ID
    with client.application.app_context():
        from app.models import Product
        product = Product.query.first()
        if product:
            product_id = product.id
            
            response = client.get(f'/api/v1/products/{product_id}')
            assert response.status_code == 200
            
            data = json.loads(response.data)
            assert 'result' in data
            assert data['result']['id'] == product_id