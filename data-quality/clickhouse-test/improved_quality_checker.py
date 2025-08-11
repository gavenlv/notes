#!/usr/bin/env python3
"""
改进版数据质量检查脚本
解决原有脚本中的问题并添加新功能
"""

import os
import sys
import yaml
import json
import time
import argparse
from datetime import datetime
from clickhouse_driver import Client
from concurrent.futures import ThreadPoolExecutor, as_completed

class ImprovedDataQualityChecker:
    def __init__(self, config_file="configs/data-quality-config.yml"):
        self.config = self._load_config(config_file)
        self.client = None
        self.results = []
        self.timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.violation_samples = {}  # 存储违规记录样本
        self.max_samples = 5  # 每个规则最多存储的违规样本数
        
    def _load_config(self, config_file):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"错误: 配置文件 {config_file} 未找到")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"解析配置文件时出错: {e}")
            sys.exit(1)
    
    def _load_rules(self, rules_file):
        """加载规则文件"""
        try:
            with open(rules_file, 'r', encoding='utf-8') as f:
                rules = yaml.safe_load(f)
                return rules if isinstance(rules, list) else [rules]
        except FileNotFoundError:
            print(f"错误: 规则文件 {rules_file} 未找到")
            sys.exit(1)
        except yaml.YAMLError as e:
            print(f"解析规则文件时出错: {e}")
            sys.exit(1)
    
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
    
    def _get_violation_samples(self, rule):
        """获取违规记录样本"""
        try:
            rule_info = rule.get('rule', {})
            rule_name = rule_info.get('name', 'unknown')
            target = rule_info.get('target', {})
            database = target.get('database', 'default')
            table = target.get('table', '')
            
            if not table:
                return []
            
            # 根据规则类型构建不同的样本查询
            rule_type = rule.get('rule_type', '')
            samples = []
            
            if rule_type == 'completeness':
                # 获取空值样本
                columns = rule_info.get('columns', [])
                for column in columns:
                    column_name = column.get('name', '')
                    if column.get('required', False):
                        # 检查NULL值
                        query = f"SELECT * FROM {database}.{table} WHERE {column_name} IS NULL LIMIT {self.max_samples}"
                        null_samples = self.client.execute(query)
                        if null_samples:
                            samples.extend([{"type": f"{column_name}_null", "data": row} for row in null_samples])
                        
                        # 检查空字符串
                        if column.get('data_type', '').lower() == 'string':
                            query = f"SELECT * FROM {database}.{table} WHERE {column_name} = '' LIMIT {self.max_samples}"
                            empty_samples = self.client.execute(query)
                            if empty_samples:
                                samples.extend([{"type": f"{column_name}_empty", "data": row} for row in empty_samples])
                
                # 检查重复值
                key_columns = []
                for check in rule_info.get('checks', {}).values():
                    if check.get('enabled', False) and 'key_columns' in check:
                        key_columns = check.get('key_columns', [])
                
                if key_columns:
                    key_str = ', '.join(key_columns)
                    query = f"""
                    SELECT * FROM {database}.{table}
                    WHERE ({key_str}) IN (
                        SELECT {key_str} FROM {database}.{table}
                        GROUP BY {key_str}
                        HAVING count(*) > 1
                    )
                    LIMIT {self.max_samples}
                    """
                    duplicate_samples = self.client.execute(query)
                    if duplicate_samples:
                        samples.extend([{"type": "duplicate", "data": row} for row in duplicate_samples])
            
            elif rule_type == 'accuracy':
                # 获取数据范围违规样本
                columns = rule_info.get('columns', [])
                for column in columns:
                    column_name = column.get('name', '')
                    validation_rules = column.get('validation_rules', [])
                    
                    for validation in validation_rules:
                        if validation.get('type') == 'range':
                            min_value = validation.get('min_value')
                            max_value = validation.get('max_value')
                            
                            if min_value is not None:
                                query = f"SELECT * FROM {database}.{table} WHERE {column_name} < {min_value} LIMIT {self.max_samples}"
                                min_violation_samples = self.client.execute(query)
                                if min_violation_samples:
                                    samples.extend([{"type": f"{column_name}_below_min", "data": row} for row in min_violation_samples])
                            
                            if max_value is not None:
                                query = f"SELECT * FROM {database}.{table} WHERE {column_name} > {max_value} LIMIT {self.max_samples}"
                                max_violation_samples = self.client.execute(query)
                                if max_violation_samples:
                                    samples.extend([{"type": f"{column_name}_above_max", "data": row} for row in max_violation_samples])
            
            elif rule_type == 'consistency':
                # 获取引用完整性违规样本
                related_tables = rule_info.get('related_tables', [])
                for related in related_tables:
                    if related.get('relationship') == 'foreign_key':
                        ref_db = related.get('database', 'default')
                        ref_table = related.get('table', '')
                        key_columns = related.get('key_columns', [])
                        ref_columns = related.get('reference_columns', [])
                        
                        if key_columns and ref_columns and len(key_columns) == len(ref_columns):
                            for i in range(len(key_columns)):
                                key_col = key_columns[i]
                                ref_col = ref_columns[i]
                                
                                query = f"""
                                SELECT * FROM {database}.{table}
                                WHERE {key_col} IS NOT NULL AND {key_col} NOT IN (
                                    SELECT {ref_col} FROM {ref_db}.{ref_table}
                                )
                                LIMIT {self.max_samples}
                                """
                                ref_violation_samples = self.client.execute(query)
                                if ref_violation_samples:
                                    samples.extend([{"type": f"invalid_{key_col}_reference", "data": row} for row in ref_violation_samples])
            
            return samples
        
        except Exception as e:
            print(f"获取违规样本时出错: {e}")
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
            
            # 执行规则查询
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
            check_result = row_data.get('check_result', 'UNKNOWN')
            
            # 如果检查失败，获取违规样本
            violation_samples = []
            if check_result == 'FAIL':
                violation_samples = self._get_violation_samples(rule)
            
            # 保存违规样本
            self.violation_samples[rule_name] = violation_samples
            
            return {
                'rule_name': rule_name,
                'rule_type': rule.get('rule_type', 'unknown'),
                'description': rule_info.get('description', ''),
                'category': rule_info.get('category', ''),
                'priority': rule_info.get('priority', 'medium'),
                'status': 'COMPLETED',
                'result': row_data,
                'violation_count': len(violation_samples),
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'rule_name': rule_info.get('name', 'unknown'),
                'rule_type': rule.get('rule_type', 'unknown'),
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def run_checks_parallel(self, rules_file):
        """并行运行数据质量检查"""
        rules = self._load_rules(rules_file)
        if not rules:
            return []
        
        print(f"开始并行运行 {len(rules)} 个数据质量检查...")
        results = []
        
        # 获取最大并行作业数
        max_workers = self.config.get('quality_checks', {}).get('max_parallel_jobs', 5)
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有规则执行任务
            future_to_rule = {executor.submit(self.execute_rule, rule): rule for rule in rules}
            
            # 处理完成的任务
            for i, future in enumerate(as_completed(future_to_rule), 1):
                rule = future_to_rule[future]
                rule_info = rule.get('rule', {})
                rule_name = rule_info.get('name', f'规则 #{i}')
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'COMPLETED':
                        check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                        if check_result == 'PASS':
                            print(f"  [{i}/{len(rules)}] ✓ 通过: {rule_name}")
                        else:
                            violation_count = result.get('violation_count', 0)
                            print(f"  [{i}/{len(rules)}] ✗ 失败: {rule_name} (发现 {violation_count} 个违规样本)")
                    else:
                        print(f"  [{i}/{len(rules)}] ✗ 错误: {rule_name} - {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    print(f"  [{i}/{len(rules)}] ✗ 执行出错: {rule_name} - {str(e)}")
                    results.append({
                        'rule_name': rule_name,
                        'status': 'ERROR',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat()
                    })
        
        self.results = results
        return results
    
    def generate_enhanced_report(self, output_dir='reports'):
        """生成增强版报告"""
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        timestamp = self.timestamp
        report_files = []
        
        # 计算统计信息
        total_rules = len(self.results)
        passed_rules = len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
        failed_rules = len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
        error_rules = len([r for r in self.results if r['status'] == 'ERROR'])
        
        # 按类别和优先级分组
        rules_by_category = {}
        rules_by_priority = {'high': [], 'medium': [], 'low': []}
        
        for result in self.results:
            # 按类别分组
            category = result.get('category', 'unknown')
            if category not in rules_by_category:
                rules_by_category[category] = []
            rules_by_category[category].append(result)
            
            # 按优先级分组
            priority = result.get('priority', 'medium').lower()
            if priority in rules_by_priority:
                rules_by_priority[priority].append(result)
        
        # 生成JSON报告
        if 'json' in self.config.get('report', {}).get('format', ['json']):
            json_file = os.path.join(output_dir, f'quality_report_{timestamp}.json')
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': timestamp,
                    'summary': {
                        'total_rules': total_rules,
                        'passed_rules': passed_rules,
                        'failed_rules': failed_rules,
                        'error_rules': error_rules,
                        'pass_rate': round(passed_rules / total_rules * 100, 2) if total_rules > 0 else 0
                    },
                    'by_category': {
                        category: {
                            'total': len(rules),
                            'passed': len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS']),
                            'failed': len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL']),
                            'error': len([r for r in rules if r['status'] == 'ERROR'])
                        } for category, rules in rules_by_category.items()
                    },
                    'by_priority': {
                        priority: {
                            'total': len(rules),
                            'passed': len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS']),
                            'failed': len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL']),
                            'error': len([r for r in rules if r['status'] == 'ERROR'])
                        } for priority, rules in rules_by_priority.items() if rules
                    },
                    'results': self.results,
                    'violation_samples': self.violation_samples
                }, f, indent=2)
            report_files.append(json_file)
            print(f"✓ JSON报告已保存到: {json_file}")
        
        # 生成文本报告
        if 'txt' in self.config.get('report', {}).get('format', ['txt']):
            txt_file = os.path.join(output_dir, f'quality_report_{timestamp}.txt')
            with open(txt_file, 'w', encoding='utf-8') as f:
                f.write(f"数据质量检查报告 - {timestamp}\n")
                f.write("=" * 50 + "\n\n")
                
                # 摘要部分
                f.write("摘要:\n")
                f.write(f"  总规则数: {total_rules}\n")
                f.write(f"  通过规则数: {passed_rules}\n")
                f.write(f"  失败规则数: {failed_rules}\n")
                f.write(f"  错误规则数: {error_rules}\n")
                f.write(f"  通过率: {round(passed_rules / total_rules * 100, 2)}%\n\n" if total_rules > 0 else "  通过率: 0%\n\n")
                
                # 按类别统计
                f.write("按类别统计:\n")
                for category, rules in rules_by_category.items():
                    passed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
                    failed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
                    error = len([r for r in rules if r['status'] == 'ERROR'])
                    f.write(f"  {category}: 总数={len(rules)}, 通过={passed}, 失败={failed}, 错误={error}\n")
                f.write("\n")
                
                # 按优先级统计
                f.write("按优先级统计:\n")
                for priority in ['high', 'medium', 'low']:
                    if priority in rules_by_priority and rules_by_priority[priority]:
                        rules = rules_by_priority[priority]
                        passed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
                        failed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
                        error = len([r for r in rules if r['status'] == 'ERROR'])
                        f.write(f"  {priority}: 总数={len(rules)}, 通过={passed}, 失败={failed}, 错误={error}\n")
                f.write("\n")
                
                # 失败规则详情
                f.write("失败规则详情:\n")
                failed_count = 0
                for result in self.results:
                    if result['status'] == 'COMPLETED' and result.get('result', {}).get('check_result') == 'FAIL':
                        failed_count += 1
                        rule_name = result['rule_name']
                        rule_type = result.get('rule_type', 'unknown')
                        description = result.get('description', '')
                        priority = result.get('priority', 'medium')
                        
                        f.write(f"\n失败 #{failed_count}: {rule_name}\n")
                        f.write(f"  类型: {rule_type}\n")
                        f.write(f"  描述: {description}\n")
                        f.write(f"  优先级: {priority}\n")
                        
                        # 写入失败详情
                        f.write("  失败详情:\n")
                        for k, v in result.get('result', {}).items():
                            if k != 'check_result' and v != 0 and v != '0':
                                if 'null' in k.lower() or 'empty' in k.lower() or 'duplicate' in k.lower() or 'violation' in k.lower() or 'invalid' in k.lower() or 'negative' in k.lower():
                                    f.write(f"    {k}: {v}\n")
                        
                        # 写入违规样本
                        violation_samples = self.violation_samples.get(rule_name, [])
                        if violation_samples:
                            f.write(f"  违规样本 (最多 {len(violation_samples)} 条):\n")
                            for i, sample in enumerate(violation_samples, 1):
                                f.write(f"    样本 #{i} - 类型: {sample['type']}\n")
                                f.write(f"      数据: {sample['data']}\n")
                
                if failed_count == 0:
                    f.write("  没有失败的规则\n")
                
                # 错误规则详情
                f.write("\n错误规则详情:\n")
                error_count = 0
                for result in self.results:
                    if result['status'] == 'ERROR':
                        error_count += 1
                        rule_name = result['rule_name']
                        error = result.get('error', '未知错误')
                        
                        f.write(f"\n错误 #{error_count}: {rule_name}\n")
                        f.write(f"  错误信息: {error}\n")
                
                if error_count == 0:
                    f.write("  没有错误的规则\n")
            
            report_files.append(txt_file)
            print(f"✓ 文本报告已保存到: {txt_file}")
        
        # 生成HTML报告
        if 'html' in self.config.get('report', {}).get('format', []):
            html_file = os.path.join(output_dir, f'quality_report_{timestamp}.html')
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <title>数据质量检查报告 - {timestamp}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1, h2, h3 {{ color: #333; }}
                        .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                        .pass {{ color: green; }}
                        .fail {{ color: red; }}
                        .error {{ color: orange; }}
                        table {{ border-collapse: collapse; width: 100%; margin-bottom: 20px; }}
                        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                        th {{ background-color: #f2f2f2; }}
                        tr:nth-child(even) {{ background-color: #f9f9f9; }}
                        .details {{ margin-top: 10px; padding: 10px; background-color: #f9f9f9; border-radius: 5px; }}
                        .sample {{ margin-top: 5px; padding: 5px; background-color: #fff; border: 1px solid #ddd; border-radius: 3px; }}
                        .high {{ background-color: #ffdddd; }}
                        .medium {{ background-color: #ffffcc; }}
                        .low {{ background-color: #ddffdd; }}
                    </style>
                </head>
                <body>
                    <h1>数据质量检查报告</h1>
                    <p>生成时间: {timestamp}</p>
                    
                    <div class="summary">
                        <h2>摘要</h2>
                        <p>总规则数: {total_rules}</p>
                        <p>通过规则数: <span class="pass">{passed_rules}</span></p>
                        <p>失败规则数: <span class="fail">{failed_rules}</span></p>
                        <p>错误规则数: <span class="error">{error_rules}</span></p>
                        <p>通过率: {round(passed_rules / total_rules * 100, 2)}%</p>
                    </div>
                    
                    <h2>按类别统计</h2>
                    <table>
                        <tr>
                            <th>类别</th>
                            <th>总数</th>
                            <th>通过</th>
                            <th>失败</th>
                            <th>错误</th>
                            <th>通过率</th>
                        </tr>
                """)
                
                # 按类别统计表格
                for category, rules in rules_by_category.items():
                    passed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
                    failed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
                    error = len([r for r in rules if r['status'] == 'ERROR'])
                    pass_rate = round(passed / len(rules) * 100, 2) if len(rules) > 0 else 0
                    
                    f.write(f"""
                        <tr>
                            <td>{category}</td>
                            <td>{len(rules)}</td>
                            <td class="pass">{passed}</td>
                            <td class="fail">{failed}</td>
                            <td class="error">{error}</td>
                            <td>{pass_rate}%</td>
                        </tr>
                    """)
                
                f.write(f"""
                    </table>
                    
                    <h2>按优先级统计</h2>
                    <table>
                        <tr>
                            <th>优先级</th>
                            <th>总数</th>
                            <th>通过</th>
                            <th>失败</th>
                            <th>错误</th>
                            <th>通过率</th>
                        </tr>
                """)
                
                # 按优先级统计表格
                for priority in ['high', 'medium', 'low']:
                    if priority in rules_by_priority and rules_by_priority[priority]:
                        rules = rules_by_priority[priority]
                        passed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
                        failed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
                        error = len([r for r in rules if r['status'] == 'ERROR'])
                        pass_rate = round(passed / len(rules) * 100, 2) if len(rules) > 0 else 0
                        
                        f.write(f"""
                            <tr class="{priority}">
                                <td>{priority}</td>
                                <td>{len(rules)}</td>
                                <td class="pass">{passed}</td>
                                <td class="fail">{failed}</td>
                                <td class="error">{error}</td>
                                <td>{pass_rate}%</td>
                            </tr>
                        """)
                
                f.write(f"""
                    </table>
                    
                    <h2>失败规则详情</h2>
                """)
                
                # 失败规则详情
                failed_count = 0
                for result in self.results:
                    if result['status'] == 'COMPLETED' and result.get('result', {}).get('check_result') == 'FAIL':
                        failed_count += 1
                        rule_name = result['rule_name']
                        rule_type = result.get('rule_type', 'unknown')
                        description = result.get('description', '')
                        priority = result.get('priority', 'medium')
                        
                        f.write(f"""
                            <div class="{priority}">
                                <h3>失败 #{failed_count}: {rule_name}</h3>
                                <p>类型: {rule_type}</p>
                                <p>描述: {description}</p>
                                <p>优先级: {priority}</p>
                                
                                <div class="details">
                                    <h4>失败详情:</h4>
                                    <ul>
                        """)
                        
                        # 写入失败详情
                        for k, v in result.get('result', {}).items():
                            if k != 'check_result' and v != 0 and v != '0':
                                if 'null' in k.lower() or 'empty' in k.lower() or 'duplicate' in k.lower() or 'violation' in k.lower() or 'invalid' in k.lower() or 'negative' in k.lower():
                                    f.write(f"<li>{k}: {v}</li>\n")
                        
                        f.write("</ul>\n")
                        
                        # 写入违规样本
                        violation_samples = self.violation_samples.get(rule_name, [])
                        if violation_samples:
                            f.write(f"<h4>违规样本 (最多 {len(violation_samples)} 条):</h4>\n")
                            
                            for i, sample in enumerate(violation_samples, 1):
                                f.write(f"<div class=\"sample\">\n")
                                f.write(f"<p>样本 #{i} - 类型: {sample['type']}</p>\n")
                                f.write(f"<pre>{sample['data']}</pre>\n")
                                f.write("</div>\n")
                        
                        f.write("</div>\n</div>\n")
                
                if failed_count == 0:
                    f.write("<p>没有失败的规则</p>\n")
                
                # 错误规则详情
                f.write("<h2>错误规则详情</h2>\n")
                
                error_count = 0
                for result in self.results:
                    if result['status'] == 'ERROR':
                        error_count += 1
                        rule_name = result['rule_name']
                        error = result.get('error', '未知错误')
                        
                        f.write(f"""
                            <div class="error">
                                <h3>错误 #{error_count}: {rule_name}</h3>
                                <p>错误信息: {error}</p>
                            </div>
                        """)
                
                if error_count == 0:
                    f.write("<p>没有错误的规则</p>\n")
                
                f.write(f"""
                </body>
                </html>
                """)
            
            report_files.append(html_file)
            print(f"✓ HTML报告已保存到: {html_file}")
        
        return report_files
    
    def print_enhanced_summary(self):
        """打印增强版摘要"""
        print("\n数据质量检查摘要:")
        print("=" * 50)
        
        total_rules = len(self.results)
        passed_rules = len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
        failed_rules = len([r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
        error_rules = len([r for r in self.results if r['status'] == 'ERROR'])
        
        print(f"总规则数: {total_rules}")
        print(f"通过规则数: {passed_rules}")
        print(f"失败规则数: {failed_rules}")
        print(f"错误规则数: {error_rules}")
        print(f"通过率: {round(passed_rules / total_rules * 100, 2)}%" if total_rules > 0 else "通过率: 0%")
        
        # 按优先级统计
        print("\n按优先级统计:")
        rules_by_priority = {'high': [], 'medium': [], 'low': []}
        
        for result in self.results:
            priority = result.get('priority', 'medium').lower()
            if priority in rules_by_priority:
                rules_by_priority[priority].append(result)
        
        for priority in ['high', 'medium', 'low']:
            if priority in rules_by_priority and rules_by_priority[priority]:
                rules = rules_by_priority[priority]
                passed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
                failed = len([r for r in rules if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
                error = len([r for r in rules if r['status'] == 'ERROR'])
                
                print(f"{priority.upper()}: 总数={len(rules)}, 通过={passed}, 失败={failed}, 错误={error}")
    
    def print_enhanced_details(self):
        """打印增强版详细结果"""
        print("\n数据质量检查详细结果:")
        print("=" * 50)
        
        # 只打印失败和错误的规则
        failed_results = [r for r in self.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL']
        error_results = [r for r in self.results if r['status'] == 'ERROR']
        
        if not failed_results and not error_results:
            print("所有规则都通过了检查！")
            return
        
        # 打印失败的规则
        if failed_results:
            print("\n失败的规则:")
            for i, result in enumerate(failed_results, 1):
                rule_name = result['rule_name']
                rule_type = result.get('rule_type', 'unknown')
                priority = result.get('priority', 'medium')
                
                print(f"\n失败 #{i}: {rule_name} [优先级: {priority}]")
                print(f"  类型: {rule_type}")
                print(f"  描述: {result.get('description', '')}")
                
                # 打印失败详情
                print("  失败详情:")
                for k, v in result.get('result', {}).items():
                    if k != 'check_result' and v != 0 and v != '0':
                        if 'null' in k.lower() or 'empty' in k.lower() or 'duplicate' in k.lower() or 'violation' in k.lower() or 'invalid' in k.lower() or 'negative' in k.lower():
                            print(f"    {k}: {v}")
                
                # 打印违规样本数量
                violation_samples = self.violation_samples.get(rule_name, [])
                if violation_samples:
                    print(f"  发现 {len(violation_samples)} 个违规样本 (详情请查看报告)")
        
        # 打印错误的规则
        if error_results:
            print("\n错误的规则:")
            for i, result in enumerate(error_results, 1):
                print(f"\n错误 #{i}: {result['rule_name']}")
                print(f"  错误: {result.get('error', '未知错误')}")
    
    def run_all(self, rules_file=None):
        """运行完整测试流程"""
        print("开始ClickHouse测试环境设置和数据质量检查...")
        print("=" * 50)
        
        # 连接到ClickHouse
        if not self.connect():
            return False
        
        # 使用指定的规则文件或配置中的规则文件
        if rules_file is None:
            rules_file = self.config.get('files', {}).get('rules', 'clickhouse-test/quality_rules.yml')
        
        # 并行运行数据质量检查
        self.run_checks_parallel(rules_file)
        
        # 打印增强版摘要和详细结果
        self.print_enhanced_summary()
        self.print_enhanced_details()
        
        # 生成增强版报告
        self.generate_enhanced_report(self.config.get('report', {}).get('output_dir', 'reports'))
        
        return True

def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='改进版数据质量检查工具')
    parser.add_argument('--config', default='configs/data-quality-config.yml', help='配置文件路径')
    parser.add_argument('--rules', help='规则文件路径')
    parser.add_argument('--output-dir', help='报告输出目录')
    args = parser.parse_args()
    
    # 创建reports目录
    output_dir = args.output_dir or 'reports'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # 运行测试
    checker = ImprovedDataQualityChecker(args.config)
    success = checker.run_all(args.rules)
    
    # 设置退出码
    if not success:
        sys.exit(1)
    
    # 检查是否有失败的规则
    failed_count = len([r for r in checker.results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
    if failed_count > 0:
        print(f"\n发现 {failed_count} 个失败的数据质量检查")
        sys.exit(1)
    else:
        print("\n所有数据质量检查通过")
        sys.exit(0)

if __name__ == "__main__":
    main()