#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP消息解析器示例
演示如何解析HTTP请求和响应消息
"""

import re
from typing import Dict, List, Optional


class HTTPMessageParser:
    """HTTP消息解析器"""
    
    def __init__(self):
        """初始化解析器"""
        self.reset()
    
    def reset(self):
        """重置解析状态"""
        self.method = ""
        self.uri = ""
        self.version = ""
        self.status_code = 0
        self.reason_phrase = ""
        self.headers = {}
        self.body = ""
    
    def parse_request(self, raw_request: str) -> Dict:
        """
        解析HTTP请求消息
        
        Args:
            raw_request: 原始HTTP请求字符串
            
        Returns:
            包含解析结果的字典
        """
        self.reset()
        lines = raw_request.strip().split('\n')
        
        if not lines:
            raise ValueError("无效的HTTP请求")
        
        # 解析请求行
        request_line = lines[0].strip()
        request_parts = request_line.split()
        
        if len(request_parts) < 3:
            raise ValueError("无效的请求行格式")
            
        self.method = request_parts[0]
        self.uri = request_parts[1]
        self.version = request_parts[2]
        
        # 解析头部
        headers_end = self._parse_headers(lines[1:])
        
        # 解析消息体
        if headers_end < len(lines):
            self.body = '\n'.join(lines[headers_end+1:]).strip()
        
        return {
            'type': 'request',
            'method': self.method,
            'uri': self.uri,
            'version': self.version,
            'headers': self.headers.copy(),
            'body': self.body
        }
    
    def parse_response(self, raw_response: str) -> Dict:
        """
        解析HTTP响应消息
        
        Args:
            raw_response: 原始HTTP响应字符串
            
        Returns:
            包含解析结果的字典
        """
        self.reset()
        lines = raw_response.strip().split('\n')
        
        if not lines:
            raise ValueError("无效的HTTP响应")
        
        # 解析状态行
        status_line = lines[0].strip()
        status_parts = status_line.split()
        
        if len(status_parts) < 3:
            raise ValueError("无效的状态行格式")
            
        self.version = status_parts[0]
        self.status_code = int(status_parts[1])
        self.reason_phrase = ' '.join(status_parts[2:])
        
        # 解析头部
        headers_end = self._parse_headers(lines[1:])
        
        # 解析消息体
        if headers_end < len(lines):
            self.body = '\n'.join(lines[headers_end+1:]).strip()
        
        return {
            'type': 'response',
            'version': self.version,
            'status_code': self.status_code,
            'reason_phrase': self.reason_phrase,
            'headers': self.headers.copy(),
            'body': self.body
        }
    
    def _parse_headers(self, lines: List[str]) -> int:
        """
        解析HTTP头部
        
        Args:
            lines: 头部行列表
            
        Returns:
            头部结束位置的索引
        """
        headers_end = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # 空行表示头部结束
            if not line:
                headers_end = i
                break
            
            # 解析头部字段
            if ':' in line:
                key, value = line.split(':', 1)
                self.headers[key.strip()] = value.strip()
        
        return headers_end
    
    def display_parsed_result(self, parsed_result: Dict):
        """
        显示解析结果
        
        Args:
            parsed_result: 解析结果字典
        """
        print("=" * 60)
        print("HTTP消息解析结果")
        print("=" * 60)
        
        if parsed_result['type'] == 'request':
            print(f"消息类型: HTTP请求")
            print(f"请求方法: {parsed_result['method']}")
            print(f"请求URI: {parsed_result['uri']}")
            print(f"HTTP版本: {parsed_result['version']}")
        else:
            print(f"消息类型: HTTP响应")
            print(f"HTTP版本: {parsed_result['version']}")
            print(f"状态码: {parsed_result['status_code']}")
            print(f"状态描述: {parsed_result['reason_phrase']}")
        
        print("\n头部字段:")
        print("-" * 40)
        for key, value in parsed_result['headers'].items():
            print(f"{key}: {value}")
        
        print(f"\n消息体 ({len(parsed_result['body'])} 字符):")
        print("-" * 40)
        if parsed_result['body']:
            print(parsed_result['body'])
        else:
            print("(空)")
        
        print("=" * 60 + "\n")


def demonstrate_request_parsing():
    """演示HTTP请求解析"""
    print("=== HTTP请求解析演示 ===")
    
    # 示例HTTP请求
    sample_request = """GET /api/users?page=1&size=10 HTTP/1.1
Host: api.example.com
User-Agent: MyApp/1.0
Accept: application/json, text/plain
Accept-Language: zh-CN,zh;q=0.9,en;q=0.8
Accept-Encoding: gzip, deflate, br
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
Connection: keep-alive
Cookie: sessionId=abc123; userId=456

{"query": "users", "filters": {"active": true}}
"""
    
    parser = HTTPMessageParser()
    
    try:
        result = parser.parse_request(sample_request)
        parser.display_parsed_result(result)
    except Exception as e:
        print(f"解析失败: {e}")


def demonstrate_response_parsing():
    """演示HTTP响应解析"""
    print("=== HTTP响应解析演示 ===")
    
    # 示例HTTP响应
    sample_response = """HTTP/1.1 200 OK
Date: Mon, 01 Jan 2023 12:00:00 GMT
Content-Type: application/json; charset=utf-8
Content-Length: 256
Connection: keep-alive
Server: nginx/1.18.0
Cache-Control: no-cache, no-store, must-revalidate
Set-Cookie: sessionId=new123; Path=/; HttpOnly

{
    "users": [
        {
            "id": 1,
            "name": "张三",
            "email": "zhangsan@example.com",
            "active": true
        },
        {
            "id": 2,
            "name": "李四",
            "email": "lisi@example.com",
            "active": true
        }
    ],
    "total": 2,
    "page": 1
}
"""
    
    parser = HTTPMessageParser()
    
    try:
        result = parser.parse_response(sample_response)
        parser.display_parsed_result(result)
    except Exception as e:
        print(f"解析失败: {e}")


def main():
    """主函数"""
    print("HTTP消息解析器示例")
    print("=" * 60)
    print()
    
    # 演示请求解析
    demonstrate_request_parsing()
    
    # 演示响应解析
    demonstrate_response_parsing()
    
    print("所有演示完成!")


if __name__ == "__main__":
    main()