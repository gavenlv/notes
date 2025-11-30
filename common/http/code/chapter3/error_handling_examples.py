#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
错误处理示例
演示客户端如何处理不同状态码，实现重试机制和优雅降级处理
"""

import requests
import time
import json
from typing import Optional, Dict, Any


class HTTPClient:
    """HTTP客户端，包含错误处理机制"""
    
    def __init__(self, base_url: str, timeout: int = 30):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> Optional[requests.Response]:
        """发送HTTP请求"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, timeout=self.timeout, **kwargs)
            return response
        except requests.exceptions.Timeout:
            print(f"[错误] 请求超时: {url}")
            return None
        except requests.exceptions.ConnectionError:
            print(f"[错误] 连接失败: {url}")
            return None
        except Exception as e:
            print(f"[错误] 请求异常: {url}, 错误: {str(e)}")
            return None
    
    def handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """处理HTTP响应"""
        try:
            data = response.json()
        except json.JSONDecodeError:
            data = {"raw_content": response.text}
        
        result = {
            "status_code": response.status_code,
            "data": data,
            "headers": dict(response.headers),
            "success": response.ok
        }
        
        return result


class ErrorHandler:
    """错误处理类"""
    
    @staticmethod
    def handle_400(response_data: Dict[str, Any]) -> bool:
        """处理400错误"""
        print("[400错误] 请求参数错误")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误代码: {error_info.get('code', 'N/A')}")
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
            if "details" in error_info:
                print(f"  详细信息: {error_info['details']}")
        return False
    
    @staticmethod
    def handle_401(response_data: Dict[str, Any]) -> bool:
        """处理401错误"""
        print("[401错误] 认证失败")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
        print("  解决方案: 请检查认证令牌是否正确")
        return False
    
    @staticmethod
    def handle_403(response_data: Dict[str, Any]) -> bool:
        """处理403错误"""
        print("[403错误] 权限不足")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
        print("  解决方案: 请联系管理员确认权限")
        return False
    
    @staticmethod
    def handle_404(response_data: Dict[str, Any]) -> bool:
        """处理404错误"""
        print("[404错误] 资源未找到")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
        print("  解决方案: 请检查请求的URL是否正确")
        return False
    
    @staticmethod
    def handle_405(response_data: Dict[str, Any]) -> bool:
        """处理405错误"""
        print("[405错误] 请求方法不被允许")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
        if "Allowed" in response_data["headers"]:
            print(f"  允许的方法: {response_data['headers']['Allow']}")
        print("  解决方案: 请检查请求方法是否正确")
        return False
    
    @staticmethod
    def handle_429(response_data: Dict[str, Any]) -> bool:
        """处理429错误"""
        print("[429错误] 请求过于频繁")
        retry_after = response_data["headers"].get("Retry-After", "未知")
        print(f"  请在 {retry_after} 秒后重试")
        
        # 实现简单的等待重试
        try:
            wait_time = int(retry_after)
            print(f"  等待 {wait_time} 秒后自动重试...")
            time.sleep(wait_time)
            return True  # 表示可以重试
        except ValueError:
            print("  无法解析重试时间，跳过重试")
            return False
    
    @staticmethod
    def handle_500(response_data: Dict[str, Any]) -> bool:
        """处理500错误"""
        print("[500错误] 服务器内部错误")
        if "error" in response_data["data"]:
            error_info = response_data["data"]["error"]
            print(f"  错误信息: {error_info.get('message', 'N/A')}")
        print("  解决方案: 请稍后重试或联系系统管理员")
        return False
    
    @staticmethod
    def handle_503(response_data: Dict[str, Any]) -> bool:
        """处理503错误"""
        print("[503错误] 服务暂时不可用")
        retry_after = response_data["headers"].get("Retry-After", "未知")
        print(f"  请在 {retry_after} 秒后重试")
        
        # 实现简单的等待重试
        try:
            wait_time = int(retry_after)
            print(f"  等待 {wait_time} 秒后自动重试...")
            time.sleep(wait_time)
            return True  # 表示可以重试
        except ValueError:
            print("  无法解析重试时间，跳过重试")
            return False


class APIClient:
    """API客户端，集成错误处理"""
    
    def __init__(self, base_url: str):
        self.client = HTTPClient(base_url)
        self.error_handler = ErrorHandler()
    
    def _request_with_retry(self, method: str, endpoint: str, max_retries: int = 3, **kwargs) -> Optional[Dict[str, Any]]:
        """带重试机制的请求"""
        retries = 0
        
        while retries <= max_retries:
            response = self.client._make_request(method, endpoint, **kwargs)
            
            if response is None:
                retries += 1
                if retries <= max_retries:
                    print(f"  请求失败，{retries}秒后进行第{retries}次重试...")
                    time.sleep(retries)  # 递增延迟
                    continue
                else:
                    print("  达到最大重试次数，请求失败")
                    return None
            
            response_data = self.client.handle_response(response)
            
            # 成功响应直接返回
            if response_data["success"]:
                return response_data
            
            # 处理不同的错误状态码
            status_code = response_data["status_code"]
            print(f"[{status_code}] 处理错误响应")
            
            # 根据状态码调用相应的错误处理方法
            retry = False
            if status_code == 400:
                self.error_handler.handle_400(response_data)
            elif status_code == 401:
                self.error_handler.handle_401(response_data)
            elif status_code == 403:
                self.error_handler.handle_403(response_data)
            elif status_code == 404:
                self.error_handler.handle_404(response_data)
            elif status_code == 405:
                self.error_handler.handle_405(response_data)
            elif status_code == 429:
                retry = self.error_handler.handle_429(response_data)
            elif status_code == 500:
                self.error_handler.handle_500(response_data)
            elif status_code == 503:
                retry = self.error_handler.handle_503(response_data)
            else:
                print(f"[{status_code}] 未处理的状态码")
                print(f"  响应内容: {response_data['data']}")
            
            # 如果错误处理函数返回True，则进行重试
            if retry:
                retries = 0  # 重置重试计数
                continue
            
            # 如果不需要重试或者达到最大重试次数，则退出
            if retries >= max_retries:
                print("  达到最大重试次数，请求失败")
                return response_data
            
            retries += 1
            if retries <= max_retries:
                print(f"  {retries}秒后进行第{retries}次重试...")
                time.sleep(retries)  # 递增延迟
        
        return None
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """获取用户信息"""
        print(f"获取用户信息，用户ID: {user_id}")
        return self._request_with_retry("GET", f"/users/{user_id}")
    
    def create_user(self, name: str, email: str) -> Optional[Dict[str, Any]]:
        """创建用户"""
        print(f"创建用户: {name} ({email})")
        data = {"name": name, "email": email}
        return self._request_with_retry("POST", "/users", json=data)
    
    def update_user(self, user_id: int, name: str = None, email: str = None) -> Optional[Dict[str, Any]]:
        """更新用户信息"""
        print(f"更新用户信息，用户ID: {user_id}")
        data = {}
        if name:
            data["name"] = name
        if email:
            data["email"] = email
        return self._request_with_retry("PUT", f"/users/{user_id}", json=data)
    
    def delete_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """删除用户"""
        print(f"删除用户，用户ID: {user_id}")
        return self._request_with_retry("DELETE", f"/users/{user_id}")
    
    def search_users(self, query: str) -> Optional[Dict[str, Any]]:
        """搜索用户"""
        print(f"搜索用户，关键字: {query}")
        return self._request_with_retry("GET", f"/users/search?q={query}")
    
    def batch_delete_users(self, user_ids: list) -> Optional[Dict[str, Any]]:
        """批量删除用户"""
        print(f"批量删除用户，IDs: {user_ids}")
        data = {"ids": user_ids}
        return self._request_with_retry("DELETE", "/users/batch", json=data)


def demo_basic_error_handling():
    """演示基本错误处理"""
    print("=" * 60)
    print("基本错误处理演示")
    print("=" * 60)
    
    # 使用状态码模拟器作为测试服务器
    client = APIClient("http://localhost:5000")
    
    # 测试各种状态码
    test_endpoints = [
        ("/status/200", "GET"),
        ("/status/400", "POST"),  # 发送空数据触发400
        ("/status/401", "GET"),
        ("/status/403", "GET"),
        ("/status/404", "GET"),
        ("/status/405", "POST"),
        ("/status/429", "GET"),
        ("/status/500", "GET"),
        ("/status/503", "GET")
    ]
    
    for endpoint, method in test_endpoints:
        print(f"\n测试 {method} {endpoint}:")
        response = client.client._make_request(method, endpoint)
        if response:
            response_data = client.client.handle_response(response)
            print(f"  状态码: {response_data['status_code']}")
            print(f"  成功: {response_data['success']}")
            if not response_data['success']:
                # 调用相应的错误处理方法
                status_code = response_data["status_code"]
                if status_code == 400:
                    ErrorHandler.handle_400(response_data)
                elif status_code == 401:
                    ErrorHandler.handle_401(response_data)
                elif status_code == 403:
                    ErrorHandler.handle_403(response_data)
                elif status_code == 404:
                    ErrorHandler.handle_404(response_data)
                elif status_code == 405:
                    ErrorHandler.handle_405(response_data)
                elif status_code == 429:
                    ErrorHandler.handle_429(response_data)
                elif status_code == 500:
                    ErrorHandler.handle_500(response_data)
                elif status_code == 503:
                    ErrorHandler.handle_503(response_data)
        else:
            print("  请求失败")


def demo_api_client():
    """演示API客户端使用"""
    print("\n" + "=" * 60)
    print("API客户端使用演示")
    print("=" * 60)
    
    # 使用API响应处理器作为测试服务器
    client = APIClient("http://localhost:5001")
    
    # 获取用户列表
    print("\n1. 获取用户列表:")
    response = client._request_with_retry("GET", "/users")
    if response and response["success"]:
        print(f"  用户数量: {len(response['data']['data'])}")
        for user in response['data']['data']:
            print(f"    - {user['name']} ({user['email']})")
    
    # 创建新用户
    print("\n2. 创建新用户:")
    response = client.create_user("王五", "wangwu@example.com")
    user_id = None
    if response and response["success"]:
        user_id = response["data"]["data"]["id"]
        print(f"  用户创建成功，ID: {user_id}")
    
    # 获取单个用户
    if user_id:
        print("\n3. 获取单个用户:")
        response = client.get_user(user_id)
        if response and response["success"]:
            user = response["data"]["data"]
            print(f"  用户信息: {user['name']} ({user['email']})")
    
    # 更新用户信息
    if user_id:
        print("\n4. 更新用户信息:")
        response = client.update_user(user_id, name="王五五")
        if response and response["success"]:
            print("  用户信息更新成功")
    
    # 搜索用户
    print("\n5. 搜索用户:")
    response = client.search_users("王五")
    if response and response["success"]:
        users = response["data"]["data"]
        print(f"  找到 {len(users)} 个匹配的用户")
        for user in users:
            print(f"    - {user['name']} ({user['email']})")
    
    # 删除用户
    if user_id:
        print("\n6. 删除用户:")
        response = client.delete_user(user_id)
        if response and response["success"]:
            print("  用户删除成功")


def main():
    """主函数"""
    print("HTTP错误处理示例")
    print("=" * 60)
    print("本示例演示如何处理HTTP状态码错误")
    print("请确保以下服务正在运行:")
    print("1. HTTP状态码模拟器 (端口5000)")
    print("2. API响应处理器 (端口5001)")
    print("=" * 60)
    
    # 演示基本错误处理
    demo_basic_error_handling()
    
    # 演示API客户端使用
    demo_api_client()


if __name__ == '__main__':
    main()