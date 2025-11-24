# 第一章 Flask基础入门

## 1.1 Flask简介

Flask是一个使用Python编写的轻量级Web应用框架。它基于Werkzeug WSGI工具箱和Jinja2模板引擎。Flask被称为“微框架”，因为它使用简单的核心，但可以通过扩展增加功能。

### 主要特点：
- 简洁易学：API设计简单直观
- 灵活性高：可以根据需求选择不同的组件
- 扩展性强：丰富的第三方扩展生态
- 文档完善：官方文档详尽且易于理解

## 1.2 环境准备

### 安装Python
确保系统中已安装Python 3.6及以上版本。

### 创建虚拟环境
```bash
python -m venv flask_env
source flask_env/bin/activate  # Linux/Mac
flask_env\Scripts\activate     # Windows
```

### 安装Flask
```bash
pip install Flask
```

## 1.3 第一个Flask应用

创建一个简单的Flask应用：

```python
from flask import Flask

app = Flask(__name__)

@app.route('/')
def hello():
    return 'Hello, Flask!'

if __name__ == '__main__':
    app.run(debug=True)
```

保存为`app.py`，然后运行：
```bash
python app.py
```

访问`http://127.0.0.1:5000/`即可看到输出。

## 1.4 核心概念

### 应用对象
Flask应用实例是整个应用的核心，用于处理请求和响应。

### 路由
路由用于将URL映射到处理函数。使用`@app.route()`装饰器定义路由。

### 请求与响应
Flask通过request对象获取客户端请求信息，通过response对象返回服务器响应。

## 1.5 项目结构建议

推荐的基本项目结构：
```
my_flask_app/
├── app.py              # 应用入口
├── templates/          # 模板文件
├── static/             # 静态文件(css, js, images)
├── requirements.txt    # 依赖列表
└── venv/              # 虚拟环境
```

## 1.6 总结

本章介绍了Flask的基础知识，包括安装配置、第一个应用的创建以及核心概念的理解。下一章我们将深入学习Flask的路由机制和视图函数。