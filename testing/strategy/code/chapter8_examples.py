#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第8章：持续集成与持续测试 - 示例代码
本文件包含持续集成与持续测试的示例代码，涵盖基础CI流水线、多环境测试、
持续测试性能优化和CI安全集成等内容。
"""

import os
import sys
import json
import time
import yaml
import shutil
import subprocess
import threading
import concurrent.futures
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from enum import Enum
import logging

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# ============================================================================
# 实验1：构建基础持续集成流水线
# ============================================================================

class StageStatus(Enum):
    """流水线阶段状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class PipelineStage:
    """流水线阶段"""
    name: str
    command: str
    status: StageStatus = StageStatus.PENDING
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    output: str = ""
    error: str = ""
    dependencies: List[str] = field(default_factory=list)
    
    @property
    def duration(self) -> Optional[float]:
        """获取阶段执行时间"""
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return None

@dataclass
class PipelineResult:
    """流水线执行结果"""
    success: bool
    stages: List[PipelineStage]
    start_time: float
    end_time: float
    
    @property
    def duration(self) -> float:
        """获取流水线总执行时间"""
        return self.end_time - self.start_time
    
    @property
    def successful_stages(self) -> List[PipelineStage]:
        """获取成功的阶段"""
        return [stage for stage in self.stages if stage.status == StageStatus.SUCCESS]
    
    @property
    def failed_stages(self) -> List[PipelineStage]:
        """获取失败的阶段"""
        return [stage for stage in self.stages if stage.status == StageStatus.FAILED]

class PipelineExecutor:
    """流水线执行器"""
    
    def __init__(self, workspace_dir: str = "ci_workspace"):
        self.workspace_dir = workspace_dir
        self.stages: List[PipelineStage] = []
        self.ensure_workspace()
    
    def ensure_workspace(self):
        """确保工作目录存在"""
        if not os.path.exists(self.workspace_dir):
            os.makedirs(self.workspace_dir)
    
    def add_stage(self, name: str, command: str, dependencies: List[str] = None):
        """添加流水线阶段"""
        stage = PipelineStage(
            name=name,
            command=command,
            dependencies=dependencies or []
        )
        self.stages.append(stage)
        logger.info(f"添加阶段: {name}")
    
    def execute_stage(self, stage: PipelineStage) -> bool:
        """执行单个阶段"""
        logger.info(f"开始执行阶段: {stage.name}")
        stage.status = StageStatus.RUNNING
        stage.start_time = time.time()
        
        try:
            # 执行命令
            result = subprocess.run(
                stage.command,
                shell=True,
                cwd=self.workspace_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5分钟超时
            )
            
            stage.output = result.stdout
            stage.error = result.stderr
            stage.end_time = time.time()
            
            if result.returncode == 0:
                stage.status = StageStatus.SUCCESS
                logger.info(f"阶段 {stage.name} 执行成功，耗时 {stage.duration:.2f} 秒")
                return True
            else:
                stage.status = StageStatus.FAILED
                logger.error(f"阶段 {stage.name} 执行失败: {stage.error}")
                return False
                
        except subprocess.TimeoutExpired:
            stage.status = StageStatus.FAILED
            stage.error = "执行超时"
            stage.end_time = time.time()
            logger.error(f"阶段 {stage.name} 执行超时")
            return False
        except Exception as e:
            stage.status = StageStatus.FAILED
            stage.error = str(e)
            stage.end_time = time.time()
            logger.error(f"阶段 {stage.name} 执行异常: {e}")
            return False
    
    def execute(self) -> PipelineResult:
        """执行整个流水线"""
        logger.info("开始执行流水线")
        start_time = time.time()
        
        # 按依赖关系排序阶段
        sorted_stages = self._sort_stages_by_dependencies()
        
        # 执行阶段
        for stage in sorted_stages:
            # 检查依赖是否成功
            if not self._check_dependencies(stage):
                stage.status = StageStatus.SKIPPED
                logger.warning(f"阶段 {stage.name} 因依赖失败而跳过")
                continue
            
            success = self.execute_stage(stage)
            if not success:
                # 如果关键阶段失败，停止执行
                logger.error(f"关键阶段 {stage.name} 失败，停止流水线执行")
                break
        
        end_time = time.time()
        
        # 创建结果
        result = PipelineResult(
            success=all(stage.status in [StageStatus.SUCCESS, StageStatus.SKIPPED] for stage in self.stages),
            stages=self.stages,
            start_time=start_time,
            end_time=end_time
        )
        
        logger.info(f"流水线执行完成，总耗时 {result.duration:.2f} 秒")
        return result
    
    def _sort_stages_by_dependencies(self) -> List[PipelineStage]:
        """根据依赖关系对阶段进行拓扑排序"""
        # 创建阶段名称到阶段的映射
        stage_map = {stage.name: stage for stage in self.stages}
        
        # 拓扑排序
        sorted_stages = []
        visited = set()
        
        def visit(stage_name: str):
            if stage_name in visited:
                return
            
            visited.add(stage_name)
            stage = stage_map[stage_name]
            
            # 先访问依赖
            for dep_name in stage.dependencies:
                if dep_name in stage_map:
                    visit(dep_name)
            
            sorted_stages.append(stage)
        
        for stage in self.stages:
            visit(stage.name)
        
        return sorted_stages
    
    def _check_dependencies(self, stage: PipelineStage) -> bool:
        """检查阶段的依赖是否成功"""
        stage_map = {s.name: s for s in self.stages}
        
        for dep_name in stage.dependencies:
            if dep_name in stage_map:
                dep_stage = stage_map[dep_name]
                if dep_stage.status != StageStatus.SUCCESS:
                    return False
        
        return True
    
    def generate_report(self, result: PipelineResult, output_file: str = None) -> str:
        """生成流水线执行报告"""
        report_lines = []
        report_lines.append("# 持续集成流水线执行报告")
        report_lines.append(f"执行时间: {time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(result.start_time))}")
        report_lines.append(f"总耗时: {result.duration:.2f} 秒")
        report_lines.append(f"执行结果: {'成功' if result.success else '失败'}")
        report_lines.append("")
        
        # 阶段执行情况
        report_lines.append("## 阶段执行情况")
        report_lines.append("| 阶段名称 | 状态 | 耗时(秒) |")
        report_lines.append("|---------|------|---------|")
        
        for stage in result.stages:
            duration_str = f"{stage.duration:.2f}" if stage.duration else "N/A"
            report_lines.append(f"| {stage.name} | {stage.status.value} | {duration_str} |")
        
        report_lines.append("")
        
        # 失败阶段详情
        if result.failed_stages:
            report_lines.append("## 失败阶段详情")
            for stage in result.failed_stages:
                report_lines.append(f"### {stage.name}")
                report_lines.append(f"**错误信息**: {stage.error}")
                report_lines.append("")
        
        # 输出详情
        report_lines.append("## 阶段输出详情")
        for stage in result.stages:
            report_lines.append(f"### {stage.name}")
            if stage.output:
                report_lines.append("```\n" + stage.output + "\n```")
            if stage.error:
                report_lines.append("```\n" + stage.error + "\n```")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已保存到: {output_file}")
        
        return report_content

def demo_basic_ci_pipeline():
    """演示基础CI流水线"""
    print("=== 实验1：构建基础持续集成流水线 ===")
    
    # 创建示例项目
    project_dir = "sample_project"
    os.makedirs(project_dir, exist_ok=True)
    
    # 创建示例Python文件
    sample_code = """
def add(a, b):
    return a + b

def multiply(a, b):
    return a * b

def divide(a, b):
    if b == 0:
        raise ValueError("除数不能为零")
    return a / b

if __name__ == "__main__":
    print("Hello, CI Pipeline!")
    print(f"2 + 3 = {add(2, 3)}")
    print(f"2 * 3 = {multiply(2, 3)}")
    print(f"6 / 3 = {divide(6, 3)}")
"""
    
    with open(os.path.join(project_dir, "calculator.py"), 'w', encoding='utf-8') as f:
        f.write(sample_code)
    
    # 创建测试文件
    test_code = """
import unittest
import sys
import os

# 添加项目目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from calculator import add, multiply, divide

class TestCalculator(unittest.TestCase):
    def test_add(self):
        self.assertEqual(add(2, 3), 5)
        self.assertEqual(add(-1, 1), 0)
    
    def test_multiply(self):
        self.assertEqual(multiply(2, 3), 6)
        self.assertEqual(multiply(-2, 3), -6)
    
    def test_divide(self):
        self.assertEqual(divide(6, 3), 2)
        with self.assertRaises(ValueError):
            divide(1, 0)

if __name__ == "__main__":
    unittest.main()
"""
    
    with open(os.path.join(project_dir, "test_calculator.py"), 'w', encoding='utf-8') as f:
        f.write(test_code)
    
    # 创建requirements.txt
    requirements = "# 示例项目依赖\nrequests==2.25.1\n"
    with open(os.path.join(project_dir, "requirements.txt"), 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    # 创建流水线执行器
    executor = PipelineExecutor(project_dir)
    
    # 添加流水线阶段
    executor.add_stage("检出代码", f"echo '检出代码到 {project_dir}'")
    executor.add_stage("安装依赖", f"pip install -r requirements.txt")
    executor.add_stage("代码检查", f"python -m py_compile calculator.py")
    executor.add_stage("运行测试", f"python -m unittest test_calculator.py -v")
    executor.add_stage("打包应用", f"echo '打包应用完成'")
    
    # 执行流水线
    result = executor.execute()
    
    # 生成报告
    report = executor.generate_report(result, "ci_pipeline_report.md")
    
    # 打印摘要
    print(f"\n流水线执行结果: {'成功' if result.success else '失败'}")
    print(f"总耗时: {result.duration:.2f} 秒")
    print(f"成功阶段: {len(result.successful_stages)}")
    print(f"失败阶段: {len(result.failed_stages)}")
    
    # 清理示例文件
    try:
        shutil.rmtree(project_dir)
    except:
        pass
    
    return executor


# ============================================================================
# 实验2：实现多环境持续测试
# ============================================================================

class Environment(Enum):
    """环境枚举"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"

@dataclass
class EnvironmentConfig:
    """环境配置"""
    name: Environment
    host: str
    port: int
    database_url: str
    api_key: str
    features: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name.value,
            "host": self.host,
            "port": self.port,
            "database_url": self.database_url,
            "api_key": self.api_key,
            "features": self.features
        }

class MultiEnvironmentTester:
    """多环境测试器"""
    
    def __init__(self):
        self.environments: Dict[Environment, EnvironmentConfig] = {}
        self.test_results: Dict[Environment, Dict] = {}
    
    def add_environment(self, config: EnvironmentConfig):
        """添加环境配置"""
        self.environments[config.name] = config
        logger.info(f"添加环境: {config.name.value}")
    
    def run_tests(self, environment: Environment, test_suite: str = "all") -> Dict:
        """在指定环境中运行测试"""
        if environment not in self.environments:
            raise ValueError(f"环境 {environment.value} 未配置")
        
        config = self.environments[environment]
        logger.info(f"在环境 {environment.value} 中运行测试: {test_suite}")
        
        # 模拟测试执行
        start_time = time.time()
        
        # 根据环境选择不同的测试策略
        if environment == Environment.DEVELOPMENT:
            # 开发环境：运行单元测试和基本集成测试
            test_results = {
                "unit_tests": self._run_unit_tests(),
                "integration_tests": self._run_basic_integration_tests(config)
            }
        elif environment == Environment.TESTING:
            # 测试环境：运行完整测试套件
            test_results = {
                "unit_tests": self._run_unit_tests(),
                "integration_tests": self._run_full_integration_tests(config),
                "api_tests": self._run_api_tests(config),
                "ui_tests": self._run_ui_tests(config)
            }
        elif environment == Environment.STAGING:
            # 预生产环境：运行完整测试和性能测试
            test_results = {
                "unit_tests": self._run_unit_tests(),
                "integration_tests": self._run_full_integration_tests(config),
                "api_tests": self._run_api_tests(config),
                "ui_tests": self._run_ui_tests(config),
                "performance_tests": self._run_performance_tests(config),
                "security_tests": self._run_security_tests(config)
            }
        elif environment == Environment.PRODUCTION:
            # 生产环境：运行监控测试和冒烟测试
            test_results = {
                "smoke_tests": self._run_smoke_tests(config),
                "monitoring_tests": self._run_monitoring_tests(config)
            }
        
        end_time = time.time()
        
        # 计算总体结果
        total_tests = sum(len(results) for results in test_results.values() if isinstance(results, dict))
        passed_tests = sum(
            sum(1 for result in results.values() if result.get("status") == "passed")
            for results in test_results.values() if isinstance(results, dict)
        )
        
        result = {
            "environment": environment.value,
            "test_suite": test_suite,
            "start_time": start_time,
            "end_time": end_time,
            "duration": end_time - start_time,
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": total_tests - passed_tests,
            "success_rate": passed_tests / total_tests if total_tests > 0 else 0,
            "test_results": test_results
        }
        
        self.test_results[environment] = result
        return result
    
    def run_parallel_tests(self, environments: List[Environment], test_suite: str = "all") -> Dict[Environment, Dict]:
        """在多个环境中并行运行测试"""
        logger.info(f"在多个环境中并行运行测试: {[env.value for env in environments]}")
        
        results = {}
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=len(environments)) as executor:
            # 提交所有测试任务
            future_to_env = {
                executor.submit(self.run_tests, env, test_suite): env
                for env in environments
            }
            
            # 收集结果
            for future in concurrent.futures.as_completed(future_to_env):
                env = future_to_env[future]
                try:
                    result = future.result()
                    results[env] = result
                except Exception as e:
                    logger.error(f"环境 {env.value} 测试执行失败: {e}")
                    results[env] = {
                        "environment": env.value,
                        "error": str(e),
                        "success": False
                    }
        
        return results
    
    def _run_unit_tests(self) -> Dict:
        """运行单元测试"""
        # 模拟单元测试
        time.sleep(1)  # 模拟测试执行时间
        return {
            "test_add": {"status": "passed", "duration": 0.1},
            "test_multiply": {"status": "passed", "duration": 0.1},
            "test_divide": {"status": "passed", "duration": 0.1}
        }
    
    def _run_basic_integration_tests(self, config: EnvironmentConfig) -> Dict:
        """运行基本集成测试"""
        # 模拟基本集成测试
        time.sleep(2)  # 模拟测试执行时间
        return {
            "test_database_connection": {"status": "passed", "duration": 0.5},
            "test_api_connection": {"status": "passed", "duration": 0.3}
        }
    
    def _run_full_integration_tests(self, config: EnvironmentConfig) -> Dict:
        """运行完整集成测试"""
        # 模拟完整集成测试
        time.sleep(3)  # 模拟测试执行时间
        return {
            "test_database_connection": {"status": "passed", "duration": 0.5},
            "test_api_connection": {"status": "passed", "duration": 0.3},
            "test_message_queue": {"status": "passed", "duration": 0.7},
            "test_cache": {"status": "passed", "duration": 0.4}
        }
    
    def _run_api_tests(self, config: EnvironmentConfig) -> Dict:
        """运行API测试"""
        # 模拟API测试
        time.sleep(2)  # 模拟测试执行时间
        return {
            "test_get_users": {"status": "passed", "duration": 0.2},
            "test_create_user": {"status": "passed", "duration": 0.3},
            "test_update_user": {"status": "passed", "duration": 0.2},
            "test_delete_user": {"status": "passed", "duration": 0.2}
        }
    
    def _run_ui_tests(self, config: EnvironmentConfig) -> Dict:
        """运行UI测试"""
        # 模拟UI测试
        time.sleep(5)  # 模拟测试执行时间
        return {
            "test_login_page": {"status": "passed", "duration": 1.0},
            "test_user_profile": {"status": "passed", "duration": 1.5},
            "test_user_dashboard": {"status": "passed", "duration": 2.0}
        }
    
    def _run_performance_tests(self, config: EnvironmentConfig) -> Dict:
        """运行性能测试"""
        # 模拟性能测试
        time.sleep(10)  # 模拟测试执行时间
        return {
            "test_load_time": {"status": "passed", "duration": 3.0, "value": "1.2s"},
            "test_concurrent_users": {"status": "passed", "duration": 4.0, "value": "1000"},
            "test_response_time": {"status": "passed", "duration": 3.0, "value": "200ms"}
        }
    
    def _run_security_tests(self, config: EnvironmentConfig) -> Dict:
        """运行安全测试"""
        # 模拟安全测试
        time.sleep(3)  # 模拟测试执行时间
        return {
            "test_sql_injection": {"status": "passed", "duration": 1.0},
            "test_xss": {"status": "passed", "duration": 1.0},
            "test_authentication": {"status": "passed", "duration": 1.0}
        }
    
    def _run_smoke_tests(self, config: EnvironmentConfig) -> Dict:
        """运行冒烟测试"""
        # 模拟冒烟测试
        time.sleep(1)  # 模拟测试执行时间
        return {
            "test_homepage": {"status": "passed", "duration": 0.2},
            "test_login": {"status": "passed", "duration": 0.3},
            "test_basic_functionality": {"status": "passed", "duration": 0.5}
        }
    
    def _run_monitoring_tests(self, config: EnvironmentConfig) -> Dict:
        """运行监控测试"""
        # 模拟监控测试
        time.sleep(1)  # 模拟测试执行时间
        return {
            "test_server_health": {"status": "passed", "duration": 0.2},
            "test_database_health": {"status": "passed", "duration": 0.3},
            "test_api_health": {"status": "passed", "duration": 0.2}
        }
    
    def generate_environment_report(self, results: Dict[Environment, Dict], output_file: str = None) -> str:
        """生成多环境测试报告"""
        report_lines = []
        report_lines.append("# 多环境持续测试报告")
        report_lines.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 环境测试概览
        report_lines.append("## 环境测试概览")
        report_lines.append("| 环境 | 测试套件 | 总测试数 | 通过数 | 失败数 | 成功率 | 耗时(秒) |")
        report_lines.append("|------|---------|---------|--------|--------|--------|----------|")
        
        for env, result in results.items():
            if "error" in result:
                report_lines.append(f"| {env.value} | - | - | - | - | - | - | 错误: {result['error']} |")
            else:
                report_lines.append(
                    f"| {env.value} | {result['test_suite']} | {result['total_tests']} | "
                    f"{result['passed_tests']} | {result['failed_tests']} | "
                    f"{result['success_rate']:.2%} | {result['duration']:.2f} |"
                )
        
        report_lines.append("")
        
        # 详细测试结果
        for env, result in results.items():
            if "error" in result:
                continue
                
            report_lines.append(f"## {env.value} 环境详细结果")
            
            for test_type, tests in result["test_results"].items():
                report_lines.append(f"### {test_type}")
                report_lines.append("| 测试名称 | 状态 | 耗时(秒) |")
                report_lines.append("|---------|------|----------|")
                
                for test_name, test_result in tests.items():
                    status = test_result["status"]
                    duration = test_result.get("duration", 0)
                    value = test_result.get("value", "")
                    
                    if value:
                        report_lines.append(f"| {test_name} | {status} | {duration} | {value} |")
                    else:
                        report_lines.append(f"| {test_name} | {status} | {duration} | |")
                
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已保存到: {output_file}")
        
        return report_content

def demo_multi_environment_testing():
    """演示多环境持续测试"""
    print("\n=== 实验2：实现多环境持续测试 ===")
    
    # 创建多环境测试器
    tester = MultiEnvironmentTester()
    
    # 添加环境配置
    dev_config = EnvironmentConfig(
        name=Environment.DEVELOPMENT,
        host="dev.example.com",
        port=8080,
        database_url="sqlite:///dev.db",
        api_key="dev-api-key",
        features=["debug", "verbose_logging"]
    )
    tester.add_environment(dev_config)
    
    test_config = EnvironmentConfig(
        name=Environment.TESTING,
        host="test.example.com",
        port=8080,
        database_url="postgresql://user:pass@test.example.com/testdb",
        api_key="test-api-key",
        features=["test_data", "mock_services"]
    )
    tester.add_environment(test_config)
    
    staging_config = EnvironmentConfig(
        name=Environment.STAGING,
        host="staging.example.com",
        port=443,
        database_url="postgresql://user:pass@staging.example.com/stagingdb",
        api_key="staging-api-key",
        features=["production_like", "real_data"]
    )
    tester.add_environment(staging_config)
    
    # 在开发环境运行测试
    dev_result = tester.run_tests(Environment.DEVELOPMENT)
    print(f"开发环境测试完成，成功率: {dev_result['success_rate']:.2%}")
    
    # 在测试环境运行测试
    test_result = tester.run_tests(Environment.TESTING)
    print(f"测试环境测试完成，成功率: {test_result['success_rate']:.2%}")
    
    # 在预生产环境运行测试
    staging_result = tester.run_tests(Environment.STAGING)
    print(f"预生产环境测试完成，成功率: {staging_result['success_rate']:.2%}")
    
    # 并行运行多个环境的测试
    parallel_results = tester.run_parallel_tests([
        Environment.DEVELOPMENT, 
        Environment.TESTING, 
        Environment.STAGING
    ])
    
    # 生成报告
    report = tester.generate_environment_report(parallel_results, "multi_environment_test_report.md")
    
    # 打印摘要
    print("\n多环境测试摘要:")
    for env, result in parallel_results.items():
        if "error" in result:
            print(f"- {env.value}: 测试失败 - {result['error']}")
        else:
            print(f"- {env.value}: {result['passed_tests']}/{result['total_tests']} 测试通过 ({result['success_rate']:.2%})")
    
    return tester


# ============================================================================
# 实验3：持续测试性能优化
# ============================================================================

class TestOptimizer:
    """测试优化器"""
    
    def __init__(self):
        self.test_history: List[Dict] = []
        self.code_change_history: List[Dict] = []
    
    def record_test_execution(self, test_name: str, duration: float, success: bool, 
                             affected_files: List[str] = None):
        """记录测试执行结果"""
        record = {
            "test_name": test_name,
            "duration": duration,
            "success": success,
            "timestamp": time.time(),
            "affected_files": affected_files or []
        }
        self.test_history.append(record)
    
    def record_code_change(self, changed_files: List[str], change_type: str = "feature"):
        """记录代码变更"""
        record = {
            "changed_files": changed_files,
            "change_type": change_type,
            "timestamp": time.time()
        }
        self.code_change_history.append(record)
    
    def select_relevant_tests(self, changed_files: List[str], max_tests: int = None) -> List[str]:
        """基于代码变更选择相关测试"""
        # 统计每个测试与变更文件的关联度
        test_scores = {}
        
        for test_record in self.test_history:
            test_name = test_record["test_name"]
            test_files = test_record["affected_files"]
            
            # 计算测试与变更文件的关联度
            score = 0
            for changed_file in changed_files:
                for test_file in test_files:
                    if changed_file == test_file:
                        score += 10  # 完全匹配
                    elif self._files_related(changed_file, test_file):
                        score += 5  # 相关文件
            
            # 考虑测试的历史执行时间和成功率
            if test_record["success"]:
                score += 2  # 成功的测试优先级更高
            
            # 考虑测试的最近执行时间
            time_factor = 1.0 / (1.0 + (time.time() - test_record["timestamp"]) / 86400)  # 天数
            score *= time_factor
            
            test_scores[test_name] = test_scores.get(test_name, 0) + score
        
        # 按分数排序
        sorted_tests = sorted(test_scores.items(), key=lambda x: x[1], reverse=True)
        
        # 返回前N个测试
        if max_tests:
            return [test_name for test_name, _ in sorted_tests[:max_tests]]
        else:
            return [test_name for test_name, _ in sorted_tests]
    
    def optimize_test_order(self, tests: List[str]) -> List[str]:
        """优化测试执行顺序"""
        # 统计每个测试的平均执行时间和失败率
        test_stats = {}
        
        for test_record in self.test_history:
            test_name = test_record["test_name"]
            if test_name not in test_stats:
                test_stats[test_name] = {
                    "total_duration": 0,
                    "execution_count": 0,
                    "failure_count": 0
                }
            
            test_stats[test_name]["total_duration"] += test_record["duration"]
            test_stats[test_stats]["execution_count"] += 1
            
            if not test_record["success"]:
                test_stats[test_name]["failure_count"] += 1
        
        # 计算优先级分数
        test_priorities = {}
        for test_name in tests:
            if test_name in test_stats:
                stats = test_stats[test_name]
                avg_duration = stats["total_duration"] / stats["execution_count"]
                failure_rate = stats["failure_count"] / stats["execution_count"]
                
                # 快速失败的测试优先级更高
                priority = failure_rate * 100 - avg_duration
                test_priorities[test_name] = priority
            else:
                # 没有历史记录的测试优先级中等
                test_priorities[test_name] = 50
        
        # 按优先级排序
        sorted_tests = sorted(tests, key=lambda x: test_priorities.get(x, 50), reverse=True)
        return sorted_tests
    
    def parallelize_tests(self, tests: List[str], max_workers: int = 4) -> List[List[str]]:
        """将测试分组以便并行执行"""
        # 统计每个测试的平均执行时间
        test_durations = {}
        
        for test_record in self.test_history:
            test_name = test_record["test_name"]
            if test_name not in test_durations:
                test_durations[test_name] = []
            test_durations[test_name].append(test_record["duration"])
        
        # 计算平均执行时间
        avg_durations = {}
        for test_name, durations in test_durations.items():
            avg_durations[test_name] = sum(durations) / len(durations)
        
        # 对于没有历史记录的测试，假设平均执行时间为1秒
        for test_name in tests:
            if test_name not in avg_durations:
                avg_durations[test_name] = 1.0
        
        # 使用贪心算法将测试分组，使每组总执行时间尽可能相等
        test_groups = [[] for _ in range(max_workers)]
        group_durations = [0.0] * max_workers
        
        # 按执行时间降序排序测试
        sorted_tests = sorted(tests, key=lambda x: avg_durations.get(x, 1.0), reverse=True)
        
        for test_name in sorted_tests:
            # 找到当前总执行时间最短的组
            min_group_index = min(range(max_workers), key=lambda i: group_durations[i])
            
            # 将测试添加到该组
            test_groups[min_group_index].append(test_name)
            group_durations[min_group_index] += avg_durations[test_name]
        
        return test_groups
    
    def _files_related(self, file1: str, file2: str) -> bool:
        """判断两个文件是否相关"""
        # 简单的相关性判断：同目录或文件名相似
        dir1 = os.path.dirname(file1)
        dir2 = os.path.dirname(file2)
        
        if dir1 == dir2:
            return True
        
        # 检查文件名是否相似
        name1 = os.path.splitext(os.path.basename(file1))[0]
        name2 = os.path.splitext(os.path.basename(file2))[0]
        
        # 如果一个文件名是另一个文件名的前缀，则认为相关
        if name1.startswith(name2) or name2.startswith(name1):
            return True
        
        return False
    
    def generate_optimization_report(self, original_tests: List[str], 
                                  optimized_tests: List[str], 
                                  test_groups: List[List[str]] = None,
                                  output_file: str = None) -> str:
        """生成测试优化报告"""
        report_lines = []
        report_lines.append("# 测试优化报告")
        report_lines.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 优化前后对比
        report_lines.append("## 优化前后对比")
        report_lines.append(f"- 原始测试数量: {len(original_tests)}")
        report_lines.append(f"- 优化后测试数量: {len(optimized_tests)}")
        report_lines.append(f"- 减少测试数量: {len(original_tests) - len(optimized_tests)}")
        report_lines.append(f"- 优化比例: {(len(original_tests) - len(optimized_tests)) / len(original_tests):.2%}")
        report_lines.append("")
        
        # 测试执行顺序优化
        report_lines.append("## 测试执行顺序优化")
        report_lines.append("| 顺序 | 测试名称 | 优先级分数 |")
        report_lines.append("|------|----------|------------|")
        
        for i, test_name in enumerate(optimized_tests[:10]):  # 只显示前10个
            # 计算优先级分数
            priority = 50  # 默认分数
            
            for test_record in self.test_history:
                if test_record["test_name"] == test_name:
                    if test_record["success"]:
                        priority += 2
                    break
            
            report_lines.append(f"| {i+1} | {test_name} | {priority} |")
        
        report_lines.append("")
        
        # 并行测试分组
        if test_groups:
            report_lines.append("## 并行测试分组")
            report_lines.append(f"最大并行数: {len(test_groups)}")
            report_lines.append("")
            
            for i, group in enumerate(test_groups):
                report_lines.append(f"### 组 {i+1}")
                report_lines.append(f"测试数量: {len(group)}")
                
                # 估算组执行时间
                group_duration = 0
                for test_name in group:
                    for test_record in self.test_history:
                        if test_record["test_name"] == test_name:
                            group_duration += test_record["duration"]
                            break
                
                report_lines.append(f"预估执行时间: {group_duration:.2f} 秒")
                report_lines.append("测试列表:")
                
                for test_name in group:
                    report_lines.append(f"- {test_name}")
                
                report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已保存到: {output_file}")
        
        return report_content

def demo_test_performance_optimization():
    """演示持续测试性能优化"""
    print("\n=== 实验3：持续测试性能优化 ===")
    
    # 创建测试优化器
    optimizer = TestOptimizer()
    
    # 模拟历史测试数据
    test_names = [
        "test_user_login", "test_user_registration", "test_user_profile_update",
        "test_product_search", "test_product_detail", "test_product_add_to_cart",
        "test_order_creation", "test_order_payment", "test_order_history",
        "test_admin_dashboard", "test_admin_user_management", "test_admin_product_management",
        "test_api_authentication", "test_api_user_endpoints", "test_api_product_endpoints",
        "test_ui_navigation", "test_ui_forms", "test_ui_responsive_design",
        "test_database_connection", "test_database_queries", "test_database_transactions",
        "test_performance_load", "test_performance_stress", "test_security_authentication"
    ]
    
    # 模拟测试执行历史
    import random
    for test_name in test_names:
        for _ in range(random.randint(5, 20)):  # 每个测试执行5-20次
            duration = random.uniform(0.5, 10.0)  # 执行时间0.5-10秒
            success = random.random() > 0.1  # 90%成功率
            
            # 模拟受影响的文件
            affected_files = []
            if "user" in test_name:
                affected_files.append("models/user.py")
                affected_files.append("views/user_views.py")
            if "product" in test_name:
                affected_files.append("models/product.py")
                affected_files.append("views/product_views.py")
            if "order" in test_name:
                affected_files.append("models/order.py")
                affected_files.append("views/order_views.py")
            if "admin" in test_name:
                affected_files.append("views/admin_views.py")
            if "api" in test_name:
                affected_files.append("api/endpoints.py")
            if "ui" in test_name:
                affected_files.append("static/js/app.js")
                affected_files.append("templates/base.html")
            if "database" in test_name:
                affected_files.append("models/base.py")
            if "performance" in test_name:
                affected_files.append("utils/performance.py")
            if "security" in test_name:
                affected_files.append("utils/security.py")
            
            optimizer.record_test_execution(test_name, duration, success, affected_files)
    
    # 模拟代码变更
    changed_files = [
        "models/user.py",
        "views/user_views.py",
        "static/js/app.js"
    ]
    optimizer.record_code_change(changed_files)
    
    # 选择相关测试
    relevant_tests = optimizer.select_relevant_tests(changed_files, max_tests=15)
    print(f"从 {len(test_names)} 个测试中选择了 {len(relevant_tests)} 个相关测试")
    
    # 优化测试执行顺序
    optimized_tests = optimizer.optimize_test_order(relevant_tests)
    print(f"优化了测试执行顺序")
    
    # 并行化测试
    test_groups = optimizer.parallelize_tests(optimized_tests, max_workers=4)
    print(f"将测试分为 {len(test_groups)} 组以便并行执行")
    
    # 生成优化报告
    report = optimizer.generate_optimization_report(
        test_names, 
        optimized_tests, 
        test_groups,
        "test_optimization_report.md"
    )
    
    # 打印摘要
    print("\n测试优化摘要:")
    print(f"- 原始测试数量: {len(test_names)}")
    print(f"- 优化后测试数量: {len(optimized_tests)}")
    print(f"- 减少比例: {(len(test_names) - len(optimized_tests)) / len(test_names):.2%}")
    print(f"- 并行组数: {len(test_groups)}")
    
    # 估算执行时间
    original_time = sum(random.uniform(0.5, 10.0) for _ in test_names)
    optimized_time = max(
        sum(random.uniform(0.5, 10.0) for _ in group) 
        for group in test_groups
    )
    
    print(f"- 预估原始执行时间: {original_time:.2f} 秒")
    print(f"- 预估优化后执行时间: {optimized_time:.2f} 秒")
    print(f"- 执行时间减少: {(original_time - optimized_time) / original_time:.2%}")
    
    return optimizer


# ============================================================================
# 实验4：持续集成安全集成
# ============================================================================

class SecurityScanner:
    """安全扫描器"""
    
    def __init__(self):
        self.scan_results = []
    
    def run_static_security_scan(self, project_path: str) -> Dict:
        """运行静态安全扫描"""
        logger.info(f"开始静态安全扫描: {project_path}")
        
        # 模拟静态安全扫描
        time.sleep(3)
        
        # 模拟发现的安全问题
        vulnerabilities = [
            {
                "type": "SQL注入",
                "severity": "高",
                "file": "models/user.py",
                "line": 25,
                "description": "直接拼接SQL查询，可能导致SQL注入攻击",
                "recommendation": "使用参数化查询或ORM框架"
            },
            {
                "type": "硬编码密钥",
                "severity": "中",
                "file": "config/settings.py",
                "line": 10,
                "description": "代码中硬编码了API密钥",
                "recommendation": "使用环境变量或配置文件存储敏感信息"
            },
            {
                "type": "弱加密算法",
                "severity": "中",
                "file": "utils/crypto.py",
                "line": 15,
                "description": "使用了MD5哈希算法",
                "recommendation": "使用更安全的哈希算法，如SHA-256或bcrypt"
            }
        ]
        
        result = {
            "scan_type": "静态安全扫描",
            "target": project_path,
            "start_time": time.time() - 3,
            "end_time": time.time(),
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "high_severity": len([v for v in vulnerabilities if v["severity"] == "高"]),
            "medium_severity": len([v for v in vulnerabilities if v["severity"] == "中"]),
            "low_severity": len([v for v in vulnerabilities if v["severity"] == "低"])
        }
        
        self.scan_results.append(result)
        return result
    
    def run_dependency_security_scan(self, requirements_file: str) -> Dict:
        """运行依赖安全扫描"""
        logger.info(f"开始依赖安全扫描: {requirements_file}")
        
        # 模拟依赖安全扫描
        time.sleep(2)
        
        # 模拟发现的依赖安全问题
        vulnerabilities = [
            {
                "package": "requests",
                "version": "2.20.0",
                "cve": "CVE-2019-11326",
                "severity": "高",
                "description": "请求库中存在重定向漏洞",
                "recommendation": "升级到2.21.0或更高版本"
            },
            {
                "package": "urllib3",
                "version": "1.24.2",
                "cve": "CVE-2019-11324",
                "severity": "中",
                "description": "URL解析器中存在漏洞",
                "recommendation": "升级到1.25.3或更高版本"
            }
        ]
        
        result = {
            "scan_type": "依赖安全扫描",
            "target": requirements_file,
            "start_time": time.time() - 2,
            "end_time": time.time(),
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "high_severity": len([v for v in vulnerabilities if v["severity"] == "高"]),
            "medium_severity": len([v for v in vulnerabilities if v["severity"] == "中"]),
            "low_severity": len([v for v in vulnerabilities if v["severity"] == "低"])
        }
        
        self.scan_results.append(result)
        return result
    
    def run_container_security_scan(self, image_name: str) -> Dict:
        """运行容器安全扫描"""
        logger.info(f"开始容器安全扫描: {image_name}")
        
        # 模拟容器安全扫描
        time.sleep(4)
        
        # 模拟发现的容器安全问题
        vulnerabilities = [
            {
                "package": "openssl",
                "version": "1.1.1",
                "cve": "CVE-2021-3711",
                "severity": "高",
                "description": "OpenSSL中存在缓冲区溢出漏洞",
                "recommendation": "升级到OpenSSL 1.1.1l或更高版本"
            },
            {
                "package": "curl",
                "version": "7.68.0",
                "cve": "CVE-2021-22876",
                "severity": "中",
                "description": "cURL中存在信息泄露漏洞",
                "recommendation": "升级到cURL 7.75.0或更高版本"
            },
            {
                "package": "nginx",
                "version": "1.18.0",
                "cve": "CVE-2021-23017",
                "severity": "中",
                "description": "nginx中存在内存泄露漏洞",
                "recommendation": "升级到nginx 1.20.1或更高版本"
            }
        ]
        
        result = {
            "scan_type": "容器安全扫描",
            "target": image_name,
            "start_time": time.time() - 4,
            "end_time": time.time(),
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "high_severity": len([v for v in vulnerabilities if v["severity"] == "高"]),
            "medium_severity": len([v for v in vulnerabilities if v["severity"] == "中"]),
            "low_severity": len([v for v in vulnerabilities if v["severity"] == "低"])
        }
        
        self.scan_results.append(result)
        return result
    
    def run_dynamic_security_scan(self, target_url: str) -> Dict:
        """运行动态安全扫描"""
        logger.info(f"开始动态安全扫描: {target_url}")
        
        # 模拟动态安全扫描
        time.sleep(5)
        
        # 模拟发现的动态安全问题
        vulnerabilities = [
            {
                "type": "XSS",
                "severity": "高",
                "url": f"{target_url}/search",
                "parameter": "q",
                "payload": "<script>alert('XSS')</script>",
                "description": "搜索功能中存在跨站脚本漏洞",
                "recommendation": "对用户输入进行适当的HTML编码"
            },
            {
                "type": "CSRF",
                "severity": "中",
                "url": f"{target_url}/user/profile",
                "description": "用户资料更新功能缺少CSRF保护",
                "recommendation": "实施CSRF令牌验证"
            }
        ]
        
        result = {
            "scan_type": "动态安全扫描",
            "target": target_url,
            "start_time": time.time() - 5,
            "end_time": time.time(),
            "vulnerabilities": vulnerabilities,
            "total_vulnerabilities": len(vulnerabilities),
            "high_severity": len([v for v in vulnerabilities if v["severity"] == "高"]),
            "medium_severity": len([v for v in vulnerabilities if v["severity"] == "中"]),
            "low_severity": len([v for v in vulnerabilities if v["severity"] == "低"])
        }
        
        self.scan_results.append(result)
        return result
    
    def check_security_gate(self, max_high: int = 0, max_medium: int = 5, max_low: int = 10) -> bool:
        """检查安全门禁"""
        total_high = sum(result["high_severity"] for result in self.scan_results)
        total_medium = sum(result["medium_severity"] for result in self.scan_results)
        total_low = sum(result["low_severity"] for result in self.scan_results)
        
        passed = (
            total_high <= max_high and
            total_medium <= max_medium and
            total_low <= max_low
        )
        
        logger.info(f"安全门禁检查:")
        logger.info(f"- 高危漏洞: {total_high} (阈值: {max_high})")
        logger.info(f"- 中危漏洞: {total_medium} (阈值: {max_medium})")
        logger.info(f"- 低危漏洞: {total_low} (阈值: {max_low})")
        logger.info(f"- 结果: {'通过' if passed else '失败'}")
        
        return passed
    
    def generate_security_report(self, output_file: str = None) -> str:
        """生成安全扫描报告"""
        report_lines = []
        report_lines.append("# 安全扫描报告")
        report_lines.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 扫描概览
        total_vulnerabilities = sum(result["total_vulnerabilities"] for result in self.scan_results)
        total_high = sum(result["high_severity"] for result in self.scan_results)
        total_medium = sum(result["medium_severity"] for result in self.scan_results)
        total_low = sum(result["low_severity"] for result in self.scan_results)
        
        report_lines.append("## 扫描概览")
        report_lines.append(f"- 总漏洞数: {total_vulnerabilities}")
        report_lines.append(f"- 高危漏洞: {total_high}")
        report_lines.append(f"- 中危漏洞: {total_medium}")
        report_lines.append(f"- 低危漏洞: {total_low}")
        report_lines.append("")
        
        # 各扫描类型结果
        for result in self.scan_results:
            report_lines.append(f"## {result['scan_type']}")
            report_lines.append(f"目标: {result['target']}")
            report_lines.append(f"扫描时间: {result['end_time'] - result['start_time']:.2f} 秒")
            report_lines.append(f"漏洞总数: {result['total_vulnerabilities']}")
            report_lines.append("")
            
            if result["vulnerabilities"]:
                report_lines.append("### 漏洞详情")
                report_lines.append("| 类型 | 严重程度 | 位置 | 描述 | 修复建议 |")
                report_lines.append("|------|----------|------|------|----------|")
                
                for vuln in result["vulnerabilities"]:
                    if "file" in vuln:
                        location = f"{vuln['file']}:{vuln.get('line', 'N/A')}"
                    elif "url" in vuln:
                        location = vuln["url"]
                    elif "package" in vuln:
                        location = f"{vuln['package']}:{vuln.get('version', 'N/A')}"
                    else:
                        location = "N/A"
                    
                    report_lines.append(
                        f"| {vuln.get('type', vuln.get('package', 'N/A'))} | {vuln['severity']} | "
                        f"{location} | {vuln['description']} | {vuln['recommendation']} |"
                    )
                
                report_lines.append("")
        
        # 安全门禁结果
        report_lines.append("## 安全门禁")
        passed = self.check_security_gate()
        report_lines.append(f"结果: {'通过' if passed else '失败'}")
        report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"报告已保存到: {output_file}")
        
        return report_content

def demo_ci_security_integration():
    """演示持续集成安全集成"""
    print("\n=== 实验4：持续集成安全集成 ===")
    
    # 创建示例项目
    project_dir = "secure_project"
    os.makedirs(project_dir, exist_ok=True)
    
    # 创建示例代码文件
    vulnerable_code = """
import sqlite3
import hashlib

def get_user(user_id):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # SQL注入漏洞
    query = "SELECT * FROM users WHERE id = " + user_id
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def hash_password(password):
    # 弱加密算法
    return hashlib.md5(password.encode()).hexdigest()
"""
    
    with open(os.path.join(project_dir, "models/user.py"), 'w', encoding='utf-8') as f:
        f.write(vulnerable_code)
    
    # 创建配置文件
    config_code = """
# 硬编码密钥
API_KEY = "sk-1234567890abcdef"
DATABASE_URL = "sqlite:///production.db"
"""
    
    with open(os.path.join(project_dir, "config/settings.py"), 'w', encoding='utf-8') as f:
        f.write(config_code)
    
    # 创建加密工具文件
    crypto_code = """
import hashlib

def encrypt(data):
    # 弱加密算法
    return hashlib.md5(data.encode()).hexdigest()
"""
    
    with open(os.path.join(project_dir, "utils/crypto.py"), 'w', encoding='utf-8') as f:
        f.write(crypto_code)
    
    # 创建依赖文件
    requirements = "requests==2.20.0\nurllib3==1.24.2\n"
    with open(os.path.join(project_dir, "requirements.txt"), 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    # 创建安全扫描器
    scanner = SecurityScanner()
    
    # 运行各种安全扫描
    scanner.run_static_security_scan(project_dir)
    scanner.run_dependency_security_scan(os.path.join(project_dir, "requirements.txt"))
    scanner.run_container_security_scan("myapp:latest")
    scanner.run_dynamic_security_scan("https://myapp.example.com")
    
    # 检查安全门禁
    passed = scanner.check_security_gate(max_high=1, max_medium=5, max_low=10)
    
    # 生成安全报告
    report = scanner.generate_security_report("security_scan_report.md")
    
    # 打印摘要
    total_vulnerabilities = sum(result["total_vulnerabilities"] for result in scanner.scan_results)
    total_high = sum(result["high_severity"] for result in scanner.scan_results)
    total_medium = sum(result["medium_severity"] for result in scanner.scan_results)
    total_low = sum(result["low_severity"] for result in scanner.scan_results)
    
    print(f"\n安全扫描摘要:")
    print(f"- 总漏洞数: {total_vulnerabilities}")
    print(f"- 高危漏洞: {total_high}")
    print(f"- 中危漏洞: {total_medium}")
    print(f"- 低危漏洞: {total_low}")
    print(f"- 安全门禁: {'通过' if passed else '失败'}")
    
    # 清理示例文件
    try:
        shutil.rmtree(project_dir)
    except:
        pass
    
    return scanner


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("持续集成与持续测试 - 示例代码")
    print("=" * 50)
    
    # 运行所有实验
    demo_basic_ci_pipeline()
    demo_multi_environment_testing()
    demo_test_performance_optimization()
    demo_ci_security_integration()
    
    print("\n所有实验已完成！")
    print("\n持续集成与持续测试核心要点:")
    print("1. 设计高效的流水线，提供快速反馈")
    print("2. 实施多环境测试策略，确保质量")
    print("3. 优化测试性能，提高执行效率")
    print("4. 集成安全扫描，实现安全左移")
    print("5. 设置合理的安全门禁，平衡安全与效率")
    print("6. 持续监控和改进CI/CT流程")
    print("7. 培养团队DevOps文化，促进协作")


if __name__ == "__main__":
    main()