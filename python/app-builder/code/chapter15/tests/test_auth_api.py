import pytest
import json

class TestAuthApi:
    
    def test_login_success(self, client, init_database):
        """测试成功登录"""
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'access_token' in data
        assert 'user' in data
    
    def test_login_invalid_credentials(self, client, init_database):
        """测试无效凭证登录"""
        login_data = {
            'username': 'invalid',
            'password': 'wrongpassword'
        }
        
        response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert response.status_code == 401
    
    def test_get_user_profile(self, client, init_database):
        """测试获取用户资料"""
        # 先登录获取token
        login_data = {
            'username': 'admin',
            'password': 'admin'
        }
        
        login_response = client.post(
            '/api/v1/auth/login',
            data=json.dumps(login_data),
            content_type='application/json'
        )
        
        assert login_response.status_code == 200
        token_data = json.loads(login_response.data)
        access_token = token_data['access_token']
        
        # 使用token获取用户资料
        response = client.get(
            '/api/v1/auth/profile',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        assert data['user']['username'] == 'admin'
    
    def test_access_protected_endpoint_without_token(self, client, init_database):
        """测试无token访问受保护端点"""
        response = client.get('/api/v1/auth/profile')
        assert response.status_code == 401