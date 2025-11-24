import pytest
import json
from app.models import Product, Category

class TestProductApi:
    
    def test_get_products(self, client, init_database):
        """测试获取产品列表"""
        response = client.get('/api/v1/product/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        assert len(data['result']) == 2
    
    def test_create_product(self, client, init_database):
        """测试创建产品"""
        # 获取类别ID
        category = init_database.session.query(Category).first()
        
        new_product = {
            'name': '新笔记本电脑',
            'description': '高性能笔记本电脑',
            'price': 12999.99,
            'stock_quantity': 50,
            'category': category.id,
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/product/',
            data=json.dumps(new_product),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # 验证产品已创建
        product = init_database.session.query(Product).filter_by(name='新笔记本电脑').first()
        assert product is not None
        assert product.price == 12999.99
    
    def test_get_product_detail(self, client, init_database):
        """测试获取产品详情"""
        product = init_database.session.query(Product).first()
        
        response = client.get(f'/api/v1/product/{product.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        assert data['result']['id'] == product.id
        assert data['result']['name'] == product.name
    
    def test_update_product(self, client, init_database):
        """测试更新产品"""
        product = init_database.session.query(Product).first()
        
        update_data = {
            'name': '更新的产品名称',
            'price': 7999.99
        }
        
        response = client.put(
            f'/api/v1/product/{product.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # 验证产品已更新
        updated_product = init_database.session.query(Product).get(product.id)
        assert updated_product.name == '更新的产品名称'
        assert updated_product.price == 7999.99
    
    def test_delete_product(self, client, init_database):
        """测试删除产品"""
        product = init_database.session.query(Product).first()
        
        response = client.delete(f'/api/v1/product/{product.id}')
        assert response.status_code == 200
        
        # 验证产品已删除
        deleted_product = init_database.session.query(Product).get(product.id)
        assert deleted_product is None
    
    def test_search_products(self, client, init_database):
        """测试搜索产品"""
        # 按名称搜索
        response = client.get('/api/v1/product/?name=手机')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        # 应该找到"智能手机"
        assert len(data['result']) >= 1
    
    def test_product_validation(self, client, init_database):
        """测试产品数据验证"""
        category = init_database.session.query(Category).first()
        
        # 测试无效价格
        invalid_product = {
            'name': '无效产品',
            'price': -100,  # 无效价格
            'category': category.id
        }
        
        response = client.post(
            '/api/v1/product/',
            data=json.dumps(invalid_product),
            content_type='application/json'
        )
        
        # 应该返回验证错误
        assert response.status_code == 422