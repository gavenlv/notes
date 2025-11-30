#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookies安全分析工具
用于分析和评估网站Cookies的安全性
"""

import requests
import urllib.parse
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import hashlib
from datetime import datetime
import re


@dataclass
class CookieSecurityIssue:
    """Cookie安全问题"""
    severity: str  # high, medium, low
    issue_type: str
    description: str
    recommendation: str
    affected_cookies: List[str]


@dataclass
class CookieAnalysisResult:
    """Cookie分析结果"""
    url: str
    total_cookies: int
    secure_cookies: int
    httponly_cookies: int
    samesite_cookies: int
    issues: List[CookieSecurityIssue]
    cookie_details: List[Dict[str, any]]
    timestamp: str


class CookiesSecurityAnalyzer:
    """Cookies安全分析器"""
    
    def __init__(self):
        self.session = requests.Session()
        # 设置常见的浏览器User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_website_cookies(self, url: str, follow_redirects: bool = True) -> CookieAnalysisResult:
        """
        分析网站的Cookies安全性
        
        Args:
            url (str): 目标网站URL
            follow_redirects (bool): 是否跟随重定向
            
        Returns:
            CookieAnalysisResult: 分析结果
        """
        try:
            # 发送请求并获取响应
            response = self.session.get(url, allow_redirects=follow_redirects, timeout=10)
            
            # 分析Cookies
            cookie_details = self._extract_cookie_details(response)
            
            # 评估安全问题
            issues = self._evaluate_security_issues(cookie_details, url)
            
            # 统计信息
            total_cookies = len(cookie_details)
            secure_cookies = sum(1 for cookie in cookie_details if cookie.get('secure', False))
            httponly_cookies = sum(1 for cookie in cookie_details if cookie.get('httponly', False))
            samesite_cookies = sum(1 for cookie in cookie_details if cookie.get('samesite') != 'None')
            
            return CookieAnalysisResult(
                url=url,
                total_cookies=total_cookies,
                secure_cookies=secure_cookies,
                httponly_cookies=httponly_cookies,
                samesite_cookies=samesite_cookies,
                issues=issues,
                cookie_details=cookie_details,
                timestamp=datetime.now().isoformat()
            )
            
        except Exception as e:
            raise Exception(f"分析网站Cookies时发生错误: {str(e)}")
    
    def _extract_cookie_details(self, response) -> List[Dict[str, any]]:
        """
        提取响应中的Cookie详细信息
        
        Args:
            response: HTTP响应对象
            
        Returns:
            List[Dict[str, any]]: Cookie详情列表
        """
        cookie_details = []
        
        # 从Set-Cookie头部提取Cookie信息
        if 'Set-Cookie' in response.headers:
            set_cookie_headers = response.headers.get_all('Set-Cookie') if hasattr(response.headers, 'get_all') else [response.headers['Set-Cookie']]
            
            for cookie_header in set_cookie_headers:
                cookie_detail = self._parse_set_cookie_header(cookie_header)
                if cookie_detail:
                    cookie_details.append(cookie_detail)
        
        return cookie_details
    
    def _parse_set_cookie_header(self, cookie_header: str) -> Optional[Dict[str, any]]:
        """
        解析Set-Cookie头部
        
        Args:
            cookie_header (str): Set-Cookie头部字符串
            
        Returns:
            Optional[Dict[str, any]]: 解析后的Cookie信息
        """
        try:
            # 分离Cookie名值对和属性
            parts = cookie_header.split(';')
            if not parts:
                return None
            
            # 解析Cookie名值对
            name_value = parts[0].strip()
            if '=' not in name_value:
                return None
                
            name, value = name_value.split('=', 1)
            cookie_info = {
                'name': name.strip(),
                'value': value.strip(),
                'domain': '',
                'path': '/',
                'expires': '',
                'max_age': '',
                'secure': False,
                'httponly': False,
                'samesite': 'None'
            }
            
            # 解析其他属性
            for part in parts[1:]:
                part = part.strip().lower()
                if part.startswith('domain='):
                    cookie_info['domain'] = part[7:].strip()
                elif part.startswith('path='):
                    cookie_info['path'] = part[5:].strip()
                elif part.startswith('expires='):
                    cookie_info['expires'] = part[8:].strip()
                elif part.startswith('max-age='):
                    cookie_info['max_age'] = part[8:].strip()
                elif part == 'secure':
                    cookie_info['secure'] = True
                elif part == 'httponly':
                    cookie_info['httponly'] = True
                elif part.startswith('samesite='):
                    cookie_info['samesite'] = part[9:].strip().capitalize()
            
            return cookie_info
            
        except Exception as e:
            print(f"解析Cookie头部时发生错误: {str(e)}")
            return None
    
    def _evaluate_security_issues(self, cookie_details: List[Dict[str, any]], url: str) -> List[CookieSecurityIssue]:
        """
        评估Cookie安全问题
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            url (str): 目标URL
            
        Returns:
            List[CookieSecurityIssue]: 安全问题列表
        """
        issues = []
        insecure_cookies = []
        httponly_missing_cookies = []
        samesite_missing_cookies = []
        
        # 检查每个Cookie的安全属性
        for cookie in cookie_details:
            name = cookie['name']
            
            # 检查Secure属性
            if not cookie.get('secure', False):
                insecure_cookies.append(name)
            
            # 检查HttpOnly属性
            if not cookie.get('httponly', False):
                httponly_missing_cookies.append(name)
            
            # 检查SameSite属性
            if cookie.get('samesite', 'None') == 'None':
                samesite_missing_cookies.append(name)
        
        # 生成安全问题报告
        if insecure_cookies:
            issues.append(CookieSecurityIssue(
                severity='high',
                issue_type='missing_secure_flag',
                description=f'以下Cookies缺少Secure标志，可能通过非HTTPS连接传输: {", ".join(insecure_cookies)}',
                recommendation='为所有Cookies设置Secure标志，确保只通过HTTPS传输',
                affected_cookies=insecure_cookies
            ))
        
        if httponly_missing_cookies:
            issues.append(CookieSecurityIssue(
                severity='medium',
                issue_type='missing_httponly_flag',
                description=f'以下Cookies缺少HttpOnly标志，可能受到XSS攻击: {", ".join(httponly_missing_cookies)}',
                recommendation='为敏感Cookies设置HttpOnly标志，防止JavaScript访问',
                affected_cookies=httponly_missing_cookies
            ))
        
        if samesite_missing_cookies:
            issues.append(CookieSecurityIssue(
                severity='medium',
                issue_type='missing_samesite_attribute',
                description=f'以下Cookies缺少SameSite属性，可能受到CSRF攻击: {", ".join(samesite_missing_cookies)}',
                recommendation='为Cookies设置SameSite=Lax或SameSite=Strict属性',
                affected_cookies=samesite_missing_cookies
            ))
        
        # 检查Cookie命名安全性
        weak_named_cookies = self._check_cookie_naming_security(cookie_details)
        if weak_named_cookies:
            issues.append(CookieSecurityIssue(
                severity='low',
                issue_type='weak_cookie_naming',
                description=f'以下Cookies使用了不安全的命名方式: {", ".join(weak_named_cookies)}',
                recommendation='避免在Cookie名称中暴露敏感信息，如"user", "admin", "session"等',
                affected_cookies=weak_named_cookies
            ))
        
        # 检查Cookie值安全性
        unsafe_value_cookies = self._check_cookie_value_security(cookie_details)
        if unsafe_value_cookies:
            issues.append(CookieSecurityIssue(
                severity='medium',
                issue_type='unsafe_cookie_values',
                description=f'以下Cookies的值可能存在安全隐患: {", ".join(unsafe_value_cookies)}',
                recommendation='避免在Cookie值中存储敏感信息，如用户ID、权限等',
                affected_cookies=unsafe_value_cookies
            ))
        
        return issues
    
    def _check_cookie_naming_security(self, cookie_details: List[Dict[str, any]]) -> List[str]:
        """
        检查Cookie命名安全性
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            
        Returns:
            List[str]: 不安全命名的Cookie名称列表
        """
        unsafe_names = []
        # 常见的不安全Cookie名称模式
        unsafe_patterns = [
            r'user.*',
            r'admin.*',
            r'session.*',
            r'auth.*',
            r'token.*',
            r'password.*',
            r'credit.*',
            r'bank.*'
        ]
        
        for cookie in cookie_details:
            name = cookie['name'].lower()
            for pattern in unsafe_patterns:
                if re.match(pattern, name):
                    unsafe_names.append(cookie['name'])
                    break
        
        return unsafe_names
    
    def _check_cookie_value_security(self, cookie_details: List[Dict[str, any]]) -> List[str]:
        """
        检查Cookie值安全性
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            
        Returns:
            List[str]: 值存在安全隐患的Cookie名称列表
        """
        unsafe_values = []
        
        for cookie in cookie_details:
            value = cookie['value'].lower()
            name = cookie['name'].lower()
            
            # 检查是否包含明显的敏感信息
            sensitive_patterns = [
                r'^[0-9]{4,}$',  # 看起来像用户ID或账号
                r'[a-f0-9]{32}',  # MD5哈希
                r'[a-f0-9]{40}',  # SHA1哈希
                r'[a-f0-9]{64}',  # SHA256哈希
                r'(admin|root|super)',  # 管理员相关
                r'(password|passwd|pwd)',  # 密码相关
                r'(credit|card|bank)'  # 金融相关
            ]
            
            for pattern in sensitive_patterns:
                if re.search(pattern, value):
                    unsafe_values.append(cookie['name'])
                    break
            
            # 特殊检查：如果Cookie名称暗示它应该是安全的，但值看起来像明文
            if any(keyword in name for keyword in ['token', 'session', 'auth']) and \
               len(value) < 50 and not re.match(r'^[a-f0-9]+$', value):
                unsafe_values.append(cookie['name'])
        
        return unsafe_values
    
    def generate_security_report(self, analysis_result: CookieAnalysisResult) -> str:
        """
        生成安全分析报告
        
        Args:
            analysis_result (CookieAnalysisResult): 分析结果
            
        Returns:
            str: 格式化的安全报告
        """
        report = []
        report.append("=" * 60)
        report.append("COOKIES安全分析报告")
        report.append("=" * 60)
        report.append(f"目标网站: {analysis_result.url}")
        report.append(f"分析时间: {analysis_result.timestamp}")
        report.append("")
        
        # 基本统计
        report.append("基本统计:")
        report.append(f"  总Cookies数: {analysis_result.total_cookies}")
        report.append(f"  Secure Cookies: {analysis_result.secure_cookies}/{analysis_result.total_cookies}")
        report.append(f"  HttpOnly Cookies: {analysis_result.httponly_cookies}/{analysis_result.total_cookies}")
        report.append(f"  SameSite Cookies: {analysis_result.samesite_cookies}/{analysis_result.total_cookies}")
        report.append("")
        
        # 安全等级评估
        security_score = self._calculate_security_score(analysis_result)
        report.append(f"安全评分: {security_score}/100")
        report.append(f"安全等级: {self._get_security_level(security_score)}")
        report.append("")
        
        # 安全问题详情
        if analysis_result.issues:
            report.append("发现的安全问题:")
            for i, issue in enumerate(analysis_result.issues, 1):
                severity_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}[issue.severity]
                report.append(f"  {i}. [{severity_icon}] {issue.issue_type}")
                report.append(f"     描述: {issue.description}")
                report.append(f"     建议: {issue.recommendation}")
                report.append(f"     影响Cookies: {', '.join(issue.affected_cookies)}")
                report.append("")
        else:
            report.append("✅ 未发现明显安全问题")
            report.append("")
        
        # Cookie详情
        report.append("Cookies详情:")
        for cookie in analysis_result.cookie_details:
            report.append(f"  名称: {cookie['name']}")
            report.append(f"    值: {cookie['value'][:50]}{'...' if len(cookie['value']) > 50 else ''}")
            report.append(f"    Domain: {cookie['domain']}")
            report.append(f"    Path: {cookie['path']}")
            report.append(f"    Secure: {'✅' if cookie.get('secure') else '❌'}")
            report.append(f"    HttpOnly: {'✅' if cookie.get('httponly') else '❌'}")
            report.append(f"    SameSite: {cookie.get('samesite', 'None')}")
            report.append("")
        
        return "\n".join(report)
    
    def _calculate_security_score(self, analysis_result: CookieAnalysisResult) -> int:
        """
        计算安全评分
        
        Args:
            analysis_result (CookieAnalysisResult): 分析结果
            
        Returns:
            int: 安全评分 (0-100)
        """
        if analysis_result.total_cookies == 0:
            return 100
        
        score = 100
        
        # Secure标志缺失扣分
        missing_secure = analysis_result.total_cookies - analysis_result.secure_cookies
        score -= missing_secure * 10
        
        # HttpOnly标志缺失扣分
        missing_httponly = analysis_result.total_cookies - analysis_result.httponly_cookies
        score -= missing_httponly * 5
        
        # SameSite属性缺失扣分
        missing_samesite = analysis_result.total_cookies - analysis_result.samesite_cookies
        score -= missing_samesite * 3
        
        # 高危问题额外扣分
        high_severity_issues = sum(1 for issue in analysis_result.issues if issue.severity == 'high')
        score -= high_severity_issues * 15
        
        # 中等风险问题扣分
        medium_severity_issues = sum(1 for issue in analysis_result.issues if issue.severity == 'medium')
        score -= medium_severity_issues * 5
        
        return max(0, min(100, score))
    
    def _get_security_level(self, score: int) -> str:
        """
        根据评分获取安全等级
        
        Args:
            score (int): 安全评分
            
        Returns:
            str: 安全等级描述
        """
        if score >= 90:
            return "优秀 (Excellent)"
        elif score >= 70:
            return "良好 (Good)"
        elif score >= 50:
            return "一般 (Fair)"
        elif score >= 30:
            return "较差 (Poor)"
        else:
            return "危险 (Critical)"


def demo_cookies_security_analysis():
    """演示Cookies安全分析工具的使用"""
    print("Cookies安全分析工具演示")
    print("=" * 40)
    
    # 创建分析器实例
    analyzer = CookiesSecurityAnalyzer()
    
    # 示例1: 分析本地测试服务器
    try:
        print("\n1. 分析本地测试服务器...")
        # 这里我们模拟一个简单的分析过程
        # 在实际使用中，您需要有一个正在运行的服务器来测试
        
        # 创建模拟的分析结果
        mock_cookie_details = [
            {
                'name': 'sessionid',
                'value': 'abc123xyz',
                'domain': 'localhost',
                'path': '/',
                'secure': False,
                'httponly': True,
                'samesite': 'Lax'
            },
            {
                'name': 'user_pref',
                'value': 'theme=dark',
                'domain': 'localhost',
                'path': '/',
                'secure': False,
                'httponly': False,
                'samesite': 'None'
            },
            {
                'name': 'tracking_id',
                'value': 'track987654321',
                'domain': 'localhost',
                'path': '/',
                'secure': True,
                'httponly': False,
                'samesite': 'None'
            }
        ]
        
        mock_issues = [
            CookieSecurityIssue(
                severity='high',
                issue_type='missing_secure_flag',
                description='Cookies缺少Secure标志，可能通过非HTTPS连接传输: sessionid, user_pref',
                recommendation='为所有Cookies设置Secure标志，确保只通过HTTPS传输',
                affected_cookies=['sessionid', 'user_pref']
            ),
            CookieSecurityIssue(
                severity='medium',
                issue_type='missing_httponly_flag',
                description='Cookies缺少HttpOnly标志，可能受到XSS攻击: user_pref, tracking_id',
                recommendation='为敏感Cookies设置HttpOnly标志，防止JavaScript访问',
                affected_cookies=['user_pref', 'tracking_id']
            ),
            CookieSecurityIssue(
                severity='medium',
                issue_type='missing_samesite_attribute',
                description='Cookies缺少SameSite属性，可能受到CSRF攻击: user_pref, tracking_id',
                recommendation='为Cookies设置SameSite=Lax或SameSite=Strict属性',
                affected_cookies=['user_pref', 'tracking_id']
            )
        ]
        
        mock_result = CookieAnalysisResult(
            url='http://localhost:5000',
            total_cookies=3,
            secure_cookies=1,
            httponly_cookies=1,
            samesite_cookies=1,
            issues=mock_issues,
            cookie_details=mock_cookie_details,
            timestamp=datetime.now().isoformat()
        )
        
        # 生成并打印报告
        report = analyzer.generate_security_report(mock_result)
        print(report)
        
    except Exception as e:
        print(f"分析过程中发生错误: {str(e)}")
    
    # 示例2: 展示如何分析真实网站
    print("\n2. 如何分析真实网站:")
    print("   analyzer = CookiesSecurityAnalyzer()")
    print("   result = analyzer.analyze_website_cookies('https://example.com')")
    print("   report = analyzer.generate_security_report(result)")
    print("   print(report)")
    
    # 安全建议总结
    print("\n" + "=" * 60)
    print("COOKIES安全最佳实践总结:")
    print("=" * 60)
    print("1. 始终设置Secure标志")
    print("2. 为敏感Cookies设置HttpOnly标志")
    print("3. 使用SameSite属性防止CSRF攻击")
    print("4. 避免在Cookie名称和值中暴露敏感信息")
    print("5. 限制Cookie的作用域(Domain和Path)")
    print("6. 设置合适的过期时间")
    print("7. 对Cookie值进行加密或签名")
    print("8. 定期审计和监控Cookies使用情况")


if __name__ == '__main__':
    demo_cookies_security_analysis()