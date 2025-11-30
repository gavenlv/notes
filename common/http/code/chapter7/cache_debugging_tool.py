#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTTP缓存调试工具
用于分析和调试HTTP缓存行为
"""

import requests
import json
import time
from datetime import datetime
from urllib.parse import urlparse
import argparse


class CacheDebugger:
    """HTTP缓存调试器"""
    
    def __init__(self):
        self.session = requests.Session()
        self.debug_info = []
    
    def debug_request(self, url, method='GET', headers=None, **kwargs):
        """
        发送HTTP请求并记录缓存相关信息
        
        Args:
            url (str): 请求URL
            method (str): HTTP方法
            headers (dict): 请求头部
            **kwargs: 其他请求参数
            
        Returns:
            requests.Response: HTTP响应对象
        """
        if headers is None:
            headers = {}
        
        # 添加调试信息
        request_info = {
            'timestamp': datetime.now().isoformat(),
            'url': url,
            'method': method,
            'request_headers': dict(headers),
            'kwargs': kwargs
        }
        
        print(f"\n[{request_info['timestamp']}] 发送 {method} 请求到 {url}")
        print("请求头部:")
        for key, value in headers.items():
            print(f"  {key}: {value}")
        
        # 发送请求
        response = self.session.request(method, url, headers=headers, **kwargs)
        
        # 记录响应信息
        response_info = {
            'status_code': response.status_code,
            'response_headers': dict(response.headers),
            'elapsed_time': response.elapsed.total_seconds()
        }
        
        request_info.update(response_info)
        self.debug_info.append(request_info)
        
        print(f"\n响应状态: {response.status_code}")
        print(f"响应时间: {response.elapsed.total_seconds():.3f}s")
        
        # 分析缓存相关头部
        self._analyze_cache_headers(response)
        
        return response
    
    def _analyze_cache_headers(self, response):
        """
        分析缓存相关头部
        
        Args:
            response (requests.Response): HTTP响应对象
        """
        cache_headers = [
            'Cache-Control', 'Expires', 'ETag', 'Last-Modified',
            'Age', 'Vary', 'Pragma'
        ]
        
        print("\n缓存相关头部:")
        for header in cache_headers:
            value = response.headers.get(header)
            if value:
                print(f"  {header}: {value}")
                
                # 特殊分析
                if header == 'Cache-Control':
                    self._analyze_cache_control(value)
                elif header == 'Age':
                    print(f"    缓存年龄: {value}秒")
        
        # 判断是否来自缓存
        if response.status_code == 304:
            print("  响应来源: 缓存 (304 Not Modified)")
        elif 'X-Cache' in response.headers:
            print(f"  X-Cache: {response.headers['X-Cache']}")
        elif 'Age' in response.headers:
            age = int(response.headers['Age'])
            if age > 0:
                print(f"  响应来源: 可能来自缓存 (Age={age})")
    
    def _analyze_cache_control(self, cache_control):
        """
        分析Cache-Control头部
        
        Args:
            cache_control (str): Cache-Control头部值
        """
        directives = [d.strip() for d in cache_control.split(',')]
        print("    指令分析:")
        
        for directive in directives:
            if '=' in directive:
                key, value = directive.split('=', 1)
                key = key.strip()
                value = value.strip()
                
                if key == 'max-age':
                    seconds = int(value)
                    print(f"      最大缓存时间: {seconds}秒 ({seconds//3600}小时{seconds%3600//60}分钟{seconds%60}秒)")
                elif key == 's-maxage':
                    seconds = int(value)
                    print(f"      共享缓存最大时间: {seconds}秒")
                else:
                    print(f"      {key}: {value}")
            else:
                print(f"      {directive}")
    
    def compare_responses(self, response1, response2):
        """
        比较两个响应的缓存行为
        
        Args:
            response1 (requests.Response): 第一个响应
            response2 (requests.Response): 第二个响应
        """
        print("\n响应比较:")
        print(f"状态码: {response1.status_code} -> {response2.status_code}")
        print(f"响应时间: {response1.elapsed.total_seconds():.3f}s -> {response2.elapsed.total_seconds():.3f}s")
        
        # 比较ETag
        etag1 = response1.headers.get('ETag')
        etag2 = response2.headers.get('ETag')
        if etag1 and etag2:
            if etag1 == etag2:
                print(f"ETag相同: {etag1}")
            else:
                print(f"ETag不同: {etag1} -> {etag2}")
        
        # 比较Last-Modified
        lm1 = response1.headers.get('Last-Modified')
        lm2 = response2.headers.get('Last-Modified')
        if lm1 and lm2:
            print(f"Last-Modified: {lm1} -> {lm2}")
    
    def generate_report(self):
        """生成调试报告"""
        print("\n" + "="*50)
        print("HTTP缓存调试报告")
        print("="*50)
        
        total_requests = len(self.debug_info)
        print(f"总请求数: {total_requests}")
        
        cache_hits = sum(1 for info in self.debug_info if info['status_code'] == 304)
        print(f"缓存命中数: {cache_hits}")
        
        avg_response_time = sum(info['elapsed_time'] for info in self.debug_info) / total_requests
        print(f"平均响应时间: {avg_response_time:.3f}s")
        
        print("\n详细请求记录:")
        for i, info in enumerate(self.debug_info, 1):
            print(f"\n{i}. {info['method']} {info['url']}")
            print(f"   时间: {info['timestamp']}")
            print(f"   状态: {info['status_code']}")
            print(f"   耗时: {info['elapsed_time']:.3f}s")
            
            cache_control = info['response_headers'].get('Cache-Control')
            if cache_control:
                print(f"   Cache-Control: {cache_control}")
            
            etag = info['response_headers'].get('ETag')
            if etag:
                print(f"   ETag: {etag}")
    
    def test_conditional_requests(self, url):
        """
        测试条件请求
        
        Args:
            url (str): 测试URL
        """
        print(f"\n测试条件请求: {url}")
        
        # 首次请求获取ETag和Last-Modified
        print("1. 首次请求获取缓存标识")
        response1 = self.debug_request(url)
        
        etag = response1.headers.get('ETag')
        last_modified = response1.headers.get('Last-Modified')
        
        # 使用ETag进行条件请求
        if etag:
            print(f"\n2. 使用ETag进行条件请求: {etag}")
            headers = {'If-None-Match': etag}
            response2 = self.debug_request(url, headers=headers)
            self.compare_responses(response1, response2)
        
        # 使用Last-Modified进行条件请求
        if last_modified:
            print(f"\n3. 使用Last-Modified进行条件请求: {last_modified}")
            headers = {'If-Modified-Since': last_modified}
            response3 = self.debug_request(url, headers=headers)
            self.compare_responses(response1, response3)


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description='HTTP缓存调试工具')
    parser.add_argument('url', help='要测试的URL')
    parser.add_argument('--test-conditional', action='store_true', 
                       help='测试条件请求')
    parser.add_argument('--repeat', type=int, default=1,
                       help='重复请求次数')
    
    args = parser.parse_args()
    
    debugger = CacheDebugger()
    
    if args.test_conditional:
        # 测试条件请求
        debugger.test_conditional_requests(args.url)
    else:
        # 普通请求测试
        for i in range(args.repeat):
            if i > 0:
                print(f"\n等待2秒后发送第{i+1}次请求...")
                time.sleep(2)
            
            debugger.debug_request(args.url)
    
    # 生成报告
    debugger.generate_report()


def demo_usage():
    """演示工具使用方法"""
    print("HTTP缓存调试工具使用演示")
    print("=" * 30)
    
    debugger = CacheDebugger()
    
    # 示例URL（需要替换为实际可访问的URL）
    urls = [
        'https://httpbin.org/cache/60',  # 支持缓存的资源
        'https://httpbin.org/etag/abc123',  # 支持ETag的资源
    ]
    
    for url in urls:
        print(f"\n测试URL: {url}")
        
        # 首次请求
        print("1. 首次请求")
        response1 = debugger.debug_request(url)
        
        # 等待一小段时间后再次请求
        time.sleep(1)
        print("\n2. 第二次请求（测试缓存）")
        response2 = debugger.debug_request(url)
        
        # 比较响应
        debugger.compare_responses(response1, response2)
    
    # 生成最终报告
    debugger.generate_report()


if __name__ == '__main__':
    # 如果没有命令行参数，则运行演示
    import sys
    if len(sys.argv) == 1:
        demo_usage()
    else:
        main()