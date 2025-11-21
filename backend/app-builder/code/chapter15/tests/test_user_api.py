import pytest
import json

class TestUserApi:
    
    def test_get_users_list(self, client, init_database):
        """测试获取用户列表"""
        # 先登录获取管理员权限
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
        
        response = client.get(
            '/api/v1/user/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
    
    def test_get_user_detail(self, client, init_database):
        """测试获取用户详情"""
        # 先登录
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
        
        # 获取用户ID
        users_response = client.get(
            '/api/v1/user/',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert users_response.status_code == 200
        users_data = json.loads(users_response.data)
        user_id = users_data['result'][0]['id']
        
        # 获取用户详情
        response = client.get(
            f'/api/v1/user/{user_id}',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'result' in data
        assert data['result']['id'] == user_id
    
    def test_user_profile_endpoints(self, client, init_database):
        """测试用户资料端点"""
        # 先登录
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
        
        # 获取自己的资料
        response = client.get(
            '/api/v1/user/profile',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'user' in data
        
        # 更新自己的资料
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name'
        }
        
        response = client.put(
            '/api/v1/user/profile',
            data=json.dumps(update_data),
            content_type='application/json',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200