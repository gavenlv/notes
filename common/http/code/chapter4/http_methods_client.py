#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP请求方法客户端实现示例
使用requests库演示GET、POST、PUT、DELETE等方法的使用
"""

import requests
import json
import time
from typing import Optional, Dict, Any


class HTTPMethodsClient:
    """HTTP请求方法客户端示例"""
    
    def __init__(self, base_url: str = "http://localhost:5003"):
        """
        初始化客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        
        # 设置默认请求头
        self.session.headers.update({
            'User-Agent': 'HTTP-Methods-Client/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        发送HTTP请求的通用方法
        
        Args:
            method: HTTP方法
            endpoint: API端点
            **kwargs: 其他请求参数
            
        Returns:
            requests.Response: 响应对象
        """
        url = f"{self.base_url}{endpoint}"
        print(f"\n[{method}] {url}")
        
        # 如果有数据，打印请求数据
        if 'json' in kwargs and kwargs['json']:
            print(f"请求数据: {json.dumps(kwargs['json'], ensure_ascii=False, indent=2)}")
        
        try:
            response = self.session.request(method, url, **kwargs)
            print(f"响应状态码: {response.status_code}")
            
            # 打印响应内容（如果是JSON）
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    print(f"响应数据: {json.dumps(response.json(), ensure_ascii=False, indent=2)}")
                except json.JSONDecodeError:
                    print(f"响应内容: {response.text[:200]}...")
            else:
                print(f"响应内容: {response.text[:200]}...")
                
            return response
        except requests.exceptions.RequestException as e:
            print(f"请求失败: {e}")
            raise
    
    def get_users(self, page: int = 1, per_page: int = 10, search: str = "") -> Optional[Dict[Any, Any]]:
        """
        GET /users - 获取用户列表
        
        Args:
            page: 页码
            per_page: 每页数量
            search: 搜索关键词
            
        Returns:
            用户列表数据或None
        """
        params = {}
        if page > 1:
            params['page'] = page
        if per_page != 10:
            params['per_page'] = per_page
        if search:
            params['search'] = search
            
        response = self._make_request('GET', '/users', params=params)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict[Any, Any]]:
        """
        GET /users/<id> - 获取单个用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            用户数据或None
        """
        response = self._make_request('GET', f'/users/{user_id}')
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def create_user(self, name: str, email: str) -> Optional[Dict[Any, Any]]:
        """
        POST /users - 创建新用户
        
        Args:
            name: 用户姓名
            email: 用户邮箱
            
        Returns:
            新创建的用户数据或None
        """
        data = {
            "name": name,
            "email": email
        }
        
        response = self._make_request('POST', '/users', json=data)
        
        if response.status_code in [200, 201]:
            return response.json()
        return None
    
    def update_user(self, user_id: int, **kwargs) -> Optional[Dict[Any, Any]]:
        """
        PUT /users/<id> - 更新用户信息
        
        Args:
            user_id: 用户ID
            **kwargs: 要更新的字段（name, email）
            
        Returns:
            更新后的用户数据或None
        """
        response = self._make_request('PUT', f'/users/{user_id}', json=kwargs)
        
        if response.status_code == 200:
            return response.json()
        return None
    
    def delete_user(self, user_id: int) -> bool:
        """
        DELETE /users/<id> - 删除用户
        
        Args:
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        response = self._make_request('DELETE', f'/users/{user_id}')
        
        return response.status_code in [200, 204]
    
    def head_user(self, user_id: int) -> Optional[requests.Response]:
        """
        HEAD /users/<id> - 获取用户元信息
        
        Args:
            user_id: 用户ID
            
        Returns:
            响应对象或None
        """
        return self._make_request('HEAD', f'/users/{user_id}')
    
    def options_users(self) -> Optional[requests.Response]:
        """
        OPTIONS /users - 获取支持的HTTP方法
        
        Returns:
            响应对象或None
        """
        return self._make_request('OPTIONS', '/users')
    
    def options_user(self, user_id: int) -> Optional[requests.Response]:
        """
        OPTIONS /users/<id> - 获取单个用户支持的HTTP方法
        
        Args:
            user_id: 用户ID
            
        Returns:
            响应对象或None
        """
        return self._make_request('OPTIONS', f'/users/{user_id}')


def demonstrate_http_methods():
    """演示各种HTTP方法的使用"""
    print("HTTP请求方法客户端实现示例")
    print("=" * 50)
    
    # 创建客户端实例
    client = HTTPMethodsClient()
    
    # 等待服务器启动
    print("等待服务器启动...")
    time.sleep(2)
    
    try:
        # 1. GET方法 - 获取用户列表
        print("\n1. GET方法演示 - 获取用户列表")
        print("-" * 30)
        users_data = client.get_users()
        if users_data and users_data.get('success'):
            print(f"成功获取 {len(users_data['data']['users'])} 个用户")
        
        # 2. POST方法 - 创建新用户
        print("\n2. POST方法演示 - 创建新用户")
        print("-" * 30)
        new_user = client.create_user("王五", "wangwu@example.com")
        user_id = None
        if new_user and new_user.get('success'):
            user_id = new_user['data']['id']
            print(f"成功创建用户，ID: {user_id}")
        
        # 3. GET方法 - 获取单个用户
        if user_id:
            print("\n3. GET方法演示 - 获取单个用户")
            print("-" * 30)
            user_data = client.get_user(user_id)
            if user_data and user_data.get('success'):
                print(f"用户信息: {user_data['data']['name']} ({user_data['data']['email']})")
        
        # 4. PUT方法 - 更新用户信息
        if user_id:
            print("\n4. PUT方法演示 - 更新用户信息")
            print("-" * 30)
            updated_user = client.update_user(user_id, name="王五五", email="wangwu5@example.com")
            if updated_user and updated_user.get('success'):
                print(f"用户信息更新成功: {updated_user['data']['name']} ({updated_user['data']['email']})")
        
        # 5. HEAD方法 - 获取用户元信息
        if user_id:
            print("\n5. HEAD方法演示 - 获取用户元信息")
            print("-" * 30)
            head_response = client.head_user(user_id)
            if head_response:
                print(f"响应头信息:")
                for key, value in head_response.headers.items():
                    print(f"  {key}: {value}")
        
        # 6. OPTIONS方法 - 获取支持的HTTP方法
        print("\n6. OPTIONS方法演示 - 获取支持的HTTP方法")
        print("-" * 30)
        options_response = client.options_users()
        if options_response:
            allow_header = options_response.headers.get('Allow')
            if allow_header:
                print(f"支持的HTTP方法: {allow_header}")
        
        # 7. DELETE方法 - 删除用户
        if user_id:
            print("\n7. DELETE方法演示 - 删除用户")
            print("-" * 30)
            deleted = client.delete_user(user_id)
            if deleted:
                print(f"用户删除成功")
        
        # 8. 错误处理演示
        print("\n8. 错误处理演示")
        print("-" * 30)
        # 尝试获取不存在的用户
        error_response = client.get_user(999999)
        if error_response and not error_response.get('success'):
            print(f"错误处理正常工作: {error_response['error']['message']}")
            
    except Exception as e:
        print(f"演示过程中出现错误: {e}")


def main():
    """主函数"""
    demonstrate_http_methods()


if __name__ == '__main__':
    main()