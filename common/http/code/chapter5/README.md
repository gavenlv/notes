# HTTP课程第5章代码示例

## 概述

本目录包含HTTP课程第5章"HTTP头部详解与实战应用"的所有代码示例。这些示例展示了HTTP头部的各种用法，包括缓存控制、安全头部设置、内容协商、跨域资源共享等方面的实际应用。

## 代码示例列表

1. `http_headers_analyzer.py` - HTTP头部分析工具
2. `cache_control_examples.py` - 缓存控制示例
3. `security_headers_demo.py` - 安全头部设置示例
4. `cors_headers_demo.py` - CORS跨域头部示例
5. `content_negotiation_demo.py` - 内容协商示例

## 环境要求

- Python 3.7+
- Flask==2.3.2
- requests==2.31.0

## 运行说明

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 运行各个示例文件：
   ```
   python http_headers_analyzer.py
   python cache_control_examples.py
   python security_headers_demo.py
   python cors_headers_demo.py
   python content_negotiation_demo.py
   ```

## 代码实现细节

### http_headers_analyzer.py
实现了HTTP头部分析工具，可以分析网站的安全头部和缓存头部设置情况。

### cache_control_examples.py
展示了如何在服务端和客户端正确设置和使用缓存控制头部。

### security_headers_demo.py
演示了各种安全头部的设置方法及其作用。

### cors_headers_demo.py
展示了CORS相关头部的配置和使用。

### content_negotiation_demo.py
演示了内容协商头部的使用方法。

## 学习建议

1. 先理解每个示例的核心概念
2. 运行代码观察输出结果
3. 修改代码参数查看不同效果
4. 结合第5章文档理解实际应用场景

## 注意事项

1. 部分示例需要网络连接
2. 某些安全头部可能需要HTTPS环境才能完全生效
3. 实际部署时需要根据具体需求调整头部设置