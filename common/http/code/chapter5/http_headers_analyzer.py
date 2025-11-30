#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP头部分析工具
用于分析网站的HTTP头部设置情况，包括安全头部和缓存头部
"""

import requests
import json
from urllib.parse import urlparse
from typing import Dict, List, Optional
import argparse


class HttpHeadersAnalyzer:
    """HTTP头部分析器"""
    
    def __init__(self, url: str, timeout: int = 10):
        """
        初始化分析器
        
        Args:
            url: 要分析的URL
            timeout: 请求超时时间（秒）
        """
        self.url = url
        self.timeout = timeout
        self.response = None
        self.headers = {}
    
    def fetch_headers(self) -> Optional[Dict]:
        """
        获取URL的HTTP头部
        
        Returns:
            头部字典或None（如果获取失败）
        """
        try:
            # 使用HEAD请求获取头部信息
            self.response = requests.head(
                self.url, 
                timeout=self.timeout, 
                allow_redirects=True,
                headers={
                    'User-Agent': 'HTTP-Headers-Analyzer/1.0'
                }
            )
            self.headers = self.response.headers
            return dict(self.headers)
        except requests.exceptions.RequestException as e:
            print(f"获取头部失败: {e}")
            # 如果HEAD请求失败，尝试GET请求
            try:
                self.response = requests.get(
                    self.url, 
                    timeout=self.timeout, 
                    allow_redirects=True,
                    headers={
                        'User-Agent': 'HTTP-Headers-Analyzer/1.0'
                    }
                )
                self.headers = self.response.headers
                return dict(self.headers)
            except requests.exceptions.RequestException as e2:
                print(f"GET请求也失败: {e2}")
                return None
    
    def analyze_security_headers(self) -> Dict[str, any]:
        """
        分析安全相关头部
        
        Returns:
            安全头部分析结果
        """
        if not self.headers:
            self.fetch_headers()
        
        if not self.headers:
            return {"error": "无法获取头部信息"}
        
        # 定义重要的安全头部
        security_headers = {
            'Strict-Transport-Security': {
                'description': 'HSTS头部，强制HTTPS连接',
                'recommended': True,
                'details': '格式: max-age=<seconds>; includeSubDomains; preload'
            },
            'X-Content-Type-Options': {
                'description': '防止MIME类型嗅探',
                'recommended': True,
                'details': '推荐值: nosniff'
            },
            'X-Frame-Options': {
                'description': '防止点击劫持',
                'recommended': True,
                'details': '可选值: DENY, SAMEORIGIN, ALLOW-FROM uri'
            },
            'X-XSS-Protection': {
                'description': 'XSS保护（现代浏览器已逐渐弃用）',
                'recommended': False,
                'details': '推荐使用CSP替代'
            },
            'Content-Security-Policy': {
                'description': '内容安全策略，防止XSS等攻击',
                'recommended': True,
                'details': '定义允许加载的资源来源'
            },
            'Content-Security-Policy-Report-Only': {
                'description': 'CSP报告模式，不阻止只报告',
                'recommended': False,
                'details': '用于测试CSP策略'
            },
            'Expect-CT': {
                'description': '证书透明度执行',
                'recommended': False,
                'details': '确保使用了证书透明度'
            },
            'Feature-Policy': {
                'description': '功能策略（已废弃，被Permissions-Policy替代）',
                'recommended': False,
                'details': '控制浏览器功能的使用'
            },
            'Permissions-Policy': {
                'description': '权限策略，控制浏览器功能的使用',
                'recommended': True,
                'details': '替代Feature-Policy的新标准'
            },
            'Referrer-Policy': {
                'description': '控制Referer头部的发送',
                'recommended': True,
                'details': '可选值: no-referrer, no-referrer-when-downgrade等'
            }
        }
        
        results = {}
        for header, info in security_headers.items():
            value = self.headers.get(header)
            results[header] = {
                'present': value is not None,
                'value': value,
                'description': info['description'],
                'recommended': info['recommended'],
                'details': info['details']
            }
        
        return results
    
    def analyze_cache_headers(self) -> Dict[str, any]:
        """
        分析缓存相关头部
        
        Returns:
            缓存头部分析结果
        """
        if not self.headers:
            self.fetch_headers()
        
        if not self.headers:
            return {"error": "无法获取头部信息"}
        
        # 定义缓存相关头部
        cache_headers = {
            'Cache-Control': {
                'description': '缓存控制指令',
                'important': True
            },
            'Expires': {
                'description': '过期时间',
                'important': True
            },
            'Last-Modified': {
                'description': '最后修改时间',
                'important': True
            },
            'ETag': {
                'description': '实体标签',
                'important': True
            },
            'Age': {
                'description': '响应年龄',
                'important': False
            },
            'Vary': {
                'description': '缓存键变化依据',
                'important': True
            }
        }
        
        results = {}
        for header, info in cache_headers.items():
            value = self.headers.get(header)
            results[header] = {
                'present': value is not None,
                'value': value,
                'description': info['description'],
                'important': info['important']
            }
        
        # 分析缓存控制策略
        cache_control = self.headers.get('Cache-Control', '')
        results['cache_strategy'] = self._analyze_cache_strategy(cache_control)
        
        return results
    
    def _analyze_cache_strategy(self, cache_control: str) -> Dict[str, any]:
        """
        分析缓存控制策略
        
        Args:
            cache_control: Cache-Control头部值
            
        Returns:
            缓存策略分析结果
        """
        if not cache_control:
            return {
                'strategy': '未设置',
                'details': '没有设置缓存控制指令'
            }
        
        directives = [d.strip() for d in cache_control.split(',')]
        strategy = {
            'no_cache': 'no-cache' in directives,
            'no_store': 'no-store' in directives,
            'public': 'public' in directives,
            'private': 'private' in directives,
            'max_age': None,
            'must_revalidate': 'must-revalidate' in directives
        }
        
        # 提取max-age值
        for directive in directives:
            if directive.startswith('max-age='):
                try:
                    strategy['max_age'] = int(directive.split('=')[1])
                except (ValueError, IndexError):
                    strategy['max_age'] = '无效值'
                break
        
        # 判断缓存策略类型
        if strategy['no_store']:
            strategy_type = '禁止缓存'
        elif strategy['no_cache']:
            strategy_type = '验证缓存'
        elif strategy['max_age'] is not None and strategy['max_age'] > 0:
            strategy_type = f'缓存{strategy["max_age"]}秒'
        else:
            strategy_type = '默认缓存'
        
        return {
            'strategy': strategy_type,
            'directives': directives,
            'parsed': strategy
        }
    
    def analyze_content_headers(self) -> Dict[str, any]:
        """
        分析内容相关头部
        
        Returns:
            内容头部分析结果
        """
        if not self.headers:
            self.fetch_headers()
        
        if not self.headers:
            return {"error": "无法获取头部信息"}
        
        content_headers = {
            'Content-Type': {
                'description': '内容类型和字符编码',
                'required': True
            },
            'Content-Length': {
                'description': '内容长度（字节）',
                'required': False
            },
            'Content-Encoding': {
                'description': '内容编码方式',
                'required': False
            },
            'Content-Language': {
                'description': '内容语言',
                'required': False
            },
            'Content-Location': {
                'description': '内容实际位置',
                'required': False
            }
        }
        
        results = {}
        for header, info in content_headers.items():
            value = self.headers.get(header)
            results[header] = {
                'present': value is not None,
                'value': value,
                'description': info['description'],
                'required': info['required']
            }
        
        return results
    
    def get_basic_info(self) -> Dict[str, any]:
        """
        获取基本响应信息
        
        Returns:
            基本信息字典
        """
        if not self.response:
            self.fetch_headers()
        
        if not self.response:
            return {"error": "无法获取响应信息"}
        
        return {
            'status_code': self.response.status_code,
            'reason': self.response.reason,
            'url': self.response.url,
            'headers_count': len(self.headers),
            'server': self.headers.get('Server', '未知'),
            'content_type': self.headers.get('Content-Type', '未知')
        }
    
    def print_analysis_report(self):
        """打印完整的分析报告"""
        print(f"HTTP头部分析报告 - {self.url}")
        print("=" * 60)
        
        # 基本信息
        basic_info = self.get_basic_info()
        if 'error' not in basic_info:
            print(f"\n基本信息:")
            print(f"  状态码: {basic_info['status_code']} {basic_info['reason']}")
            print(f"  最终URL: {basic_info['url']}")
            print(f"  服务器: {basic_info['server']}")
            print(f"  内容类型: {basic_info['content_type']}")
            print(f"  头部数量: {basic_info['headers_count']}")
        
        # 安全头部分析
        print(f"\n安全头部分析:")
        print("-" * 40)
        security_results = self.analyze_security_headers()
        if 'error' not in security_results:
            security_headers = [
                'Strict-Transport-Security',
                'X-Content-Type-Options',
                'X-Frame-Options',
                'Content-Security-Policy',
                'Permissions-Policy',
                'Referrer-Policy'
            ]
            
            for header in security_headers:
                result = security_results.get(header, {})
                if result.get('present'):
                    status = "✓ 已设置"
                    print(f"  {header}: {status}")
                    print(f"    值: {result['value']}")
                else:
                    status = "✗ 未设置"
                    print(f"  {header}: {status} - {result.get('description', '')}")
        else:
            print(f"  错误: {security_results['error']}")
        
        # 缓存头部分析
        print(f"\n缓存头部分析:")
        print("-" * 40)
        cache_results = self.analyze_cache_headers()
        if 'error' not in cache_results:
            cache_headers = ['Cache-Control', 'Expires', 'Last-Modified', 'ETag']
            for header in cache_headers:
                result = cache_results.get(header, {})
                if result.get('present'):
                    status = "✓ 已设置"
                    print(f"  {header}: {status}")
                    print(f"    值: {result['value']}")
                else:
                    status = "✗ 未设置"
                    print(f"  {header}: {status} - {result.get('description', '')}")
            
            # 缓存策略
            cache_strategy = cache_results.get('cache_strategy', {})
            if cache_strategy:
                print(f"  缓存策略: {cache_strategy.get('strategy', '未知')}")
                directives = cache_strategy.get('directives', [])
                if directives:
                    print(f"    指令: {', '.join(directives)}")
        else:
            print(f"  错误: {cache_results['error']}")
        
        # 内容头部分析
        print(f"\n内容头部分析:")
        print("-" * 40)
        content_results = self.analyze_content_headers()
        if 'error' not in content_results:
            content_headers = ['Content-Type', 'Content-Length', 'Content-Encoding']
            for header in content_headers:
                result = content_results.get(header, {})
                if result.get('present'):
                    status = "✓ 已设置"
                    print(f"  {header}: {status}")
                    print(f"    值: {result['value']}")
                else:
                    status = "✗ 未设置"
                    required = "（必需）" if result.get('required') else ""
                    print(f"  {header}: {status} {required}- {result.get('description', '')}")
        else:
            print(f"  错误: {content_results['error']}")
        
        # 显示所有头部（简洁版）
        print(f"\n所有头部（前10个）:")
        print("-" * 40)
        header_items = list(self.headers.items())[:10]
        for name, value in header_items:
            print(f"  {name}: {value}")
        
        if len(self.headers) > 10:
            print(f"  ... 还有 {len(self.headers) - 10} 个头部")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='HTTP头部分析工具')
    parser.add_argument('url', help='要分析的URL')
    parser.add_argument('--timeout', type=int, default=10, help='请求超时时间（秒）')
    
    args = parser.parse_args()
    
    # 确保URL包含协议
    url = args.url
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"开始分析: {url}")
    
    # 创建分析器并执行分析
    analyzer = HttpHeadersAnalyzer(url, args.timeout)
    analyzer.print_analysis_report()


if __name__ == '__main__':
    main()