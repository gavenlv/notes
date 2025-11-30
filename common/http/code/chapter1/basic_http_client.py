#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础HTTP客户端示例
演示如何使用socket手动构建HTTP请求
"""

import socket
import ssl
from urllib.parse import urlparse


def send_http_request(url, method="GET", headers=None, body=None):
    """
    发送HTTP请求
    
    Args:
        url (str): 请求的URL
        method (str): HTTP方法，默认为GET
        headers (dict): HTTP头部信息
        body (str): 请求体
        
    Returns:
        str: 服务器响应
    """
    # 解析URL
    parsed_url = urlparse(url)
    host = parsed_url.hostname
    port = parsed_url.port or (443 if parsed_url.scheme == 'https' else 80)
    path = parsed_url.path or '/'
    
    # 构建HTTP请求
    request_lines = [
        f"{method} {path} HTTP/1.1",
        f"Host: {host}",
        "Connection: close",
        "User-Agent: CustomHTTPClient/1.0"
    ]
    
    # 添加自定义头部
    if headers:
        for key, value in headers.items():
            request_lines.append(f"{key}: {value}")
    
    # 添加请求体
    if body:
        request_lines.append(f"Content-Length: {len(body)}")
        request_lines.append("")  # 空行分隔头部和体
        request_lines.append(body)
    else:
        request_lines.append("")  # 空行结束请求
    
    request = "\r\n".join(request_lines) + "\r\n"
    
    print(f"发送请求到 {host}:{port}")
    print("请求内容:")
    print(request)
    print("-" * 50)
    
    try:
        # 创建socket连接
        if parsed_url.scheme == 'https':
            # HTTPS连接
            context = ssl.create_default_context()
            with socket.create_connection((host, port)) as sock:
                with context.wrap_socket(sock, server_hostname=host) as ssock:
                    ssock.send(request.encode())
                    response = ssock.recv(4096)
                    return response.decode()
        else:
            # HTTP连接
            with socket.create_connection((host, port)) as sock:
                sock.send(request.encode())
                response = sock.recv(4096)
                return response.decode()
                
    except Exception as e:
        return f"请求失败: {e}"


def main():
    """主函数"""
    print("=== 基础HTTP客户端示例 ===\n")
    
    # 示例1: 简单的GET请求
    print("1. 发送简单的GET请求")
    response = send_http_request("http://httpbin.org/get")
    print("响应内容:")
    print(response[:500] + "..." if len(response) > 500 else response)
    print("\n" + "="*60 + "\n")
    
    # 示例2: 带自定义头部的GET请求
    print("2. 发送带自定义头部的GET请求")
    headers = {
        "Accept": "application/json",
        "Custom-Header": "MyValue"
    }
    response = send_http_request("http://httpbin.org/headers", headers=headers)
    print("响应内容:")
    print(response[:500] + "..." if len(response) > 500 else response)
    print("\n" + "="*60 + "\n")
    
    # 示例3: POST请求
    print("3. 发送POST请求")
    body = '{"name": "test", "value": "example"}'
    headers = {
        "Content-Type": "application/json"
    }
    response = send_http_request(
        "http://httpbin.org/post", 
        method="POST", 
        headers=headers, 
        body=body
    )
    print("响应内容:")
    print(response[:500] + "..." if len(response) > 500 else response)
    print("\n" + "="*60 + "\n")
    
    # 示例4: HTTPS请求
    print("4. 发送HTTPS请求")
    response = send_http_request("https://httpbin.org/get")
    print("响应内容:")
    print(response[:500] + "..." if len(response) > 500 else response)


if __name__ == "__main__":
    main()