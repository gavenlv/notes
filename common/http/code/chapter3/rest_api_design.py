#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RESTful API状态码设计示例
展示完整的用户管理API示例，演示REST操作对应的状态码
"""

from flask import Flask, jsonify, request, abort
import json
import re
from datetime import datetime


app = Flask(__name__)


# 模拟数据库存储
users_db = {}
next_user_id = 1

# 模拟认证令牌
VALID_TOKENS = {
    "admin_token": {"role": "admin", "user_id": 0},
    "user_token": {"role": "user", "user_id": 0}
}


def require_auth(role=None):
    """认证装饰器"""
    def decorator(f):
        def wrapper(*args, **kwargs):
            auth_header = request.headers.get('Authorization')
            
            if not auth_header:
                return jsonify({
                    "error": {
                        "code": "UNAUTHORIZED",
                        "message": "缺少认证信息",
                        "details": "请在请求头中提供Authorization字段"
                    }
                }), 401
            
            if not auth_header.startswith('Bearer '):
                return jsonify({
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "认证令牌格式错误",
                        "details": "请使用Bearer令牌格式"
                    }
                }), 401
            
            token = auth_header.split(' ')[1]
            if token not in VALID_TOKENS:
                return jsonify({
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "无效的认证令牌",
                        "details": "请提供有效的认证令牌"
                    }
                }), 401
            
            user_info = VALID_TOKENS[token]
            if role and user_info["role"] != role:
                return jsonify({
                    "error": {
                        "code": "FORBIDDEN",
                        "message": "权限不足",
                        "details": f"此操作需要 {role} 权限"
                    }
                }), 403
            
            # 将用户信息添加到请求上下文
            request.user_info = user_info
            return f(*args, **kwargs)
        wrapper.__name__ = f.__name__
        return wrapper
    return decorator


def validate_email(email):
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None


def validate_user_data(data, required_fields=None):
    """验证用户数据"""
    if required_fields is None:
        required_fields = ['name', 'email']
    
    errors = []
    
    # 检查必需字段
    for field in required_fields:
        if field not in data:
            errors.append(f"缺少必需字段: {field}")
    
    # 验证字段值
    if 'name' in data and len(data['name'].strip()) == 0:
        errors.append("姓名不能为空")
    
    if 'email' in data:
        if len(data['email'].strip()) == 0:
            errors.append("邮箱不能为空")
        elif not validate_email(data['email']):
            errors.append("邮箱格式不正确")
        else:
            # 检查邮箱是否已存在
            for user in users_db.values():
                if user['email'] == data['email']:
                    errors.append(f"邮箱 {data['email']} 已被使用")
                    break
    
    return errors


class UserAPI:
    """用户管理API"""
    
    @staticmethod
    def get_users():
        """获取用户列表"""
        # 支持分页
        page = request.args.get('page', 1, type=int)
        per_page = min(request.args.get('per_page', 10, type=int), 100)  # 最大每页100条
        
        start = (page - 1) * per_page
        end = start + per_page
        users_list = list(users_db.values())[start:end]
        
        return jsonify({
            "data": users_list,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": len(users_db),
                "pages": (len(users_db) + per_page - 1) // per_page
            }
        }), 200
    
    @staticmethod
    def get_user(user_id):
        """获取单个用户"""
        if user_id not in users_db:
            return jsonify({
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "用户未找到",
                    "details": f"用户ID {user_id} 不存在"
                }
            }), 404
        
        return jsonify({
            "data": users_db[user_id]
        }), 200
    
    @staticmethod
    def create_user():
        """创建新用户"""
        data = request.get_json()
        
        # 验证请求数据
        if not data:
            return jsonify({
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "请求数据不能为空",
                    "details": "请提供有效的JSON数据"
                }
            }), 400
        
        errors = validate_user_data(data)
        if errors:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "details": errors
                }
            }), 400
        
        # 创建新用户
        global next_user_id
        new_user = {
            "id": next_user_id,
            "name": data['name'].strip(),
            "email": data['email'].strip(),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        users_db[next_user_id] = new_user
        next_user_id += 1
        
        return jsonify({
            "data": new_user,
            "message": "用户创建成功"
        }), 201
    
    @staticmethod
    def update_user(user_id):
        """更新用户信息"""
        if user_id not in users_db:
            return jsonify({
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "用户未找到",
                    "details": f"用户ID {user_id} 不存在"
                }
            }), 404
        
        data = request.get_json()
        
        if not data:
            return jsonify({
                "error": {
                    "code": "INVALID_REQUEST",
                    "message": "请求数据不能为空",
                    "details": "请提供有效的JSON数据"
                }
            }), 400
        
        # 只验证提供的字段
        provided_fields = {k: v for k, v in data.items() if k in ['name', 'email']}
        errors = validate_user_data(provided_fields, required_fields=[])
        if errors:
            return jsonify({
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "数据验证失败",
                    "details": errors
                }
            }), 400
        
        # 更新用户信息
        user = users_db[user_id]
        if 'name' in data:
            user['name'] = data['name'].strip()
        if 'email' in data:
            user['email'] = data['email'].strip()
        user['updated_at'] = datetime.now().isoformat()
        
        return jsonify({
            "data": user,
            "message": "用户信息更新成功"
        }), 200
    
    @staticmethod
    def delete_user(user_id):
        """删除用户"""
        if user_id not in users_db:
            return jsonify({
                "error": {
                    "code": "USER_NOT_FOUND",
                    "message": "用户未找到",
                    "details": f"用户ID {user_id} 不存在"
                }
            }), 404
        
        deleted_user = users_db.pop(user_id)
        
        return jsonify({
            "message": "用户删除成功"
        }), 200
    
    @staticmethod
    def search_users():
        """搜索用户"""
        query = request.args.get('q', '').strip()
        
        if not query:
            return jsonify({
                "error": {
                    "code": "MISSING_QUERY",
                    "message": "搜索关键字不能为空",
                    "details": "请提供搜索关键字 q"
                }
            }), 400
        
        # 简单的模糊匹配搜索
        results = []
        for user in users_db.values():
            if query.lower() in user['name'].lower() or query.lower() in user['email'].lower():
                results.append(user)
        
        return jsonify({
            "data": results,
            "meta": {
                "query": query,
                "count": len(results)
            }
        }), 200


# API路由定义
@app.route('/')
def index():
    """API首页"""
    return jsonify({
        "message": "用户管理API",
        "version": "1.0.0",
        "description": "完整的用户管理RESTful API示例",
        "endpoints": {
            "GET /users": "获取用户列表（支持分页）",
            "GET /users/{id}": "获取单个用户",
            "POST /users": "创建新用户",
            "PUT /users/{id}": "更新用户信息",
            "DELETE /users/{id}": "删除用户",
            "GET /users/search": "搜索用户"
        },
        "authentication": {
            "header": "Authorization: Bearer {token}",
            "tokens": {
                "admin_token": "管理员权限",
                "user_token": "普通用户权限"
            }
        }
    }), 200


@app.route('/users', methods=['GET'])
@require_auth()
def get_users():
    """获取用户列表"""
    return UserAPI.get_users()


@app.route('/users/<int:user_id>', methods=['GET'])
@require_auth()
def get_user(user_id):
    """获取单个用户"""
    return UserAPI.get_user(user_id)


@app.route('/users', methods=['POST'])
@require_auth()
def create_user():
    """创建新用户"""
    return UserAPI.create_user()


@app.route('/users/<int:user_id>', methods=['PUT'])
@require_auth()
def update_user(user_id):
    """更新用户信息"""
    return UserAPI.update_user(user_id)


@app.route('/users/<int:user_id>', methods=['DELETE'])
@require_auth(role='admin')  # 只有管理员可以删除用户
def delete_user(user_id):
    """删除用户"""
    return UserAPI.delete_user(user_id)


@app.route('/users/search', methods=['GET'])
@require_auth()
def search_users():
    """搜索用户"""
    return UserAPI.search_users()


# 自定义错误处理
@app.errorhandler(404)
def not_found(error):
    """处理404错误"""
    return jsonify({
        "error": {
            "code": "ENDPOINT_NOT_FOUND",
            "message": "请求的端点未找到",
            "details": "请检查URL路径是否正确"
        }
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """处理405错误"""
    return jsonify({
        "error": {
            "code": "METHOD_NOT_ALLOWED",
            "message": "请求方法不被允许",
            "details": "请检查请求方法是否正确"
        }
    }), 405


@app.errorhandler(415)
def unsupported_media_type(error):
    """处理415错误"""
    return jsonify({
        "error": {
            "code": "UNSUPPORTED_MEDIA_TYPE",
            "message": "不支持的媒体类型",
            "details": "请确保Content-Type为application/json"
        }
    }), 415


@app.errorhandler(500)
def internal_error(error):
    """处理500错误"""
    return jsonify({
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "服务器内部错误",
            "details": "请联系系统管理员"
        }
    }), 500


def main():
    """主函数"""
    print("RESTful API状态码设计示例")
    print("=" * 50)
    print("启动服务器...")
    print("访问 http://localhost:5002 查看API说明")
    print("\n可用的认证令牌:")
    print("- admin_token (管理员权限)")
    print("- user_token (普通用户权限)")
    print("\n使用 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 添加一些示例数据
    global next_user_id
    users_db[1] = {
        "id": 1,
        "name": "张三",
        "email": "zhangsan@example.com",
        "created_at": "2023-01-01T12:00:00",
        "updated_at": "2023-01-01T12:00:00"
    }
    users_db[2] = {
        "id": 2,
        "name": "李四",
        "email": "lisi@example.com",
        "created_at": "2023-01-02T12:00:00",
        "updated_at": "2023-01-02T12:00:00"
    }
    next_user_id = 3
    
    # 启动Flask应用
    app.run(host='localhost', port=5002, debug=True)


if __name__ == '__main__':
    main()