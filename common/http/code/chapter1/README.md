# 第1章代码示例说明

## 概述

本目录包含了第1章"HTTP协议简介与历史发展"的所有代码示例，帮助读者更好地理解HTTP协议的基本概念和工作原理。

## 代码示例列表

1. **basic_http_client.py** - 简单的HTTP客户端实现
2. **http_server_example.py** - 基础HTTP服务器示例
3. **http_request_response.py** - HTTP请求和响应的详细示例

## 环境要求

- Python 3.6+
- pip包管理器

## 运行说明

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 运行HTTP客户端示例

```bash
python basic_http_client.py
```

### 3. 运行HTTP服务器示例

```bash
python http_server_example.py
```

然后在浏览器中访问 `http://localhost:8080`

### 4. 查看HTTP请求响应示例

```bash
python http_request_response.py
```

## 代码说明

### basic_http_client.py

展示了如何使用Python的socket库手动构建HTTP请求：

```python
import socket

# 创建socket连接
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('httpbin.org', 80))

# 发送HTTP GET请求
request = "GET /get HTTP/1.1\r\nHost: httpbin.org\r\n\r\n"
sock.send(request.encode())

# 接收响应
response = sock.recv(4096)
print(response.decode())
```

### http_server_example.py

实现了简单的HTTP服务器：

```python
from http.server import HTTPServer, BaseHTTPRequestHandler

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'<h1>Hello, World!</h1>')

if __name__ == '__main__':
    server = HTTPServer(('localhost', 8080), SimpleHTTPRequestHandler)
    server.serve_forever()
```

### http_request_response.py

详细展示了HTTP请求和响应的结构：

```python
import requests

# 发送GET请求
response = requests.get('https://httpbin.org/get')

# 打印请求信息
print("Request URL:", response.url)
print("Request Headers:", response.request.headers)

# 打印响应信息
print("Status Code:", response.status_code)
print("Response Headers:", response.headers)
print("Response Body:", response.text)
```

## 学习建议

1. 依次运行各个示例，观察输出结果
2. 修改代码中的参数，观察变化
3. 结合第1章的理论知识，理解代码实现原理
4. 尝试扩展示例功能，加深理解

## 注意事项

1. 确保网络连接正常
2. 部分示例可能需要管理员权限运行
3. 如果端口被占用，请修改代码中的端口号
4. 建议在虚拟环境中运行代码示例