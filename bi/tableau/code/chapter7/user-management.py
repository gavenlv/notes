#!/usr/bin/env python3
"""
Tableau Server用户管理脚本
使用Tableau Server REST API进行用户和权限管理
"""

import requests
import json
import sys
import getpass

class TableauServerManager:
    def __init__(self, server_url, username, password, site_id=""):
        """初始化Tableau Server连接"""
        self.server_url = server_url.rstrip('/')
        self.username = username
        self.password = password
        self.site_id = site_id
        self.api_version = "3.19"  # 使用最新的API版本
        self.auth_token = None
        self.site_id = site_id
        
    def sign_in(self):
        """登录Tableau Server并获取认证令牌"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/auth/signin"
            headers = {"Content-Type": "application/json"}
            
            payload = {
                "credentials": {
                    "name": self.username,
                    "password": self.password,
                    "site": {"contentUrl": self.site_id}
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            self.auth_token = result["credentials"]["token"]
            self.site_id = result["credentials"]["site"]["id"]
            
            print(f"成功登录Tableau Server: {self.server_url}")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"登录失败: {e}")
            return False
    
    def sign_out(self):
        """登出Tableau Server"""
        if self.auth_token:
            try:
                url = f"{self.server_url}/api/{self.api_version}/auth/signout"
                headers = {"X-Tableau-Auth": self.auth_token}
                requests.post(url, headers=headers)
            except requests.exceptions.RequestException:
                pass
    
    def _get_headers(self):
        """获取请求头"""
        return {"X-Tableau-Auth": self.auth_token}
    
    def add_user(self, username, site_role="Viewer", auth_setting="ServerDefault"):
        """添加用户到站点"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/users"
            headers = self._get_headers()
            headers.update({"Content-Type": "application/json"})
            
            payload = {
                "user": {
                    "name": username,
                    "siteRole": site_role,
                    "authSetting": auth_setting
                }
            }
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            user_id = result["user"]["id"]
            print(f"成功添加用户: {username} (ID: {user_id})")
            return user_id
            
        except requests.exceptions.RequestException as e:
            print(f"添加用户失败: {e}")
            return None
    
    def add_user_to_group(self, user_id, group_id):
        """将用户添加到组"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/groups/{group_id}/users"
            headers = self._get_headers()
            headers.update({"Content-Type": "application/json"})
            
            payload = {"user": {"id": user_id}}
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            print(f"成功将用户(ID: {user_id})添加到组(ID: {group_id})")
            return True
            
        except requests.exceptions.RequestException as e:
            print(f"添加用户到组失败: {e}")
            return False
    
    def create_group(self, group_name):
        """创建组"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/groups"
            headers = self._get_headers()
            headers.update({"Content-Type": "application/json"})
            
            payload = {"group": {"name": group_name}}
            
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            
            result = response.json()
            group_id = result["group"]["id"]
            print(f"成功创建组: {group_name} (ID: {group_id})")
            return group_id
            
        except requests.exceptions.RequestException as e:
            print(f"创建组失败: {e}")
            return None
    
    def list_users(self):
        """列出站点中的所有用户"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/users"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            users = result["users"]["user"]
            
            print(f"站点中共有 {len(users)} 个用户:")
            for user in users:
                print(f"  - {user['name']} (ID: {user['id']}, 角色: {user['siteRole']})")
                
            return users
            
        except requests.exceptions.RequestException as e:
            print(f"获取用户列表失败: {e}")
            return []
    
    def list_groups(self):
        """列出站点中的所有组"""
        try:
            url = f"{self.server_url}/api/{self.api_version}/sites/{self.site_id}/groups"
            headers = self._get_headers()
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            groups = result["groups"]["group"]
            
            print(f"站点中共有 {len(groups)} 个组:")
            for group in groups:
                print(f"  - {group['name']} (ID: {group['id']})")
                
            return groups
            
        except requests.exceptions.RequestException as e:
            print(f"获取组列表失败: {e}")
            return []

def main():
    """主函数 - 演示用户管理操作"""
    print("Tableau Server 用户管理工具")
    print("=" * 50)
    
    # 获取服务器信息
    server_url = input("请输入Tableau Server URL (如: https://tableau.example.com): ")
    username = input("请输入用户名: ")
    password = getpass.getpass("请输入密码: ")
    site_id = input("请输入站点ID (默认为空，按回车跳过): ") or ""
    
    # 创建管理器实例
    manager = TableauServerManager(server_url, username, password, site_id)
    
    # 登录
    if not manager.sign_in():
        print("无法登录，程序退出")
        sys.exit(1)
    
    try:
        # 列出当前用户
        print("\n当前用户列表:")
        manager.list_users()
        
        # 列出当前组
        print("\n当前组列表:")
        manager.list_groups()
        
        # 创建一个新组
        group_name = "DataAnalysts"
        print(f"\n创建新组: {group_name}")
        group_id = manager.create_group(group_name)
        
        if group_id:
            # 添加新用户
            new_username = "newuser@example.com"
            print(f"\n添加新用户: {new_username}")
            user_id = manager.add_user(new_username, site_role="Explorer")
            
            if user_id:
                # 将用户添加到组
                print(f"\n将用户添加到组: {group_name}")
                manager.add_user_to_group(user_id, group_id)
        
        print("\n操作完成!")
        
    finally:
        # 登出
        manager.sign_out()
        print("已登出Tableau Server")

if __name__ == "__main__":
    main()