#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP请求和响应详细示例
演示HTTP请求和响应的完整结构
"""

import requests
import json
from datetime import datetime


def demonstrate_get_request():
    """演示GET请求"""
    print("=== GET请求示例 ===")
    
    # 发送GET请求
    url = "https://httpbin.org/get"
    params = {
        "name": "张三",
        "age": "25",
        "city": "北京"
    }
    
    response = requests.get(url, params=params)
    
    print(f"请求URL: {response.url}")
    print(f"请求方法: {response.request.method}")
    print(f"请求头部: {dict(response.request.headers)}")
    print(f"请求体: {response.request.body}")
    print("-" * 50)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头部: {dict(response.headers)}")
    print(f"响应体: {response.text[:200]}...")
    print("=" * 60 + "\n")


def demonstrate_post_request():
    """演示POST请求"""
    print("=== POST请求示例 ===")
    
    # 发送POST请求
    url = "https://httpbin.org/post"
    data = {
        "username": "testuser",
        "email": "test@example.com",
        "message": "这是一条测试消息"
    }
    
    # JSON格式请求
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "CustomClient/1.0"
    }
    
    response = requests.post(url, json=data, headers=headers)
    
    print(f"请求URL: {response.url}")
    print(f"请求方法: {response.request.method}")
    print(f"请求头部: {dict(response.request.headers)}")
    print(f"请求体: {response.request.body}")
    print("-" * 50)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头部: {dict(response.headers)}")
    print(f"响应体: {response.text[:200]}...")
    print("=" * 60 + "\n")


def demonstrate_put_request():
    """演示PUT请求"""
    print("=== PUT请求示例 ===")
    
    # 发送PUT请求
    url = "https://httpbin.org/put"
    data = {
        "id": "123",
        "name": "更新后的名称",
        "status": "active"
    }
    
    response = requests.put(url, json=data)
    
    print(f"请求URL: {response.url}")
    print(f"请求方法: {response.request.method}")
    print(f"请求头部: {dict(response.request.headers)}")
    print(f"请求体: {response.request.body}")
    print("-" * 50)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头部: {dict(response.headers)}")
    print(f"响应体: {response.text[:200]}...")
    print("=" * 60 + "\n")


def demonstrate_delete_request():
    """演示DELETE请求"""
    print("=== DELETE请求示例 ===")
    
    # 发送DELETE请求
    url = "https://httpbin.org/delete"
    
    response = requests.delete(url)
    
    print(f"请求URL: {response.url}")
    print(f"请求方法: {response.request.method}")
    print(f"请求头部: {dict(response.request.headers)}")
    print(f"请求体: {response.request.body}")
    print("-" * 50)
    print(f"响应状态码: {response.status_code}")
    print(f"响应头部: {dict(response.headers)}")
    print(f"响应体: {response.text[:200]}...")
    print("=" * 60 + "\n")


def demonstrate_custom_headers():
    """演示自定义头部"""
    print("=== 自定义头部示例 ===")
    
    url = "https://httpbin.org/headers"
    headers = {
        "Authorization": "Bearer your-token-here",
        "X-Custom-Header": "CustomValue",
        "Accept": "application/json",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8"
    }
    
    response = requests.get(url, headers=headers)
    
    print(f"请求头部: {dict(response.request.headers)}")
    print("-" * 50)
    print(f"响应状态码: {response.status_code}")
    print("响应体中的请求头部:")
    response_data = response.json()
    print(json.dumps(response_data.get("headers", {}), indent=2, ensure_ascii=False))
    print("=" * 60 + "\n")


def demonstrate_response_details():
    """演示响应详细信息"""
    print("=== 响应详细信息示例 ===")
    
    url = "https://httpbin.org/get"
    response = requests.get(url)
    
    print(f"响应状态码: {response.status_code}")
    print(f"响应原因: {response.reason}")
    print(f"响应头部: {dict(response.headers)}")
    print(f"响应编码: {response.encoding}")
    print(f"响应内容类型: {response.headers.get('Content-Type')}")
    print(f"响应内容长度: {len(response.content)} 字节")
    print(f"是否成功: {response.ok}")
    print(f"历史重定向: {response.history}")
    
    # 解析JSON响应
    try:
        json_data = response.json()
        print(f"JSON数据键: {list(json_data.keys())}")
    except json.JSONDecodeError:
        print("响应不是有效的JSON格式")
    
    print("=" * 60 + "\n")


def demonstrate_error_handling():
    """演示错误处理"""
    print("=== 错误处理示例 ===")
    
    # 测试404错误
    try:
        response = requests.get("https://httpbin.org/status/404")
        print(f"404响应状态码: {response.status_code}")
        print(f"是否成功: {response.ok}")
        response.raise_for_status()  # 这会抛出异常
    except requests.exceptions.HTTPError as e:
        print(f"HTTP错误: {e}")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    
    # 测试超时
    try:
        response = requests.get("https://httpbin.org/delay/5", timeout=2)
    except requests.exceptions.Timeout:
        print("请求超时")
    except requests.exceptions.RequestException as e:
        print(f"请求异常: {e}")
    
    print("=" * 60 + "\n")


def main():
    """主函数"""
    print("HTTP请求和响应详细示例")
    print("=" * 60)
    print()
    
    # 演示各种HTTP方法
    demonstrate_get_request()
    demonstrate_post_request()
    demonstrate_put_request()
    demonstrate_delete_request()
    
    # 演示自定义头部
    demonstrate_custom_headers()
    
    # 演示响应详细信息
    demonstrate_response_details()
    
    # 演示错误处理
    demonstrate_error_handling()
    
    print("所有示例演示完成!")


if __name__ == "__main__":
    main()