#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
会话管理客户端示例
演示了如何与会话管理服务器进行交互，处理认证和会话维持
"""

import requests
import json
from typing import Optional, Dict, Any
from urllib.parse import urljoin


class SessionManagementClient:
    """会话管理客户端"""
    
    def __init__(self, base_url: str = "http://localhost:5000"):
        """
        初始化客户端
        
        Args:
            base_url (str): 服务器基础URL
        """
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()  # 使用requests.Session保持Cookie
        
    def login(self, username: str, password: str) -> bool:
        """
        用户登录
        
        Args:
            username (str): 用户名
            password (str): 密码
            
        Returns:
            bool: 登录是否成功
        """
        login_url = urljoin(self.base_url, '/login')
        
        # 准备登录数据
        login_data = {
            'username': username,
            'password': password
        }
        
        try:
            # 发送登录请求
            response = self.session.post(login_url, data=login_data)
            
            # 检查登录是否成功（通过状态码和重定向）
            if response.status_code == 200 and 'session_id' in response.cookies:
                print(f"登录成功！会话ID: {response.cookies.get('session_id')[:10]}...")
                return True
            else:
                print(f"登录失败: {response.status_code}")
                if '用户名或密码错误' in response.text:
                    print("原因: 用户名或密码错误")
                return False
                
        except requests.RequestException as e:
            print(f"登录请求失败: {e}")
            return False
    
    def logout(self) -> bool:
        """
        用户登出
        
        Returns:
            bool: 登出是否成功
        """
        logout_url = urljoin(self.base_url, '/logout')
        
        try:
            response = self.session.get(logout_url)
            if response.status_code == 200:
                print("登出成功！")
                return True
            else:
                print(f"登出失败: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"登出请求失败: {e}")
            return False
    
    def check_session(self) -> Optional[Dict[Any, Any]]:
        """
        检查当前会话状态
        
        Returns:
            Optional[Dict]: 会话信息，如果未认证则返回None
        """
        check_url = urljoin(self.base_url, '/api/session/check')
        
        try:
            response = self.session.get(check_url)
            
            if response.status_code == 200:
                session_info = response.json()
                if session_info.get('authenticated'):
                    print("会话有效")
                    return session_info
                else:
                    print("会话无效或已过期")
                    return None
            else:
                print(f"检查会话失败: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"检查会话请求失败: {e}")
            return None
    
    def access_protected_resource(self) -> Optional[Dict[Any, Any]]:
        """
        访问受保护的资源
        
        Returns:
            Optional[Dict]: 资源数据，如果无权限则返回None
        """
        protected_url = urljoin(self.base_url, '/api/protected')
        
        try:
            response = self.session.get(protected_url)
            
            if response.status_code == 200:
                data = response.json()
                print("成功访问受保护资源")
                return data
            elif response.status_code == 401:
                print("访问被拒绝：未认证")
                return None
            else:
                print(f"访问受保护资源失败: {response.status_code}")
                return None
                
        except requests.RequestException as e:
            print(f"访问受保护资源失败: {e}")
            return None
    
    def access_admin_panel(self) -> bool:
        """
        访问管理员面板
        
        Returns:
            bool: 是否有访问权限
        """
        admin_url = urljoin(self.base_url, '/admin')
        
        try:
            response = self.session.get(admin_url)
            
            if response.status_code == 200 and '管理员面板' in response.text:
                print("成功访问管理员面板")
                return True
            elif response.status_code == 403:
                print("访问被拒绝：权限不足")
                return False
            elif response.status_code == 401:
                print("访问被拒绝：未认证")
                return False
            else:
                print(f"访问管理员面板失败: {response.status_code}")
                return False
                
        except requests.RequestException as e:
            print(f"访问管理员面板失败: {e}")
            return False
    
    def get_cookies(self) -> Dict[str, str]:
        """
        获取当前会话的Cookies
        
        Returns:
            Dict[str, str]: Cookies字典
        """
        return dict(self.session.cookies)
    
    def clear_cookies(self):
        """清除所有Cookies"""
        self.session.cookies.clear()
        print("已清除所有Cookies")


def demo_session_client():
    """演示会话管理客户端的使用"""
    print("=== 会话管理客户端演示 ===")
    
    # 创建客户端实例
    client = SessionManagementClient("http://localhost:5000")
    
    # 1. 尝试访问受保护资源（未登录状态）
    print("\n1. 未登录状态下访问受保护资源:")
    client.access_protected_resource()
    
    # 2. 用户登录
    print("\n2. 用户登录:")
    if client.login('admin', 'password'):
        print("登录成功")
        
        # 3. 检查会话状态
        print("\n3. 检查会话状态:")
        session_info = client.check_session()
        if session_info:
            print(f"当前用户: {session_info['user']['username']}")
            print(f"会话创建时间: {session_info['session']['created_at']}")
        
        # 4. 访问受保护资源
        print("\n4. 访问受保护资源:")
        protected_data = client.access_protected_resource()
        if protected_data:
            print(f"获取到数据: {protected_data}")
        
        # 5. 访问管理员面板
        print("\n5. 访问管理员面板:")
        client.access_admin_panel()
        
        # 6. 查看当前Cookies
        print("\n6. 当前Cookies:")
        cookies = client.get_cookies()
        for name, value in cookies.items():
            print(f"  {name}: {value[:20]}..." if len(value) > 20 else f"  {name}: {value}")
        
        # 7. 普通用户登录测试
        print("\n7. 切换到普通用户:")
        client.clear_cookies()  # 清除之前的会话
        if client.login('user1', 'password123'):
            print("普通用户登录成功")
            
            # 访问受保护资源
            print("\n访问受保护资源:")
            client.access_protected_resource()
            
            # 尝试访问管理员面板
            print("\n尝试访问管理员面板:")
            client.access_admin_panel()
            
            # 登出
            print("\n普通用户登出:")
            client.logout()
    
    # 8. 登出原用户
    print("\n8. 原用户登出:")
    client.clear_cookies()  # 清除之前的会话
    if client.login('admin', 'password'):  # 重新登录
        client.logout()
    
    # 9. 错误登录测试
    print("\n9. 错误登录测试:")
    client.login('admin', 'wrongpassword')


def interactive_demo():
    """交互式演示"""
    print("=== 交互式会话管理演示 ===")
    print("请输入服务器地址 (默认: http://localhost:5000): ", end="")
    base_url = input().strip()
    if not base_url:
        base_url = "http://localhost:5000"
    
    client = SessionManagementClient(base_url)
    
    while True:
        print("\n请选择操作:")
        print("1. 登录")
        print("2. 检查会话")
        print("3. 访问受保护资源")
        print("4. 访问管理员面板")
        print("5. 登出")
        print("6. 查看Cookies")
        print("7. 清除Cookies")
        print("0. 退出")
        print("请输入选项: ", end="")
        
        choice = input().strip()
        
        if choice == '1':
            username = input("用户名: ")
            password = input("密码: ")
            client.login(username, password)
        
        elif choice == '2':
            client.check_session()
        
        elif choice == '3':
            client.access_protected_resource()
        
        elif choice == '4':
            client.access_admin_panel()
        
        elif choice == '5':
            client.logout()
        
        elif choice == '6':
            cookies = client.get_cookies()
            if cookies:
                print("当前Cookies:")
                for name, value in cookies.items():
                    print(f"  {name}: {value[:30]}..." if len(value) > 30 else f"  {name}: {value}")
            else:
                print("没有Cookies")
        
        elif choice == '7':
            client.clear_cookies()
        
        elif choice == '0':
            print("再见！")
            break
        
        else:
            print("无效选项，请重新选择")


if __name__ == '__main__':
    # 运行演示
    demo_session_client()
    
    # 如果需要交互式演示，取消下面的注释
    # print("\n" + "="*50)
    # interactive_demo()