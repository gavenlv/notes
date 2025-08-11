#!/usr/bin/env python3
"""
完整的ClickHouse测试环境运行脚本
执行DDL创建表、插入测试数据、运行数据质量检查并生成报告
"""

import os
import sys
import yaml
import json
import time
from datetime import datetime
from clickhouse_driver import Client

# 配置信息
CONFIG = {
    'clickhouse': {
        'host': 'localhost',
        'port': 9000,
        'database': 'data_quality_test',
        'user': 'admin',
        'password': 'admin',
        'secure': False,
        'timeout': 30
    },
    'files': {
        'schema': 'clickhouse-test/schema.sql',
        'data': 'clickhouse-test/insert_data.sql',
        'rules': 'clickhouse-test/quality_rules.yml'
    },
    'report': {
        'output_dir': 'reports',
        'format': ['json', 'txt']
    }
}

class ClickHouseTestRunner:
    def __init__(self, config):
        self.config = config
        self.client = None
        self.results = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
    def connect(self):
        """连接到ClickHouse服务器"""
        try:
            ch_config = self.config['clickhouse']
            self.client = Client(
                host=ch_config['host'],
                port=ch_config['port'],
                database=ch_config['database'],
                user=ch_config['user'],
                password=ch_config['password'],
                secure=ch_config['secure'],
                settings={'timeout': ch_config['timeout']}
            )
            self.client.execute('SELECT 1')
            print("✓ 成功连接到ClickHouse服务器")
            return True
        except Exception as e:
            print(f"✗ 连接到ClickHouse服务器失败: {e}")
            return False
    
    def execute_file(self, file_path):
        """执行SQL文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                sql = f.read()
                
            # 分割SQL语句
            statements = [s.strip() for s in sql.split(';') if s.strip()]
            
            for statement in statements:
                try:
                    self.client.execute(statement)
                except Exception as e:
                    print(f"✗ 执行SQL语句失败: {statement[:100]}...")
                    print(f"  错误: {e}")
            
            print(f"✓ 成功执行SQL文件: {file_path}")
            return True
        except Exception as e:
            print(f"✗ 执行SQL文件失败: {file_path}")
            print(f"  错误: {e}")
            return False
    
    def load_rules(self, rules_file):
        """加载数据质量规则"""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                return rules if isinstance(rules, list) else [rules]
        except Exception as e:
            print(f"✗ 加载规则文件失败: {rules_file}")
            print(f"  错误: {e}")
            return []
    
    def execute_rule(self, rule):
        """执行单个数据质量规则"""
        try:
            rule_info = rule.get('rule', {})
            rule_name = rule_info.get('name', 'unknown')
            template = rule_info.get('template', '')
            
            if not template:
                return {
                    'rule_name': rule_name,
                    'status': 'ERROR',
                    'error': 'SQL模板为空',
                    'timestamp': datetime.now().isoformat()
                }
            
            result = self.client.execute(template, with_column_types=True)
            
            columns = [col[0] for col in result[1]]
            rows = result[0]
            
            if not rows:
                return {
                    'rule_name': rule_name,
                    'status': 'ERROR',
                    'error': '查询没有返回结果',
                    'timestamp': datetime.now().isoformat()
                }
            
            row_data = dict(zip(columns, rows[0]))
            
            return {
                'rule_name': rule_name,
                'rule_type': rule.get('rule_type', 'unknown'),
                'description': rule_info.get('description', ''),
                'status': 'COMPLETED',
                'result': row_data,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'rule_name': rule_info.get('name', 'unknown'),
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_quality_checks(self, rules_file):
        """运行所有数据质量检查"""
        rules = self.load_rules(rules_file)
        if not rules:
            return []
        
        print(f"开始运行 {len(rules)} 个数据质量检查...")
        results = []
        
        for i, rule in enumerate(rules, 1):
            rule_info = rule.get('rule', {})
            rule_name = rule_info.get('name', f'规则 #{i}')
            print(f"  [{i}/{len(rules)}] 执行规则: {rule_name}")
            
            result = self.execute_rule(rule)
            results.append(result)
            
            if result['status'] == 'COMPLETED':
                check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                if check_result == 'PASS':
                    print(f"    ✓ 通过")
                else:
                    print(f"    ✗ 失败")
            else:
                print(f"    ✗ 错误: {result.get('error', '未知错误')}")
        
        self.results = results
        return results
    
    def generate_report(self, output_dir='reports'):
        """生成报告"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = self.timestamp
        report_files = []
        
        # 生成JSON报告
        if 'json' in self.config['report']['format']:
            json_file = os.path.join(output_dir, f'quality_report_{timestamp}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'total_rules': len(self.results),
                    'passed_rules': len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS']),
                    'failed_rules': len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL']),
                    'error_rules': len([r for r in self.results if r['status'] == 'ERROR']),
                    'results': self.results
                }, f, indent=2)
            report_files.append(json_file)
            print(f"✓ JSON报告已保存到: {json_file}")
        
        # 生成文本报告
        if 'txt' in self.config['report']['format']:
            txt_file = os.path.join(output_dir, f'quality_report_{timestamp}.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"数据质量检查报告 - {timestamp}\n")
                f.write("=" * 50 + "\n\n")
                
                f.write("摘要:\n")
                f.write(f"  总规则数: {len(self.results)}\n")
                f.write(f"  通过规则数: {len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])}\n")
                f.write(f"  失败规则数: {len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])}\n")
                f.write(f"  错误规则数: {len([r for r in self.results if r['status'] == 'ERROR'])}\n\n")
                
                f.write("详细结果:\n")
                for i, result in enumerate(self.results, 1):
                    f.write(f"\n规则 #{i}: {result['rule_name']}\n")
                    f.write(f"  类型: {result.get('rule_type', 'unknown')}\n")
                    f.write(f"  描述: {result.get('description', '')}\n")
                    f.write(f"  状态: {result['status']}\n")
                    
                    if result['status'] == 'COMPLETED':
                        f.write(f"  检查结果: {result.get('result', {}).get('check_result', 'UNKNOWN')}\n")
                        f.write("  详细数据:\n")
                        for k, v in result.get('result', {}).items():
                            if k != 'check_result':
                                f.write(f"    {k}: {v}\n")
                    else:
                        f.write(f"  错误: {result.get('error', '未知错误')}\n")
            
            report_files.append(txt_file)
            print(f"✓ 文本报告已保存到: {txt_file}")
        
        return report_files
    
    def print_summary(self):
        """打印摘要结果"""
        print("\n数据质量检查摘要:")
        print("=" * 50)
        print(f"总规则数: {len(self.results)}")
        print(f"通过规则数: {len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])}")
        print(f"失败规则数: {len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])}")
        print(f"错误规则数: {len([r for r in self.results if r['status'] == 'ERROR'])}")
    
    def print_detailed_results(self):
        """打印详细结果"""
        print("\n数据质量检查详细结果:")
        print("=" * 50)
        
        for i, result in enumerate(self.results, 1):
            print(f"\n规则 #{i}: {result['rule_name']}")
            print(f"  类型: {result.get('rule_type', 'unknown')}")
            print(f"  描述: {result.get('description', '')}")
            print(f"  状态: {result['status']}")
            
            if result['status'] == 'COMPLETED':
                check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                print(f"  检查结果: {check_result}")
                
                if check_result == 'FAIL':
                    print("  失败详情:")
                    for k, v in result.get('result', {}).items():
                        if k != 'check_result' and v != 0 and v != '0':
                            if 'null' in k.lower() or 'empty' in k.lower() or 'duplicate' in k.lower() or 'violation' in k.lower() or 'invalid' in k.lower() or 'negative' in k.lower():
                                print(f"    {k}: {v}")
            else:
                print(f"  错误: {result.get('error', '未知错误')}")
    
    def run_all(self):
        """运行完整测试流程"""
        print("开始ClickHouse测试环境设置和数据质量检查...")
        print("=" * 50)
        
        # 连接到ClickHouse
        if not self.connect():
            return False
        
        # 执行DDL创建表
        if not self.execute_file(self.config['files']['schema']):
            return False
        
        # 插入测试数据
        if not self.execute_file(self.config['files']['data']):
            return False
        
        # 运行数据质量检查
        self.run_quality_checks(self.config['files']['rules'])
        
        # 打印结果
        self.print_summary()
        self.print_detailed_results()
        
        # 生成报告
        self.generate_report(self.config['report']['output_dir'])
        
        return True

def main():
    # 创建reports目录
    if not os.path.exists('reports'):
        os.makedirs('reports')
    
    # 运行测试
    runner = ClickHouseTestRunner(CONFIG)
    success = runner.run_all()
    
    # 设置退出码
    if not success:
        sys.exit(1)
    
    # 检查是否有失败的规则
    failed_count = len([r for r in runner.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
    if failed_count > 0:
        print(f"\n发现 {failed_count} 个失败的数据质量检查")
        sys.exit(1)
    else:
        print("\n所有数据质量检查通过")
        sys.exit(0)

if __name__ == "__main__":
    main()