#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第4章：自动化测试框架 - 示例代码
本文件包含自动化测试框架的示例代码，涵盖框架设计、页面对象模式、数据驱动测试、
报告生成等内容。
"""

import os
import sys
import unittest
import time
import json
import csv
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional
from abc import ABC, abstractmethod
import threading
import concurrent.futures
from dataclasses import dataclass

# 模拟Selenium WebDriver（实际使用时需要安装selenium）
class MockWebDriver:
    """模拟WebDriver类，用于演示"""
    def __init__(self, browser="chrome"):
        self.browser = browser
        self.current_url = ""
        self.page_source = ""
        self.title = ""
        self.elements = {}
    
    def get(self, url):
        self.current_url = url
        # 模拟页面加载
        if "login" in url:
            self.page_source = "<html><body><form><input id='username' type='text'><input id='password' type='password'><button id='login-btn'>Login</button></form></body></html>"
            self.title = "Login Page"
        elif "dashboard" in url:
            self.page_source = "<html><body><h1>Welcome to Dashboard</h1><div id='welcome-msg'>Welcome, User!</div></body></html>"
            self.title = "Dashboard"
    
    def find_element(self, by, value):
        element_id = f"{by}_{value}"
        if element_id not in self.elements:
            self.elements[element_id] = MockWebElement(value)
        return self.elements[element_id]
    
    def find_elements(self, by, value):
        return [self.find_element(by, value)]
    
    def quit(self):
        pass

class MockWebElement:
    """模拟WebElement类，用于演示"""
    def __init__(self, identifier):
        self.identifier = identifier
        self.text = ""
        self.value = ""
    
    def send_keys(self, text):
        self.value = text
    
    def click(self):
        pass
    
    def clear(self):
        self.value = ""
    
    def get_attribute(self, attr):
        if attr == "value":
            return self.value
        return ""

# 模拟By类
class By:
    ID = "id"
    NAME = "name"
    CLASS_NAME = "class name"
    TAG_NAME = "tag name"
    CSS_SELECTOR = "css selector"
    XPATH = "xpath"

# ============================================================================
# 实验1：构建基础自动化测试框架
# ============================================================================

class ConfigManager:
    """配置管理组件"""
    
    def __init__(self, config_file=None):
        self.config_file = config_file or os.path.join(os.path.dirname(__file__), "config.json")
        self.config = self._load_config()
    
    def _load_config(self) -> Dict[str, Any]:
        """加载配置文件"""
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return self._get_default_config()
        except json.JSONDecodeError:
            raise ValueError(f"Invalid JSON in config file: {self.config_file}")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "browser": "chrome",
            "headless": False,
            "timeout": 10,
            "base_url": "https://example.com",
            "log_level": "INFO",
            "report_format": "html",
            "parallel_execution": False,
            "max_workers": 2
        }
    
    def get(self, key: str, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any):
        """设置配置值"""
        self.config[key] = value
    
    def save(self):
        """保存配置到文件"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)


class LogManager:
    """日志管理组件"""
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(LogManager, cls).__new__(cls)
                    cls._instance._initialize()
        return cls._instance
    
    def _initialize(self):
        """初始化日志系统"""
        self.logger = logging.getLogger("TestFramework")
        self.logger.setLevel(logging.INFO)
        
        # 创建日志目录
        log_dir = os.path.join(os.path.dirname(__file__), "logs")
        os.makedirs(log_dir, exist_ok=True)
        
        # 清除现有处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 创建文件处理器
        log_file = os.path.join(log_dir, f"test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        self.logger.info(message)
    
    def error(self, message):
        self.logger.error(message)
    
    def warning(self, message):
        self.logger.warning(message)
    
    def debug(self, message):
        self.logger.debug(message)


class ReportManager:
    """报告生成组件"""
    
    def __init__(self, report_dir=None):
        self.report_dir = report_dir or os.path.join(os.path.dirname(__file__), "reports")
        os.makedirs(self.report_dir, exist_ok=True)
        self.test_results = []
        self.start_time = datetime.now()
    
    def add_test_result(self, test_name: str, status: str, duration: float, 
                       error_msg=None, screenshot=None):
        """添加测试结果"""
        result = {
            "test_name": test_name,
            "status": status,  # "passed", "failed", "skipped"
            "duration": duration,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "error_message": error_msg,
            "screenshot": screenshot
        }
        self.test_results.append(result)
    
    def generate_summary(self) -> Dict[str, Any]:
        """生成测试摘要"""
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results if r["status"] == "passed")
        failed_tests = sum(1 for r in self.test_results if r["status"] == "failed")
        skipped_tests = sum(1 for r in self.test_results if r["status"] == "skipped")
        total_duration = sum(r["duration"] for r in self.test_results)
        
        return {
            "total_tests": total_tests,
            "passed_tests": passed_tests,
            "failed_tests": failed_tests,
            "skipped_tests": skipped_tests,
            "pass_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            "total_duration": total_duration,
            "start_time": self.start_time.strftime("%Y-%m-%d %H:%M:%S"),
            "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    
    def generate_html_report(self) -> str:
        """生成HTML报告"""
        summary = self.generate_summary()
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试报告</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; margin-bottom: 20px; }}
                .test-result {{ margin-bottom: 10px; padding: 10px; border-radius: 5px; }}
                .passed {{ background-color: #dff0d8; }}
                .failed {{ background-color: #f2dede; }}
                .skipped {{ background-color: #d9edf7; }}
                table {{ border-collapse: collapse; width: 100%; }}
                th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                th {{ background-color: #f2f2f2; }}
            </style>
        </head>
        <body>
            <h1>自动化测试报告</h1>
            
            <div class="summary">
                <h2>测试摘要</h2>
                <table>
                    <tr><th>总测试数</th><td>{summary['total_tests']}</td></tr>
                    <tr><th>通过测试</th><td>{summary['passed_tests']}</td></tr>
                    <tr><th>失败测试</th><td>{summary['failed_tests']}</td></tr>
                    <tr><th>跳过测试</th><td>{summary['skipped_tests']}</td></tr>
                    <tr><th>通过率</th><td>{summary['pass_rate']:.2f}%</td></tr>
                    <tr><th>总执行时间</th><td>{summary['total_duration']:.2f}秒</td></tr>
                    <tr><th>开始时间</th><td>{summary['start_time']}</td></tr>
                    <tr><th>结束时间</th><td>{summary['end_time']}</td></tr>
                </table>
            </div>
            
            <h2>测试详情</h2>
        """
        
        for result in self.test_results:
            status_class = result["status"]
            html += f"""
            <div class="test-result {status_class}">
                <h3>{result['test_name']}</h3>
                <p><strong>状态:</strong> {result['status']}</p>
                <p><strong>执行时间:</strong> {result['duration']:.2f}秒</p>
                <p><strong>时间戳:</strong> {result['timestamp']}</p>
            """
            
            if result["error_message"]:
                html += f"<p><strong>错误信息:</strong> {result['error_message']}</p>"
            
            if result["screenshot"]:
                html += f"<p><strong>截图:</strong> <a href='{result['screenshot']}'>查看截图</a></p>"
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    def save_report(self, filename=None):
        """保存测试报告"""
        if not filename:
            filename = f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        
        report_path = os.path.join(self.report_dir, filename)
        html_report = self.generate_html_report()
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_report)
        
        # 同时保存JSON格式的原始数据
        json_filename = filename.replace('.html', '.json')
        json_path = os.path.join(self.report_dir, json_filename)
        
        report_data = {
            "summary": self.generate_summary(),
            "test_results": self.test_results
        }
        
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, ensure_ascii=False, indent=2)
        
        return report_path


class BaseTest:
    """测试基类，提供通用功能"""
    
    def __init__(self):
        self.config = ConfigManager()
        self.logger = LogManager()
        self.report = ReportManager()
        self.driver = None
    
    def setup(self):
        """测试前置操作"""
        browser = self.config.get("browser", "chrome")
        self.driver = MockWebDriver(browser)
        self.logger.info(f"启动浏览器: {browser}")
    
    def teardown(self):
        """测试后置操作"""
        if self.driver:
            self.driver.quit()
            self.logger.info("关闭浏览器")
    
    def run_test(self, test_func, test_name):
        """运行测试并记录结果"""
        start_time = time.time()
        status = "passed"
        error_msg = None
        
        try:
            self.setup()
            test_func()
            self.logger.info(f"测试 {test_name} 通过")
        except Exception as e:
            status = "failed"
            error_msg = str(e)
            self.logger.error(f"测试 {test_name} 失败: {error_msg}")
        finally:
            self.teardown()
            duration = time.time() - start_time
            self.report.add_test_result(test_name, status, duration, error_msg)
    
    def save_report(self):
        """保存测试报告"""
        return self.report.save_report()


def demo_basic_framework():
    """演示基础自动化测试框架"""
    print("=== 实验1：构建基础自动化测试框架 ===")
    
    # 创建测试类
    class LoginTest(BaseTest):
        def test_login(self):
            """登录测试"""
            base_url = self.config.get("base_url", "https://example.com")
            self.driver.get(f"{base_url}/login")
            
            # 输入用户名和密码
            username_field = self.driver.find_element(By.ID, "username")
            password_field = self.driver.find_element(By.ID, "password")
            login_button = self.driver.find_element(By.ID, "login-btn")
            
            username_field.send_keys("testuser")
            password_field.send_keys("password123")
            login_button.click()
            
            # 验证登录成功
            assert "Dashboard" in self.driver.title
    
    # 创建测试实例并运行测试
    test = LoginTest()
    test.run_test(test.test_login, "登录功能测试")
    
    # 保存测试报告
    report_path = test.save_report()
    print(f"测试报告已保存到: {report_path}")
    
    # 打印测试摘要
    summary = test.report.generate_summary()
    print(f"测试摘要: 总数 {summary['total_tests']}, 通过 {summary['passed_tests']}, 失败 {summary['failed_tests']}")
    
    return test


# ============================================================================
# 实验2：实现页面对象模式
# ============================================================================

class BasePage:
    """页面对象基类"""
    
    def __init__(self, driver):
        self.driver = driver
        self.logger = LogManager()
    
    def open(self, url):
        """打开页面"""
        self.driver.get(url)
        self.logger.info(f"打开页面: {url}")
    
    def find_element(self, locator):
        """查找元素"""
        by, value = locator
        return self.driver.find_element(by, value)
    
    def click(self, locator):
        """点击元素"""
        element = self.find_element(locator)
        element.click()
        self.logger.info(f"点击元素: {locator}")
    
    def type_text(self, locator, text):
        """输入文本"""
        element = self.find_element(locator)
        element.clear()
        element.send_keys(text)
        self.logger.info(f"输入文本: {text} 到 {locator}")
    
    def get_text(self, locator):
        """获取元素文本"""
        element = self.find_element(locator)
        return element.text
    
    def wait_for_element(self, locator, timeout=10):
        """等待元素出现"""
        # 简化实现，实际应用中应使用WebDriverWait
        time.sleep(1)
        return self.find_element(locator)


class LoginPage(BasePage):
    """登录页面对象"""
    
    # 定位器
    USERNAME_INPUT = (By.ID, "username")
    PASSWORD_INPUT = (By.ID, "password")
    LOGIN_BUTTON = (By.ID, "login-btn")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://example.com/login"
    
    def open(self):
        """打开登录页面"""
        super().open(self.url)
    
    def login(self, username, password):
        """执行登录操作"""
        self.type_text(self.USERNAME_INPUT, username)
        self.type_text(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        self.logger.info(f"执行登录操作: 用户名 {username}")
        
        # 返回下一个页面对象
        return DashboardPage(self.driver)


class DashboardPage(BasePage):
    """仪表板页面对象"""
    
    # 定位器
    WELCOME_MESSAGE = (By.ID, "welcome-msg")
    
    def __init__(self, driver):
        super().__init__(driver)
        self.url = "https://example.com/dashboard"
    
    def get_welcome_message(self):
        """获取欢迎消息"""
        return self.get_text(self.WELCOME_MESSAGE)
    
    def is_displayed(self):
        """检查页面是否显示"""
        try:
            self.find_element(self.WELCOME_MESSAGE)
            return True
        except:
            return False


def demo_page_object_model():
    """演示页面对象模式"""
    print("\n=== 实验2：实现页面对象模式 ===")
    
    # 创建测试类
    class LoginTestWithPOM(BaseTest):
        def test_login_with_pom(self):
            """使用页面对象模式的登录测试"""
            # 创建页面对象
            login_page = LoginPage(self.driver)
            
            # 打开登录页面
            login_page.open()
            
            # 执行登录操作
            dashboard_page = login_page.login("testuser", "password123")
            
            # 验证登录成功
            assert dashboard_page.is_displayed(), "仪表板页面未正确显示"
            welcome_msg = dashboard_page.get_welcome_message()
            assert "Welcome" in welcome_msg, f"欢迎消息不正确: {welcome_msg}"
    
    # 创建测试实例并运行测试
    test = LoginTestWithPOM()
    test.run_test(test.test_login_with_pom, "使用页面对象模式的登录测试")
    
    # 保存测试报告
    report_path = test.save_report()
    print(f"测试报告已保存到: {report_path}")
    
    # 打印测试摘要
    summary = test.report.generate_summary()
    print(f"测试摘要: 总数 {summary['total_tests']}, 通过 {summary['passed_tests']}, 失败 {summary['failed_tests']}")
    
    return test


# ============================================================================
# 实验3：实现数据驱动测试
# ============================================================================

class DataReader:
    """数据读取器"""
    
    @staticmethod
    def read_csv_data(file_path):
        """从CSV文件读取测试数据"""
        data = []
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                data.append(row)
        return data
    
    @staticmethod
    def read_json_data(file_path):
        """从JSON文件读取测试数据"""
        with open(file_path, 'r', encoding='utf-8') as file:
            return json.load(file)
    
    @staticmethod
    def read_excel_data(file_path):
        """从Excel文件读取测试数据（需要安装openpyxl或xlrd）"""
        # 这里只是示例，实际实现需要安装相应的库
        data = []
        # 实际代码会使用pandas或openpyxl读取Excel
        return data


class DataDrivenTest(BaseTest):
    """数据驱动测试基类"""
    
    def run_data_driven_test(self, test_func, test_name_prefix, data_source):
        """运行数据驱动测试"""
        if isinstance(data_source, str):
            # 从文件读取数据
            if data_source.endswith('.csv'):
                test_data = DataReader.read_csv_data(data_source)
            elif data_source.endswith('.json'):
                test_data = DataReader.read_json_data(data_source)
            else:
                raise ValueError(f"不支持的数据文件格式: {data_source}")
        else:
            # 直接使用提供的数据
            test_data = data_source
        
        # 为每条数据运行测试
        for i, data in enumerate(test_data):
            test_name = f"{test_name_prefix}_{i+1}"
            self.run_single_data_test(test_func, test_name, data)
    
    def run_single_data_test(self, test_func, test_name, data):
        """运行单个数据测试"""
        start_time = time.time()
        status = "passed"
        error_msg = None
        
        try:
            self.setup()
            test_func(data)
            self.logger.info(f"测试 {test_name} 通过")
        except Exception as e:
            status = "failed"
            error_msg = str(e)
            self.logger.error(f"测试 {test_name} 失败: {error_msg}")
        finally:
            self.teardown()
            duration = time.time() - start_time
            self.report.add_test_result(test_name, status, duration, error_msg, str(data))


def create_sample_test_data():
    """创建示例测试数据"""
    # 创建CSV测试数据
    os.makedirs("data", exist_ok=True)
    csv_data = [
        {"username": "validuser", "password": "validpass", "expected_result": "success"},
        {"username": "invaliduser", "password": "validpass", "expected_result": "failure"},
        {"username": "validuser", "password": "invalidpass", "expected_result": "failure"},
        {"username": "", "password": "validpass", "expected_result": "failure"},
        {"username": "validuser", "password": "", "expected_result": "failure"}
    ]
    
    csv_file = "data/login_test_data.csv"
    with open(csv_file, 'w', newline='', encoding='utf-8') as file:
        fieldnames = ["username", "password", "expected_result"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    # 创建JSON测试数据
    json_data = [
        {"username": "user1", "password": "pass1", "expected_result": "success"},
        {"username": "user2", "password": "pass2", "expected_result": "success"},
        {"username": "user3", "password": "wrongpass", "expected_result": "failure"}
    ]
    
    json_file = "data/login_test_data.json"
    with open(json_file, 'w', encoding='utf-8') as file:
        json.dump(json_data, file, ensure_ascii=False, indent=2)
    
    return csv_file, json_file


def demo_data_driven_test():
    """演示数据驱动测试"""
    print("\n=== 实验3：实现数据驱动测试 ===")
    
    # 创建示例测试数据
    csv_file, json_file = create_sample_test_data()
    print(f"已创建测试数据文件: {csv_file}, {json_file}")
    
    # 创建测试类
    class DataDrivenLoginTest(DataDrivenTest):
        def test_login_with_data(self, data):
            """使用数据驱动测试登录功能"""
            # 创建页面对象
            login_page = LoginPage(self.driver)
            
            # 打开登录页面
            login_page.open()
            
            # 从数据中获取用户名和密码
            username = data["username"]
            password = data["password"]
            expected_result = data["expected_result"]
            
            # 执行登录操作
            dashboard_page = login_page.login(username, password)
            
            # 根据预期结果验证
            if expected_result == "success":
                assert dashboard_page.is_displayed(), f"使用 {username}/{password} 登录应该成功"
            else:
                # 简化实现，实际应用中需要检查错误消息
                pass
    
    # 创建测试实例
    test = DataDrivenLoginTest()
    
    # 使用CSV数据运行测试
    print("\n使用CSV数据运行测试:")
    test.run_data_driven_test(
        test.test_login_with_data,
        "CSV数据驱动登录测试",
        csv_file
    )
    
    # 使用JSON数据运行测试
    print("\n使用JSON数据运行测试:")
    test.run_data_driven_test(
        test.test_login_with_data,
        "JSON数据驱动登录测试",
        json_file
    )
    
    # 使用直接提供的数据运行测试
    print("\n使用直接提供的数据运行测试:")
    direct_data = [
        {"username": "direct1", "password": "pass1", "expected_result": "success"},
        {"username": "direct2", "password": "wrongpass", "expected_result": "failure"}
    ]
    
    test.run_data_driven_test(
        test.test_login_with_data,
        "直接数据驱动登录测试",
        direct_data
    )
    
    # 保存测试报告
    report_path = test.save_report()
    print(f"\n测试报告已保存到: {report_path}")
    
    # 打印测试摘要
    summary = test.report.generate_summary()
    print(f"测试摘要: 总数 {summary['total_tests']}, 通过 {summary['passed_tests']}, 失败 {summary['failed_tests']}")
    
    return test


# ============================================================================
# 实验4：并行测试执行
# ============================================================================

class ParallelTestRunner:
    """并行测试运行器"""
    
    def __init__(self, max_workers=None):
        self.config = ConfigManager()
        self.max_workers = max_workers or self.config.get("max_workers", 2)
        self.logger = LogManager()
        self.report = ReportManager()
    
    def run_tests_parallel(self, test_classes):
        """并行运行测试"""
        start_time = time.time()
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有测试任务
            futures = []
            for test_class in test_classes:
                future = executor.submit(self._run_test_class, test_class)
                futures.append(future)
            
            # 等待所有测试完成
            for future in concurrent.futures.as_completed(futures):
                try:
                    test_results = future.result()
                    # 合并测试结果
                    for result in test_results:
                        self.report.test_results.append(result)
                except Exception as e:
                    self.logger.error(f"测试执行出错: {str(e)}")
        
        total_time = time.time() - start_time
        self.logger.info(f"并行测试执行完成，总耗时: {total_time:.2f}秒")
        
        return self.report
    
    def _run_test_class(self, test_class):
        """运行单个测试类"""
        test_instance = test_class()
        test_methods = [method for method in dir(test_instance) if method.startswith('test_')]
        
        test_results = []
        for method_name in test_methods:
            test_method = getattr(test_instance, method_name)
            
            start_time = time.time()
            status = "passed"
            error_msg = None
            
            try:
                test_instance.setup()
                test_method()
                self.logger.info(f"测试 {method_name} 通过")
            except Exception as e:
                status = "failed"
                error_msg = str(e)
                self.logger.error(f"测试 {method_name} 失败: {error_msg}")
            finally:
                test_instance.teardown()
                duration = time.time() - start_time
                
                result = {
                    "test_name": f"{test_class.__name__}.{method_name}",
                    "status": status,
                    "duration": duration,
                    "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "error_message": error_msg,
                    "screenshot": None
                }
                test_results.append(result)
        
        return test_results


def demo_parallel_test_execution():
    """演示并行测试执行"""
    print("\n=== 实验4：并行测试执行 ===")
    
    # 创建测试类
    class ParallelTest1(BaseTest):
        def test_parallel_1(self):
            """并行测试1"""
            self.driver.get("https://example.com/test1")
            time.sleep(1)  # 模拟测试操作
            assert "Test1" in self.driver.title
    
    class ParallelTest2(BaseTest):
        def test_parallel_2(self):
            """并行测试2"""
            self.driver.get("https://example.com/test2")
            time.sleep(1)  # 模拟测试操作
            assert "Test2" in self.driver.title
    
    class ParallelTest3(BaseTest):
        def test_parallel_3(self):
            """并行测试3"""
            self.driver.get("https://example.com/test3")
            time.sleep(1)  # 模拟测试操作
            assert "Test3" in self.driver.title
    
    # 创建并行测试运行器
    runner = ParallelTestRunner(max_workers=3)
    
    # 并行运行测试
    test_classes = [ParallelTest1, ParallelTest2, ParallelTest3]
    report = runner.run_tests_parallel(test_classes)
    
    # 保存测试报告
    report_path = report.save_report()
    print(f"并行测试报告已保存到: {report_path}")
    
    # 打印测试摘要
    summary = report.generate_summary()
    print(f"测试摘要: 总数 {summary['total_tests']}, 通过 {summary['passed_tests']}, 失败 {summary['failed_tests']}")
    
    return runner


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("自动化测试框架 - 示例代码")
    print("=" * 50)
    
    # 确保输出目录存在
    os.makedirs("output", exist_ok=True)
    
    # 运行所有实验
    demo_basic_framework()
    demo_page_object_model()
    demo_data_driven_test()
    demo_parallel_test_execution()
    
    print("\n所有实验已完成！")
    print("生成的文件:")
    print("- logs/: 日志文件目录")
    print("- reports/: 测试报告目录")
    print("- data/: 测试数据目录")


if __name__ == "__main__":
    main()