#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP状态码模拟器
模拟各种HTTP状态码的返回，帮助理解不同状态码的含义和使用场景
"""

from flask import Flask, jsonify, request, abort
import json


app = Flask(__name__)


@app.route('/')
def index():
    """首页，提供API说明"""
    return jsonify({
        "message": "HTTP状态码模拟器",
        "description": "这是一个用于演示各种HTTP状态码的模拟器",
        "endpoints": {
            "/status/200": "200 OK - 请求成功",
            "/status/201": "201 Created - 资源已创建",
            "/status/204": "204 No Content - 请求成功但无内容",
            "/status/301": "301 Moved Permanently - 永久重定向",
            "/status/302": "302 Found - 临时重定向",
            "/status/400": "400 Bad Request - 请求错误",
            "/status/401": "401 Unauthorized - 未授权",
            "/status/403": "403 Forbidden - 禁止访问",
            "/status/404": "404 Not Found - 资源未找到",
            "/status/405": "405 Method Not Allowed - 方法不允许",
            "/status/429": "429 Too Many Requests - 请求过多",
            "/status/500": "500 Internal Server Error - 服务器内部错误",
            "/status/503": "503 Service Unavailable - 服务不可用"
        }
    })


@app.route('/status/200')
def status_200():
    """200 OK - 请求成功"""
    return jsonify({
        "status": "success",
        "message": "请求处理成功",
        "data": {
            "id": 1,
            "name": "示例数据",
            "timestamp": "2023-01-01T12:00:00Z"
        }
    }), 200


@app.route('/status/201', methods=['POST'])
def status_201():
    """201 Created - 资源已创建"""
    data = request.get_json() or {}
    return jsonify({
        "status": "created",
        "message": "资源创建成功",
        "resource": {
            "id": 123,
            "data": data,
            "created_at": "2023-01-01T12:00:00Z"
        }
    }), 201


@app.route('/status/204', methods=['DELETE'])
def status_204():
    """204 No Content - 请求成功但无内容"""
    # 不返回任何内容，只返回204状态码
    return '', 204


@app.route('/status/301')
def status_301():
    """301 Moved Permanently - 永久重定向"""
    return jsonify({
        "message": "资源已永久移动",
        "new_location": "http://localhost:5000/status/200"
    }), 301, {'Location': 'http://localhost:5000/status/200'}


@app.route('/status/302')
def status_302():
    """302 Found - 临时重定向"""
    return jsonify({
        "message": "资源临时移动",
        "temporary_location": "http://localhost:5000/status/200"
    }), 302, {'Location': 'http://localhost:5000/status/200'}


@app.route('/status/400', methods=['POST'])
def status_400():
    """400 Bad Request - 请求错误"""
    data = request.get_json()
    
    if not data:
        return jsonify({
            "error": "bad_request",
            "message": "请求体不能为空",
            "details": "请提供有效的JSON数据"
        }), 400
    
    if 'required_field' not in data:
        return jsonify({
            "error": "missing_field",
            "message": "缺少必需字段",
            "details": "字段 'required_field' 是必需的"
        }), 400
    
    return jsonify({"message": "这行代码不应该被执行"}), 200


@app.route('/status/401')
def status_401():
    """401 Unauthorized - 未授权"""
    auth_header = request.headers.get('Authorization')
    
    if not auth_header:
        return jsonify({
            "error": "unauthorized",
            "message": "缺少认证信息",
            "details": "请在请求头中提供Authorization字段"
        }), 401
    
    if not auth_header.startswith('Bearer '):
        return jsonify({
            "error": "invalid_token",
            "message": "认证令牌格式错误",
            "details": "请使用Bearer令牌格式"
        }), 401
    
    token = auth_header.split(' ')[1]
    if token != 'valid_token':
        return jsonify({
            "error": "invalid_token",
            "message": "无效的认证令牌",
            "details": "请提供有效的认证令牌"
        }), 401
    
    return jsonify({"message": "认证成功"}), 200


@app.route('/status/403')
def status_403():
    """403 Forbidden - 禁止访问"""
    user_role = request.headers.get('X-User-Role', 'guest')
    
    if user_role != 'admin':
        return jsonify({
            "error": "forbidden",
            "message": "权限不足",
            "details": "只有管理员用户才能访问此资源"
        }), 403
    
    return jsonify({"message": "管理员访问成功"}), 200


@app.route('/status/404')
def status_404():
    """404 Not Found - 资源未找到"""
    return jsonify({
        "error": "not_found",
        "message": "请求的资源不存在",
        "details": "请检查URL路径是否正确"
    }), 404


@app.route('/status/405')
def status_405():
    """405 Method Not Allowed - 方法不允许"""
    return jsonify({
        "error": "method_not_allowed",
        "message": "请求方法不被允许",
        "allowed_methods": ["GET", "POST"],
        "details": "此端点只支持GET和POST方法"
    }), 405, {'Allow': 'GET, POST'}


@app.route('/status/429')
def status_429():
    """429 Too Many Requests - 请求过多"""
    # 这里简化处理，实际应用中应该有请求计数机制
    return jsonify({
        "error": "too_many_requests",
        "message": "请求过于频繁",
        "details": "请降低请求频率",
        "retry_after": 60
    }), 429, {'Retry-After': '60'}


@app.route('/status/500')
def status_500():
    """500 Internal Server Error - 服务器内部错误"""
    # 故意触发一个异常来演示500错误
    raise Exception("模拟服务器内部错误")


@app.route('/status/503')
def status_503():
    """503 Service Unavailable - 服务不可用"""
    return jsonify({
        "error": "service_unavailable",
        "message": "服务暂时不可用",
        "details": "系统正在维护中，请稍后再试",
        "retry_after": 300
    }), 503, {'Retry-After': '300'}


@app.errorhandler(404)
def not_found(error):
    """全局404处理"""
    return jsonify({
        "error": "endpoint_not_found",
        "message": "请求的端点不存在",
        "details": "请检查URL路径是否正确"
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """全局500处理"""
    return jsonify({
        "error": "internal_server_error",
        "message": "服务器内部错误",
        "details": "请联系系统管理员"
    }), 500


def main():
    """主函数"""
    print("HTTP状态码模拟器")
    print("=" * 50)
    print("启动服务器...")
    print("访问 http://localhost:5000 查看API说明")
    print("使用 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动Flask应用
    app.run(host='localhost', port=5000, debug=True)


if __name__ == '__main__':
    main()