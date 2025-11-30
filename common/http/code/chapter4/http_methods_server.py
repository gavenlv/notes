#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTTP请求方法服务端实现示例
使用Flask框架实现完整的RESTful API，演示GET、POST、PUT、DELETE等方法的使用
"""

from flask import Flask, jsonify, request, abort
import json
import logging
from datetime import datetime


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# 模拟数据库存储
users_db = {
    1: {
        "id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00"
    },
    2: {
        "id": 2,
        "name": "李四",
        "email": "lisi@example.com",
        "created_at": "2023-01-02T12:00:00",
        "updated_at": "2023-01-02T12:00:00"
    }
}

next_user_id = 3


class APIResponse:
    """API响应格式化类"""
    
    @staticmethod
    def success(data=None, message="请求成功", status_code=200):
        """成功响应"""
        response = {
            "success": True,
            "message": message,
            "data": data
        }
        return jsonify(response), status_code
    
    @staticmethod
    def error(message, error_code, details=None, status_code=400):
        """错误响应"""
        response = {
            "success": False,
            "error": {
                "code": error_code,
                "message": message
            }
        }
        
        if details:
            response["error"]["details"] = details
            
        logger.error(f"API Error: {error_code} - {message}")
        return jsonify(response), status_code


@app.route('/')
def index():
    """API首页"""
    return APIResponse.success({
        "message": "HTTP请求方法服务端实现示例",
        "description": "演示GET、POST、PUT、DELETE等HTTP方法的使用",
        "endpoints": {
            "GET /users": "获取用户列表",
            "GET /users/<id>": "获取单个用户",
            "POST /users": "创建新用户",
            "PUT /users/<id>": "更新用户信息",
            "DELETE /users/<id>": "删除用户",
            "HEAD /users/<id>": "获取用户元信息",
            "OPTIONS /users": "获取支持的HTTP方法"
        }
    })


@app.route('/users', methods=['GET'])
def get_users():
    """GET /users - 获取用户列表"""
    logger.info("获取用户列表")
    
    # 支持分页参数
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    
    # 支持搜索参数
    search = request.args.get('search', '').strip().lower()
    
    # 过滤用户数据
    filtered_users = list(users_db.values())
    if search:
        filtered_users = [
            user for user in filtered_users
            if search in user['name'].lower() or search in user['email'].lower()
        ]
    
    # 分页处理
    start = (page - 1) * per_page
    end = start + per_page
    paginated_users = filtered_users[start:end]
    
    return APIResponse.success({
        "users": paginated_users,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(filtered_users),
            "pages": (len(filtered_users) + per_page - 1) // per_page
        }
    })


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """GET /users/<id> - 获取单个用户"""
    logger.info(f"获取用户信息，用户ID: {user_id}")
    
    if user_id not in users_db:
        return APIResponse.error(
            "用户未找到",
            "USER_NOT_FOUND",
            f"用户ID {user_id} 不存在",
            404
        )
    
    return APIResponse.success(users_db[user_id])


@app.route('/users', methods=['POST'])
def create_user():
    """POST /users - 创建新用户"""
    data = request.get_json()
    
    # 验证请求数据
    if not data:
        return APIResponse.error(
            "请求数据不能为空",
            "INVALID_REQUEST",
            "请提供有效的JSON数据",
            400
        )
    
    # 验证必需字段
    if 'name' not in data or 'email' not in data:
        return APIResponse.error(
            "缺少必需字段",
            "MISSING_FIELDS",
            "name 和 email 字段都是必需的",
            400
        )
    
    # 验证字段值
    name = data['name'].strip()
    email = data['email'].strip()
    
    if not name:
        return APIResponse.error(
            "姓名不能为空",
            "INVALID_NAME",
            "请提供有效的姓名",
            400
        )
    
    if not email or '@' not in email:
        return APIResponse.error(
            "邮箱格式不正确",
            "INVALID_EMAIL",
            "请提供有效的邮箱地址",
            400
        )
    
    # 检查邮箱是否已存在
    for user in users_db.values():
        if user['email'] == email:
            return APIResponse.error(
                "邮箱已被使用",
                "EMAIL_EXISTS",
                f"邮箱 {email} 已被其他用户使用",
                409
            )
    
    # 创建新用户
    global next_user_id
    new_user = {
        "id": next_user_id,
        "name": name,
        "email": email,
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    
    users_db[next_user_id] = new_user
    next_user_id += 1
    
    logger.info(f"创建新用户: {new_user}")
    return APIResponse.success(new_user, "用户创建成功", 201)


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """PUT /users/<id> - 更新用户信息"""
    if user_id not in users_db:
        return APIResponse.error(
            "用户未找到",
            "USER_NOT_FOUND",
            f"用户ID {user_id} 不存在",
            404
        )
    
    data = request.get_json()
    
    if not data:
        return APIResponse.error(
            "请求数据不能为空",
            "INVALID_REQUEST",
            "请提供有效的JSON数据",
            400
        )
    
    # 更新用户信息
    user = users_db[user_id]
    
    if 'name' in data:
        name = data['name'].strip()
        if not name:
            return APIResponse.error(
                "姓名不能为空",
                "INVALID_NAME",
                "请提供有效的姓名",
                400
            )
        user['name'] = name
    
    if 'email' in data:
        email = data['email'].strip()
        if not email or '@' not in email:
            return APIResponse.error(
                "邮箱格式不正确",
                "INVALID_EMAIL",
                "请提供有效的邮箱地址",
                400
            )
        
        # 检查邮箱是否被其他用户使用
        for uid, u in users_db.items():
            if uid != user_id and u['email'] == email:
                return APIResponse.error(
                    "邮箱已被使用",
                    "EMAIL_EXISTS",
                    f"邮箱 {email} 已被其他用户使用",
                    409
                )
        user['email'] = email
    
    user['updated_at'] = datetime.now().isoformat()
    
    logger.info(f"更新用户信息: {user}")
    return APIResponse.success(user, "用户信息更新成功")


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """DELETE /users/<id> - 删除用户"""
    if user_id not in users_db:
        return APIResponse.error(
            "用户未找到",
            "USER_NOT_FOUND",
            f"用户ID {user_id} 不存在",
            404
        )
    
    deleted_user = users_db.pop(user_id)
    logger.info(f"删除用户: {deleted_user}")
    return APIResponse.success(None, "用户删除成功", 204)


@app.route('/users/<int:user_id>', methods=['HEAD'])
def head_user(user_id):
    """HEAD /users/<id> - 获取用户元信息"""
    logger.info(f"获取用户元信息，用户ID: {user_id}")
    
    if user_id not in users_db:
        response = jsonify({"error": "用户未找到"})
        response.status_code = 404
        return response
    
    # HEAD请求只返回头部信息，不返回响应体
    response = jsonify({})
    response.status_code = 200
    return response


@app.route('/users', methods=['OPTIONS'])
def options_users():
    """OPTIONS /users - 获取支持的HTTP方法"""
    logger.info("获取支持的HTTP方法")
    
    # 返回支持的HTTP方法
    response = jsonify({
        "methods": ["GET", "POST", "PUT", "DELETE", "HEAD", "OPTIONS"],
        "description": "用户管理API支持的HTTP方法"
    })
    response.headers['Allow'] = 'GET, POST, PUT, DELETE, HEAD, OPTIONS'
    response.status_code = 200
    return response


@app.route('/users/<int:user_id>', methods=['OPTIONS'])
def options_user(user_id):
    """OPTIONS /users/<id> - 获取单个用户支持的HTTP方法"""
    logger.info(f"获取单个用户支持的HTTP方法，用户ID: {user_id}")
    
    # 检查用户是否存在
    if user_id not in users_db:
        response = jsonify({"error": "用户未找到"})
        response.status_code = 404
        return response
    
    # 返回支持的HTTP方法
    response = jsonify({
        "methods": ["GET", "PUT", "DELETE", "HEAD", "OPTIONS"],
        "description": "单个用户资源支持的HTTP方法"
    })
    response.headers['Allow'] = 'GET, PUT, DELETE, HEAD, OPTIONS'
    response.status_code = 200
    return response


# 自定义错误处理
@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return APIResponse.error(
        "请求的资源未找到",
        "NOT_FOUND",
        "请检查URL路径是否正确",
        404
    )


@app.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    return APIResponse.error(
        "请求方法不被允许",
        "METHOD_NOT_ALLOWED",
        "请检查请求方法是否正确",
        405
    )


@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return APIResponse.error(
        "服务器内部错误",
        "INTERNAL_ERROR",
        "请联系系统管理员",
        500
    )


def main():
    """主函数"""
    print("HTTP请求方法服务端实现示例")
    print("=" * 50)
    print("启动服务器...")
    print("访问 http://localhost:5003 查看API说明")
    print("使用 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动Flask应用
    app.run(host='localhost', port=5003, debug=True)


if __name__ == '__main__':
    main()