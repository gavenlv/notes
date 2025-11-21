import pytest
import json
from app.models import Category

class TestCategoryApi:
    
    def test_get_categories(self, client, init_database):
        """测试获取类别列表"""
        response = client.get('/api/v1/category/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        assert len(data['result']) == 2
    
    def test_create_category(self, client, init_database):
        """测试创建类别"""
        new_category = {
            'name': '新类别',
            'description': '新类别的描述',
            'is_active': True
        }
        
        response = client.post(
            '/api/v1/category/',
            data=json.dumps(new_category),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # 验证类别已创建
        category = init_database.session.query(Category).filter_by(name='新类别').first()
        assert category is not None
        assert category.description == '新类别的描述'
    
    def test_get_category_detail(self, client, init_database):
        """测试获取类别详情"""
        category = init_database.session.query(Category).first()
        
        response = client.get(f'/api/v1/category/{category.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        assert data['result']['id'] == category.id
        assert data['result']['name'] == category.name
    
    def test_update_category(self, client, init_database):
        """测试更新类别"""
        category = init_database.session.query(Category).first()
        
        update_data = {
            'name': '更新的类别名称',
            'description': '更新的描述'
        }
        
        response = client.put(
            f'/api/v1/category/{category.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # 验证类别已更新
        updated_category = init_database.session.query(Category).get(category.id)
        assert updated_category.name == '更新的类别名称'
        assert updated_category.description == '更新的描述'
    
    def test_delete_category(self, client, init_database):
        """测试删除类别"""
        category = init_database.session.query(Category).first()
        
        response = client.delete(f'/api/v1/category/{category.id}')
        assert response.status_code == 200
        
        # 验证类别已删除
        deleted_category = init_database.session.query(Category).get(category.id)
        assert deleted_category is None
    
    def test_category_validation(self, client, init_database):
        """测试类别数据验证"""
        # 测试名称过长
        invalid_category = {
            'name': 'A' * 60,  # 超过50个字符
            'description': '无效类别的描述'
        }
        
        response = client.post(
            '/api/v1/category/',
            data=json.dumps(invalid_category),
            content_type='application/json'
        )
        
        # 应该返回验证错误
        assert response.status_code == 422