#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部客户端示例
展示如何在Python客户端中处理HTTP头部
"""

import requests
import json
from typing import Dict, Optional, List
import time


class HttpHeadersClient:
    """HTTP头部客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化客户端
        
        Args:
            base_url: 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        # 设置默认头部
        self.session.headers.update({
            'User-Agent': 'HttpHeadersClient/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    def get_users(self) -> Optional[Dict]:
        """
        获取用户列表
        
        Returns:
            响应数据或None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/users")
            print(f"GET /api/users")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头部:")
            for name, value in response.headers.items():
                print(f"    {name}: {value}")
            
            # 检查缓存相关头部
            cache_control = response.headers.get('Cache-Control')
            etag = response.headers.get('ETag')
            if cache_control:
                print(f"  缓存控制: {cache_control}")
            if etag:
                print(f"  ETag: {etag}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
            return None
    
    def create_user(self, name: str, email: str) -> Optional[Dict]:
        """
        创建新用户
        
        Args:
            name: 用户名
            email: 邮箱
            
        Returns:
            响应数据或None
        """
        data = {
            "name": name,
            "email": email
        }
        
        try:
            response = self.session.post(f"{self.base_url}/api/users", json=data)
            print(f"\nPOST /api/users")
            print(f"  发送数据: {data}")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头部:")
            for name, value in response.headers.items():
                print(f"    {name}: {value}")
            
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
            return None
    
    def get_user_with_etag(self, user_id: int) -> Optional[Dict]:
        """
        使用ETag获取用户（条件请求）
        
        Args:
            user_id: 用户ID
            
        Returns:
            响应数据或None
        """
        # 第一次请求获取ETag
        try:
            response = self.session.get(f"{self.base_url}/api/users/{user_id}")
            print(f"\nGET /api/users/{user_id} (首次请求)")
            print(f"  状态码: {response.status_code}")
            
            if response.status_code == 200:
                etag = response.headers.get('ETag')
                data = response.json()
                print(f"  ETag: {etag}")
                print(f"  数据: {data}")
                
                # 第二次请求使用If-None-Match头部
                if etag:
                    print(f"\nGET /api/users/{user_id} (使用ETag条件请求)")
                    headers = {'If-None-Match': etag}
                    response2 = self.session.get(
                        f"{self.base_url}/api/users/{user_id}", 
                        headers=headers
                    )
                    print(f"  状态码: {response2.status_code}")
                    if response2.status_code == 304:
                        print(f"  服务器返回304 Not Modified - 使用缓存")
                        return data  # 返回缓存的数据
                    else:
                        print(f"  服务器返回新数据")
                        return response2.json()
            else:
                print(f"  错误: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
            return None
    
    def access_secure_data(self, token: Optional[str] = None) -> Optional[Dict]:
        """
        访问安全数据
        
        Args:
            token: 认证令牌
            
        Returns:
            响应数据或None
        """
        headers = {}
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        try:
            response = self.session.get(
                f"{self.base_url}/api/secure-data",
                headers=headers
            )
            print(f"\nGET /api/secure-data")
            print(f"  认证令牌: {'已提供' if token else '未提供'}")
            print(f"  状态码: {response.status_code}")
            print(f"  响应头部:")
            for name, value in response.headers.items():
                print(f"    {name}: {value}")
            
            # 检查认证相关头部
            www_authenticate = response.headers.get('WWW-Authenticate')
            if www_authenticate:
                print(f"  WWW-Authenticate: {www_authenticate}")
            
            if response.status_code == 200:
                return response.json()
            elif response.status_code == 401:
                print(f"  认证失败: 需要有效的认证令牌")
                return {"error": "认证失败", "status_code": 401}
            else:
                response.raise_for_status()
                return response.json()
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
            return None
    
    def test_cache_strategies(self):
        """测试不同缓存策略"""
        cache_types = ['default', 'public', 'private', 'no-cache']
        
        for cache_type in cache_types:
            try:
                response = self.session.get(
                    f"{self.base_url}/api/cache-example",
                    params={'type': cache_type}
                )
                print(f"\nGET /api/cache-example?type={cache_type}")
                print(f"  状态码: {response.status_code}")
                
                cache_control = response.headers.get('Cache-Control')
                if cache_control:
                    print(f"  Cache-Control: {cache_control}")
                
                etag = response.headers.get('ETag')
                if etag:
                    print(f"  ETag: {etag}")
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"  数据: {data}")
                else:
                    print(f"  错误: {response.status_code}")
                    
            except requests.exceptions.RequestException as e:
                print(f"  错误: {e}")
    
    def test_cors_request(self):
        """测试CORS请求"""
        try:
            # 设置Origin头部
            headers = {'Origin': 'http://example.com'}
            
            # 测试GET请求
            response = self.session.get(
                f"{self.base_url}/api/cors-example",
                headers=headers
            )
            print(f"\nGET /api/cors-example (CORS测试)")
            print(f"  Origin: http://example.com")
            print(f"  状态码: {response.status_code}")
            
            # 检查CORS相关头部
            cors_headers = [
                'Access-Control-Allow-Origin',
                'Access-Control-Allow-Credentials',
                'Access-Control-Allow-Methods',
                'Access-Control-Allow-Headers'
            ]
            
            for header in cors_headers:
                value = response.headers.get(header)
                if value:
                    print(f"  {header}: {value}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  数据: {data}")
            
            # 测试POST请求
            post_data = {"message": "Hello CORS"}
            response2 = self.session.post(
                f"{self.base_url}/api/cors-example",
                json=post_data,
                headers=headers
            )
            print(f"\nPOST /api/cors-example (CORS测试)")
            print(f"  发送数据: {post_data}")
            print(f"  状态码: {response2.status_code}")
            
            for header in cors_headers:
                value = response2.headers.get(header)
                if value:
                    print(f"  {header}: {value}")
            
            if response2.status_code == 200:
                data2 = response2.json()
                print(f"  数据: {data2}")
                
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
    
    def inspect_all_headers(self, endpoint: str = "/") -> Optional[Dict]:
        """
        检查指定端点的所有头部
        
        Args:
            endpoint: 要检查的端点
            
        Returns:
            响应数据或None
        """
        try:
            response = self.session.get(f"{self.base_url}{endpoint}")
            print(f"\nGET {endpoint} (完整头部检查)")
            print(f"  状态码: {response.status_code}")
            print(f"  所有响应头部:")
            
            for name, value in response.headers.items():
                print(f"    {name}: {value}")
            
            if response.status_code == 200:
                try:
                    return response.json()
                except json.JSONDecodeError:
                    return {"content": response.text[:200] + "..."}
            else:
                print(f"  错误: {response.status_code}")
                return None
                
        except requests.exceptions.RequestException as e:
            print(f"  错误: {e}")
            return None


def main():
    """主函数"""
    print("HTTP头部客户端示例")
    print("=" * 50)
    
    client = HttpHeadersClient()
    
    # 1. 获取用户列表
    print("\n1. 获取用户列表")
    client.get_users()
    
    # 2. 创建新用户
    print("\n2. 创建新用户")
    client.create_user("王五", "wangwu@example.com")
    
    # 3. 使用ETag获取用户
    print("\n3. 使用ETag获取用户")
    client.get_user_with_etag(1)
    
    # 4. 访问安全数据（无认证）
    print("\n4. 访问安全数据（无认证）")
    client.access_secure_data()
    
    # 5. 访问安全数据（有效认证）
    print("\n5. 访问安全数据（有效认证）")
    client.access_secure_data("valid-token")
    
    # 6. 访问安全数据（无效认证）
    print("\n6. 访问安全数据（无效认证）")
    client.access_secure_data("invalid-token")
    
    # 7. 测试缓存策略
    print("\n7. 测试缓存策略")
    client.test_cache_strategies()
    
    # 8. 测试CORS请求
    print("\n8. 测试CORS请求")
    client.test_cors_request()
    
    # 9. 检查首页所有头部
    print("\n9. 检查首页所有头部")
    client.inspect_all_headers("/")


if __name__ == '__main__':
    main()