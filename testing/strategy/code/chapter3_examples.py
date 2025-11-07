#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第3章：测试策略与最佳实践 - 示例代码
本文件包含测试策略与最佳实践的示例代码，涵盖测试策略制定、风险分析、测试计划、
测试度量、持续测试、测试团队管理等内容。
"""

import os
import sys
import unittest
import time
import json
import random
from datetime import datetime, timedelta
from unittest.mock import Mock, patch
import subprocess
import logging
from typing import List, Dict, Tuple, Any

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# 实验1：测试策略制定
# ============================================================================

class TestStrategy:
    """测试策略类，用于制定和管理测试策略"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.test_levels = ["单元测试", "集成测试", "系统测试", "验收测试"]
        self.test_types = ["功能测试", "性能测试", "安全测试", "兼容性测试", "可用性测试"]
        self.risk_levels = ["高", "中", "低"]
        self.strategy = {}
        
    def analyze_risks(self, features: List[str]) -> Dict[str, str]:
        """分析功能风险级别"""
        risk_analysis = {}
        for feature in features:
            # 简单的风险评估逻辑（实际项目中会更复杂）
            if "支付" in feature or "安全" in feature or "核心" in feature:
                risk_analysis[feature] = "高"
            elif "用户" in feature or "数据" in feature:
                risk_analysis[feature] = "中"
            else:
                risk_analysis[feature] = "低"
        return risk_analysis
    
    def determine_test_scope(self, risk_analysis: Dict[str, str]) -> Dict[str, List[str]]:
        """根据风险分析确定测试范围"""
        test_scope = {}
        
        for feature, risk in risk_analysis.items():
            if risk == "高":
                test_scope[feature] = ["单元测试", "集成测试", "系统测试", "验收测试", 
                                      "功能测试", "性能测试", "安全测试"]
            elif risk == "中":
                test_scope[feature] = ["单元测试", "集成测试", "系统测试", 
                                      "功能测试", "性能测试"]
            else:
                test_scope[feature] = ["单元测试", "功能测试"]
                
        return test_scope
    
    def allocate_resources(self, test_scope: Dict[str, List[str]], total_days: int) -> Dict[str, int]:
        """分配测试资源（时间）"""
        total_tests = sum(len(tests) for tests in test_scope.values())
        resource_allocation = {}
        
        for feature, tests in test_scope.items():
            # 根据测试数量分配时间
            allocation = int((len(tests) / total_tests) * total_days)
            resource_allocation[feature] = max(1, allocation)  # 至少分配1天
            
        return resource_allocation
    
    def create_strategy(self, features: List[str], total_days: int) -> Dict:
        """创建完整的测试策略"""
        risk_analysis = self.analyze_risks(features)
        test_scope = self.determine_test_scope(risk_analysis)
        resource_allocation = self.allocate_resources(test_scope, total_days)
        
        self.strategy = {
            "project_name": self.project_name,
            "total_days": total_days,
            "risk_analysis": risk_analysis,
            "test_scope": test_scope,
            "resource_allocation": resource_allocation,
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.strategy
    
    def save_strategy(self, file_path: str):
        """保存测试策略到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.strategy, f, ensure_ascii=False, indent=2)
        logger.info(f"测试策略已保存到 {file_path}")
    
    def load_strategy(self, file_path: str):
        """从文件加载测试策略"""
        with open(file_path, 'r', encoding='utf-8') as f:
            self.strategy = json.load(f)
        logger.info(f"测试策略已从 {file_path} 加载")
    
    def print_strategy(self):
        """打印测试策略"""
        if not self.strategy:
            print("没有可用的测试策略")
            return
            
        print(f"\n=== {self.strategy['project_name']} 测试策略 ===")
        print(f"创建时间: {self.strategy['created_at']}")
        print(f"总测试时间: {self.strategy['total_days']} 天")
        
        print("\n风险分析:")
        for feature, risk in self.strategy['risk_analysis'].items():
            print(f"  {feature}: {risk}风险")
        
        print("\n测试范围:")
        for feature, tests in self.strategy['test_scope'].items():
            print(f"  {feature}: {', '.join(tests)}")
        
        print("\n资源分配:")
        for feature, days in self.strategy['resource_allocation'].items():
            print(f"  {feature}: {days}天")


def demo_test_strategy():
    """演示测试策略制定"""
    print("=== 实验1：测试策略制定 ===")
    
    # 创建测试策略实例
    strategy = TestStrategy("电商平台项目")
    
    # 定义项目功能
    features = [
        "用户注册与登录",
        "商品浏览与搜索",
        "购物车管理",
        "订单处理",
        "支付系统",
        "用户评价系统",
        "后台管理系统"
    ]
    
    # 制定测试策略（假设总测试时间为30天）
    strategy_data = strategy.create_strategy(features, total_days=30)
    
    # 打印策略
    strategy.print_strategy()
    
    # 保存策略
    os.makedirs("output", exist_ok=True)
    strategy.save_strategy("output/test_strategy.json")
    
    return strategy


# ============================================================================
# 实验2：测试计划制定
# ============================================================================

class TestPlan:
    """测试计划类，用于制定和管理测试计划"""
    
    def __init__(self, project_name: str, strategy: Dict):
        self.project_name = project_name
        self.strategy = strategy
        self.test_plan = {}
        
    def create_test_cases(self, feature: str, test_types: List[str]) -> List[Dict]:
        """为特定功能创建测试用例"""
        test_cases = []
        
        for test_type in test_types:
            # 简化的测试用例生成逻辑
            if test_type == "功能测试":
                test_cases.append({
                    "id": f"TC_{feature}_FUNC_001",
                    "title": f"验证{feature}基本功能",
                    "type": "功能测试",
                    "priority": "高",
                    "steps": [
                        f"1. 访问{feature}页面",
                        f"2. 执行{feature}操作",
                        f"3. 验证操作结果"
                    ],
                    "expected_result": f"{feature}功能正常工作"
                })
            elif test_type == "性能测试":
                test_cases.append({
                    "id": f"TC_{feature}_PERF_001",
                    "title": f"验证{feature}性能指标",
                    "type": "性能测试",
                    "priority": "中",
                    "steps": [
                        f"1. 准备{feature}性能测试环境",
                        f"2. 执行{feature}性能测试",
                        f"3. 收集性能数据"
                    ],
                    "expected_result": f"{feature}响应时间小于2秒"
                })
            elif test_type == "安全测试":
                test_cases.append({
                    "id": f"TC_{feature}_SEC_001",
                    "title": f"验证{feature}安全性",
                    "type": "安全测试",
                    "priority": "高",
                    "steps": [
                        f"1. 准备{feature}安全测试环境",
                        f"2. 执行{feature}安全测试",
                        f"3. 验证安全防护措施"
                    ],
                    "expected_result": f"{feature}安全防护有效"
                })
        
        return test_cases
    
    def schedule_test_execution(self, resource_allocation: Dict[str, int]) -> Dict[str, Dict]:
        """安排测试执行计划"""
        schedule = {}
        current_day = 1
        
        # 按风险级别排序功能（高风险优先）
        sorted_features = sorted(
            resource_allocation.items(),
            key=lambda x: self.strategy['risk_analysis'].get(x[0], "低"),
            reverse=True
        )
        
        for feature, days in sorted_features:
            schedule[feature] = {
                "start_day": current_day,
                "end_day": current_day + days - 1,
                "duration_days": days
            }
            current_day += days
        
        return schedule
    
    def create_test_plan(self):
        """创建完整的测试计划"""
        test_cases = {}
        test_scope = self.strategy.get("test_scope", {})
        
        # 为每个功能创建测试用例
        for feature, test_types in test_scope.items():
            test_cases[feature] = self.create_test_cases(feature, test_types)
        
        # 安排测试执行计划
        schedule = self.schedule_test_execution(self.strategy.get("resource_allocation", {}))
        
        self.test_plan = {
            "project_name": self.project_name,
            "strategy_summary": {
                "total_features": len(test_scope),
                "total_days": self.strategy.get("total_days", 0),
                "risk_distribution": self._count_risks()
            },
            "test_cases": test_cases,
            "schedule": schedule,
            "test_environment": {
                "development": "开发环境",
                "staging": "预发布环境",
                "production": "生产环境"
            },
            "test_team": {
                "test_manager": "测试经理",
                "test_leads": ["功能测试负责人", "性能测试负责人", "安全测试负责人"],
                "testers": ["测试工程师1", "测试工程师2", "测试工程师3"]
            },
            "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.test_plan
    
    def _count_risks(self) -> Dict[str, int]:
        """统计风险分布"""
        risk_counts = {"高": 0, "中": 0, "低": 0}
        for risk in self.strategy.get("risk_analysis", {}).values():
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
        return risk_counts
    
    def save_test_plan(self, file_path: str):
        """保存测试计划到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.test_plan, f, ensure_ascii=False, indent=2)
        logger.info(f"测试计划已保存到 {file_path}")
    
    def print_test_plan_summary(self):
        """打印测试计划摘要"""
        if not self.test_plan:
            print("没有可用的测试计划")
            return
            
        print(f"\n=== {self.test_plan['project_name']} 测试计划摘要 ===")
        print(f"创建时间: {self.test_plan['created_at']}")
        
        summary = self.test_plan["strategy_summary"]
        print(f"功能总数: {summary['total_features']}")
        print(f"总测试天数: {summary['total_days']}")
        
        print("\n风险分布:")
        for risk, count in summary['risk_distribution'].items():
            print(f"  {risk}风险: {count}个功能")
        
        print("\n测试用例总数:")
        total_cases = sum(len(cases) for cases in self.test_plan['test_cases'].values())
        print(f"  {total_cases}个测试用例")
        
        print("\n测试执行计划:")
        for feature, schedule in self.test_plan['schedule'].items():
            print(f"  {feature}: 第{schedule['start_day']}天 - 第{schedule['end_day']}天 ({schedule['duration_days']}天)")


def demo_test_plan():
    """演示测试计划制定"""
    print("\n=== 实验2：测试计划制定 ===")
    
    # 使用之前创建的测试策略
    strategy = TestStrategy("电商平台项目")
    strategy.load_strategy("output/test_strategy.json")
    
    # 创建测试计划
    test_plan = TestPlan("电商平台项目", strategy.strategy)
    plan_data = test_plan.create_test_plan()
    
    # 打印测试计划摘要
    test_plan.print_test_plan_summary()
    
    # 保存测试计划
    test_plan.save_test_plan("output/test_plan.json")
    
    return test_plan


# ============================================================================
# 实验3：测试度量与报告
# ============================================================================

class TestMetrics:
    """测试度量类，用于收集和分析测试度量数据"""
    
    def __init__(self):
        self.test_results = {}
        self.metrics = {}
        
    def record_test_result(self, feature: str, test_case_id: str, result: str, 
                          execution_time: float, defects: List[str] = None):
        """记录测试结果"""
        if feature not in self.test_results:
            self.test_results[feature] = {}
            
        self.test_results[feature][test_case_id] = {
            "result": result,  # "通过", "失败", "阻塞", "跳过"
            "execution_time": execution_time,
            "defects": defects or [],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def calculate_test_coverage(self, total_test_cases: int, executed_test_cases: int) -> float:
        """计算测试覆盖率"""
        if total_test_cases == 0:
            return 0.0
        return (executed_test_cases / total_test_cases) * 100
    
    def calculate_pass_rate(self, total_test_cases: int, passed_test_cases: int) -> float:
        """计算测试通过率"""
        if total_test_cases == 0:
            return 0.0
        return (passed_test_cases / total_test_cases) * 100
    
    def calculate_defect_density(self, total_defects: int, total_test_cases: int) -> float:
        """计算缺陷密度"""
        if total_test_cases == 0:
            return 0.0
        return total_defects / total_test_cases
    
    def calculate_test_efficiency(self, total_execution_time: float, total_test_cases: int) -> float:
        """计算测试效率（测试用例/小时）"""
        if total_execution_time == 0:
            return 0.0
        return total_test_cases / (total_execution_time / 3600)  # 转换为小时
    
    def generate_test_metrics(self) -> Dict:
        """生成测试度量数据"""
        total_test_cases = 0
        executed_test_cases = 0
        passed_test_cases = 0
        failed_test_cases = 0
        blocked_test_cases = 0
        skipped_test_cases = 0
        total_defects = 0
        total_execution_time = 0
        
        # 统计测试结果
        for feature_results in self.test_results.values():
            for test_case in feature_results.values():
                total_test_cases += 1
                total_execution_time += test_case["execution_time"]
                total_defects += len(test_case["defects"])
                
                if test_case["result"] == "通过":
                    passed_test_cases += 1
                    executed_test_cases += 1
                elif test_case["result"] == "失败":
                    failed_test_cases += 1
                    executed_test_cases += 1
                elif test_case["result"] == "阻塞":
                    blocked_test_cases += 1
                    executed_test_cases += 1
                elif test_case["result"] == "跳过":
                    skipped_test_cases += 1
        
        # 计算度量指标
        self.metrics = {
            "test_coverage": self.calculate_test_coverage(total_test_cases, executed_test_cases),
            "pass_rate": self.calculate_pass_rate(executed_test_cases, passed_test_cases),
            "fail_rate": self.calculate_pass_rate(executed_test_cases, failed_test_cases),
            "defect_density": self.calculate_defect_density(total_defects, total_test_cases),
            "test_efficiency": self.calculate_test_efficiency(total_execution_time, executed_test_cases),
            "summary": {
                "total_test_cases": total_test_cases,
                "executed_test_cases": executed_test_cases,
                "passed_test_cases": passed_test_cases,
                "failed_test_cases": failed_test_cases,
                "blocked_test_cases": blocked_test_cases,
                "skipped_test_cases": skipped_test_cases,
                "total_defects": total_defects,
                "total_execution_time": total_execution_time
            },
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return self.metrics
    
    def generate_test_report(self) -> str:
        """生成测试报告"""
        if not self.metrics:
            self.generate_test_metrics()
        
        report = f"""
=== 测试报告 ===
生成时间: {self.metrics['generated_at']}

测试概况:
- 总测试用例数: {self.metrics['summary']['total_test_cases']}
- 已执行测试用例: {self.metrics['summary']['executed_test_cases']}
- 通过测试用例: {self.metrics['summary']['passed_test_cases']}
- 失败测试用例: {self.metrics['summary']['failed_test_cases']}
- 阻塞测试用例: {self.metrics['summary']['blocked_test_cases']}
- 跳过测试用例: {self.metrics['summary']['skipped_test_cases']}
- 发现缺陷总数: {self.metrics['summary']['total_defects']}
- 总执行时间: {self.metrics['summary']['total_execution_time']:.2f}秒

度量指标:
- 测试覆盖率: {self.metrics['test_coverage']:.2f}%
- 测试通过率: {self.metrics['pass_rate']:.2f}%
- 测试失败率: {self.metrics['fail_rate']:.2f}%
- 缺陷密度: {self.metrics['defect_density']:.2f}缺陷/测试用例
- 测试效率: {self.metrics['test_efficiency']:.2f}测试用例/小时

按功能统计:
"""
        
        # 添加按功能的统计
        for feature, results in self.test_results.items():
            feature_total = len(results)
            feature_passed = sum(1 for r in results.values() if r["result"] == "通过")
            feature_failed = sum(1 for r in results.values() if r["result"] == "失败")
            feature_defects = sum(len(r["defects"]) for r in results.values())
            
            report += f"""
{feature}:
  - 测试用例数: {feature_total}
  - 通过: {feature_passed}
  - 失败: {feature_failed}
  - 缺陷数: {feature_defects}
"""
        
        return report
    
    def save_metrics(self, file_path: str):
        """保存度量数据到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.metrics, f, ensure_ascii=False, indent=2)
        logger.info(f"测试度量数据已保存到 {file_path}")
    
    def save_report(self, file_path: str):
        """保存测试报告到文件"""
        report = self.generate_test_report()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"测试报告已保存到 {file_path}")


def demo_test_metrics():
    """演示测试度量与报告"""
    print("\n=== 实验3：测试度量与报告 ===")
    
    # 创建测试度量实例
    metrics = TestMetrics()
    
    # 模拟测试结果
    test_results = [
        ("用户注册与登录", "TC_用户注册与登录_FUNC_001", "通过", 5.2, []),
        ("用户注册与登录", "TC_用户注册与登录_PERF_001", "失败", 12.3, ["性能不达标"]),
        ("用户注册与登录", "TC_用户注册与登录_SEC_001", "通过", 8.7, []),
        ("支付系统", "TC_支付系统_FUNC_001", "失败", 15.6, ["支付失败"]),
        ("支付系统", "TC_支付系统_PERF_001", "通过", 10.2, []),
        ("支付系统", "TC_支付系统_SEC_001", "通过", 13.4, []),
        ("商品浏览与搜索", "TC_商品浏览与搜索_FUNC_001", "通过", 6.8, []),
        ("商品浏览与搜索", "TC_商品浏览与搜索_PERF_001", "通过", 9.5, []),
        ("订单处理", "TC_订单处理_FUNC_001", "通过", 7.3, []),
        ("订单处理", "TC_订单处理_PERF_001", "阻塞", 0.0, []),
    ]
    
    # 记录测试结果
    for feature, test_id, result, time, defects in test_results:
        metrics.record_test_result(feature, test_id, result, time, defects)
    
    # 生成度量数据
    metrics_data = metrics.generate_test_metrics()
    
    # 打印关键度量指标
    print("\n关键度量指标:")
    print(f"测试覆盖率: {metrics_data['test_coverage']:.2f}%")
    print(f"测试通过率: {metrics_data['pass_rate']:.2f}%")
    print(f"缺陷密度: {metrics_data['defect_density']:.2f}缺陷/测试用例")
    print(f"测试效率: {metrics_data['test_efficiency']:.2f}测试用例/小时")
    
    # 生成并保存测试报告
    report = metrics.generate_test_report()
    print(report)
    
    # 保存度量和报告
    metrics.save_metrics("output/test_metrics.json")
    metrics.save_report("output/test_report.txt")
    
    return metrics


# ============================================================================
# 实验4：持续测试与DevOps集成
# ============================================================================

class ContinuousTesting:
    """持续测试类，用于模拟CI/CD流水线中的持续测试"""
    
    def __init__(self, project_name: str):
        self.project_name = project_name
        self.pipeline_stages = [
            "代码提交",
            "静态代码分析",
            "单元测试",
            "构建应用",
            "部署到测试环境",
            "集成测试",
            "安全扫描",
            "部署到预发布环境",
            "端到端测试",
            "性能测试",
            "部署到生产环境"
        ]
        self.pipeline_results = {}
    
    def run_static_code_analysis(self, code_changes: List[str]) -> Dict:
        """运行静态代码分析"""
        print("执行静态代码分析...")
        time.sleep(1)  # 模拟分析时间
        
        # 模拟分析结果
        issues = []
        for change in code_changes:
            if "支付" in change and "安全" not in change:
                issues.append({
                    "file": change,
                    "issue": "支付功能缺少安全检查",
                    "severity": "高"
                })
            elif "密码" in change and "加密" not in change:
                issues.append({
                    "file": change,
                    "issue": "密码未加密存储",
                    "severity": "高"
                })
        
        result = {
            "stage": "静态代码分析",
            "status": "通过" if not issues else "失败",
            "issues_found": len(issues),
            "issues": issues,
            "execution_time": 1.0
        }
        
        print(f"静态代码分析完成，发现{len(issues)}个问题")
        return result
    
    def run_unit_tests(self, test_files: List[str]) -> Dict:
        """运行单元测试"""
        print("执行单元测试...")
        time.sleep(2)  # 模拟测试时间
        
        # 模拟测试结果
        total_tests = len(test_files) * 5  # 假设每个文件有5个测试
        passed_tests = int(total_tests * 0.95)  # 95%通过率
        failed_tests = total_tests - passed_tests
        
        result = {
            "stage": "单元测试",
            "status": "通过" if failed_tests == 0 else "失败",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests) * 100,
            "execution_time": 2.0
        }
        
        print(f"单元测试完成，通过率: {result['pass_rate']:.2f}%")
        return result
    
    def run_integration_tests(self, test_modules: List[str]) -> Dict:
        """运行集成测试"""
        print("执行集成测试...")
        time.sleep(3)  # 模拟测试时间
        
        # 模拟测试结果
        total_tests = len(test_modules) * 3  # 假设每个模块有3个集成测试
        passed_tests = int(total_tests * 0.90)  # 90%通过率
        failed_tests = total_tests - passed_tests
        
        result = {
            "stage": "集成测试",
            "status": "通过" if failed_tests == 0 else "失败",
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "pass_rate": (passed_tests / total_tests) * 100,
            "execution_time": 3.0
        }
        
        print(f"集成测试完成，通过率: {result['pass_rate']:.2f}%")
        return result
    
    def run_security_scan(self, application_url: str) -> Dict:
        """运行安全扫描"""
        print(f"执行安全扫描: {application_url}...")
        time.sleep(2)  # 模拟扫描时间
        
        # 模拟扫描结果
        vulnerabilities = []
        if "payment" in application_url.lower():
            vulnerabilities.append({
                "type": "SQL注入",
                "severity": "高",
                "description": "支付页面存在SQL注入漏洞"
            })
        
        if "admin" in application_url.lower():
            vulnerabilities.append({
                "type": "弱密码",
                "severity": "中",
                "description": "管理员页面使用弱密码"
            })
        
        result = {
            "stage": "安全扫描",
            "status": "通过" if not vulnerabilities else "失败",
            "vulnerabilities_found": len(vulnerabilities),
            "vulnerabilities": vulnerabilities,
            "execution_time": 2.0
        }
        
        print(f"安全扫描完成，发现{len(vulnerabilities)}个漏洞")
        return result
    
    def run_performance_tests(self, application_url: str) -> Dict:
        """运行性能测试"""
        print(f"执行性能测试: {application_url}...")
        time.sleep(4)  # 模拟测试时间
        
        # 模拟测试结果
        avg_response_time = random.uniform(0.5, 3.0)  # 随机响应时间
        throughput = random.uniform(100, 500)  # 随机吞吐量
        
        # 判断性能是否达标
        performance_ok = avg_response_time < 2.0 and throughput > 200
        
        result = {
            "stage": "性能测试",
            "status": "通过" if performance_ok else "失败",
            "avg_response_time": avg_response_time,
            "throughput": throughput,
            "target_response_time": 2.0,
            "target_throughput": 200,
            "execution_time": 4.0
        }
        
        print(f"性能测试完成，平均响应时间: {avg_response_time:.2f}秒，吞吐量: {throughput:.2f}请求/秒")
        return result
    
    def run_pipeline(self, code_changes: List[str], test_files: List[str], 
                    test_modules: List[str], application_url: str) -> Dict:
        """运行完整的CI/CD流水线"""
        print(f"\n开始执行{self.project_name}的CI/CD流水线...")
        
        pipeline_start_time = time.time()
        pipeline_status = "通过"
        
        # 运行各个阶段
        results = []
        
        # 静态代码分析
        result = self.run_static_code_analysis(code_changes)
        results.append(result)
        if result["status"] == "失败":
            pipeline_status = "失败"
        
        # 单元测试
        if pipeline_status == "通过":
            result = self.run_unit_tests(test_files)
            results.append(result)
            if result["status"] == "失败":
                pipeline_status = "失败"
        
        # 集成测试
        if pipeline_status == "通过":
            result = self.run_integration_tests(test_modules)
            results.append(result)
            if result["status"] == "失败":
                pipeline_status = "失败"
        
        # 安全扫描
        if pipeline_status == "通过":
            result = self.run_security_scan(application_url)
            results.append(result)
            if result["status"] == "失败":
                pipeline_status = "失败"
        
        # 性能测试
        if pipeline_status == "通过":
            result = self.run_performance_tests(application_url)
            results.append(result)
            if result["status"] == "失败":
                pipeline_status = "失败"
        
        pipeline_end_time = time.time()
        total_execution_time = pipeline_end_time - pipeline_start_time
        
        # 汇总结果
        self.pipeline_results = {
            "pipeline_name": f"{self.project_name} CI/CD流水线",
            "status": pipeline_status,
            "total_execution_time": total_execution_time,
            "stages": results,
            "started_at": datetime.fromtimestamp(pipeline_start_time).strftime("%Y-%m-%d %H:%M:%S"),
            "completed_at": datetime.fromtimestamp(pipeline_end_time).strftime("%Y-%m-%d %H:%M:%S")
        }
        
        print(f"\nCI/CD流水线执行完成，状态: {pipeline_status}")
        return self.pipeline_results
    
    def generate_pipeline_report(self) -> str:
        """生成流水线报告"""
        if not self.pipeline_results:
            return "没有可用的流水线结果"
        
        report = f"""
=== CI/CD流水线报告 ===
流水线名称: {self.pipeline_results['pipeline_name']}
执行状态: {self.pipeline_results['status']}
开始时间: {self.pipeline_results['started_at']}
完成时间: {self.pipeline_results['completed_at']}
总执行时间: {self.pipeline_results['total_execution_time']:.2f}秒

阶段执行结果:
"""
        
        for stage in self.pipeline_results["stages"]:
            report += f"""
{stage['stage']}:
  - 状态: {stage['status']}
  - 执行时间: {stage['execution_time']:.2f}秒
"""
            
            if stage["stage"] == "静态代码分析":
                report += f"  - 发现问题: {stage['issues_found']}个\n"
            elif stage["stage"] in ["单元测试", "集成测试"]:
                report += f"  - 测试通过率: {stage['pass_rate']:.2f}%\n"
            elif stage["stage"] == "安全扫描":
                report += f"  - 发现漏洞: {stage['vulnerabilities_found']}个\n"
            elif stage["stage"] == "性能测试":
                report += f"  - 平均响应时间: {stage['avg_response_time']:.2f}秒\n"
                report += f"  - 吞吐量: {stage['throughput']:.2f}请求/秒\n"
        
        return report
    
    def save_pipeline_results(self, file_path: str):
        """保存流水线结果到文件"""
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.pipeline_results, f, ensure_ascii=False, indent=2)
        logger.info(f"流水线结果已保存到 {file_path}")
    
    def save_pipeline_report(self, file_path: str):
        """保存流水线报告到文件"""
        report = self.generate_pipeline_report()
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(report)
        logger.info(f"流水线报告已保存到 {file_path}")


def demo_continuous_testing():
    """演示持续测试与DevOps集成"""
    print("\n=== 实验4：持续测试与DevOps集成 ===")
    
    # 创建持续测试实例
    ct = ContinuousTesting("电商平台项目")
    
    # 模拟输入数据
    code_changes = ["payment.py", "user_auth.py", "product_catalog.py", "order_processing.py"]
    test_files = ["test_payment.py", "test_user_auth.py", "test_product_catalog.py", "test_order_processing.py"]
    test_modules = ["payment_module", "user_auth_module", "product_catalog_module", "order_processing_module"]
    application_url = "https://staging.example.com/payment"
    
    # 运行CI/CD流水线
    pipeline_results = ct.run_pipeline(code_changes, test_files, test_modules, application_url)
    
    # 生成并打印流水线报告
    report = ct.generate_pipeline_report()
    print(report)
    
    # 保存结果和报告
    ct.save_pipeline_results("output/pipeline_results.json")
    ct.save_pipeline_report("output/pipeline_report.txt")
    
    return ct


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("测试策略与最佳实践 - 示例代码")
    print("=" * 50)
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 运行所有实验
    demo_test_strategy()
    demo_test_plan()
    demo_test_metrics()
    demo_continuous_testing()
    
    print("\n所有实验已完成！")
    print("生成的文件:")
    print("- output/test_strategy.json: 测试策略")
    print("- output/test_plan.json: 测试计划")
    print("- output/test_metrics.json: 测试度量数据")
    print("- output/test_report.txt: 测试报告")
    print("- output/pipeline_results.json: CI/CD流水线结果")
    print("- output/pipeline_report.txt: CI/CD流水线报告")


if __name__ == "__main__":
    main()