#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP消息构造器示例
演示如何手动构造HTTP请求和响应消息
"""

from typing import Dict, Optional
from datetime import datetime


class HTTPMessageBuilder:
    """HTTP消息构造器"""
    
    def __init__(self):
        """初始化构造器"""
        pass
    
    def build_request(self, 
                     method: str,
                     uri: str,
                     version: str = "HTTP/1.1",
                     headers: Optional[Dict[str, str]] = None,
                     body: str = "") -> str:
        """
        构造HTTP请求消息
        
        Args:
            method: HTTP方法 (GET, POST, PUT, DELETE等)
            uri: 请求URI
            version: HTTP版本
            headers: 请求头部字段字典
            body: 请求体内容
            
        Returns:
            构造的HTTP请求字符串
        """
        # 构造请求行
        request_line = f"{method} {uri} {version}"
        
        # 构造头部
        header_lines = []
        if headers:
            for key, value in headers.items():
                header_lines.append(f"{key}: {value}")
        
        # 添加必需的头部字段
        if "Host" not in (headers or {}):
            # 从URI中提取主机名（简化处理）
            host = uri.split("/")[2] if len(uri.split("/")) > 2 else "localhost"
            header_lines.append(f"Host: {host}")
        
        if "User-Agent" not in (headers or {}):
            header_lines.append("User-Agent: HTTPMessageBuilder/1.0")
        
        # 如果有请求体，添加Content-Length头部
        if body:
            if "Content-Length" not in (headers or {}):
                header_lines.append(f"Content-Length: {len(body.encode('utf-8'))}")
        
        # 组合请求消息
        headers_str = "\r\n".join(header_lines)
        request_message = f"{request_line}\r\n{headers_str}\r\n\r\n{body}"
        
        return request_message
    
    def build_response(self,
                       status_code: int,
                       reason_phrase: str,
                       version: str = "HTTP/1.1",
                       headers: Optional[Dict[str, str]] = None,
                       body: str = "") -> str:
        """
        构造HTTP响应消息
        
        Args:
            status_code: 状态码
            reason_phrase: 状态描述
            version: HTTP版本
            headers: 响应头部字段字典
            body: 响应体内容
            
        Returns:
            构造的HTTP响应字符串
        """
        # 构造状态行
        status_line = f"{version} {status_code} {reason_phrase}"
        
        # 构造头部
        header_lines = []
        if headers:
            for key, value in headers.items():
                header_lines.append(f"{key}: {value}")
        
        # 添加默认头部字段
        if "Date" not in (headers or {}):
            header_lines.append(f"Date: {datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')}")
        
        if "Server" not in (headers or {}):
            header_lines.append("Server: HTTPMessageBuilder/1.0")
        
        # 如果有响应体，添加Content-Length和Content-Type头部
        if body:
            if "Content-Length" not in (headers or {}):
                header_lines.append(f"Content-Length: {len(body.encode('utf-8'))}")
            if "Content-Type" not in (headers or {}):
                header_lines.append("Content-Type: text/plain; charset=utf-8")
        
        # 组合响应消息
        headers_str = "\r\n".join(header_lines)
        response_message = f"{status_line}\r\n{headers_str}\r\n\r\n{body}"
        
        return response_message
    
    def display_message(self, message: str, message_type: str = "HTTP"):
        """
        显示HTTP消息
        
        Args:
            message: HTTP消息字符串
            message_type: 消息类型 ("HTTP请求" 或 "HTTP响应")
        """
        print("=" * 60)
        print(f"{message_type}消息")
        print("=" * 60)
        print(message)
        print("=" * 60 + "\n")


def demonstrate_request_building():
    """演示HTTP请求构造"""
    print("=== HTTP请求构造演示 ===")
    
    builder = HTTPMessageBuilder()
    
    # 构造简单的GET请求
    print("1. 构造GET请求:")
    get_request = builder.build_request(
        method="GET",
        uri="/index.html"
    )
    builder.display_message(get_request, "HTTP请求")
    
    # 构造带参数的GET请求
    print("2. 构造带参数的GET请求:")
    get_with_params = builder.build_request(
        method="GET",
        uri="/api/users?id=123&name=张三",
        headers={
            "Accept": "application/json",
            "Authorization": "Bearer token123"
        }
    )
    builder.display_message(get_with_params, "HTTP请求")
    
    # 构造POST请求
    print("3. 构造POST请求:")
    post_request = builder.build_request(
        method="POST",
        uri="/api/users",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json"
        },
        body='{"name": "王五", "email": "wangwu@example.com"}'
    )
    builder.display_message(post_request, "HTTP请求")
    
    # 构造PUT请求
    print("4. 构造PUT请求:")
    put_request = builder.build_request(
        method="PUT",
        uri="/api/users/123",
        headers={
            "Content-Type": "application/json"
        },
        body='{"id": 123, "name": "王五更新", "email": "wangwu_updated@example.com"}'
    )
    builder.display_message(put_request, "HTTP请求")


def demonstrate_response_building():
    """演示HTTP响应构造"""
    print("=== HTTP响应构造演示 ===")
    
    builder = HTTPMessageBuilder()
    
    # 构造200 OK响应
    print("1. 构造200 OK响应:")
    ok_response = builder.build_response(
        status_code=200,
        reason_phrase="OK",
        headers={
            "Content-Type": "text/html; charset=utf-8"
        },
        body="<html><body><h1>Hello, World!</h1></body></html>"
    )
    builder.display_message(ok_response, "HTTP响应")
    
    # 构造404 Not Found响应
    print("2. 构造404 Not Found响应:")
    not_found_response = builder.build_response(
        status_code=404,
        reason_phrase="Not Found",
        body="<html><body><h1>404 - 页面未找到</h1></body></html>"
    )
    builder.display_message(not_found_response, "HTTP响应")
    
    # 构造JSON响应
    print("3. 构造JSON响应:")
    json_response = builder.build_response(
        status_code=200,
        reason_phrase="OK",
        headers={
            "Content-Type": "application/json"
        },
        body='{"users": [{"id": 1, "name": "张三"}, {"id": 2, "name": "李四"}], "total": 2}'
    )
    builder.display_message(json_response, "HTTP响应")


def main():
    """主函数"""
    print("HTTP消息构造器示例")
    print("=" * 60)
    print()
    
    # 演示请求构造
    demonstrate_request_building()
    
    # 演示响应构造
    demonstrate_response_building()
    
    print("所有演示完成!")


if __name__ == "__main__":
    main()