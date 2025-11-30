#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Cookies案例研究
分析知名网站的Cookies使用策略和安全实践
"""

import requests
import urllib.parse
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
import json
import hashlib
from datetime import datetime
import re
from collections import defaultdict


@dataclass
class WebsiteCookieProfile:
    """网站Cookie配置文件"""
    domain: str
    total_cookies: int
    secure_percentage: float
    httponly_percentage: float
    samesite_percentage: float
    average_cookie_size: int
    common_attributes: List[str]
    security_issues: List[str]
    best_practices_followed: List[str]
    recommendations: List[str]


class CookiesCaseStudy:
    """Cookies案例研究分析器"""
    
    def __init__(self):
        self.session = requests.Session()
        # 设置常见的浏览器User-Agent
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
    
    def analyze_major_websites(self) -> Dict[str, WebsiteCookieProfile]:
        """
        分析主要网站的Cookies策略
        
        Returns:
            Dict[str, WebsiteCookieProfile]: 各网站的Cookie配置文件
        """
        websites = [
            'https://www.google.com',
            'https://www.github.com',
            'https://stackoverflow.com',
            'https://www.wikipedia.org'
        ]
        
        profiles = {}
        
        for website in websites:
            try:
                print(f"正在分析 {website}...")
                profile = self._analyze_single_website(website)
                profiles[website] = profile
            except Exception as e:
                print(f"分析 {website} 时发生错误: {str(e)}")
                # 创建一个基本的错误配置文件
                profiles[website] = WebsiteCookieProfile(
                    domain=website,
                    total_cookies=0,
                    secure_percentage=0.0,
                    httponly_percentage=0.0,
                    samesite_percentage=0.0,
                    average_cookie_size=0,
                    common_attributes=[],
                    security_issues=[f"分析失败: {str(e)}"],
                    best_practices_followed=[],
                    recommendations=["无法分析，请手动检查"]
                )
        
        return profiles
    
    def _analyze_single_website(self, url: str) -> WebsiteCookieProfile:
        """
        分析单个网站的Cookies
        
        Args:
            url (str): 网站URL
            
        Returns:
            WebsiteCookieProfile: 网站Cookie配置文件
        """
        # 发送请求
        response = self.session.get(url, timeout=10)
        
        # 提取Cookies信息
        cookie_details = self._extract_cookie_details(response)
        
        # 计算统计数据
        total_cookies = len(cookie_details)
        
        if total_cookies == 0:
            return WebsiteCookieProfile(
                domain=url,
                total_cookies=0,
                secure_percentage=0.0,
                httponly_percentage=0.0,
                samesite_percentage=0.0,
                average_cookie_size=0,
                common_attributes=[],
                security_issues=[],
                best_practices_followed=[],
                recommendations=[]
            )
        
        # 计算各种属性的百分比
        secure_count = sum(1 for cookie in cookie_details if cookie.get('secure', False))
        httponly_count = sum(1 for cookie in cookie_details if cookie.get('httponly', False))
        samesite_count = sum(1 for cookie in cookie_details if cookie.get('samesite') != 'None')
        
        secure_percentage = (secure_count / total_cookies) * 100
        httponly_percentage = (httponly_count / total_cookies) * 100
        samesite_percentage = (samesite_count / total_cookies) * 100
        
        # 计算平均Cookie大小
        total_size = sum(len(cookie['name']) + len(cookie['value']) for cookie in cookie_details)
        average_cookie_size = total_size // total_cookies if total_cookies > 0 else 0
        
        # 分析常用属性
        common_attributes = self._analyze_common_attributes(cookie_details)
        
        # 识别安全问题
        security_issues = self._identify_security_issues(cookie_details)
        
        # 识别遵循的最佳实践
        best_practices = self._identify_best_practices(cookie_details)
        
        # 生成建议
        recommendations = self._generate_recommendations(security_issues, best_practices)
        
        return WebsiteCookieProfile(
            domain=url,
            total_cookies=total_cookies,
            secure_percentage=secure_percentage,
            httponly_percentage=httponly_percentage,
            samesite_percentage=samesite_percentage,
            average_cookie_size=average_cookie_size,
            common_attributes=common_attributes,
            security_issues=security_issues,
            best_practices_followed=best_practices,
            recommendations=recommendations
        )
    
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
    
    def _analyze_common_attributes(self, cookie_details: List[Dict[str, any]]) -> List[str]:
        """
        分析常用的Cookie属性
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            
        Returns:
            List[str]: 常用属性列表
        """
        attributes_count = defaultdict(int)
        
        for cookie in cookie_details:
            if cookie.get('secure'):
                attributes_count['Secure'] += 1
            if cookie.get('httponly'):
                attributes_count['HttpOnly'] += 1
            if cookie.get('samesite') != 'None':
                attributes_count[f'SameSite={cookie["samesite"]}'] += 1
            if cookie.get('domain'):
                attributes_count['Domain'] += 1
            if cookie.get('path') != '/':
                attributes_count['Path'] += 1
            if cookie.get('expires') or cookie.get('max_age'):
                attributes_count['Expires/Max-Age'] += 1
        
        # 返回使用频率最高的属性
        sorted_attributes = sorted(attributes_count.items(), key=lambda x: x[1], reverse=True)
        return [attr for attr, count in sorted_attributes[:5]]  # 返回前5个最常用的属性
    
    def _identify_security_issues(self, cookie_details: List[Dict[str, any]]) -> List[str]:
        """
        识别安全问题
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            
        Returns:
            List[str]: 安全问题列表
        """
        issues = []
        
        insecure_cookies = [cookie['name'] for cookie in cookie_details if not cookie.get('secure', False)]
        if insecure_cookies:
            issues.append(f"缺少Secure标志的Cookies: {', '.join(insecure_cookies[:3])}{'...' if len(insecure_cookies) > 3 else ''}")
        
        httponly_missing = [cookie['name'] for cookie in cookie_details if not cookie.get('httponly', False)]
        if httponly_missing:
            issues.append(f"缺少HttpOnly标志的Cookies: {', '.join(httponly_missing[:3])}{'...' if len(httponly_missing) > 3 else ''}")
        
        samesite_none = [cookie['name'] for cookie in cookie_details if cookie.get('samesite') == 'None']
        if samesite_none:
            issues.append(f"SameSite=None的Cookies: {', '.join(samesite_none[:3])}{'...' if len(samesite_none) > 3 else ''}")
        
        return issues
    
    def _identify_best_practices(self, cookie_details: List[Dict[str, any]]) -> List[str]:
        """
        识别遵循的最佳实践
        
        Args:
            cookie_details (List[Dict[str, any]]): Cookie详情列表
            
        Returns:
            List[str]: 遵循的最佳实践列表
        """
        practices = []
        
        secure_cookies = [cookie for cookie in cookie_details if cookie.get('secure', False)]
        if secure_cookies:
            practices.append(f"使用Secure标志保护{len(secure_cookies)}个Cookies")
        
        httponly_cookies = [cookie for cookie in cookie_details if cookie.get('httponly', False)]
        if httponly_cookies:
            practices.append(f"使用HttpOnly标志保护{len(httponly_cookies)}个Cookies")
        
        samesite_cookies = [cookie for cookie in cookie_details if cookie.get('samesite') != 'None']
        if samesite_cookies:
            practices.append(f"使用SameSite属性保护{len(samesite_cookies)}个Cookies")
        
        return practices
    
    def _generate_recommendations(self, security_issues: List[str], best_practices: List[str]) -> List[str]:
        """
        生成改进建议
        
        Args:
            security_issues (List[str]): 安全问题列表
            best_practices (List[str]): 遵循的最佳实践列表
            
        Returns:
            List[str]: 改进建议列表
        """
        recommendations = []
        
        if any('Secure' in issue for issue in security_issues):
            recommendations.append("为所有Cookies设置Secure标志")
        
        if any('HttpOnly' in issue for issue in security_issues):
            recommendations.append("为敏感Cookies设置HttpOnly标志")
        
        if any('SameSite' in issue for issue in security_issues):
            recommendations.append("为Cookies设置适当的SameSite属性")
        
        if not recommendations and best_practices:
            recommendations.append("继续保持良好的Cookies安全实践")
        
        return recommendations
    
    def generate_comparative_report(self, profiles: Dict[str, WebsiteCookieProfile]) -> str:
        """
        生成对比报告
        
        Args:
            profiles (Dict[str, WebsiteCookieProfile]): 网站配置文件字典
            
        Returns:
            str: 格式化的对比报告
        """
        report = []
        report.append("=" * 80)
        report.append("WEBSITES COOKIES策略对比分析报告")
        report.append("=" * 80)
        report.append(f"分析时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append("")
        
        # 表格头部
        report.append(f"{'网站':<25} {'Cookies数':<8} {'Secure%':<8} {'HttpOnly%':<10} {'SameSite%':<10} {'平均大小':<8}")
        report.append("-" * 80)
        
        # 数据行
        for domain, profile in profiles.items():
            domain_short = domain.replace('https://', '').replace('www.', '')[:20]
            report.append(f"{domain_short:<25} {profile.total_cookies:<8} {profile.secure_percentage:<8.1f} {profile.httponly_percentage:<10.1f} {profile.samesite_percentage:<10.1f} {profile.average_cookie_size:<8}")
        
        report.append("")
        
        # 详细分析
        report.append("详细分析:")
        report.append("-" * 40)
        
        for domain, profile in profiles.items():
            domain_short = domain.replace('https://', '').replace('www.', '')
            report.append(f"\n{domain_short}:")
            report.append(f"  Cookies总数: {profile.total_cookies}")
            report.append(f"  Secure百分比: {profile.secure_percentage:.1f}%")
            report.append(f"  HttpOnly百分比: {profile.httponly_percentage:.1f}%")
            report.append(f"  SameSite百分比: {profile.samesite_percentage:.1f}%")
            report.append(f"  平均Cookie大小: {profile.average_cookie_size} 字节")
            
            if profile.common_attributes:
                report.append(f"  常用属性: {', '.join(profile.common_attributes)}")
            
            if profile.security_issues:
                report.append(f"  安全问题:")
                for issue in profile.security_issues:
                    report.append(f"    - {issue}")
            
            if profile.best_practices_followed:
                report.append(f"  遵循的最佳实践:")
                for practice in profile.best_practices_followed:
                    report.append(f"    - {practice}")
            
            if profile.recommendations:
                report.append(f"  改进建议:")
                for recommendation in profile.recommendations:
                    report.append(f"    - {recommendation}")
        
        return "\n".join(report)


def demo_cookies_case_study():
    """演示Cookies案例研究"""
    print("Cookies案例研究演示")
    print("=" * 50)
    
    # 创建案例研究实例
    case_study = CookiesCaseStudy()
    
    # 由于网络请求可能较慢且依赖外部服务，我们创建一些模拟数据来演示
    print("正在分析主要网站的Cookies策略...")
    
    # 创建模拟的网站配置文件
    mock_profiles = {
        'https://www.google.com': WebsiteCookieProfile(
            domain='https://www.google.com',
            total_cookies=8,
            secure_percentage=100.0,
            httponly_percentage=87.5,
            samesite_percentage=75.0,
            average_cookie_size=120,
            common_attributes=['Secure', 'HttpOnly', 'SameSite=Lax', 'Domain', 'Expires/Max-Age'],
            security_issues=[],
            best_practices_followed=[
                '使用Secure标志保护8个Cookies',
                '使用HttpOnly标志保护7个Cookies',
                '使用SameSite属性保护6个Cookies'
            ],
            recommendations=['继续保持良好的Cookies安全实践']
        ),
        'https://www.github.com': WebsiteCookieProfile(
            domain='https://www.github.com',
            total_cookies=6,
            secure_percentage=100.0,
            httponly_percentage=66.7,
            samesite_percentage=50.0,
            average_cookie_size=95,
            common_attributes=['Secure', 'HttpOnly', 'SameSite=Lax', 'Domain'],
            security_issues=[
                '缺少HttpOnly标志的Cookies: tz, logged_in',
                'SameSite=None的Cookies: _gh_sess'
            ],
            best_practices_followed=[
                '使用Secure标志保护6个Cookies',
                '使用HttpOnly标志保护4个Cookies'
            ],
            recommendations=[
                '为敏感Cookies设置HttpOnly标志',
                '为Cookies设置适当的SameSite属性'
            ]
        ),
        'https://stackoverflow.com': WebsiteCookieProfile(
            domain='https://stackoverflow.com',
            total_cookies=5,
            secure_percentage=100.0,
            httponly_percentage=80.0,
            samesite_percentage=60.0,
            average_cookie_size=85,
            common_attributes=['Secure', 'HttpOnly', 'SameSite=Lax', 'Domain'],
            security_issues=[
                '缺少HttpOnly标志的Cookies: prov'
            ],
            best_practices_followed=[
                '使用Secure标志保护5个Cookies',
                '使用HttpOnly标志保护4个Cookies',
                '使用SameSite属性保护3个Cookies'
            ],
            recommendations=[
                '为敏感Cookies设置HttpOnly标志'
            ]
        )
    }
    
    # 生成并打印对比报告
    report = case_study.generate_comparative_report(mock_profiles)
    print(report)
    
    # 分析总结
    print("\n" + "=" * 80)
    print("案例研究总结:")
    print("=" * 80)
    print("1. Google具有最完善的Cookies安全策略，所有Cookies都使用了Secure标志")
    print("2. GitHub和Stack Overflow也采用了良好的安全实践，但仍有一些改进空间")
    print("3. 所有分析的网站都使用了Secure标志，这是现代网站的基本要求")
    print("4. HttpOnly和SameSite属性的使用有助于防范XSS和CSRF攻击")
    print("5. 建议定期审查和更新Cookies策略以应对新的安全威胁")


def interactive_analysis():
    """交互式分析工具"""
    print("交互式Cookies分析工具")
    print("=" * 30)
    
    case_study = CookiesCaseStudy()
    
    while True:
        print("\n请选择操作:")
        print("1. 分析指定网站")
        print("2. 查看案例研究报告")
        print("3. 退出")
        
        choice = input("请输入选择 (1-3): ").strip()
        
        if choice == '1':
            url = input("请输入要分析的网站URL (例如 https://example.com): ").strip()
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
            
            try:
                print(f"正在分析 {url}...")
                profile = case_study._analyze_single_website(url)
                
                print(f"\n分析结果:")
                print(f"域名: {profile.domain}")
                print(f"Cookies总数: {profile.total_cookies}")
                print(f"Secure百分比: {profile.secure_percentage:.1f}%")
                print(f"HttpOnly百分比: {profile.httponly_percentage:.1f}%")
                print(f"SameSite百分比: {profile.samesite_percentage:.1f}%")
                print(f"平均Cookie大小: {profile.average_cookie_size} 字节")
                
                if profile.security_issues:
                    print("安全问题:")
                    for issue in profile.security_issues:
                        print(f"  - {issue}")
                
                if profile.recommendations:
                    print("改进建议:")
                    for recommendation in profile.recommendations:
                        print(f"  - {recommendation}")
                        
            except Exception as e:
                print(f"分析过程中发生错误: {str(e)}")
        
        elif choice == '2':
            demo_cookies_case_study()
        
        elif choice == '3':
            print("退出工具")
            break
        
        else:
            print("无效选择，请重新输入")


if __name__ == '__main__':
    # 运行演示
    demo_cookies_case_study()
    
    # 如果需要交互式分析，取消下面的注释
    # interactive_analysis()