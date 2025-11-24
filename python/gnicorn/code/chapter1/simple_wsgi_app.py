# simple_wsgi_app.py
# 一个简单的WSGI应用示例

def application(environ, start_response):
    """简单的WSGI应用
    
    Args:
        environ: 包含HTTP请求信息的字典
        start_response: 用于发送HTTP响应头的可调用对象
    
    Returns:
        包含响应体的字节串列表
    """
    # 获取请求路径
    path = environ.get('PATH_INFO', '/')
    
    # 设置响应状态和头
    status = '200 OK'
    headers = [('Content-type', 'text/plain')]
    start_response(status, headers)
    
    # 根据路径返回不同内容
    if path == '/':
        return [b"Hello, Gunicorn!"]
    elif path == '/about':
        return [b"This is a simple WSGI application running on Gunicorn."]
    elif path == '/info':
        # 显示请求信息
        info_lines = []
        for key, value in environ.items():
            if not key.startswith('wsgi.'):
                info_lines.append(f"{key}: {value}")
        
        info_text = "\n".join(info_lines)
        return [info_text.encode('utf-8')]
    else:
        return [b"404 Not Found"]