#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
API响应处理器
演示如何在服务端正确处理和返回状态码，以及统一的错误响应格式
"""

from flask import Flask, jsonify, request, abort
import json
import logging


# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)


# 模拟数据库存储
users_db = {
    1: {"id": 1, "name": "张三", "email": "zhangsan@example.com"},
    2: {"id": 2, "name": "李四", "email": "lisi@example.com"}
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
    """首页"""
    return APIResponse.success({
        "message": "API响应处理器示例",
        "description": "演示如何正确处理和返回HTTP状态码",
        "endpoints": {
            "GET /users": "获取用户列表",
            "GET /users/<id>": "获取单个用户",
            "POST /users": "创建新用户",
            "PUT /users/<id>": "更新用户信息",
            "DELETE /users/<id>": "删除用户"
        }
    })


@app.route('/users', methods=['GET'])
def get_users():
    """获取用户列表"""
    logger.info("获取用户列表")
    return APIResponse.success(list(users_db.values()), "用户列表获取成功")


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    """获取单个用户"""
    logger.info(f"获取用户信息，用户ID: {user_id}")
    
    if user_id not in users_db:
        return APIResponse.error(
            "用户未找到",
            "USER_NOT_FOUND",
            f"用户ID {user_id} 不存在",
            404
        )
    
    return APIResponse.success(users_db[user_id], "用户信息获取成功")


@app.route('/users', methods=['POST'])
def create_user():
    """创建新用户"""
    data = request.get_json()
    
    # 验证请求数据
    if not data:
        return APIResponse.error(
            "请求数据不能为空",
            "INVALID_REQUEST",
            "请提供有效的JSON数据",
            400
        )
    
    if 'name' not in data or 'email' not in data:
        return APIResponse.error(
            "缺少必需字段",
            "MISSING_FIELDS",
            "name 和 email 字段都是必需的",
            400
        )
    
    # 检查邮箱是否已存在
    for user in users_db.values():
        if user['email'] == data['email']:
            return APIResponse.error(
                "邮箱已被使用",
                "EMAIL_EXISTS",
                f"邮箱 {data['email']} 已被其他用户使用",
                409
            )
    
    # 创建新用户
    global next_user_id
    new_user = {
        "id": next_user_id,
        "name": data['name'],
        "email": data['email']
    }
    
    users_db[next_user_id] = new_user
    next_user_id += 1
    
    logger.info(f"创建新用户: {new_user}")
    return APIResponse.success(new_user, "用户创建成功", 201)


@app.route('/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    """更新用户信息"""
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
        user['name'] = data['name']
    if 'email' in data:
        # 检查邮箱是否被其他用户使用
        for uid, u in users_db.items():
            if uid != user_id and u['email'] == data['email']:
                return APIResponse.error(
                    "邮箱已被使用",
                    "EMAIL_EXISTS",
                    f"邮箱 {data['email']} 已被其他用户使用",
                    409
                )
        user['email'] = data['email']
    
    logger.info(f"更新用户信息: {user}")
    return APIResponse.success(user, "用户信息更新成功")


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    """删除用户"""
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


@app.route('/users/search', methods=['GET'])
def search_users():
    """搜索用户"""
    query = request.args.get('q', '')
    
    if not query:
        return APIResponse.error(
            "搜索关键字不能为空",
            "MISSING_QUERY",
            "请提供搜索关键字 q",
            400
        )
    
    # 简单的模糊匹配搜索
    results = []
    for user in users_db.values():
        if query.lower() in user['name'].lower() or query.lower() in user['email'].lower():
            results.append(user)
    
    logger.info(f"搜索用户，关键字: {query}，结果数量: {len(results)}")
    return APIResponse.success(results, f"找到 {len(results)} 个匹配的用户")


@app.route('/users/batch', methods=['DELETE'])
def batch_delete_users():
    """批量删除用户"""
    data = request.get_json()
    
    if not data or 'ids' not in data:
        return APIResponse.error(
            "缺少用户ID列表",
            "MISSING_IDS",
            "请提供要删除的用户ID列表",
            400
        )
    
    ids = data['ids']
    if not isinstance(ids, list):
        return APIResponse.error(
            "用户ID必须是数组",
            "INVALID_FORMAT",
            "ids 字段必须是一个数组",
            400
        )
    
    deleted_count = 0
    not_found_ids = []
    
    for user_id in ids:
        if user_id in users_db:
            users_db.pop(user_id)
            deleted_count += 1
        else:
            not_found_ids.append(user_id)
    
    message = f"成功删除 {deleted_count} 个用户"
    if not_found_ids:
        message += f"，{len(not_found_ids)} 个用户未找到"
    
    logger.info(f"批量删除用户，总数: {len(ids)}，成功: {deleted_count}")
    
    return APIResponse.success({
        "deleted_count": deleted_count,
        "not_found_ids": not_found_ids
    }, message)


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
    print("API响应处理器")
    print("=" * 50)
    print("启动服务器...")
    print("访问 http://localhost:5001 查看API说明")
    print("使用 Ctrl+C 停止服务器")
    print("=" * 50)
    
    # 启动Flask应用
    app.run(host='localhost', port=5001, debug=True)


if __name__ == '__main__':
    main()