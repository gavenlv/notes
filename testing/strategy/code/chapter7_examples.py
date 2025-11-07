#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
第7章：安全测试 - 示例代码
本文件包含安全测试的示例代码，涵盖静态代码分析、动态应用安全测试、
渗透测试基础和安全测试自动化等内容。
"""

import os
import re
import json
import time
import hashlib
import random
import string
import sqlite3
import requests
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from abc import ABC, abstractmethod
from urllib.parse import urlparse, parse_qs
import base64
import html

# ============================================================================
# 实验1：静态代码安全分析
# ============================================================================

@dataclass
class Vulnerability:
    """漏洞数据类"""
    type: str
    severity: str  # 高、中、低
    file_path: str
    line_number: int
    description: str
    recommendation: str

class StaticCodeAnalyzer:
    """静态代码安全分析器"""
    
    def __init__(self):
        self.vulnerabilities: List[Vulnerability] = []
        self.security_patterns = {
            "sql_injection": [
                r"execute\s*\(\s*['\"].*?\+.*?['\"]",
                r"query\s*\(\s*['\"].*?\+.*?['\"]",
                r"cursor\.execute\s*\(\s*['\"].*?\+.*?['\"]"
            ],
            "xss": [
                r"innerHTML\s*=\s*.*?\+",
                r"document\.write\s*\(\s*.*?\+",
                r"eval\s*\(\s*.*?\+"
            ],
            "hardcoded_password": [
                r"password\s*=\s*['\"][^'\"]{4,}['\"]",
                r"pwd\s*=\s*['\"][^'\"]{4,}['\"]",
                r"passwd\s*=\s*['\"][^'\"]{4,}['\"]"
            ],
            "weak_crypto": [
                r"md5\s*\(",
                r"sha1\s*\(",
                r"DES\s*\("
            ],
            "path_traversal": [
                r"open\s*\(\s*.*?\+.*?\)",
                r"file\s*\(\s*.*?\+.*?\)",
                r"readfile\s*\(\s*.*?\+.*?\)"
            ]
        }
    
    def analyze_file(self, file_path: str) -> List[Vulnerability]:
        """分析单个文件"""
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return []
        
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                
                for line_num, line in enumerate(lines, 1):
                    for vuln_type, patterns in self.security_patterns.items():
                        for pattern in patterns:
                            if re.search(pattern, line, re.IGNORECASE):
                                severity = self._get_severity(vuln_type)
                                description = self._get_description(vuln_type)
                                recommendation = self._get_recommendation(vuln_type)
                                
                                vulnerability = Vulnerability(
                                    type=vuln_type,
                                    severity=severity,
                                    file_path=file_path,
                                    line_number=line_num,
                                    description=description,
                                    recommendation=recommendation
                                )
                                
                                vulnerabilities.append(vulnerability)
        except Exception as e:
            print(f"分析文件时出错: {e}")
        
        return vulnerabilities
    
    def analyze_directory(self, directory_path: str, extensions: List[str] = None) -> List[Vulnerability]:
        """分析目录中的所有文件"""
        if extensions is None:
            extensions = ['.py', '.js', '.php', '.java', '.c', '.cpp']
        
        all_vulnerabilities = []
        
        for root, _, files in os.walk(directory_path):
            for file in files:
                if any(file.endswith(ext) for ext in extensions):
                    file_path = os.path.join(root, file)
                    vulnerabilities = self.analyze_file(file_path)
                    all_vulnerabilities.extend(vulnerabilities)
        
        return all_vulnerabilities
    
    def _get_severity(self, vuln_type: str) -> str:
        """根据漏洞类型获取严重程度"""
        severity_map = {
            "sql_injection": "高",
            "xss": "高",
            "hardcoded_password": "中",
            "weak_crypto": "中",
            "path_traversal": "高"
        }
        return severity_map.get(vuln_type, "低")
    
    def _get_description(self, vuln_type: str) -> str:
        """根据漏洞类型获取描述"""
        descriptions = {
            "sql_injection": "可能存在SQL注入漏洞，直接将用户输入拼接到SQL查询中",
            "xss": "可能存在跨站脚本漏洞，直接将用户输入插入到HTML中",
            "hardcoded_password": "硬编码密码，可能导致密码泄露",
            "weak_crypto": "使用了弱加密算法，容易被破解",
            "path_traversal": "可能存在路径遍历漏洞，允许访问系统敏感文件"
        }
        return descriptions.get(vuln_type, "未知安全漏洞")
    
    def _get_recommendation(self, vuln_type: str) -> str:
        """根据漏洞类型获取修复建议"""
        recommendations = {
            "sql_injection": "使用参数化查询或ORM框架，避免直接拼接SQL",
            "xss": "对用户输入进行HTML编码，使用安全的DOM操作方法",
            "hardcoded_password": "使用环境变量或配置文件存储密码，避免硬编码",
            "weak_crypto": "使用强加密算法，如AES-256、SHA-256等",
            "path_traversal": "验证和限制文件路径，使用白名单机制"
        }
        return recommendations.get(vuln_type, "请咨询安全专家")
    
    def generate_report(self, vulnerabilities: List[Vulnerability], output_file: str = None) -> str:
        """生成安全分析报告"""
        report_lines = []
        report_lines.append("# 静态代码安全分析报告")
        report_lines.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"发现漏洞总数: {len(vulnerabilities)}")
        report_lines.append("")
        
        # 按严重程度统计
        severity_count = {"高": 0, "中": 0, "低": 0}
        for vuln in vulnerabilities:
            severity_count[vuln.severity] += 1
        
        report_lines.append("## 漏洞严重程度分布")
        report_lines.append(f"- 高危: {severity_count['高']}")
        report_lines.append(f"- 中危: {severity_count['中']}")
        report_lines.append(f"- 低危: {severity_count['低']}")
        report_lines.append("")
        
        # 按类型统计
        type_count = {}
        for vuln in vulnerabilities:
            type_count[vuln.type] = type_count.get(vuln.type, 0) + 1
        
        report_lines.append("## 漏洞类型分布")
        for vuln_type, count in type_count.items():
            report_lines.append(f"- {vuln_type}: {count}")
        report_lines.append("")
        
        # 详细漏洞列表
        report_lines.append("## 漏洞详情")
        for i, vuln in enumerate(vulnerabilities, 1):
            report_lines.append(f"### {i}. {vuln.type} ({vuln.severity})")
            report_lines.append(f"**文件**: {vuln.file_path}")
            report_lines.append(f"**行号**: {vuln.line_number}")
            report_lines.append(f"**描述**: {vuln.description}")
            report_lines.append(f"**修复建议**: {vuln.recommendation}")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"报告已保存到: {output_file}")
        
        return report_content

def demo_static_code_analysis():
    """演示静态代码安全分析"""
    print("=== 实验1：静态代码安全分析 ===")
    
    # 创建示例代码文件
    sample_code_dir = "sample_code"
    os.makedirs(sample_code_dir, exist_ok=True)
    
    # 创建包含漏洞的示例代码
    vulnerable_code = """
import sqlite3

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # SQL注入漏洞
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def get_user_input():
    # XSS漏洞
    user_input = input("请输入内容: ")
    print("<div>" + user_input + "</div>")
    
    # 硬编码密码
    password = "admin123"
    
    # 弱加密
    import hashlib
    hashed_password = hashlib.md5(password.encode()).hexdigest()
    
    return hashed_password

def read_file(filename):
    # 路径遍历漏洞
    file_path = "/var/www/" + filename
    with open(file_path, 'r') as f:
        return f.read()
"""
    
    with open(os.path.join(sample_code_dir, "vulnerable.py"), 'w', encoding='utf-8') as f:
        f.write(vulnerable_code)
    
    # 创建安全代码示例
    secure_code = """
import sqlite3
import hashlib
import os

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 使用参数化查询防止SQL注入
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    cursor.execute(query, (username, password))
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def get_user_input():
    # 对用户输入进行HTML编码防止XSS
    user_input = input("请输入内容: ")
    encoded_input = html.escape(user_input)
    print("<div>" + encoded_input + "</div>")
    
    # 从环境变量获取密码
    password = os.environ.get('APP_PASSWORD')
    
    # 使用强加密算法
    hashed_password = hashlib.sha256(password.encode()).hexdigest()
    
    return hashed_password

def read_file(filename):
    # 验证文件名防止路径遍历
    if not filename or '/' in filename or '..' in filename:
        return "无效的文件名"
    
    # 使用白名单机制
    allowed_files = ['profile.txt', 'settings.json']
    if filename not in allowed_files:
        return "文件不在允许列表中"
    
    file_path = os.path.join('/var/www/', filename)
    with open(file_path, 'r') as f:
        return f.read()
"""
    
    with open(os.path.join(sample_code_dir, "secure.py"), 'w', encoding='utf-8') as f:
        f.write(secure_code)
    
    # 创建静态代码分析器
    analyzer = StaticCodeAnalyzer()
    
    # 分析示例代码
    print("\n分析示例代码中的安全漏洞...")
    vulnerabilities = analyzer.analyze_directory(sample_code_dir)
    
    # 生成报告
    report = analyzer.generate_report(vulnerabilities, "security_analysis_report.md")
    
    # 打印摘要
    print(f"\n发现 {len(vulnerabilities)} 个安全漏洞")
    for vuln in vulnerabilities:
        print(f"- {vuln.type} ({vuln.severity}): {vuln.file_path}:{vuln.line_number}")
    
    # 清理示例文件
    try:
        for file in os.listdir(sample_code_dir):
            os.remove(os.path.join(sample_code_dir, file))
        os.rmdir(sample_code_dir)
    except:
        pass
    
    return analyzer


# ============================================================================
# 实验2：动态应用安全测试
# ============================================================================

class WebVulnerabilityScanner:
    """Web漏洞扫描器"""
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = requests.Session()
        self.vulnerabilities = []
    
    def scan_sql_injection(self, test_param: str = "id") -> List[Dict]:
        """扫描SQL注入漏洞"""
        print(f"\n扫描SQL注入漏洞，测试参数: {test_param}")
        
        payloads = [
            "' OR '1'='1",
            "' OR '1'='1' --",
            "' OR '1'='1' /*",
            "'; DROP TABLE users; --",
            "' UNION SELECT NULL, username, password FROM users --"
        ]
        
        found_vulnerabilities = []
        
        for payload in payloads:
            try:
                # 构造测试URL
                test_url = f"{self.base_url}?{test_param}={payload}"
                response = self.session.get(test_url, timeout=5)
                
                # 检查响应中是否包含SQL错误信息
                sql_errors = [
                    "you have an error in your sql syntax",
                    "warning: mysql",
                    "unclosed quotation mark",
                    "microsoft ole db provider for odbc drivers error"
                ]
                
                for error in sql_errors:
                    if error.lower() in response.text.lower():
                        vulnerability = {
                            "type": "SQL注入",
                            "url": test_url,
                            "payload": payload,
                            "evidence": error,
                            "severity": "高"
                        }
                        found_vulnerabilities.append(vulnerability)
                        print(f"发现SQL注入漏洞: {test_url}")
                        break
                        
            except Exception as e:
                print(f"测试URL失败: {test_url}, 错误: {e}")
        
        return found_vulnerabilities
    
    def scan_xss(self, test_param: str = "search") -> List[Dict]:
        """扫描XSS漏洞"""
        print(f"\n扫描XSS漏洞，测试参数: {test_param}")
        
        payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//",
            "<svg onload=alert('XSS')>",
            "javascript:alert('XSS')"
        ]
        
        found_vulnerabilities = []
        
        for payload in payloads:
            try:
                # 构造测试URL
                test_url = f"{self.base_url}?{test_param}={payload}"
                response = self.session.get(test_url, timeout=5)
                
                # 检查响应中是否包含payload
                if payload in response.text:
                    vulnerability = {
                        "type": "XSS",
                        "url": test_url,
                        "payload": payload,
                        "evidence": "Payload在响应中反射",
                        "severity": "高"
                    }
                    found_vulnerabilities.append(vulnerability)
                    print(f"发现XSS漏洞: {test_url}")
                    
            except Exception as e:
                print(f"测试URL失败: {test_url}, 错误: {e}")
        
        return found_vulnerabilities
    
    def scan_directory_traversal(self, test_param: str = "file") -> List[Dict]:
        """扫描目录遍历漏洞"""
        print(f"\n扫描目录遍历漏洞，测试参数: {test_param}")
        
        payloads = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
            "....//....//....//etc/passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
        
        found_vulnerabilities = []
        
        for payload in payloads:
            try:
                # 构造测试URL
                test_url = f"{self.base_url}?{test_param}={payload}"
                response = self.session.get(test_url, timeout=5)
                
                # 检查响应中是否包含系统文件内容
                indicators = ["root:x:0:0", "# Copyright", "[fonts]", "# For 16-bit app"]
                
                for indicator in indicators:
                    if indicator in response.text:
                        vulnerability = {
                            "type": "目录遍历",
                            "url": test_url,
                            "payload": payload,
                            "evidence": indicator,
                            "severity": "高"
                        }
                        found_vulnerabilities.append(vulnerability)
                        print(f"发现目录遍历漏洞: {test_url}")
                        break
                        
            except Exception as e:
                print(f"测试URL失败: {test_url}, 错误: {e}")
        
        return found_vulnerabilities
    
    def scan_command_injection(self, test_param: str = "cmd") -> List[Dict]:
        """扫描命令注入漏洞"""
        print(f"\n扫描命令注入漏洞，测试参数: {test_param}")
        
        payloads = [
            "; ls -la",
            "& dir",
            "| whoami",
            "&& cat /etc/passwd",
            "`id`"
        ]
        
        found_vulnerabilities = []
        
        for payload in payloads:
            try:
                # 构造测试URL
                test_url = f"{self.base_url}?{test_param}={payload}"
                response = self.session.get(test_url, timeout=5)
                
                # 检查响应中是否包含命令执行结果
                indicators = ["total ", "root:", "uid=", "gid=", "Volume Serial Number"]
                
                for indicator in indicators:
                    if indicator in response.text:
                        vulnerability = {
                            "type": "命令注入",
                            "url": test_url,
                            "payload": payload,
                            "evidence": indicator,
                            "severity": "高"
                        }
                        found_vulnerabilities.append(vulnerability)
                        print(f"发现命令注入漏洞: {test_url}")
                        break
                        
            except Exception as e:
                print(f"测试URL失败: {test_url}, 错误: {e}")
        
        return found_vulnerabilities
    
    def scan_all(self) -> List[Dict]:
        """执行所有漏洞扫描"""
        print(f"开始扫描 {self.base_url} 的安全漏洞...")
        
        all_vulnerabilities = []
        
        # 扫描各种漏洞
        all_vulnerabilities.extend(self.scan_sql_injection())
        all_vulnerabilities.extend(self.scan_xss())
        all_vulnerabilities.extend(self.scan_directory_traversal())
        all_vulnerabilities.extend(self.scan_command_injection())
        
        return all_vulnerabilities
    
    def generate_report(self, vulnerabilities: List[Dict], output_file: str = None) -> str:
        """生成漏洞扫描报告"""
        report_lines = []
        report_lines.append("# Web应用安全漏洞扫描报告")
        report_lines.append(f"扫描目标: {self.base_url}")
        report_lines.append(f"扫描时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append(f"发现漏洞总数: {len(vulnerabilities)}")
        report_lines.append("")
        
        # 按严重程度统计
        severity_count = {"高": 0, "中": 0, "低": 0}
        for vuln in vulnerabilities:
            severity_count[vuln["severity"]] += 1
        
        report_lines.append("## 漏洞严重程度分布")
        report_lines.append(f"- 高危: {severity_count['高']}")
        report_lines.append(f"- 中危: {severity_count['中']}")
        report_lines.append(f"- 低危: {severity_count['低']}")
        report_lines.append("")
        
        # 按类型统计
        type_count = {}
        for vuln in vulnerabilities:
            vuln_type = vuln["type"]
            type_count[vuln_type] = type_count.get(vuln_type, 0) + 1
        
        report_lines.append("## 漏洞类型分布")
        for vuln_type, count in type_count.items():
            report_lines.append(f"- {vuln_type}: {count}")
        report_lines.append("")
        
        # 详细漏洞列表
        report_lines.append("## 漏洞详情")
        for i, vuln in enumerate(vulnerabilities, 1):
            report_lines.append(f"### {i}. {vuln['type']} ({vuln['severity']})")
            report_lines.append(f"**URL**: {vuln['url']}")
            report_lines.append(f"**Payload**: `{vuln['payload']}`")
            report_lines.append(f"**证据**: {vuln['evidence']}")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"报告已保存到: {output_file}")
        
        return report_content

def demo_dynamic_security_testing():
    """演示动态应用安全测试"""
    print("\n=== 实验2：动态应用安全测试 ===")
    
    # 使用公共测试API
    target_url = "https://httpbin.org/get"
    
    # 创建Web漏洞扫描器
    scanner = WebVulnerabilityScanner(target_url)
    
    # 执行扫描
    vulnerabilities = scanner.scan_all()
    
    # 生成报告
    report = scanner.generate_report(vulnerabilities, "web_vulnerability_report.md")
    
    # 打印摘要
    print(f"\n扫描完成，发现 {len(vulnerabilities)} 个潜在漏洞")
    for vuln in vulnerabilities:
        print(f"- {vuln['type']} ({vuln['severity']}): {vuln['url']}")
    
    return scanner


# ============================================================================
# 实验3：渗透测试基础
# ============================================================================

class PenetrationTester:
    """渗透测试基础工具集"""
    
    def __init__(self, target: str):
        self.target = target
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def information_gathering(self) -> Dict:
        """信息收集"""
        print(f"\n开始对 {self.target} 进行信息收集...")
        
        info = {}
        
        try:
            # 基本HTTP信息
            response = self.session.get(self.target, timeout=5)
            info['status_code'] = response.status_code
            info['server'] = response.headers.get('Server', 'Unknown')
            info['powered_by'] = response.headers.get('X-Powered-By', 'Unknown')
            info['content_type'] = response.headers.get('Content-Type', 'Unknown')
            
            # 解析URL
            parsed_url = urlparse(self.target)
            info['scheme'] = parsed_url.scheme
            info['domain'] = parsed_url.netloc
            info['path'] = parsed_url.path
            
            # 提取页面中的链接
            import re
            links = re.findall(r'href=[\'"]?([^\'" >]+)', response.text)
            info['links'] = links[:10]  # 只取前10个链接
            
            print(f"信息收集完成，状态码: {info['status_code']}")
            
        except Exception as e:
            print(f"信息收集失败: {e}")
        
        return info
    
    def subdomain_enumeration(self, domain: str) -> List[str]:
        """子域名枚举"""
        print(f"\n开始对 {domain} 进行子域名枚举...")
        
        # 常见子域名前缀
        subdomains = [
            "www", "mail", "ftp", "admin", "test", "dev", "api", "blog", 
            "shop", "forum", "support", "vpn", "remote", "secure", "staging"
        ]
        
        found_subdomains = []
        
        for subdomain in subdomains:
            subdomain_url = f"{subdomain}.{domain}"
            try:
                response = self.session.get(f"http://{subdomain_url}", timeout=3)
                if response.status_code < 500:  # 排除服务器错误
                    found_subdomains.append(subdomain_url)
                    print(f"发现子域名: {subdomain_url}")
            except:
                pass
        
        return found_subdomains
    
    def port_scanning(self, host: str, ports: List[int] = None) -> Dict:
        """端口扫描"""
        if ports is None:
            ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 8080, 8443]
        
        print(f"\n开始对 {host} 进行端口扫描...")
        
        open_ports = []
        
        for port in ports:
            try:
                # 使用socket连接测试端口
                import socket
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((host, port))
                sock.close()
                
                if result == 0:
                    open_ports.append(port)
                    print(f"端口 {port} 开放")
            except Exception as e:
                print(f"扫描端口 {port} 时出错: {e}")
        
        return {"host": host, "open_ports": open_ports}
    
    def directory_bruteforce(self, base_url: str, wordlist: List[str] = None) -> List[str]:
        """目录暴力破解"""
        if wordlist is None:
            wordlist = [
                "admin", "login", "test", "dev", "backup", "config", "uploads",
                "images", "css", "js", "api", "docs", "files", "tmp", "logs"
            ]
        
        print(f"\n开始对 {base_url} 进行目录暴力破解...")
        
        found_directories = []
        
        for directory in wordlist:
            url = f"{base_url}/{directory}"
            try:
                response = self.session.get(url, timeout=3)
                if response.status_code == 200:
                    found_directories.append(url)
                    print(f"发现目录: {url}")
            except:
                pass
        
        return found_directories
    
    def test_common_credentials(self, login_url: str, usernames: List[str], passwords: List[str]) -> Dict:
        """测试常见凭据"""
        print(f"\n开始对 {login_url} 进行常见凭据测试...")
        
        successful_logins = []
        
        for username in usernames:
            for password in passwords:
                try:
                    # 尝试POST请求登录
                    response = self.session.post(
                        login_url,
                        data={"username": username, "password": password},
                        timeout=5
                    )
                    
                    # 检查响应是否包含登录成功的标志
                    if "dashboard" in response.text.lower() or "welcome" in response.text.lower():
                        successful_logins.append({
                            "username": username,
                            "password": password
                        })
                        print(f"发现有效凭据: {username}/{password}")
                        
                except Exception as e:
                    print(f"测试凭据 {username}/{password} 时出错: {e}")
        
        return {"login_url": login_url, "successful_logins": successful_logins}
    
    def generate_report(self, results: Dict, output_file: str = None) -> str:
        """生成渗透测试报告"""
        report_lines = []
        report_lines.append("# 渗透测试基础报告")
        report_lines.append(f"目标: {self.target}")
        report_lines.append(f"测试时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        
        # 信息收集结果
        if "information_gathering" in results:
            info = results["information_gathering"]
            report_lines.append("## 信息收集")
            report_lines.append(f"- 状态码: {info.get('status_code', 'Unknown')}")
            report_lines.append(f"- 服务器: {info.get('server', 'Unknown')}")
            report_lines.append(f"- 技术栈: {info.get('powered_by', 'Unknown')}")
            report_lines.append("")
        
        # 子域名枚举结果
        if "subdomain_enumeration" in results:
            subdomains = results["subdomain_enumeration"]
            report_lines.append("## 子域名枚举")
            if subdomains:
                for subdomain in subdomains:
                    report_lines.append(f"- {subdomain}")
            else:
                report_lines.append("- 未发现子域名")
            report_lines.append("")
        
        # 端口扫描结果
        if "port_scanning" in results:
            port_result = results["port_scanning"]
            report_lines.append("## 端口扫描")
            open_ports = port_result.get("open_ports", [])
            if open_ports:
                for port in open_ports:
                    report_lines.append(f"- 端口 {port} 开放")
            else:
                report_lines.append("- 未发现开放端口")
            report_lines.append("")
        
        # 目录暴力破解结果
        if "directory_bruteforce" in results:
            directories = results["directory_bruteforce"]
            report_lines.append("## 目录暴力破解")
            if directories:
                for directory in directories:
                    report_lines.append(f"- {directory}")
            else:
                report_lines.append("- 未发现隐藏目录")
            report_lines.append("")
        
        # 凭据测试结果
        if "test_common_credentials" in results:
            credentials = results["test_common_credentials"]
            report_lines.append("## 凭据测试")
            successful_logins = credentials.get("successful_logins", [])
            if successful_logins:
                for login in successful_logins:
                    report_lines.append(f"- {login['username']}/{login['password']}")
            else:
                report_lines.append("- 未发现有效凭据")
            report_lines.append("")
        
        report_content = "\n".join(report_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            print(f"报告已保存到: {output_file}")
        
        return report_content

def demo_penetration_testing():
    """演示渗透测试基础"""
    print("\n=== 实验3：渗透测试基础 ===")
    
    # 使用公共测试网站
    target = "https://httpbin.org"
    
    # 创建渗透测试器
    pentester = PenetrationTester(target)
    
    # 执行各种测试
    results = {}
    
    # 信息收集
    results["information_gathering"] = pentester.information_gathering()
    
    # 子域名枚举
    domain = "httpbin.org"
    results["subdomain_enumeration"] = pentester.subdomain_enumeration(domain)
    
    # 端口扫描
    host = "httpbin.org"
    results["port_scanning"] = pentester.port_scanning(host)
    
    # 目录暴力破解
    base_url = "https://httpbin.org"
    results["directory_bruteforce"] = pentester.directory_bruteforce(base_url)
    
    # 生成报告
    report = pentester.generate_report(results, "penetration_test_report.md")
    
    # 打印摘要
    print("\n渗透测试完成")
    print(f"发现 {len(results['subdomain_enumeration'])} 个子域名")
    print(f"发现 {len(results['port_scanning']['open_ports'])} 个开放端口")
    print(f"发现 {len(results['directory_bruteforce'])} 个目录")
    
    return pentester


# ============================================================================
# 实验4：安全测试自动化
# ============================================================================

class SecurityTestAutomation:
    """安全测试自动化框架"""
    
    def __init__(self):
        self.test_results = []
        self.static_analyzer = StaticCodeAnalyzer()
    
    def run_sast_scan(self, project_path: str) -> Dict:
        """运行静态应用安全测试"""
        print(f"\n开始对 {project_path} 进行静态应用安全测试...")
        
        vulnerabilities = self.static_analyzer.analyze_directory(project_path)
        
        result = {
            "test_type": "SAST",
            "target": project_path,
            "vulnerabilities": len(vulnerabilities),
            "details": vulnerabilities
        }
        
        self.test_results.append(result)
        
        print(f"SAST扫描完成，发现 {len(vulnerabilities)} 个潜在漏洞")
        
        return result
    
    def run_dast_scan(self, target_url: str) -> Dict:
        """运行动态应用安全测试"""
        print(f"\n开始对 {target_url} 进行动态应用安全测试...")
        
        scanner = WebVulnerabilityScanner(target_url)
        vulnerabilities = scanner.scan_all()
        
        result = {
            "test_type": "DAST",
            "target": target_url,
            "vulnerabilities": len(vulnerabilities),
            "details": vulnerabilities
        }
        
        self.test_results.append(result)
        
        print(f"DAST扫描完成，发现 {len(vulnerabilities)} 个潜在漏洞")
        
        return result
    
    def run_dependency_check(self, requirements_file: str) -> Dict:
        """运行依赖安全检查"""
        print(f"\n开始对 {requirements_file} 进行依赖安全检查...")
        
        if not os.path.exists(requirements_file):
            print(f"依赖文件不存在: {requirements_file}")
            return {"test_type": "Dependency Check", "target": requirements_file, "vulnerabilities": 0, "details": []}
        
        # 模拟依赖检查（实际应用中应使用专业工具如Snyk、Safety等）
        known_vulnerable_packages = {
            "requests": "2.20.0",
            "urllib3": "1.24.2",
            "pillow": "6.2.0"
        }
        
        vulnerabilities = []
        
        try:
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # 简单解析包名和版本
                        parts = line.split('==')
                        package = parts[0].lower()
                        version = parts[1] if len(parts) > 1 else "unknown"
                        
                        # 检查是否是已知漏洞版本
                        if package in known_vulnerable_packages and version == known_vulnerable_packages[package]:
                            vulnerabilities.append({
                                "package": package,
                                "version": version,
                                "cve": f"CVE-2020-{random.randint(1000, 9999)}",
                                "severity": "高"
                            })
        
        except Exception as e:
            print(f"解析依赖文件时出错: {e}")
        
        result = {
            "test_type": "Dependency Check",
            "target": requirements_file,
            "vulnerabilities": len(vulnerabilities),
            "details": vulnerabilities
        }
        
        self.test_results.append(result)
        
        print(f"依赖检查完成，发现 {len(vulnerabilities)} 个潜在漏洞")
        
        return result
    
    def run_container_security_scan(self, image_name: str) -> Dict:
        """运行容器安全扫描"""
        print(f"\n开始对 {image_name} 进行容器安全扫描...")
        
        # 模拟容器安全扫描（实际应用中应使用专业工具如Trivy、Clair等）
        vulnerabilities = [
            {
                "package": "openssl",
                "version": "1.1.1",
                "cve": "CVE-2021-3711",
                "severity": "高"
            },
            {
                "package": "curl",
                "version": "7.68.0",
                "cve": "CVE-2021-22876",
                "severity": "中"
            }
        ]
        
        result = {
            "test_type": "Container Security Scan",
            "target": image_name,
            "vulnerabilities": len(vulnerabilities),
            "details": vulnerabilities
        }
        
        self.test_results.append(result)
        
        print(f"容器安全扫描完成，发现 {len(vulnerabilities)} 个潜在漏洞")
        
        return result
    
    def generate_security_dashboard(self, output_file: str = None) -> str:
        """生成安全测试仪表板"""
        total_vulnerabilities = sum(result["vulnerabilities"] for result in self.test_results)
        
        dashboard_lines = []
        dashboard_lines.append("# 安全测试仪表板")
        dashboard_lines.append(f"生成时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
        dashboard_lines.append(f"总漏洞数: {total_vulnerabilities}")
        dashboard_lines.append("")
        
        # 测试结果概览
        dashboard_lines.append("## 测试结果概览")
        dashboard_lines.append("| 测试类型 | 目标 | 漏洞数 | 状态 |")
        dashboard_lines.append("|---------|------|--------|------|")
        
        for result in self.test_results:
            status = "失败" if result["vulnerabilities"] > 0 else "通过"
            dashboard_lines.append(f"| {result['test_type']} | {result['target']} | {result['vulnerabilities']} | {status} |")
        
        dashboard_lines.append("")
        
        # 漏洞严重程度分布
        severity_count = {"高": 0, "中": 0, "低": 0}
        
        for result in self.test_results:
            for vuln in result["details"]:
                severity = vuln.get("severity", "低")
                severity_count[severity] += 1
        
        dashboard_lines.append("## 漏洞严重程度分布")
        dashboard_lines.append(f"- 高危: {severity_count['高']}")
        dashboard_lines.append(f"- 中危: {severity_count['中']}")
        dashboard_lines.append(f"- 低危: {severity_count['低']}")
        dashboard_lines.append("")
        
        # 漏洞类型分布
        type_count = {}
        
        for result in self.test_results:
            for vuln in result["details"]:
                vuln_type = vuln.get("type", "未知")
                type_count[vuln_type] = type_count.get(vuln_type, 0) + 1
        
        dashboard_lines.append("## 漏洞类型分布")
        for vuln_type, count in type_count.items():
            dashboard_lines.append(f"- {vuln_type}: {count}")
        dashboard_lines.append("")
        
        # 安全评分
        max_score = 100
        high_penalty = 10
        medium_penalty = 5
        low_penalty = 1
        
        score = max_score - (severity_count["高"] * high_penalty + 
                           severity_count["中"] * medium_penalty + 
                           severity_count["低"] * low_penalty)
        
        score = max(0, score)  # 确保分数不低于0
        
        dashboard_lines.append("## 安全评分")
        dashboard_lines.append(f"当前安全评分: {score}/100")
        
        if score >= 90:
            dashboard_lines.append("安全状态: 优秀")
        elif score >= 70:
            dashboard_lines.append("安全状态: 良好")
        elif score >= 50:
            dashboard_lines.append("安全状态: 一般")
        else:
            dashboard_lines.append("安全状态: 需要改进")
        
        dashboard_content = "\n".join(dashboard_lines)
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(dashboard_content)
            print(f"安全仪表板已保存到: {output_file}")
        
        return dashboard_content
    
    def set_security_gate(self, max_high_vulnerabilities: int = 0, 
                         max_medium_vulnerabilities: int = 5, 
                         max_low_vulnerabilities: int = 10) -> bool:
        """设置安全门禁并检查是否通过"""
        severity_count = {"高": 0, "中": 0, "低": 0}
        
        for result in self.test_results:
            for vuln in result["details"]:
                severity = vuln.get("severity", "低")
                severity_count[severity] += 1
        
        passed = (
            severity_count["高"] <= max_high_vulnerabilities and
            severity_count["中"] <= max_medium_vulnerabilities and
            severity_count["低"] <= max_low_vulnerabilities
        )
        
        print(f"\n安全门禁检查:")
        print(f"- 高危漏洞: {severity_count['高']} (阈值: {max_high_vulnerabilities})")
        print(f"- 中危漏洞: {severity_count['中']} (阈值: {max_medium_vulnerabilities})")
        print(f"- 低危漏洞: {severity_count['低']} (阈值: {max_low_vulnerabilities})")
        print(f"- 结果: {'通过' if passed else '失败'}")
        
        return passed

def demo_security_test_automation():
    """演示安全测试自动化"""
    print("\n=== 实验4：安全测试自动化 ===")
    
    # 创建示例项目
    sample_project_dir = "sample_project"
    os.makedirs(sample_project_dir, exist_ok=True)
    
    # 创建示例代码文件
    vulnerable_code = """
import sqlite3
import requests

def login(username, password):
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # SQL注入漏洞
    query = "SELECT * FROM users WHERE username = '" + username + "' AND password = '" + password + "'"
    cursor.execute(query)
    
    user = cursor.fetchone()
    conn.close()
    
    return user

def fetch_data(url):
    # 不安全的请求
    response = requests.get(url, verify=False)
    return response.text
"""
    
    with open(os.path.join(sample_project_dir, "app.py"), 'w', encoding='utf-8') as f:
        f.write(vulnerable_code)
    
    # 创建示例依赖文件
    requirements = "requests==2.20.0\nurllib3==1.24.2\npillow==6.2.0\n"
    with open(os.path.join(sample_project_dir, "requirements.txt"), 'w', encoding='utf-8') as f:
        f.write(requirements)
    
    # 创建安全测试自动化框架
    automation = SecurityTestAutomation()
    
    # 运行各种安全测试
    automation.run_sast_scan(sample_project_dir)
    automation.run_dast_scan("https://httpbin.org/get")
    automation.run_dependency_check(os.path.join(sample_project_dir, "requirements.txt"))
    automation.run_container_security_scan("nginx:latest")
    
    # 生成安全仪表板
    dashboard = automation.generate_security_dashboard("security_dashboard.md")
    
    # 检查安全门禁
    passed = automation.set_security_gate(max_high_vulnerabilities=2, max_medium_vulnerabilities=5, max_low_vulnerabilities=10)
    
    # 清理示例文件
    try:
        for file in os.listdir(sample_project_dir):
            os.remove(os.path.join(sample_project_dir, file))
        os.rmdir(sample_project_dir)
    except:
        pass
    
    return automation


# ============================================================================
# 主函数：运行所有实验
# ============================================================================

def main():
    """运行所有实验"""
    print("安全测试 - 示例代码")
    print("=" * 50)
    
    # 运行所有实验
    demo_static_code_analysis()
    demo_dynamic_security_testing()
    demo_penetration_testing()
    demo_security_test_automation()
    
    print("\n所有实验已完成！")
    print("\n安全测试核心要点:")
    print("1. 结合静态和动态测试方法，全面覆盖安全风险")
    print("2. 定期更新漏洞库和测试工具，保持检测能力")
    print("3. 建立安全测试自动化流程，提高效率和一致性")
    print("4. 设置安全门禁，确保代码质量")
    print("5. 培养安全意识，将安全融入开发全过程")
    print("6. 及时修复漏洞，降低安全风险")
    print("7. 持续监控和评估安全状况")


if __name__ == "__main__":
    main()