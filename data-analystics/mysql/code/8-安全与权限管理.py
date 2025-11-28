#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
MySQL安全与权限管理代码示例
包含用户管理、权限控制、角色管理、数据加密和安全审计等功能的演示

使用方法:
    python 8-安全与权限管理.py [选项]

示例:
    python 8-安全与权限管理.py --demo user_management
    python 8-安全与权限管理.py --demo role_management
    python 8-安全与权限管理.py --demo encryption
    python 8-安全与权限管理.py --demo audit
    python 8-安全与权限管理.py --demo sql_injection
"""

import sys
import os
import pymysql
import hashlib
import secrets
import random
import string
import time
import json
import logging
import argparse
import re
import html
from cryptography.fernet import Fernet
from contextlib import contextmanager
from typing import List, Dict, Tuple, Optional, Union
from datetime import datetime, timedelta

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('mysql_security.log')
    ]
)
logger = logging.getLogger(__name__)

class SecurityException(Exception):
    """安全相关异常类"""
    pass

class MySQLSecurityDemo:
    """MySQL安全与权限管理演示类"""
    
    def __init__(self, host='localhost', user='root', password='', database='mysql'):
        """
        初始化MySQL连接
        
        Args:
            host: MySQL服务器地址
            user: 用户名
            password: 密码
            database: 数据库名
        """
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.connection = None
        
        # 加密相关
        self.encryption_key = Fernet.generate_key()
        self.cipher_suite = Fernet(self.encryption_key)
        
        # 初始化连接
        self._connect()
    
    def _connect(self):
        """建立MySQL连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            logger.info(f"成功连接到MySQL服务器: {self.host}")
        except Exception as e:
            logger.error(f"连接MySQL服务器失败: {e}")
            raise
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("已关闭MySQL连接")
    
    @contextmanager
    def cursor(self):
        """上下文管理器，用于自动处理cursor"""
        cursor = None
        try:
            cursor = self.connection.cursor()
            yield cursor
        except Exception as e:
            if self.connection:
                self.connection.rollback()
            logger.error(f"执行查询时出错: {e}")
            raise
        finally:
            if cursor:
                cursor.close()
    
    def execute_query(self, query: str, params=None, fetch_all=True):
        """
        执行SQL查询
        
        Args:
            query: SQL查询语句
            params: 查询参数
            fetch_all: 是否获取所有结果
            
        Returns:
            查询结果
        """
        try:
            with self.cursor() as cursor:
                cursor.execute(query, params)
                
                if query.strip().upper().startswith(('SELECT', 'SHOW', 'DESCRIBE', 'EXPLAIN')):
                    if fetch_all:
                        return cursor.fetchall()
                    else:
                        return cursor.fetchone()
                else:
                    self.connection.commit()
                    return cursor.rowcount
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            raise
    
    def hash_password(self, password: str, salt: str = None) -> Tuple[str, str]:
        """
        使用SHA-256加盐哈希密码
        
        Args:
            password: 原始密码
            salt: 盐值，如果不提供则生成随机盐值
            
        Returns:
            (哈希后的密码, 盐值)
        """
        if salt is None:
            salt = secrets.token_hex(16)
        
        # 将密码和盐值组合后进行SHA-256哈希
        hashed = hashlib.sha256((password + salt).encode('utf-8')).hexdigest()
        return hashed, salt
    
    def generate_strong_password(self, length=16):
        """
        生成强密码
        
        Args:
            length: 密码长度
            
        Returns:
            生成的密码字符串
        """
        # 确保密码包含大写字母、小写字母、数字和特殊字符
        lower = random.choices(string.ascii_lowercase, k=1)
        upper = random.choices(string.ascii_uppercase, k=1)
        digits = random.choices(string.digits, k=1)
        special = random.choices('!@#$%^&*()_+-=[]{}|;:,.<>?', k=1)
        
        # 剩余字符从所有字符集中随机选择
        all_chars = string.ascii_letters + string.digits + '!@#$%^&*()_+-=[]{}|;:,.<>?'
        remaining = random.choices(all_chars, k=length-4)
        
        # 合并所有字符并打乱顺序
        password_chars = lower + upper + digits + special + remaining
        random.shuffle(password_chars)
        
        return ''.join(password_chars)
    
    def encrypt_data(self, data: str) -> bytes:
        """
        使用Fernet加密数据
        
        Args:
            data: 要加密的字符串
            
        Returns:
            加密后的字节数据
        """
        return self.cipher_suite.encrypt(data.encode('utf-8'))
    
    def decrypt_data(self, encrypted_data: bytes) -> str:
        """
        使用Fernet解密数据
        
        Args:
            encrypted_data: 要解密的字节数据
            
        Returns:
            解密后的字符串
        """
        return self.cipher_suite.decrypt(encrypted_data).decode('utf-8')

class UserManagementDemo(MySQLSecurityDemo):
    """用户管理演示"""
    
    def create_secure_user(self, username: str, hostname: str = '%', password: str = None, 
                          password_expired: bool = False, account_locked: bool = False):
        """
        创建安全用户
        
        Args:
            username: 用户名
            hostname: 主机名
            password: 密码，如果不提供则自动生成
            password_expired: 密码是否立即过期
            account_locked: 账户是否锁定
            
        Returns:
            创建的用户信息
        """
        try:
            # 如果没有提供密码，则生成强密码
            if not password:
                password = self.generate_strong_password()
            
            # 构建创建用户的SQL
            user_sql = f"CREATE USER '{username}'@'{hostname}' IDENTIFIED BY '{password}'"
            
            # 执行创建用户
            self.execute_query(user_sql)
            
            # 设置额外属性
            if password_expired:
                self.execute_query(f"ALTER USER '{username}'@'{hostname}' PASSWORD EXPIRE")
            
            if account_locked:
                self.execute_query(f"ALTER USER '{username}'@'{hostname}' ACCOUNT LOCK")
            
            logger.info(f"成功创建用户: {username}@{hostname}")
            return {
                'username': username,
                'hostname': hostname,
                'password': password,
                'password_expired': password_expired,
                'account_locked': account_locked
            }
        except Exception as e:
            logger.error(f"创建用户失败: {e}")
            raise
    
    def grant_privileges(self, username: str, hostname: str, privileges: List[str], 
                        database: str = '*', table: str = '*', with_grant_option: bool = False):
        """
        授予用户权限
        
        Args:
            username: 用户名
            hostname: 主机名
            privileges: 权限列表
            database: 数据库名
            table: 表名
            with_grant_option: 是否允许转授权限
        """
        try:
            # 构建授权SQL
            priv_str = ', '.join(privileges)
            grant_sql = f"GRANT {priv_str} ON `{database}`.`{table}` TO '{username}'@'{hostname}'"
            
            if with_grant_option:
                grant_sql += " WITH GRANT OPTION"
            
            # 执行授权
            self.execute_query(grant_sql)
            
            logger.info(f"成功授权 {priv_str} ON `{database}`.`{table}` TO {username}@{hostname}")
        except Exception as e:
            logger.error(f"授权失败: {e}")
            raise
    
    def revoke_privileges(self, username: str, hostname: str, privileges: List[str], 
                         database: str = '*', table: str = '*'):
        """
        撤销用户权限
        
        Args:
            username: 用户名
            hostname: 主机名
            privileges: 权限列表
            database: 数据库名
            table: 表名
        """
        try:
            # 构建撤销权限SQL
            priv_str = ', '.join(privileges)
            revoke_sql = f"REVOKE {priv_str} ON `{database}`.`{table}` FROM '{username}'@'{hostname}'"
            
            # 执行撤销权限
            self.execute_query(revoke_sql)
            
            logger.info(f"成功撤销权限 {priv_str} ON `{database}`.`{table}` FROM {username}@{hostname}")
        except Exception as e:
            logger.error(f"撤销权限失败: {e}")
            raise
    
    def list_users(self):
        """
        列出所有用户
        
        Returns:
            用户列表
        """
        try:
            query = "SELECT host, user FROM mysql.user ORDER BY host, user"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"获取用户列表失败: {e}")
            raise
    
    def show_user_grants(self, username: str, hostname: str):
        """
        显示用户权限
        
        Args:
            username: 用户名
            hostname: 主机名
            
        Returns:
            用户权限列表
        """
        try:
            query = f"SHOW GRANTS FOR '{username}'@'{hostname}'"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"获取用户权限失败: {e}")
            raise
    
    def drop_user(self, username: str, hostname: str):
        """
        删除用户
        
        Args:
            username: 用户名
            hostname: 主机名
        """
        try:
            query = f"DROP USER '{username}'@'{hostname}'"
            self.execute_query(query)
            logger.info(f"成功删除用户: {username}@{hostname}")
        except Exception as e:
            logger.error(f"删除用户失败: {e}")
            raise
    
    def change_password(self, username: str, hostname: str, new_password: str = None):
        """
        修改用户密码
        
        Args:
            username: 用户名
            hostname: 主机名
            new_password: 新密码，如果不提供则生成随机密码
            
        Returns:
            新密码
        """
        try:
            # 如果没有提供新密码，则生成强密码
            if not new_password:
                new_password = self.generate_strong_password()
            
            # 执行修改密码
            query = f"ALTER USER '{username}'@'{hostname}' IDENTIFIED BY '{new_password}'"
            self.execute_query(query)
            
            logger.info(f"成功修改用户密码: {username}@{hostname}")
            return new_password
        except Exception as e:
            logger.error(f"修改密码失败: {e}")
            raise
    
    def demo_user_management(self):
        """演示用户管理功能"""
        print("\n===== 用户管理演示 =====")
        
        try:
            # 1. 列出当前用户
            print("\n1. 当前用户列表:")
            users = self.list_users()
            for user in users:
                print(f"  - {user['user']}@{user['host']}")
            
            # 2. 创建安全用户
            print("\n2. 创建安全用户:")
            test_user = 'test_user_' + str(int(time.time()))
            user_info = self.create_secure_user(
                username=test_user,
                hostname='localhost',
                password_expired=True,
                account_locked=True
            )
            print(f"  创建用户: {user_info['username']}@{user_info['hostname']}")
            print(f"  密码: {user_info['password']}")
            print(f"  密码过期: {user_info['password_expired']}")
            print(f"  账户锁定: {user_info['account_locked']}")
            
            # 3. 授予权限
            print("\n3. 授予权限:")
            self.grant_privileges(
                username=test_user,
                hostname='localhost',
                privileges=['SELECT', 'INSERT', 'UPDATE', 'DELETE'],
                database='mysql',
                table='user',
                with_grant_option=False
            )
            print(f"  授予SELECT, INSERT, UPDATE, DELETE权限给 {test_user}@localhost")
            
            # 4. 查看用户权限
            print("\n4. 查看用户权限:")
            grants = self.show_user_grants(test_user, 'localhost')
            for grant in grants:
                print(f"  - {grant[list(grant.keys())[0]]}")
            
            # 5. 修改密码
            print("\n5. 修改密码:")
            new_password = self.change_password(test_user, 'localhost')
            print(f"  新密码: {new_password}")
            
            # 6. 解锁账户
            self.execute_query(f"ALTER USER '{test_user}'@'localhost' ACCOUNT UNLOCK")
            print(f"  解锁账户: {test_user}@localhost")
            
            # 7. 撤销权限
            print("\n7. 撤销权限:")
            self.revoke_privileges(
                username=test_user,
                hostname='localhost',
                privileges=['INSERT', 'UPDATE', 'DELETE'],
                database='mysql',
                table='user'
            )
            print(f"  撤销INSERT, UPDATE, DELETE权限")
            
            # 8. 再次查看用户权限
            print("\n8. 查看修改后的用户权限:")
            grants = self.show_user_grants(test_user, 'localhost')
            for grant in grants:
                print(f"  - {grant[list(grant.keys())[0]]}")
            
            # 9. 删除测试用户
            print("\n9. 删除测试用户:")
            self.drop_user(test_user, 'localhost')
            print(f"  删除用户: {test_user}@localhost")
            
        except Exception as e:
            logger.error(f"用户管理演示失败: {e}")

class RoleManagementDemo(MySQLSecurityDemo):
    """角色管理演示"""
    
    def create_role(self, role_name: str, comment: str = None):
        """
        创建角色
        
        Args:
            role_name: 角色名称
            comment: 角色描述
        """
        try:
            query = f"CREATE ROLE '{role_name}'"
            if comment:
                query += f" COMMENT '{comment}'"
            
            self.execute_query(query)
            logger.info(f"成功创建角色: {role_name}")
        except Exception as e:
            logger.error(f"创建角色失败: {e}")
            raise
    
    def grant_role_privileges(self, role_name: str, privileges: List[str], 
                            database: str = '*', table: str = '*'):
        """
        授予角色权限
        
        Args:
            role_name: 角色名称
            privileges: 权限列表
            database: 数据库名
            table: 表名
        """
        try:
            priv_str = ', '.join(privileges)
            query = f"GRANT {priv_str} ON `{database}`.`{table}` TO '{role_name}'"
            self.execute_query(query)
            logger.info(f"成功授权 {priv_str} 给角色 {role_name}")
        except Exception as e:
            logger.error(f"授权角色失败: {e}")
            raise
    
    def grant_role_to_user(self, username: str, hostname: str, role_names: List[str], 
                          set_default: bool = True):
        """
        将角色授予用户
        
        Args:
            username: 用户名
            hostname: 主机名
            role_names: 角色名称列表
            set_default: 是否设置为默认角色
        """
        try:
            roles_str = ", ".join([f"'{role}'" for role in role_names])
            query = f"GRANT {roles_str} TO '{username}'@'{hostname}'"
            self.execute_query(query)
            
            if set_default:
                self.execute_query(f"SET DEFAULT ROLE ALL TO '{username}'@'{hostname}'")
            
            logger.info(f"成功授予角色 {roles_str} 给用户 {username}@{hostname}")
        except Exception as e:
            logger.error(f"授予角色失败: {e}")
            raise
    
    def revoke_role_from_user(self, username: str, hostname: str, role_names: List[str]):
        """
        从用户撤销角色
        
        Args:
            username: 用户名
            hostname: 主机名
            role_names: 角色名称列表
        """
        try:
            roles_str = ", ".join([f"'{role}'" for role in role_names])
            query = f"REVOKE {roles_str} FROM '{username}'@'{hostname}'"
            self.execute_query(query)
            logger.info(f"成功撤销角色 {roles_str} 从用户 {username}@{hostname}")
        except Exception as e:
            logger.error(f"撤销角色失败: {e}")
            raise
    
    def list_roles(self):
        """
        列出所有角色
        
        Returns:
            角色列表
        """
        try:
            query = "SELECT * FROM mysql.role"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"获取角色列表失败: {e}")
            raise
    
    def show_role_grants(self, role_name: str):
        """
        显示角色权限
        
        Args:
            role_name: 角色名称
            
        Returns:
            角色权限列表
        """
        try:
            query = f"SHOW GRANTS FOR '{role_name}'"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"获取角色权限失败: {e}")
            raise
    
    def drop_role(self, role_name: str):
        """
        删除角色
        
        Args:
            role_name: 角色名称
        """
        try:
            query = f"DROP ROLE IF EXISTS '{role_name}'"
            self.execute_query(query)
            logger.info(f"成功删除角色: {role_name}")
        except Exception as e:
            logger.error(f"删除角色失败: {e}")
            raise
    
    def demo_role_management(self):
        """演示角色管理功能"""
        print("\n===== 角色管理演示 =====")
        
        try:
            # 1. 列出当前角色
            print("\n1. 当前角色列表:")
            roles = self.list_roles()
            if roles:
                for role in roles:
                    print(f"  - {role['role']}")
            else:
                print("  - 没有找到角色")
            
            # 2. 创建角色
            print("\n2. 创建角色:")
            timestamp = str(int(time.time()))
            roles_to_create = {
                'app_reader': f'应用读者角色 {timestamp}',
                'app_writer': f'应用写作者角色 {timestamp}',
                'app_admin': f'应用管理员角色 {timestamp}'
            }
            
            for role_name, comment in roles_to_create.items():
                self.create_role(role_name, comment)
                print(f"  创建角色: {role_name} - {comment}")
            
            # 3. 授予角色权限
            print("\n3. 授予角色权限:")
            
            # 授予app_reader角色读取权限
            self.grant_role_privileges('app_reader', ['SELECT'])
            print("  授予app_reader角色SELECT权限")
            
            # 授予app_writer角色读写权限
            self.grant_role_privileges('app_writer', ['SELECT', 'INSERT', 'UPDATE', 'DELETE'])
            print("  授予app_writer角色SELECT, INSERT, UPDATE, DELETE权限")
            
            # 授予app_admin角色所有权限
            self.grant_role_privileges('app_admin', ['ALL PRIVILEGES'])
            print("  授予app_admin角色ALL PRIVILEGES权限")
            
            # 4. 查看角色权限
            print("\n4. 查看角色权限:")
            for role_name in roles_to_create.keys():
                print(f"\n  角色 {role_name} 的权限:")
                grants = self.show_role_grants(role_name)
                for grant in grants:
                    print(f"    - {grant[list(grant.keys())[0]]}")
            
            # 5. 创建测试用户
            print("\n5. 创建测试用户:")
            timestamp = str(int(time.time()))
            test_users = {
                'test_reader': 'test_reader_' + timestamp,
                'test_writer': 'test_writer_' + timestamp,
                'test_admin': 'test_admin_' + timestamp
            }
            
            for user_type, username in test_users.items():
                user_info = UserManagementDemo(
                    host=self.host, 
                    user=self.user, 
                    password=self.password
                ).create_secure_user(username)
                print(f"  创建用户: {username}")
            
            # 6. 将角色授予用户
            print("\n6. 将角色授予用户:")
            self.grant_role_to_user(test_users['test_reader'], 'localhost', ['app_reader'])
            print(f"  授予app_reader角色给 {test_users['test_reader']}")
            
            self.grant_role_to_user(test_users['test_writer'], 'localhost', ['app_writer'])
            print(f"  授予app_writer角色给 {test_users['test_writer']}")
            
            self.grant_role_to_user(test_users['test_admin'], 'localhost', ['app_admin'])
            print(f"  授予app_admin角色给 {test_users['test_admin']}")
            
            # 7. 查看用户权限
            print("\n7. 查看用户权限:")
            user_manager = UserManagementDemo(
                host=self.host, 
                user=self.user, 
                password=self.password
            )
            
            for user_type, username in test_users.items():
                print(f"\n  用户 {username} 的权限:")
                grants = user_manager.show_user_grants(username, 'localhost')
                for grant in grants:
                    print(f"    - {grant[list(grant.keys())[0]]}")
            
            # 8. 测试角色
            print("\n8. 测试角色功能:")
            
            # 创建测试数据库和表
            test_db = f'test_db_{timestamp}'
            self.execute_query(f"CREATE DATABASE IF NOT EXISTS `{test_db}`")
            self.execute_query(f"USE `{test_db}`")
            self.execute_query(f"CREATE TABLE IF NOT EXISTS test_table (id INT, name VARCHAR(50))")
            self.execute_query(f"INSERT INTO test_table (id, name) VALUES (1, 'Test Data')")
            
            print(f"  创建测试数据库: {test_db}")
            
            # 授权角色访问测试数据库
            for role_name in roles_to_create.keys():
                self.grant_role_privileges(role_name, ['SELECT'], database=test_db)
                print(f"  授予{role_name}角色对{test_db}数据库的SELECT权限")
            
            # 9. 删除测试数据
            print("\n9. 清理测试数据:")
            for username in test_users.values():
                user_manager.drop_user(username, 'localhost')
                print(f"  删除用户: {username}")
            
            for role_name in roles_to_create.keys():
                self.drop_role(role_name)
                print(f"  删除角色: {role_name}")
            
            self.execute_query(f"DROP DATABASE IF EXISTS `{test_db}`")
            print(f"  删除测试数据库: {test_db}")
            
        except Exception as e:
            logger.error(f"角色管理演示失败: {e}")

class DataEncryptionDemo(MySQLSecurityDemo):
    """数据加密演示"""
    
    def create_encrypted_table(self, db_name: str, table_name: str):
        """
        创建加密表
        
        Args:
            db_name: 数据库名
            table_name: 表名
        """
        try:
            # 确保数据库存在
            self.execute_query(f"CREATE DATABASE IF NOT EXISTS `{db_name}`")
            self.execute_query(f"USE `{db_name}`")
            
            # 创建加密表
            create_table_sql = f"""
            CREATE TABLE IF NOT EXISTS `{table_name}` (
                id INT PRIMARY KEY AUTO_INCREMENT,
                name VARCHAR(100) NOT NULL,
                email VARBINARY(255),
                phone VARBINARY(50),
                credit_card VARBINARY(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB ENCRYPTION='Y'
            """
            
            self.execute_query(create_table_sql)
            logger.info(f"成功创建加密表: {db_name}.{table_name}")
        except Exception as e:
            logger.error(f"创建加密表失败: {e}")
            raise
    
    def insert_encrypted_data(self, db_name: str, table_name: str, name: str, 
                             email: str, phone: str, credit_card: str):
        """
        插入加密数据
        
        Args:
            db_name: 数据库名
            table_name: 表名
            name: 姓名（明文）
            email: 电子邮件（将加密）
            phone: 电话号码（将加密）
            credit_card: 信用卡号（将加密）
        """
        try:
            # 加密敏感数据
            encrypted_email = self.encrypt_data(email)
            encrypted_phone = self.encrypt_data(phone)
            encrypted_credit_card = self.encrypt_data(credit_card)
            
            # 插入数据
            self.execute_query(f"USE `{db_name}`")
            insert_sql = f"""
            INSERT INTO `{table_name}` (name, email, phone, credit_card)
            VALUES (%s, %s, %s, %s)
            """
            
            self.execute_query(
                insert_sql, 
                (name, encrypted_email, encrypted_phone, encrypted_credit_card)
            )
            
            logger.info(f"成功插入加密数据到 {db_name}.{table_name}")
        except Exception as e:
            logger.error(f"插入加密数据失败: {e}")
            raise
    
    def query_decrypted_data(self, db_name: str, table_name: str, id_val: int = None):
        """
        查询并解密数据
        
        Args:
            db_name: 数据库名
            table_name: 表名
            id_val: 要查询的ID，如果不提供则查询所有
            
        Returns:
            解密后的数据
        """
        try:
            self.execute_query(f"USE `{db_name}`")
            
            if id_val is not None:
                query_sql = f"SELECT id, name, email, phone, credit_card FROM `{table_name}` WHERE id = %s"
                result = self.execute_query(query_sql, (id_val,), fetch_all=False)
            else:
                query_sql = f"SELECT id, name, email, phone, credit_card FROM `{table_name}`"
                result = self.execute_query(query_sql, fetch_all=True)
            
            # 解密数据
            if isinstance(result, list):
                for row in result:
                    row['email'] = self.decrypt_data(row['email'])
                    row['phone'] = self.decrypt_data(row['phone'])
                    row['credit_card'] = self.decrypt_data(row['credit_card'])
            else:
                result['email'] = self.decrypt_data(result['email'])
                result['phone'] = self.decrypt_data(result['phone'])
                result['credit_card'] = self.decrypt_data(result['credit_card'])
            
            return result
        except Exception as e:
            logger.error(f"查询解密数据失败: {e}")
            raise
    
    def demo_encryption(self):
        """演示数据加密功能"""
        print("\n===== 数据加密演示 =====")
        
        try:
            # 1. 检查是否支持表空间加密
            print("\n1. 检查表空间加密支持:")
            encryption_support = self.execute_query("SHOW VARIABLES LIKE 'have_ssl'")
            print(f"  SSL支持: {encryption_support[0]['Value'] if encryption_support else 'Unknown'}")
            
            try:
                encryption_check = self.execute_query("SHOW VARIABLES LIKE 'innodb_encrypt_tables'")
                print(f"  表加密状态: {encryption_check[0]['Value'] if encryption_check else 'Unknown'}")
            except:
                print("  表加密状态: 不支持或未配置")
            
            # 2. 创建加密表
            print("\n2. 创建加密表:")
            timestamp = str(int(time.time()))
            test_db = f'test_encryption_{timestamp}'
            test_table = 'encrypted_data'
            
            self.create_encrypted_table(test_db, test_table)
            print(f"  创建加密表: {test_db}.{test_table}")
            
            # 3. 插入测试数据
            print("\n3. 插入加密测试数据:")
            test_data = [
                {
                    'name': '张三',
                    'email': 'zhangsan@example.com',
                    'phone': '13800138000',
                    'credit_card': '4111111111111111'
                },
                {
                    'name': '李四',
                    'email': 'lisi@example.com',
                    'phone': '13900139000',
                    'credit_card': '5123456789012345'
                },
                {
                    'name': '王五',
                    'email': 'wangwu@example.com',
                    'phone': '13700137000',
                    'credit_card': '378282246310005'
                }
            ]
            
            for data in test_data:
                self.insert_encrypted_data(
                    test_db, test_table, 
                    data['name'], data['email'], data['phone'], data['credit_card']
                )
                print(f"  插入数据: {data['name']}")
            
            # 4. 查询原始加密数据（显示为二进制）
            print("\n4. 查询原始加密数据:")
            self.execute_query(f"USE `{test_db}`")
            encrypted_data = self.execute_query(f"SELECT id, name, email, phone, credit_card FROM `{test_table}`")
            
            for row in encrypted_data:
                print(f"  ID: {row['id']}, 姓名: {row['name']}")
                print(f"    电子邮件(加密): {row['email']}")
                print(f"    电话(加密): {row['phone']}")
                print(f"    信用卡(加密): {row['credit_card']}")
            
            # 5. 查询解密后的数据
            print("\n5. 查询解密后的数据:")
            decrypted_data = self.query_decrypted_data(test_db, test_table)
            
            for row in decrypted_data:
                print(f"  ID: {row['id']}, 姓名: {row['name']}")
                print(f"    电子邮件: {row['email']}")
                print(f"    电话: {row['phone']}")
                # 信用卡号只显示后4位
                masked_card = '*' * (len(row['credit_card']) - 4) + row['credit_card'][-4:]
                print(f"    信用卡: {masked_card}")
            
            # 6. 演示哈希密码
            print("\n6. 演示密码哈希:")
            passwords = ['password123', 'MySecurePassword!', 'admin123']
            
            for pwd in passwords:
                hashed, salt = self.hash_password(pwd)
                print(f"  原始密码: {pwd}")
                print(f"    盐值: {salt}")
                print(f"    哈希值: {hashed}")
                print(f"    验证结果: {self.hash_password(pwd, salt)[0] == hashed}")
                print()
            
            # 7. 清理测试数据
            print("\n7. 清理测试数据:")
            self.execute_query(f"DROP DATABASE IF EXISTS `{test_db}`")
            print(f"  删除测试数据库: {test_db}")
            
        except Exception as e:
            logger.error(f"数据加密演示失败: {e}")

class AuditDemo(MySQLSecurityDemo):
    """审计演示"""
    
    def enable_audit_log(self):
        """启用审计日志"""
        try:
            # 检查是否已安装审计插件
            check_query = "SELECT * FROM mysql.component WHERE component_urn LIKE '%audit_log%'"
            result = self.execute_query(check_query)
            
            if not result:
                # 安装审计插件
                self.execute_query("INSTALL COMPONENT 'file://component_audit_log'")
                logger.info("已安装审计日志插件")
            
            # 配置审计日志
            self.execute_query("SET GLOBAL audit_log_format = 'JSON'")
            self.execute_query("SET GLOBAL audit_log_policy = 'ALL'")
            
            logger.info("已启用审计日志")
        except Exception as e:
            logger.error(f"启用审计日志失败: {e}")
            raise
    
    def enable_general_log(self):
        """启用通用日志"""
        try:
            self.execute_query("SET GLOBAL general_log = ON")
            self.execute_query("SET GLOBAL log_output = 'TABLE'")
            logger.info("已启用通用日志")
        except Exception as e:
            logger.error(f"启用通用日志失败: {e}")
            raise
    
    def enable_slow_query_log(self):
        """启用慢查询日志"""
        try:
            self.execute_query("SET GLOBAL slow_query_log = ON")
            self.execute_query("SET GLOBAL log_output = 'TABLE'")
            self.execute_query("SET GLOBAL long_query_time = 1")
            logger.info("已启用慢查询日志")
        except Exception as e:
            logger.error(f"启用慢查询日志失败: {e}")
            raise
    
    def query_audit_log(self, limit=10):
        """
        查询审计日志
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            审计日志记录
        """
        try:
            # 这里简化处理，实际应该从审计日志文件读取
            # 由于审计日志通常存储在文件中，这里模拟查询结果
            audit_records = [
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'connection_id': 1,
                    'user': 'root@localhost',
                    'operation': 'CONNECT',
                    'database': 'mysql',
                    'query': None,
                    'status': 0
                },
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'connection_id': 1,
                    'user': 'root@localhost',
                    'operation': 'QUERY',
                    'database': 'mysql',
                    'query': 'SHOW DATABASES',
                    'status': 0
                },
                {
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'connection_id': 1,
                    'user': 'root@localhost',
                    'operation': 'QUERY',
                    'database': 'mysql',
                    'query': 'SELECT * FROM user',
                    'status': 0
                }
            ]
            
            return audit_records[:limit]
        except Exception as e:
            logger.error(f"查询审计日志失败: {e}")
            raise
    
    def query_general_log(self, limit=10):
        """
        查询通用日志
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            通用日志记录
        """
        try:
            query = f"SELECT event_time, user_host, thread_id, server_id, command_type, argument FROM mysql.general_log ORDER BY event_time DESC LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"查询通用日志失败: {e}")
            raise
    
    def query_slow_query_log(self, limit=10):
        """
        查询慢查询日志
        
        Args:
            limit: 返回记录数限制
            
        Returns:
            慢查询日志记录
        """
        try:
            query = f"SELECT start_time, user_host, query_time, lock_time, rows_sent, rows_examined, db, sql_text FROM mysql.slow_log ORDER BY start_time DESC LIMIT {limit}"
            return self.execute_query(query)
        except Exception as e:
            logger.error(f"查询慢查询日志失败: {e}")
            raise
    
    def generate_test_queries(self):
        """生成测试查询用于演示审计日志"""
        try:
            # 执行一些测试查询
            self.execute_query("SELECT VERSION()")
            self.execute_query("SHOW DATABASES")
            self.execute_query("SHOW TABLES FROM mysql")
            self.execute_query("SELECT COUNT(*) FROM mysql.user")
            
            # 执行一些慢查询
            self.execute_query("SELECT SLEEP(2)")
            
            logger.info("已生成测试查询")
        except Exception as e:
            logger.error(f"生成测试查询失败: {e}")
            raise
    
    def demo_audit(self):
        """演示审计功能"""
        print("\n===== 审计功能演示 =====")
        
        try:
            # 1. 查看当前日志状态
            print("\n1. 查看当前日志状态:")
            
            try:
                general_log_status = self.execute_query("SHOW VARIABLES LIKE 'general_log'")
                print(f"  通用日志状态: {general_log_status[0]['Value']}")
            except:
                print("  通用日志状态: 查询失败")
            
            try:
                slow_query_log_status = self.execute_query("SHOW VARIABLES LIKE 'slow_query_log'")
                print(f"  慢查询日志状态: {slow_query_log_status[0]['Value']}")
            except:
                print("  慢查询日志状态: 查询失败")
            
            # 2. 启用日志记录
            print("\n2. 启用日志记录:")
            self.enable_general_log()
            print("  已启用通用日志")
            
            self.enable_slow_query_log()
            print("  已启用慢查询日志")
            
            try:
                self.enable_audit_log()
                print("  已启用审计日志")
            except Exception as e:
                print(f"  审计日志启用失败（可能是版本不支持）: {e}")
            
            # 3. 生成测试查询
            print("\n3. 生成测试查询:")
            self.generate_test_queries()
            print("  已生成测试查询，等待日志记录...")
            
            # 等待一下确保日志记录完成
            time.sleep(1)
            
            # 4. 查询通用日志
            print("\n4. 查询通用日志:")
            general_logs = self.query_general_log(5)
            for log in general_logs:
                print(f"  时间: {log['event_time']}")
                print(f"    用户: {log['user_host']}")
                print(f"    命令类型: {log['command_type']}")
                if log['command_type'] == 'Query':
                    # 截断长查询以便显示
                    query = log['argument']
                    if len(query) > 50:
                        query = query[:47] + "..."
                    print(f"    查询: {query}")
                print()
            
            # 5. 查询慢查询日志
            print("\n5. 查询慢查询日志:")
            try:
                slow_logs = self.query_slow_query_log(3)
                if slow_logs:
                    for log in slow_logs:
                        print(f"  开始时间: {log['start_time']}")
                        print(f"    用户: {log['user_host']}")
                        print(f"    查询时间: {log['query_time']}")
                        print(f"    数据库: {log['db']}")
                        # 截断长查询以便显示
                        query = log['sql_text']
                        if len(query) > 50:
                            query = query[:47] + "..."
                        print(f"    查询: {query}")
                        print()
                else:
                    print("  没有慢查询记录")
            except Exception as e:
                print(f"  查询慢查询日志失败: {e}")
            
            # 6. 查询审计日志
            print("\n6. 查询审计日志:")
            try:
                audit_logs = self.query_audit_log(5)
                for log in audit_logs:
                    print(f"  时间: {log['timestamp']}")
                    print(f"    连接ID: {log['connection_id']}")
                    print(f"    用户: {log['user']}")
                    print(f"    操作: {log['operation']}")
                    print(f"    数据库: {log['database']}")
                    if log['query']:
                        # 截断长查询以便显示
                        query = log['query']
                        if len(query) > 50:
                            query = query[:47] + "..."
                        print(f"    查询: {query}")
                    print()
            except Exception as e:
                print(f"  查询审计日志失败: {e}")
            
            # 7. 清理：关闭日志记录
            print("\n7. 关闭日志记录:")
            self.execute_query("SET GLOBAL general_log = OFF")
            self.execute_query("SET GLOBAL slow_query_log = OFF")
            print("  已关闭通用日志和慢查询日志")
            
        except Exception as e:
            logger.error(f"审计功能演示失败: {e}")

class SQLInjectionDemo:
    """SQL注入防护演示"""
    
    def __init__(self, host='localhost', user='root', password=''):
        """
        初始化SQL注入演示
        
        Args:
            host: MySQL服务器地址
            user: 用户名
            password: 密码
        """
        self.host = host
        self.user = user
        self.password = password
        self.connection = None
        
        # 连接到MySQL
        self._connect()
        
        # 创建测试数据库和表
        self._setup_test_environment()
    
    def _connect(self):
        """建立MySQL连接"""
        try:
            self.connection = pymysql.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                charset='utf8mb4',
                cursorclass=pymysql.cursors.DictCursor,
                autocommit=True
            )
            logger.info(f"成功连接到MySQL服务器: {self.host}")
        except Exception as e:
            logger.error(f"连接MySQL服务器失败: {e}")
            raise
    
    def _setup_test_environment(self):
        """设置测试环境"""
        try:
            cursor = self.connection.cursor()
            
            # 创建测试数据库
            cursor.execute("DROP DATABASE IF EXISTS sql_injection_demo")
            cursor.execute("CREATE DATABASE sql_injection_demo")
            cursor.execute("USE sql_injection_demo")
            
            # 创建测试表
            cursor.execute("""
                CREATE TABLE users (
                    id INT PRIMARY KEY AUTO_INCREMENT,
                    username VARCHAR(50) NOT NULL,
                    password VARCHAR(50) NOT NULL,
                    email VARCHAR(100),
                    role VARCHAR(20) DEFAULT 'user'
                )
            """)
            
            # 插入测试数据
            test_users = [
                ('admin', 'admin123', 'admin@example.com', 'admin'),
                ('user1', 'password1', 'user1@example.com', 'user'),
                ('user2', 'password2', 'user2@example.com', 'user')
            ]
            
            for user in test_users:
                cursor.execute(
                    "INSERT INTO users (username, password, email, role) VALUES (%s, %s, %s, %s)",
                    user
                )
            
            cursor.close()
            logger.info("测试环境设置完成")
        except Exception as e:
            logger.error(f"设置测试环境失败: {e}")
            raise
    
    def vulnerable_query(self, username, password):
        """
        易受SQL注入攻击的查询（仅用于演示）
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            查询结果
        """
        try:
            cursor = self.connection.cursor()
            # 危险：直接拼接字符串
            query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
            
            print(f"[危险查询] {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            
            return result
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            return []
    
    def secure_query(self, username, password):
        """
        安全的查询（使用预处理语句）
        
        Args:
            username: 用户名
            password: 密码
            
        Returns:
            查询结果
        """
        try:
            cursor = self.connection.cursor()
            # 安全：使用预处理语句
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            
            print(f"[安全查询] {query} (参数: {username}, {password})")
            cursor.execute(query, (username, password))
            result = cursor.fetchall()
            cursor.close()
            
            return result
        except Exception as e:
            logger.error(f"执行查询失败: {e}")
            return []
    
    def vulnerable_search(self, search_term):
        """
        易受SQL注入攻击的搜索（仅用于演示）
        
        Args:
            search_term: 搜索关键词
            
        Returns:
            查询结果
        """
        try:
            cursor = self.connection.cursor()
            # 危险：直接拼接字符串
            query = f"SELECT * FROM users WHERE username LIKE '%{search_term}%'"
            
            print(f"[危险搜索] {query}")
            cursor.execute(query)
            result = cursor.fetchall()
            cursor.close()
            
            return result
        except Exception as e:
            logger.error(f"执行搜索失败: {e}")
            return []
    
    def secure_search(self, search_term):
        """
        安全的搜索（使用预处理语句）
        
        Args:
            search_term: 搜索关键词
            
        Returns:
            查询结果
        """
        try:
            cursor = self.connection.cursor()
            # 安全：使用预处理语句
            query = "SELECT * FROM users WHERE username LIKE %s"
            
            print(f"[安全搜索] {query} (参数: %{search_term}%)")
            cursor.execute(query, (f"%{search_term}%",))
            result = cursor.fetchall()
            cursor.close()
            
            return result
        except Exception as e:
            logger.error(f"执行搜索失败: {e}")
            return []
    
    def validate_input(self, input_string, pattern=None):
        """
        验证输入
        
        Args:
            input_string: 输入字符串
            pattern: 验证模式，如果不提供则使用默认字母数字模式
            
        Returns:
            验证是否通过
        """
        if pattern is None:
            pattern = r'^[a-zA-Z0-9_]{3,20}$'
        
        return re.match(pattern, input_string) is not None
    
    def sanitize_input(self, input_string):
        """
        转义输入
        
        Args:
            input_string: 输入字符串
            
        Returns:
            转义后的字符串
        """
        # 转义HTML特殊字符
        escaped = html.escape(input_string)
        # 替换单引号
        escaped = escaped.replace("'", "''")
        
        return escaped
    
    def demo_sql_injection(self):
        """演示SQL注入防护"""
        print("\n===== SQL注入防护演示 =====")
        
        try:
            # 1. 正常登录测试
            print("\n1. 正常登录测试:")
            username = "admin"
            password = "admin123"
            
            print(f"尝试登录: 用户名={username}, 密码={password}")
            
            # 安全登录
            result = self.secure_query(username, password)
            if result:
                print(f"  登录成功: {result[0]['username']} ({result[0]['role']})")
            else:
                print("  登录失败")
            
            # 2. SQL注入攻击测试
            print("\n2. SQL注入攻击测试:")
            malicious_username = "admin' --"
            malicious_password = "任何密码"
            
            print(f"恶意登录尝试: 用户名={malicious_username}, 密码={malicious_password}")
            
            # 使用危险方法进行SQL注入
            result = self.vulnerable_query(malicious_username, malicious_password)
            if result:
                print(f"  [危险方法] 登录成功: {result[0]['username']} ({result[0]['role']})")
                print("  ⚠️  这证明存在SQL注入漏洞!")
            else:
                print("  [危险方法] 登录失败")
            
            # 使用安全方法防止SQL注入
            result = self.secure_query(malicious_username, malicious_password)
            if result:
                print(f"  [安全方法] 登录成功: {result[0]['username']} ({result[0]['role']})")
            else:
                print("  [安全方法] 登录失败")
                print("  ✅ 预处理语句成功防止了SQL注入!")
            
            # 3. 更复杂的SQL注入攻击
            print("\n3. 更复杂的SQL注入攻击:")
            malicious_username = "admin' OR '1'='1"
            malicious_password = "任何密码"
            
            print(f"恶意登录尝试: 用户名={malicious_username}, 密码={malicious_password}")
            
            # 使用危险方法进行SQL注入
            result = self.vulnerable_query(malicious_username, malicious_password)
            if result:
                print(f"  [危险方法] 登录成功: {result[0]['username']} ({result[0]['role']})")
                print("  ⚠️  更复杂的SQL注入也成功了!")
            else:
                print("  [危险方法] 登录失败")
            
            # 使用安全方法防止SQL注入
            result = self.secure_query(malicious_username, malicious_password)
            if result:
                print(f"  [安全方法] 登录成功: {result[0]['username']} ({result[0]['role']})")
            else:
                print("  [安全方法] 登录失败")
                print("  ✅ 预处理语句成功防止了复杂的SQL注入!")
            
            # 4. 搜索功能SQL注入测试
            print("\n4. 搜索功能SQL注入测试:")
            normal_search = "user"
            malicious_search = "user'; DROP TABLE users; --"
            
            print(f"正常搜索: {normal_search}")
            result = self.secure_search(normal_search)
            if result:
                print(f"  搜索结果: {', '.join([user['username'] for user in result])}")
            
            print(f"\n恶意搜索: {malicious_search}")
            print("  尝试删除users表的SQL注入...")
            
            # 使用危险方法进行SQL注入
            result = self.vulnerable_search(malicious_search)
            if result:
                print(f"  [危险方法] 搜索结果: {', '.join([user['username'] for user in result])}")
                print("  ⚠️  表可能已被删除，如果还有结果说明注入失败")
            else:
                print("  [危险方法] 搜索失败")
            
            # 使用安全方法防止SQL注入
            result = self.secure_search(malicious_search)
            if result:
                print(f"  [安全方法] 搜索结果: {', '.join([user['username'] for user in result])}")
            else:
                print("  [安全方法] 搜索失败")
                print("  ✅ 预处理语句成功防止了搜索功能的SQL注入!")
            
            # 5. 验证表是否仍然存在
            print("\n5. 验证表是否仍然存在:")
            try:
                cursor = self.connection.cursor()
                cursor.execute("SELECT COUNT(*) as count FROM users")
                count = cursor.fetchone()['count']
                print(f"  users表中还有 {count} 条记录")
                cursor.close()
                
                if count == 3:
                    print("  ✅ 表完整，恶意SQL注入没有成功!")
                else:
                    print("  ⚠️  表记录数不正常，可能已被恶意修改!")
            except Exception as e:
                print(f"  ⚠️  查询表失败，表可能已被删除: {e}")
            
            # 6. 输入验证演示
            print("\n6. 输入验证演示:")
            inputs = [
                "admin",           # 有效输入
                "user_123",        # 有效输入
                "admin' --",       # 无效输入（包含特殊字符）
                "a",               # 无效输入（太短）
                "a_very_long_username_that_exceeds_the_limit",  # 无效输入（太长）
            ]
            
            for input_val in inputs:
                is_valid = self.validate_input(input_val)
                sanitized = self.sanitize_input(input_val)
                
                print(f"  输入: {input_val}")
                print(f"    验证结果: {'有效' if is_valid else '无效'}")
                print(f"    转义后: {sanitized}")
                print()
            
            # 7. 最佳实践总结
            print("\n7. SQL注入防护最佳实践总结:")
            print("  ✅ 始终使用预处理语句")
            print("  ✅ 执行严格的输入验证")
            print("  ✅ 应用最小权限原则")
            print("  ✅ 使用存储过程封装数据库逻辑")
            print("  ✅ 实施Web应用防火墙")
            print("  ✅ 定期进行安全审计")
            print("  ✅ 使用ORM框架（通常内置防护机制）")
            print("  ✅ 避免直接拼接SQL字符串")
            print("  ✅ 不要在错误信息中暴露数据库细节")
            
            # 8. 清理测试环境
            print("\n8. 清理测试环境:")
            cursor = self.connection.cursor()
            cursor.execute("DROP DATABASE IF EXISTS sql_injection_demo")
            cursor.close()
            print("  已删除测试数据库")
            
        except Exception as e:
            logger.error(f"SQL注入防护演示失败: {e}")
    
    def close(self):
        """关闭数据库连接"""
        if self.connection:
            self.connection.close()
            self.connection = None
            logger.info("已关闭MySQL连接")

def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='MySQL安全与权限管理演示')
    parser.add_argument('--host', default='localhost', help='MySQL服务器地址')
    parser.add_argument('--user', default='root', help='MySQL用户名')
    parser.add_argument('--password', default='', help='MySQL密码')
    parser.add_argument('--demo', choices=['user_management', 'role_management', 'encryption', 'audit', 'sql_injection', 'all'], 
                        default='all', help='选择要运行的演示')
    
    args = parser.parse_args()
    
    try:
        # 创建连接参数
        conn_params = {
            'host': args.host,
            'user': args.user,
            'password': args.password
        }
        
        if args.demo == 'user_management' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("用户管理演示")
            print("=" * 50)
            demo = UserManagementDemo(**conn_params)
            demo.demo_user_management()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'role_management' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("角色管理演示")
            print("=" * 50)
            demo = RoleManagementDemo(**conn_params)
            demo.demo_role_management()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'encryption' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("数据加密演示")
            print("=" * 50)
            demo = DataEncryptionDemo(**conn_params)
            demo.demo_encryption()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'audit' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("审计功能演示")
            print("=" * 50)
            demo = AuditDemo(**conn_params)
            demo.demo_audit()
            demo.close()
            
            if args.demo != 'all':
                return
        
        if args.demo == 'sql_injection' or args.demo == 'all':
            print("\n" + "=" * 50)
            print("SQL注入防护演示")
            print("=" * 50)
            demo = SQLInjectionDemo(**conn_params)
            demo.demo_sql_injection()
            demo.close()
        
        print("\n" + "=" * 50)
        print("所有演示完成")
        print("=" * 50)
        
    except Exception as e:
        logger.error(f"运行演示失败: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()