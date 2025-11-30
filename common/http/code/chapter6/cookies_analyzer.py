#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP Cookies分析工具
用于解析和分析HTTP响应中的Cookie头部信息
"""

import re
from datetime import datetime
from typing import Dict, List, Optional
from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class CookieAttribute:
    """Cookie属性数据类"""
    name: str
    value: str
    domain: Optional[str] = None
    path: Optional[str] = None
    expires: Optional[datetime] = None
    max_age: Optional[int] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[str] = None


class CookiesAnalyzer:
    """Cookies分析工具类"""
    
    def __init__(self):
        # Cookie属性正则表达式
        self.cookie_patterns = {
            'domain': re.compile(r'Domain=([^;]*)', re.IGNORECASE),
            'path': re.compile(r'Path=([^;]*)', re.IGNORECASE),
            'expires': re.compile(r'Expires=([^;]*)', re.IGNORECASE),
            'max-age': re.compile(r'Max-Age=(\d+)', re.IGNORECASE),
            'secure': re.compile(r'Secure', re.IGNORECASE),
            'httponly': re.compile(r'HttpOnly', re.IGNORECASE),
            'samesite': re.compile(r'SameSite=(\w+)', re.IGNORECASE)
        }
    
    def parse_set_cookie_header(self, set_cookie_header: str) -> CookieAttribute:
        """
        解析Set-Cookie头部
        
        Args:
            set_cookie_header (str): Set-Cookie头部字符串
            
        Returns:
            CookieAttribute: 解析后的Cookie属性对象
        """
        # 分离Cookie名称/值和属性
        parts = set_cookie_header.split(';', 1)
        name_value = parts[0].strip()
        
        # 解析名称和值
        if '=' in name_value:
            name, value = name_value.split('=', 1)
        else:
            name, value = name_value, ''
        
        name = name.strip()
        value = value.strip()
        
        # 初始化Cookie属性
        cookie_attr = CookieAttribute(
            name=name,
            value=value
        )
        
        # 解析其他属性
        attributes = parts[1] if len(parts) > 1 else ""
        
        # 解析Domain
        domain_match = self.cookie_patterns['domain'].search(attributes)
        if domain_match:
            cookie_attr.domain = domain_match.group(1).strip()
        
        # 解析Path
        path_match = self.cookie_patterns['path'].search(attributes)
        if path_match:
            cookie_attr.path = path_match.group(1).strip()
        
        # 解析Expires
        expires_match = self.cookie_patterns['expires'].search(attributes)
        if expires_match:
            expires_str = expires_match.group(1).strip()
            try:
                cookie_attr.expires = datetime.strptime(expires_str, '%a, %d %b %Y %H:%M:%S GMT')
            except ValueError:
                pass  # 日期格式不正确
        
        # 解析Max-Age
        max_age_match = self.cookie_patterns['max-age'].search(attributes)
        if max_age_match:
            cookie_attr.max_age = int(max_age_match.group(1))
        
        # 解析Secure
        cookie_attr.secure = bool(self.cookie_patterns['secure'].search(attributes))
        
        # 解析HttpOnly
        cookie_attr.httponly = bool(self.cookie_patterns['httponly'].search(attributes))
        
        # 解析SameSite
        samesite_match = self.cookie_patterns['samesite'].search(attributes)
        if samesite_match:
            cookie_attr.samesite = samesite_match.group(1).strip()
        
        return cookie_attr
    
    def analyze_cookies_from_headers(self, headers: Dict[str, str]) -> List[CookieAttribute]:
        """
        从HTTP头部中分析Cookies
        
        Args:
            headers (Dict[str, str]): HTTP头部字典
            
        Returns:
            List[CookieAttribute]: 解析后的Cookie属性列表
        """
        cookies = []
        
        # 查找Set-Cookie头部
        for header_name, header_value in headers.items():
            if header_name.lower() == 'set-cookie':
                if isinstance(header_value, list):
                    # 多个Set-Cookie头部
                    for cookie_header in header_value:
                        cookie_attr = self.parse_set_cookie_header(cookie_header)
                        cookies.append(cookie_attr)
                else:
                    # 单个Set-Cookie头部
                    cookie_attr = self.parse_set_cookie_header(header_value)
                    cookies.append(cookie_attr)
        
        return cookies
    
    def analyze_security_features(self, cookie: CookieAttribute) -> Dict[str, bool]:
        """
        分析Cookie的安全特性
        
        Args:
            cookie (CookieAttribute): Cookie属性对象
            
        Returns:
            Dict[str, bool]: 安全特性分析结果
        """
        security_features = {
            'has_secure_flag': cookie.secure,
            'has_httponly_flag': cookie.httponly,
            'has_samesite_attribute': cookie.samesite is not None,
            'is_session_cookie': cookie.expires is None and cookie.max_age is None,
            'has_domain_restriction': cookie.domain is not None,
            'has_path_restriction': cookie.path is not None
        }
        
        return security_features
    
    def get_security_score(self, cookie: CookieAttribute) -> float:
        """
        计算Cookie的安全评分
        
        Args:
            cookie (CookieAttribute): Cookie属性对象
            
        Returns:
            float: 安全评分 (0-1)
        """
        security_features = self.analyze_security_features(cookie)
        
        # 安全特性权重
        weights = {
            'has_secure_flag': 0.25,
            'has_httponly_flag': 0.25,
            'has_samesite_attribute': 0.2,
            'has_domain_restriction': 0.15,
            'has_path_restriction': 0.15
        }
        
        score = 0.0
        for feature, weight in weights.items():
            if security_features.get(feature, False):
                score += weight
        
        return round(score, 2)
    
    def print_cookie_analysis(self, cookie: CookieAttribute):
        """
        打印Cookie详细分析
        
        Args:
            cookie (CookieAttribute): Cookie属性对象
        """
        print(f"\n=== Cookie分析报告 ===")
        print(f"名称: {cookie.name}")
        print(f"值: {cookie.value}")
        print(f"域名: {cookie.domain or '未设置'}")
        print(f"路径: {cookie.path or '未设置'}")
        print(f"过期时间: {cookie.expires or '会话Cookie'}")
        print(f"最大年龄: {cookie.max_age or '未设置'}秒")
        print(f"安全标志: {'是' if cookie.secure else '否'}")
        print(f"HTTP专用: {'是' if cookie.httponly else '否'}")
        print(f"SameSite: {cookie.samesite or '未设置'}")
        
        # 安全分析
        security_features = self.analyze_security_features(cookie)
        print(f"\n--- 安全性分析 ---")
        for feature, value in security_features.items():
            status = "✓" if value else "✗"
            print(f"{status} {feature}: {'是' if value else '否'}")
        
        # 安全评分
        score = self.get_security_score(cookie)
        print(f"\n安全评分: {score}/1.0")
        
        # 安全建议
        self._print_security_recommendations(cookie, security_features)
    
    def _print_security_recommendations(self, cookie: CookieAttribute, security_features: Dict[str, bool]):
        """
        打印安全建议
        
        Args:
            cookie (CookieAttribute): Cookie属性对象
            security_features (Dict[str, bool]): 安全特性分析结果
        """
        print(f"\n--- 安全建议 ---")
        
        if not security_features['has_secure_flag']:
            print("✗ 建议设置Secure标志以确保Cookie仅通过HTTPS传输")
        
        if not security_features['has_httponly_flag']:
            print("✗ 建议设置HttpOnly标志以防止XSS攻击")
        
        if not security_features['has_samesite_attribute']:
            print("✗ 建议设置SameSite属性以防止CSRF攻击")
        
        if not security_features['has_domain_restriction']:
            print("ⓘ 可考虑设置Domain属性以限制Cookie的作用域")
        
        if not security_features['has_path_restriction']:
            print("ⓘ 可考虑设置Path属性以限制Cookie的作用路径")


def demo_cookies_analyzer():
    """演示Cookies分析工具的使用"""
    analyzer = CookiesAnalyzer()
    
    # 模拟HTTP响应头部
    sample_headers = {
        'Set-Cookie': [
            'sessionid=abc123; Path=/; HttpOnly; Secure; SameSite=Lax',
            'theme=dark; Path=/; Max-Age=2592000; SameSite=Strict',
            'tracking=enabled; Path=/; Domain=example.com; Expires=Wed, 09 Jun 2024 10:18:14 GMT'
        ]
    }
    
    print("=== Cookies分析工具演示 ===")
    
    # 分析Cookies
    cookies = analyzer.analyze_cookies_from_headers(sample_headers)
    
    # 打印每个Cookie的分析结果
    for i, cookie in enumerate(cookies, 1):
        print(f"\n--- Cookie {i} ---")
        analyzer.print_cookie_analysis(cookie)


if __name__ == '__main__':
    demo_cookies_analyzer()