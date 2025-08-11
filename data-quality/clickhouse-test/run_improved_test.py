#!/usr/bin/env python3
"""
ClickHouse数据质量测试运行脚本
执行完整的测试流程：创建表、插入数据、运行数据质量检查
"""

import os
import sys
import time
import argparse
from clickhouse_driver import Client
from improved_quality_checker import ImprovedDataQualityChecker

class ClickHouseTestRunner:
    def __init__(self, host='localhost', port=9000, user='admin', password='admin', database='data_quality_test'):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.client = None
        
    def connect(self):
        """连接到ClickHouse服务器"""
        try:
            self.client = Client(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                database=self.database,
                settings={'timeout': 60}
            )
            self.client.execute('SELECT 1')
            print("✓ 成功连接到ClickHouse服务器")
            return True
        except Exception as e:
            print(f"✗ 连接到ClickHouse服务器失败: {e}")
            return False
    
    def execute_sql_file(self, file_path):
        """执行SQL文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
            
            # 分割SQL语句
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            
            for i, stmt in enumerate(statements, 1):
                try:
                    self.client.execute(stmt)
                    print(f"  [{i}/{len(statements)}] ✓ 执行SQL语句成功")
                except Exception as e:
                    print(f"  [{i}/{len(statements)}] ✗ 执行SQL语句失败: {e}")
                    print(f"    问题语句: {stmt[:100]}..." if len(stmt) > 100 else f"    问题语句: {stmt}")
                    return False
            
            return True
        except FileNotFoundError:
            print(f"✗ SQL文件未找到: {file_path}")
            return False
        except Exception as e:
            print(f"✗ 执行SQL文件时出错: {e}")
            return False
    
    def setup_test_environment(self, schema_file, data_file):
        """设置测试环境：创建表和插入数据"""
        print("\n设置ClickHouse测试环境...")
        print("=" * 50)
        
        # 执行schema.sql创建表
        print("\n创建数据库和表...")
        if not self.execute_sql_file(schema_file):
            return False
        
        # 执行insert_data.sql插入数据
        print("\n插入测试数据...")
        if not self.execute_sql_file(data_file):
            return False
        
        return True
    
    def run_data_quality_checks(self, config_file, rules_file):
        """运行数据质量检查"""
        print("\n运行数据质量检查...")
        print("=" * 50)
        
        # 创建并运行改进版数据质量检查器
        checker = ImprovedDataQualityChecker(config_file)
        return checker.run_all(rules_file)

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='ClickHouse数据质量测试运行脚本')
    parser.add_argument('--host', default='localhost', help='ClickHouse服务器主机')
    parser.add_argument('--port', type=int, default=9000, help='ClickHouse服务器端口')
    parser.add_argument('--user', default='default', help='ClickHouse用户名')
    parser.add_argument('--password', default='', help='ClickHouse密码')
    parser.add_argument('--database', default='data_quality_test', help='ClickHouse数据库名')
    parser.add_argument('--schema', default='notes/data-quality/clickhouse-test/schema.sql', help='Schema SQL文件路径')
    parser.add_argument('--data', default='notes/data-quality/clickhouse-test/insert_data.sql', help='数据插入SQL文件路径')
    parser.add_argument('--config', default='notes/data-quality/clickhouse-test/config.yml', help='数据质量配置文件路径')
    parser.add_argument('--rules', default='notes/data-quality/clickhouse-test/quality_rules.yml', help='数据质量规则文件路径')
    parser.add_argument('--skip-setup', action='store_true', help='跳过环境设置（不创建表和插入数据）')
    args = parser.parse_args()
    
    # 创建测试运行器
    runner = ClickHouseTestRunner(
        host=args.host,
        port=args.port,
        user=args.user,
        password=args.password,
        database=args.database
    )
    
    # 连接到ClickHouse
    if not runner.connect():
        sys.exit(1)
    
    # 设置测试环境（除非跳过）
    if not args.skip_setup:
        if not runner.setup_test_environment(args.schema, args.data):
            print("✗ 设置测试环境失败")
            sys.exit(1)
    
    # 运行数据质量检查
    success = runner.run_data_quality_checks(args.config, args.rules)
    
    if not success:
        print("✗ 数据质量检查失败")
        sys.exit(1)
    
    print("\n✓ 测试完成")

if __name__ == "__main__":
    main()