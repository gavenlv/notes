#!/usr/bin/env python3
"""
数据质量检查核心引擎
提供统一的接口来执行数据质量检查
"""

import os
import logging
from typing import Dict, List, Any, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime

from .rule_engine import RuleEngine
from .template_engine import TemplateEngine
from .database_adapters import DatabaseAdapterFactory
from .config_manager import ConfigManager
from .report_generator import ReportGenerator


class DataQualityEngine:
    """数据质量检查核心引擎"""
    
    def __init__(self, config_path: str = None, environment: str = "default"):
        """
        初始化数据质量引擎
        
        Args:
            config_path: 配置文件路径
            environment: 环境名称 (default, dev, test, prod)
        """
        self.environment = environment
        self.config_manager = ConfigManager(config_path, environment)
        self.config = self.config_manager.get_config()
        
        # 初始化各个组件
        self.rule_engine = RuleEngine(self.config)
        self.template_engine = TemplateEngine(self.config)
        self.db_adapter = None
        self.report_generator = ReportGenerator(self.config)
        
        # 运行时状态
        self.results = []
        self.start_time = None
        self.end_time = None
        
        # 设置日志
        self._setup_logging()
        
    def _setup_logging(self):
        """设置日志配置"""
        logging_config = self.config.get('logging', {})
        level = getattr(logging, logging_config.get('level', 'INFO'))
        
        logging.basicConfig(
            level=level,
            format=logging_config.get('format', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler(logging_config.get('file', 'data_quality.log'))
            ]
        )
        
        self.logger = logging.getLogger(__name__)
        
    def connect_database(self, database_config: Dict[str, Any] = None) -> bool:
        """
        连接到数据库
        
        Args:
            database_config: 数据库配置，如果不提供则使用默认配置
            
        Returns:
            bool: 连接是否成功
        """
        try:
            if database_config is None:
                database_config = self.config.get('database', {})
            
            db_type = database_config.get('type', 'clickhouse')
            self.db_adapter = DatabaseAdapterFactory.create_adapter(db_type, database_config)
            
            if self.db_adapter.connect():
                self.logger.info(f"成功连接到 {db_type} 数据库")
                return True
            else:
                self.logger.error(f"连接到 {db_type} 数据库失败")
                return False
                
        except Exception as e:
            self.logger.error(f"数据库连接异常: {e}")
            return False
    
    def load_rules(self, rule_paths: List[str] = None, scenario: str = None) -> List[Dict]:
        """
        加载数据质量规则
        
        Args:
            rule_paths: 规则文件路径列表
            scenario: 场景名称，用于过滤规则
            
        Returns:
            List[Dict]: 加载的规则列表
        """
        try:
            if rule_paths is None:
                rule_paths = self.config.get('rules', {}).get('paths', [])
            
            rules = self.rule_engine.load_rules(rule_paths, scenario)
            self.logger.info(f"加载了 {len(rules)} 个数据质量规则")
            return rules
            
        except Exception as e:
            self.logger.error(f"加载规则失败: {e}")
            return []
    
    def execute_rule(self, rule: Dict[str, Any]) -> Dict[str, Any]:
        """
        执行单个数据质量规则
        
        Args:
            rule: 规则配置
            
        Returns:
            Dict: 执行结果
        """
        try:
            rule_name = rule.get('rule', {}).get('name', 'unknown')
            start_time = datetime.now()
            
            # 验证规则
            if not self.rule_engine.validate_rule(rule):
                return {
                    'rule_name': rule_name,
                    'status': 'ERROR',
                    'error': '规则验证失败',
                    'timestamp': start_time.isoformat(),
                    'duration': 0
                }
            
            # 生成SQL查询
            sql_query = self.template_engine.render_rule_template(rule)
            if not sql_query:
                return {
                    'rule_name': rule_name,
                    'status': 'ERROR',
                    'error': 'SQL模板渲染失败',
                    'timestamp': start_time.isoformat(),
                    'duration': 0
                }
            
            # 执行查询
            result = self.db_adapter.execute_query(sql_query)
            if not result:
                return {
                    'rule_name': rule_name,
                    'status': 'ERROR',
                    'error': '查询执行失败或无结果',
                    'timestamp': start_time.isoformat(),
                    'duration': 0
                }
            
            # 解析结果
            parsed_result = self._parse_rule_result(result, rule)
            
            end_time = datetime.now()
            duration = (end_time - start_time).total_seconds()
            
            return {
                'rule_name': rule_name,
                'rule_type': rule.get('rule_type', 'unknown'),
                'category': rule.get('rule', {}).get('category', 'unknown'),
                'priority': rule.get('rule', {}).get('priority', 'medium'),
                'description': rule.get('rule', {}).get('description', ''),
                'status': 'COMPLETED',
                'result': parsed_result,
                'sql_query': sql_query,
                'timestamp': start_time.isoformat(),
                'duration': duration
            }
            
        except Exception as e:
            end_time = datetime.now()
            duration = (end_time - start_time if 'start_time' in locals() else 0)
            
            return {
                'rule_name': rule.get('rule', {}).get('name', 'unknown'),
                'rule_type': rule.get('rule_type', 'unknown'),
                'status': 'ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat(),
                'duration': duration
            }
    
    def _parse_rule_result(self, query_result: List[Dict], rule: Dict) -> Dict[str, Any]:
        """
        解析规则执行结果
        
        Args:
            query_result: 查询结果
            rule: 规则配置
            
        Returns:
            Dict: 解析后的结果
        """
        if not query_result:
            return {'check_result': 'ERROR', 'error': '无查询结果'}
        
        # 获取第一行结果
        row_data = query_result[0]
        
        # 如果有 check_result 字段，直接使用
        if 'check_result' in row_data:
            return row_data
        
        # 否则根据规则类型自动判断
        rule_type = rule.get('rule_type', 'unknown')
        thresholds = rule.get('rule', {}).get('thresholds', {})
        
        check_result = self._determine_check_result(row_data, rule_type, thresholds)
        row_data['check_result'] = check_result
        
        return row_data
    
    def _determine_check_result(self, data: Dict, rule_type: str, thresholds: Dict) -> str:
        """
        根据数据和阈值自动判断检查结果
        
        Args:
            data: 查询结果数据
            rule_type: 规则类型
            thresholds: 阈值配置
            
        Returns:
            str: PASS 或 FAIL
        """
        # 通用的失败条件检查
        fail_indicators = [
            'violation', 'error', 'invalid', 'missing', 'duplicate', 
            'inconsistent', 'negative', 'null', 'empty'
        ]
        
        for key, value in data.items():
            if any(indicator in key.lower() for indicator in fail_indicators):
                if isinstance(value, (int, float)) and value > 0:
                    return 'FAIL'
                elif isinstance(value, str) and value.strip():
                    return 'FAIL'
        
        # 检查阈值
        for threshold_key, threshold_value in thresholds.items():
            if threshold_key in data:
                actual_value = data[threshold_key]
                if isinstance(threshold_value, dict):
                    if 'max' in threshold_value and actual_value > threshold_value['max']:
                        return 'FAIL'
                    if 'min' in threshold_value and actual_value < threshold_value['min']:
                        return 'FAIL'
                elif isinstance(threshold_value, (int, float)) and actual_value > threshold_value:
                    return 'FAIL'
        
        return 'PASS'
    
    def execute_rules_parallel(self, rules: List[Dict], max_workers: int = None) -> List[Dict]:
        """
        并行执行多个数据质量规则
        
        Args:
            rules: 规则列表
            max_workers: 最大并行数，默认使用配置
            
        Returns:
            List[Dict]: 执行结果列表
        """
        if not rules:
            return []
        
        if max_workers is None:
            max_workers = self.config.get('execution', {}).get('max_parallel_jobs', 5)
        
        self.logger.info(f"开始并行执行 {len(rules)} 个数据质量规则，最大并行数: {max_workers}")
        
        results = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            # 提交所有任务
            future_to_rule = {executor.submit(self.execute_rule, rule): rule for rule in rules}
            
            # 处理完成的任务
            for i, future in enumerate(as_completed(future_to_rule), 1):
                rule = future_to_rule[future]
                rule_name = rule.get('rule', {}).get('name', f'规则 #{i}')
                
                try:
                    result = future.result()
                    results.append(result)
                    
                    if result['status'] == 'COMPLETED':
                        check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
                        status_icon = "OK" if check_result == 'PASS' else "FAIL"
                        self.logger.info(f"[{i}/{len(rules)}] {status_icon} {rule_name}: {check_result}")
                    else:
                        self.logger.error(f"[{i}/{len(rules)}] FAIL {rule_name}: {result.get('error', '未知错误')}")
                        
                except Exception as e:
                    self.logger.error(f"[{i}/{len(rules)}] ✗ {rule_name}: 执行异常 - {e}")
                    results.append({
                        'rule_name': rule_name,
                        'status': 'ERROR',
                        'error': str(e),
                        'timestamp': datetime.now().isoformat(),
                        'duration': 0
                    })
        
        self.results = results
        return results
    
    def run_scenario(self, scenario_name: str, database_config: Dict = None) -> Dict[str, Any]:
        """
        运行指定场景的数据质量检查
        
        Args:
            scenario_name: 场景名称
            database_config: 数据库配置
            
        Returns:
            Dict: 执行摘要
        """
        self.start_time = datetime.now()
        self.logger.info(f"开始执行数据质量场景: {scenario_name}")
        
        try:
            # 连接数据库
            if not self.connect_database(database_config):
                return {
                    'scenario': scenario_name,
                    'status': 'ERROR',
                    'error': '数据库连接失败',
                    'timestamp': self.start_time.isoformat()
                }
            
            # 加载场景规则
            rules = self.load_rules(scenario=scenario_name)
            if not rules:
                return {
                    'scenario': scenario_name,
                    'status': 'ERROR', 
                    'error': '没有找到适用的规则',
                    'timestamp': self.start_time.isoformat()
                }
            
            # 执行规则
            results = self.execute_rules_parallel(rules)
            
            self.end_time = datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            # 生成摘要
            summary = self._generate_execution_summary(scenario_name, results, duration)
            
            # 生成报告
            self.report_generator.generate_reports(results, summary)
            
            return summary
            
        except Exception as e:
            self.end_time = datetime.now()
            self.logger.error(f"场景执行失败: {e}")
            return {
                'scenario': scenario_name,
                'status': 'ERROR',
                'error': str(e),
                'timestamp': self.start_time.isoformat()
            }
    
    def _generate_execution_summary(self, scenario_name: str, results: List[Dict], duration: float) -> Dict[str, Any]:
        """
        生成执行摘要
        
        Args:
            scenario_name: 场景名称
            results: 执行结果
            duration: 执行时长
            
        Returns:
            Dict: 执行摘要
        """
        total_rules = len(results)
        passed_rules = len([r for r in results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'PASS'])
        failed_rules = len([r for r in results if r['status'] == 'COMPLETED' and r.get('result', {}).get('check_result') == 'FAIL'])
        error_rules = len([r for r in results if r['status'] == 'ERROR'])
        
        # 按类别统计
        category_stats = {}
        priority_stats = {'high': {'total': 0, 'passed': 0, 'failed': 0, 'error': 0},
                         'medium': {'total': 0, 'passed': 0, 'failed': 0, 'error': 0},
                         'low': {'total': 0, 'passed': 0, 'failed': 0, 'error': 0}}
        
        for result in results:
            category = result.get('category', 'unknown')
            priority = result.get('priority', 'medium')
            status = result.get('status')
            check_result = result.get('result', {}).get('check_result', 'UNKNOWN')
            
            # 类别统计
            if category not in category_stats:
                category_stats[category] = {'total': 0, 'passed': 0, 'failed': 0, 'error': 0}
            
            category_stats[category]['total'] += 1
            priority_stats[priority]['total'] += 1
            
            if status == 'COMPLETED':
                if check_result == 'PASS':
                    category_stats[category]['passed'] += 1
                    priority_stats[priority]['passed'] += 1
                else:
                    category_stats[category]['failed'] += 1
                    priority_stats[priority]['failed'] += 1
            else:
                category_stats[category]['error'] += 1
                priority_stats[priority]['error'] += 1
        
        return {
            'scenario': scenario_name,
            'environment': self.environment,
            'status': 'SUCCESS' if error_rules == 0 and failed_rules == 0 else 'FAILED',
            'timestamp': self.start_time.isoformat(),
            'duration': duration,
            'summary': {
                'total_rules': total_rules,
                'passed_rules': passed_rules,
                'failed_rules': failed_rules,
                'error_rules': error_rules,
                'pass_rate': round(passed_rules / total_rules * 100, 2) if total_rules > 0 else 0
            },
            'category_stats': category_stats,
            'priority_stats': priority_stats,
            'results': results
        }
    
    def get_available_scenarios(self) -> List[str]:
        """
        获取可用的场景列表
        
        Returns:
            List[str]: 场景名称列表
        """
        return self.config_manager.get_available_scenarios()
    
    def get_supported_databases(self) -> List[str]:
        """
        获取支持的数据库类型列表
        
        Returns:
            List[str]: 数据库类型列表
        """
        return DatabaseAdapterFactory.get_supported_types()
