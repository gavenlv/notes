#!/usr/bin/env python3
"""
Ansible 动态 Inventory 脚本示例
支持从多种数据源动态生成主机清单

用法:
    # 列出所有主机和组
    python dynamic-inventory.py --list
    
    # 获取特定主机信息
    python dynamic-inventory.py --host hostname
    
    # 刷新缓存
    python dynamic-inventory.py --refresh-cache
"""

import json
import argparse
import os
import sys
import time
import requests
from typing import Dict, List, Any

class DynamicInventory:
    def __init__(self):
        self.cache_file = '/tmp/ansible_dynamic_inventory_cache.json'
        self.cache_max_age = 300  # 缓存5分钟
        
        # 数据源配置
        self.data_sources = {
            'database': {
                'enabled': False,
                'connection_string': 'mysql://user:pass@localhost/cmdb'
            },
            'api': {
                'enabled': True,
                'base_url': 'https://api.example.com/v1',
                'auth_token': 'your-api-token'
            },
            'csv': {
                'enabled': True,
                'file_path': './hosts.csv'
            },
            'static': {
                'enabled': True  # 用于演示的静态数据
            }
        }
        
        self.inventory = {
            '_meta': {
                'hostvars': {}
            }
        }

    def run(self):
        """主入口函数"""
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action='store_true', 
                          help='列出所有主机和组')
        parser.add_argument('--host', help='获取特定主机的变量')
        parser.add_argument('--refresh-cache', action='store_true',
                          help='刷新缓存')
        
        args = parser.parse_args()
        
        if args.refresh_cache:
            self.refresh_cache()
            return
            
        if args.list:
            print(json.dumps(self.get_inventory(), indent=2))
        elif args.host:
            print(json.dumps(self.get_host_vars(args.host), indent=2))
        else:
            parser.print_help()

    def get_inventory(self) -> Dict[str, Any]:
        """获取完整的 inventory"""
        # 检查缓存
        if self.is_cache_valid():
            return self.load_cache()
        
        # 生成新的 inventory
        inventory = self.generate_inventory()
        
        # 保存缓存
        self.save_cache(inventory)
        
        return inventory

    def get_host_vars(self, hostname: str) -> Dict[str, Any]:
        """获取特定主机的变量"""
        inventory = self.get_inventory()
        return inventory['_meta']['hostvars'].get(hostname, {})

    def generate_inventory(self) -> Dict[str, Any]:
        """从各数据源生成 inventory"""
        inventory = {
            '_meta': {
                'hostvars': {}
            }
        }
        
        # 从各数据源收集主机信息
        hosts_data = []
        
        if self.data_sources['static']['enabled']:
            hosts_data.extend(self.get_static_hosts())
            
        if self.data_sources['csv']['enabled']:
            hosts_data.extend(self.get_csv_hosts())
            
        if self.data_sources['api']['enabled']:
            hosts_data.extend(self.get_api_hosts())
            
        if self.data_sources['database']['enabled']:
            hosts_data.extend(self.get_database_hosts())
        
        # 构建 inventory 结构
        for host_data in hosts_data:
            hostname = host_data['hostname']
            groups = host_data.get('groups', [])
            hostvars = host_data.get('vars', {})
            
            # 添加主机变量
            inventory['_meta']['hostvars'][hostname] = hostvars
            
            # 添加到组
            for group in groups:
                if group not in inventory:
                    inventory[group] = {'hosts': []}
                
                if hostname not in inventory[group]['hosts']:
                    inventory[group]['hosts'].append(hostname)
        
        # 添加组变量
        self.add_group_vars(inventory)
        
        return inventory

    def get_static_hosts(self) -> List[Dict[str, Any]]:
        """获取静态主机配置 (用于演示)"""
        return [
            {
                'hostname': 'web01.example.com',
                'groups': ['webservers', 'production'],
                'vars': {
                    'ansible_host': '10.1.1.11',
                    'ansible_user': 'ubuntu',
                    'server_role': 'web',
                    'environment': 'prod',
                    'cpu_cores': 4,
                    'memory_gb': 8
                }
            },
            {
                'hostname': 'web02.example.com',
                'groups': ['webservers', 'production'],
                'vars': {
                    'ansible_host': '10.1.1.12',
                    'ansible_user': 'ubuntu',
                    'server_role': 'web',
                    'environment': 'prod',
                    'cpu_cores': 4,
                    'memory_gb': 8
                }
            },
            {
                'hostname': 'db01.example.com',
                'groups': ['databases', 'production'],
                'vars': {
                    'ansible_host': '10.1.2.11',
                    'ansible_user': 'ubuntu',
                    'server_role': 'database',
                    'environment': 'prod',
                    'mysql_server_id': 1,
                    'cpu_cores': 8,
                    'memory_gb': 32
                }
            },
            {
                'hostname': 'dev-web01.example.com',
                'groups': ['webservers', 'development'],
                'vars': {
                    'ansible_host': '192.168.10.11',
                    'ansible_user': 'ubuntu',
                    'server_role': 'web',
                    'environment': 'dev',
                    'cpu_cores': 2,
                    'memory_gb': 4
                }
            }
        ]

    def get_csv_hosts(self) -> List[Dict[str, Any]]:
        """从 CSV 文件获取主机信息"""
        csv_file = self.data_sources['csv']['file_path']
        hosts = []
        
        if not os.path.exists(csv_file):
            return hosts
            
        try:
            import csv
            with open(csv_file, 'r') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # 解析组信息
                    groups = [g.strip() for g in row.get('groups', '').split(',') if g.strip()]
                    
                    # 构建主机变量
                    vars_dict = {}
                    for key, value in row.items():
                        if key not in ['hostname', 'groups']:
                            # 尝试转换数据类型
                            if value.isdigit():
                                vars_dict[key] = int(value)
                            elif value.lower() in ['true', 'false']:
                                vars_dict[key] = value.lower() == 'true'
                            else:
                                vars_dict[key] = value
                    
                    hosts.append({
                        'hostname': row['hostname'],
                        'groups': groups,
                        'vars': vars_dict
                    })
                    
        except Exception as e:
            print(f"Error reading CSV file: {e}", file=sys.stderr)
            
        return hosts

    def get_api_hosts(self) -> List[Dict[str, Any]]:
        """从 API 获取主机信息"""
        hosts = []
        
        try:
            base_url = self.data_sources['api']['base_url']
            token = self.data_sources['api']['auth_token']
            
            headers = {
                'Authorization': f'Bearer {token}',
                'Content-Type': 'application/json'
            }
            
            # 示例 API 调用
            # response = requests.get(f'{base_url}/hosts', headers=headers, timeout=10)
            # if response.status_code == 200:
            #     api_data = response.json()
            #     for host in api_data.get('hosts', []):
            #         hosts.append({
            #             'hostname': host['name'],
            #             'groups': host['groups'],
            #             'vars': host['attributes']
            #         })
            
            # 模拟 API 数据（实际使用时替换为真实 API 调用）
            hosts = [
                {
                    'hostname': 'api-web01.example.com',
                    'groups': ['webservers', 'api-managed'],
                    'vars': {
                        'ansible_host': '10.2.1.11',
                        'ansible_user': 'deploy',
                        'server_role': 'web',
                        'managed_by': 'api'
                    }
                }
            ]
            
        except Exception as e:
            print(f"Error fetching from API: {e}", file=sys.stderr)
            
        return hosts

    def get_database_hosts(self) -> List[Dict[str, Any]]:
        """从数据库获取主机信息"""
        hosts = []
        
        try:
            # 这里是数据库连接示例
            # import mysql.connector
            # 
            # connection = mysql.connector.connect(
            #     host='localhost',
            #     user='cmdb_user',
            #     password='password',
            #     database='cmdb'
            # )
            # 
            # cursor = connection.cursor(dictionary=True)
            # cursor.execute("""
            #     SELECT h.hostname, h.ip_address, h.environment, 
            #            GROUP_CONCAT(g.group_name) as groups
            #     FROM hosts h
            #     LEFT JOIN host_groups hg ON h.id = hg.host_id
            #     LEFT JOIN groups g ON hg.group_id = g.id
            #     WHERE h.active = 1
            #     GROUP BY h.id
            # """)
            # 
            # for row in cursor.fetchall():
            #     groups = [g.strip() for g in row['groups'].split(',') if g.strip()]
            #     hosts.append({
            #         'hostname': row['hostname'],
            #         'groups': groups,
            #         'vars': {
            #             'ansible_host': row['ip_address'],
            #             'environment': row['environment']
            #         }
            #     })
            
            pass  # 数据库查询的占位符
            
        except Exception as e:
            print(f"Error fetching from database: {e}", file=sys.stderr)
            
        return hosts

    def add_group_vars(self, inventory: Dict[str, Any]):
        """添加组变量"""
        group_vars = {
            'webservers': {
                'http_port': 80,
                'https_port': 443,
                'nginx_version': '1.18'
            },
            'databases': {
                'mysql_port': 3306,
                'backup_enabled': True
            },
            'production': {
                'environment': 'prod',
                'monitoring_enabled': True,
                'backup_retention_days': 30
            },
            'development': {
                'environment': 'dev',
                'debug_mode': True,
                'backup_retention_days': 7
            }
        }
        
        for group, vars_dict in group_vars.items():
            if group in inventory:
                if 'vars' not in inventory[group]:
                    inventory[group]['vars'] = {}
                inventory[group]['vars'].update(vars_dict)

    def is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not os.path.exists(self.cache_file):
            return False
            
        cache_age = time.time() - os.path.getmtime(self.cache_file)
        return cache_age < self.cache_max_age

    def load_cache(self) -> Dict[str, Any]:
        """加载缓存"""
        try:
            with open(self.cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading cache: {e}", file=sys.stderr)
            return self.generate_inventory()

    def save_cache(self, inventory: Dict[str, Any]):
        """保存缓存"""
        try:
            os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
            with open(self.cache_file, 'w') as f:
                json.dump(inventory, f, indent=2)
        except Exception as e:
            print(f"Error saving cache: {e}", file=sys.stderr)

    def refresh_cache(self):
        """刷新缓存"""
        if os.path.exists(self.cache_file):
            os.remove(self.cache_file)
        print("Cache refreshed")


# CSV 示例文件内容
CSV_EXAMPLE = """hostname,groups,ansible_host,ansible_user,environment,server_role,cpu_cores,memory_gb
csv-web01.example.com,"webservers,csv-managed",192.168.30.11,ubuntu,staging,web,2,4
csv-web02.example.com,"webservers,csv-managed",192.168.30.12,ubuntu,staging,web,2,4
csv-db01.example.com,"databases,csv-managed",192.168.30.21,ubuntu,staging,database,4,8
"""

def create_example_csv():
    """创建示例 CSV 文件"""
    csv_path = './hosts.csv'
    if not os.path.exists(csv_path):
        with open(csv_path, 'w') as f:
            f.write(CSV_EXAMPLE)
        print(f"Created example CSV file: {csv_path}")


if __name__ == '__main__':
    # 创建示例 CSV 文件
    create_example_csv()
    
    # 运行动态 inventory
    inventory = DynamicInventory()
    inventory.run() 