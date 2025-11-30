#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
基础HTTP服务器示例
演示如何使用Python内置的http.server模块创建简单的HTTP服务器
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import urllib.parse
from datetime import datetime


class CustomHTTPRequestHandler(BaseHTTPRequestHandler):
    """自定义HTTP请求处理器"""
    
    def do_GET(self):
        """处理GET请求"""
        print(f"收到GET请求: {self.path}")
        
        # 解析URL路径和查询参数
        parsed_path = urllib.parse.urlparse(self.path)
        path = parsed_path.path
        query_params = urllib.parse.parse_qs(parsed_path.query)
        
        # 根据路径返回不同响应
        if path == '/':
            self.send_home_page()
        elif path == '/about':
            self.send_about_page()
        elif path == '/api/time':
            self.send_current_time()
        elif path == '/api/headers':
            self.send_request_headers()
        else:
            self.send_404_page()
    
    def do_POST(self):
        """处理POST请求"""
        print(f"收到POST请求: {self.path}")
        
        # 获取请求体内容
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        # 解析JSON数据（如果有的话）
        try:
            data = json.loads(post_data.decode('utf-8'))
        except json.JSONDecodeError:
            data = {"raw_data": post_data.decode('utf-8')}
        
        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        response_data = {
            "message": "POST请求处理成功",
            "received_data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode())
    
    def do_PUT(self):
        """处理PUT请求"""
        print(f"收到PUT请求: {self.path}")
        
        # 获取请求体内容
        content_length = int(self.headers.get('Content-Length', 0))
        put_data = self.rfile.read(content_length)
        
        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "message": "PUT请求处理成功",
            "received_data": put_data.decode('utf-8'),
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode())
    
    def do_DELETE(self):
        """处理DELETE请求"""
        print(f"收到DELETE请求: {self.path}")
        
        # 返回响应
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response_data = {
            "message": "DELETE请求处理成功",
            "path": self.path,
            "timestamp": datetime.now().isoformat()
        }
        
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode())
    
    def send_home_page(self):
        """发送主页"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>HTTP服务器示例</title>
            <meta charset="utf-8">
            <style>
                body { font-family: Arial, sans-serif; margin: 40px; }
                h1 { color: #333; }
                .endpoint { background: #f5f5f5; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .method { background: #007cba; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.8em; }
            </style>
        </head>
        <body>
            <h1>HTTP服务器示例</h1>
            <p>这是一个简单的HTTP服务器示例，演示了不同HTTP方法的处理。</p>
            
            <h2>可用的端点:</h2>
            <div class="endpoint">
                <span class="method">GET</span> 
                <strong>/</strong> - 主页
            </div>
            <div class="endpoint">
                <span class="method">GET</span> 
                <strong>/about</strong> - 关于页面
            </div>
            <div class="endpoint">
                <span class="method">GET</span> 
                <strong>/api/time</strong> - 获取当前时间
            </div>
            <div class="endpoint">
                <span class="method">GET</span> 
                <strong>/api/headers</strong> - 获取请求头部信息
            </div>
            <div class="endpoint">
                <span class="method">POST</span> 
                <strong>/</strong> - 发送JSON数据
            </div>
            <div class="endpoint">
                <span class="method">PUT</span> 
                <strong>/</strong> - 更新资源
            </div>
            <div class="endpoint">
                <span class="method">DELETE</span> 
                <strong>/</strong> - 删除资源
            </div>
            
            <h2>测试说明:</h2>
            <p>可以使用curl命令测试不同的HTTP方法:</p>
            <pre>
# GET请求
curl http://localhost:8080/

# POST请求
curl -X POST -H "Content-Type: application/json" -d '{"name":"test"}' http://localhost:8080/

# PUT请求
curl -X PUT -d "update data" http://localhost:8080/

# DELETE请求
curl -X DELETE http://localhost:8080/
            </pre>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_about_page(self):
        """发送关于页面"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>关于 - HTTP服务器示例</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>关于这个HTTP服务器</h1>
            <p>这是一个用Python编写的简单HTTP服务器示例，用于演示HTTP协议的基本工作原理。</p>
            <p>支持的HTTP方法包括: GET, POST, PUT, DELETE</p>
            <a href="/">返回主页</a>
        </body>
        </html>
        """
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def send_current_time(self):
        """发送当前时间"""
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        response_data = {
            "current_time": current_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode())
    
    def send_request_headers(self):
        """发送请求头部信息"""
        headers_dict = {}
        for key, value in self.headers.items():
            headers_dict[key] = value
        
        response_data = {
            "headers": headers_dict,
            "timestamp": datetime.now().isoformat()
        }
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(response_data, ensure_ascii=False).encode())
    
    def send_404_page(self):
        """发送404页面"""
        html_content = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>404 - 页面未找到</title>
            <meta charset="utf-8">
        </head>
        <body>
            <h1>404 - 页面未找到</h1>
            <p>抱歉，您请求的页面不存在。</p>
            <a href="/">返回主页</a>
        </body>
        </html>
        """
        
        self.send_response(404)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        self.wfile.write(html_content.encode('utf-8'))
    
    def log_message(self, format, *args):
        """自定义日志输出"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {format % args}")


def run_server(host='localhost', port=8080):
    """运行HTTP服务器"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, CustomHTTPRequestHandler)
    
    print(f"HTTP服务器启动成功!")
    print(f"服务器地址: http://{host}:{port}")
    print("按 Ctrl+C 停止服务器")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n服务器已停止")
        httpd.server_close()


if __name__ == '__main__':
    run_server()