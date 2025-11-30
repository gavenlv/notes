#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
真实HTTP通信分析示例
演示如何捕获和分析真实的HTTP请求和响应
"""

import requests
import json
from urllib.parse import urlparse


class RealHTTPAnalyzer:
    """真实HTTP通信分析器"""
    
    def __init__(self):
        """初始化分析器"""
        pass
    
    def analyze_get_request(self, url: str, headers: dict = None):
        """
        分析GET请求
        
        Args:
            url: 请求URL
            headers: 请求头部
        """
        print(f"=== 分析GET请求: {url} ===")
        
        try:
            # 发送GET请求
            response = requests.get(url, headers=headers or {})
            
            # 显示请求信息
            print("请求信息:")
            print(f"  方法: {response.request.method}")
            print(f"  URL: {response.request.url}")
            print("  请求头部:")
            for key, value in response.request.headers.items():
                print(f"    {key}: {value}")
            print(f"  请求体: {response.request.body or '(空)'}")
            
            print("\n响应信息:")
            print(f"  状态码: {response.status_code}")
            print(f"  状态描述: {response.reason}")
            print("  响应头部:")
            for key, value in response.headers.items():
                print(f"    {key}: {value}")
            
            # 显示响应体预览
            content_type = response.headers.get('Content-Type', '')
            print(f"\n响应体预览 (前500字符):")
            if 'json' in content_type:
                try:
                    json_data = response.json()
                    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
                except:
                    print(response.text[:500])
            else:
                print(response.text[:500])
                
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"请求失败: {e}\n")
    
    def analyze_post_request(self, url: str, data: dict = None, headers: dict = None):
        """
        分析POST请求
        
        Args:
            url: 请求URL
            data: 请求数据
            headers: 请求头部
        """
        print(f"=== 分析POST请求: {url} ===")
        
        try:
            # 发送POST请求
            response = requests.post(url, json=data, headers=headers or {})
            
            # 显示请求信息
            print("请求信息:")
            print(f"  方法: {response.request.method}")
            print(f"  URL: {response.request.url}")
            print("  请求头部:")
            for key, value in response.request.headers.items():
                print(f"    {key}: {value}")
            print(f"  请求体: {response.request.body.decode('utf-8') if response.request.body else '(空)'}")
            
            print("\n响应信息:")
            print(f"  状态码: {response.status_code}")
            print(f"  状态描述: {response.reason}")
            print("  响应头部:")
            for key, value in response.headers.items():
                print(f"    {key}: {value}")
            
            # 显示响应体预览
            content_type = response.headers.get('Content-Type', '')
            print(f"\n响应体预览 (前500字符):")
            if 'json' in content_type:
                try:
                    json_data = response.json()
                    print(json.dumps(json_data, indent=2, ensure_ascii=False)[:500])
                except:
                    print(response.text[:500])
            else:
                print(response.text[:500])
                
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"请求失败: {e}\n")
    
    def analyze_headers_only(self, url: str):
        """
        只分析头部信息（使用HEAD请求）
        
        Args:
            url: 请求URL
        """
        print(f"=== 分析头部信息: {url} ===")
        
        try:
            # 发送HEAD请求
            response = requests.head(url)
            
            print("请求信息:")
            print(f"  方法: {response.request.method}")
            print(f"  URL: {response.request.url}")
            
            print("\n响应头部:")
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
                
            print("=" * 60 + "\n")
            
        except Exception as e:
            print(f"请求失败: {e}\n")


def demonstrate_basic_requests():
    """演示基本HTTP请求分析"""
    analyzer = RealHTTPAnalyzer()
    
    # 分析HTTPBin的GET接口
    analyzer.analyze_get_request("https://httpbin.org/get")
    
    # 分析HTTPBin的GET接口带参数
    analyzer.analyze_get_request(
        "https://httpbin.org/get",
        headers={"User-Agent": "RealHTTPAnalyzer/1.0"}
    )
    
    # 分析POST请求
    analyzer.analyze_post_request(
        "https://httpbin.org/post",
        data={"name": "张三", "age": 25, "city": "北京"},
        headers={"Content-Type": "application/json"}
    )


def demonstrate_header_analysis():
    """演示头部信息分析"""
    analyzer = RealHTTPAnalyzer()
    
    # 分析大型网站的头部信息
    websites = [
        "https://www.baidu.com",
        "https://www.github.com",
        "https://httpbin.org/get"
    ]
    
    for website in websites:
        analyzer.analyze_headers_only(website)


def demonstrate_error_handling():
    """演示错误处理"""
    analyzer = RealHTTPAnalyzer()
    
    print("=== 错误处理演示 ===")
    
    # 测试404错误
    print("1. 测试404错误:")
    analyzer.analyze_get_request("https://httpbin.org/status/404")
    
    # 测试重定向
    print("2. 测试重定向:")
    analyzer.analyze_get_request("https://httpbin.org/redirect/3")
    
    # 测试超时
    print("3. 测试超时:")
    try:
        response = requests.get("https://httpbin.org/delay/10", timeout=3)
    except requests.exceptions.Timeout:
        print("  请求超时 (这是预期的行为)")
    except Exception as e:
        print(f"  其他错误: {e}")
    
    print("=" * 60 + "\n")


def main():
    """主函数"""
    print("真实HTTP通信分析示例")
    print("=" * 60)
    print()
    
    # 演示基本请求分析
    demonstrate_basic_requests()
    
    # 演示头部信息分析
    demonstrate_header_analysis()
    
    # 演示错误处理
    demonstrate_error_handling()
    
    print("所有演示完成!")


if __name__ == "__main__":
    main()