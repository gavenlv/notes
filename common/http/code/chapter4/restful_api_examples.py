#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
RESTful API设计示例
展示如何正确使用HTTP方法设计RESTful API
"""

from flask import Flask, jsonify, request, abort
from datetime import datetime
import uuid
from typing import Dict, List, Optional


app = Flask(__name__)


# 模拟数据库
class Database:
    """模拟数据库存储"""
    
    def __init__(self):
        self.posts = {}  # 文章存储
        self.comments = {}  # 评论存储
        self.users = {}  # 用户存储
        self.init_sample_data()
    
    def init_sample_data(self):
        """初始化示例数据"""
        # 创建示例用户
        user_id = str(uuid.uuid4())
        self.users[user_id] = {
            "id": user_id,
            "username": "alice",
            "email": "alice@example.com",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        
        # 创建示例文章
        post_id = str(uuid.uuid4())
        self.posts[post_id] = {
            "id": post_id,
            "title": "第一篇文章",
            "content": "这是第一篇文章的内容。",
            "author_id": user_id,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": ["示例", "教程"],
            "published": True
        }
    
    def get_posts(self) -> List[Dict]:
        """获取所有文章"""
        return list(self.posts.values())
    
    def get_post(self, post_id: str) -> Optional[Dict]:
        """根据ID获取文章"""
        return self.posts.get(post_id)
    
    def create_post(self, data: Dict) -> Dict:
        """创建新文章"""
        post_id = str(uuid.uuid4())
        post = {
            "id": post_id,
            "title": data.get("title", ""),
            "content": data.get("content", ""),
            "author_id": data.get("author_id", ""),
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "tags": data.get("tags", []),
            "published": data.get("published", False)
        }
        self.posts[post_id] = post
        return post
    
    def update_post(self, post_id: str, data: Dict) -> Optional[Dict]:
        """更新文章"""
        if post_id not in self.posts:
            return None
        
        post = self.posts[post_id]
        post.update({
            "title": data.get("title", post["title"]),
            "content": data.get("content", post["content"]),
            "tags": data.get("tags", post["tags"]),
            "published": data.get("published", post["published"]),
            "updated_at": datetime.now().isoformat()
        })
        return post
    
    def delete_post(self, post_id: str) -> bool:
        """删除文章"""
        if post_id in self.posts:
            del self.posts[post_id]
            return True
        return False


# 初始化数据库
db = Database()


class APIResponse:
    """API响应格式化类"""
    
    @staticmethod
    def success(data=None, message="操作成功", status_code=200):
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
            
        return jsonify(response), status_code


def validate_post_data(data: Dict, required_fields: List[str] = None) -> tuple:
    """
    验证文章数据
    
    Args:
        data: 要验证的数据
        required_fields: 必需字段列表
        
    Returns:
        (is_valid, error_message)
    """
    if required_fields is None:
        required_fields = ["title", "content", "author_id"]
    
    if not data:
        return False, "请求数据不能为空"
    
    for field in required_fields:
        if field not in data or not data[field]:
            return False, f"缺少必需字段: {field}"
    
    # 验证标题长度
    if len(data["title"]) > 200:
        return False, "标题长度不能超过200字符"
    
    # 验证内容长度
    if len(data["content"]) > 10000:
        return False, "内容长度不能超过10000字符"
    
    return True, ""


@app.route('/')
def api_index():
    """API首页"""
    return APIResponse.success({
        "message": "RESTful API设计示例",
        "version": "1.0.0",
        "description": "展示如何正确使用HTTP方法设计RESTful API",
        "endpoints": {
            "GET /api/posts": "获取文章列表",
            "POST /api/posts": "创建新文章",
            "GET /api/posts/<id>": "获取单篇文章",
            "PUT /api/posts/<id>": "更新文章",
            "DELETE /api/posts/<id>": "删除文章",
            "GET /api/posts/<id>/comments": "获取文章评论",
            "POST /api/posts/<id>/comments": "为文章添加评论"
        }
    })


@app.route('/api/posts', methods=['GET'])
def get_posts():
    """GET /api/posts - 获取文章列表"""
    # 支持查询参数
    page = request.args.get('page', 1, type=int)
    per_page = min(request.args.get('per_page', 10, type=int), 100)
    published_only = request.args.get('published', 'true').lower() == 'true'
    author_id = request.args.get('author_id', '')
    tag = request.args.get('tag', '')
    
    # 获取所有文章
    posts = db.get_posts()
    
    # 应用过滤条件
    if published_only:
        posts = [post for post in posts if post.get('published', False)]
    
    if author_id:
        posts = [post for post in posts if post.get('author_id') == author_id]
    
    if tag:
        posts = [post for post in posts if tag in post.get('tags', [])]
    
    # 分页处理
    start = (page - 1) * per_page
    end = start + per_page
    paginated_posts = posts[start:end]
    
    return APIResponse.success({
        "posts": paginated_posts,
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": len(posts),
            "pages": (len(posts) + per_page - 1) // per_page
        }
    })


@app.route('/api/posts', methods=['POST'])
def create_post():
    """POST /api/posts - 创建新文章"""
    data = request.get_json()
    
    # 验证数据
    is_valid, error_message = validate_post_data(data)
    if not is_valid:
        return APIResponse.error(
            error_message,
            "INVALID_DATA",
            status_code=400
        )
    
    # 创建文章
    post = db.create_post(data)
    return APIResponse.success(post, "文章创建成功", 201)


@app.route('/api/posts/<post_id>', methods=['GET'])
def get_post(post_id):
    """GET /api/posts/<id> - 获取单篇文章"""
    post = db.get_post(post_id)
    if not post:
        return APIResponse.error(
            "文章未找到",
            "POST_NOT_FOUND",
            f"文章ID {post_id} 不存在",
            404
        )
    
    return APIResponse.success(post)


@app.route('/api/posts/<post_id>', methods=['PUT'])
def update_post(post_id):
    """PUT /api/posts/<id> - 更新文章"""
    # 检查文章是否存在
    existing_post = db.get_post(post_id)
    if not existing_post:
        return APIResponse.error(
            "文章未找到",
            "POST_NOT_FOUND",
            f"文章ID {post_id} 不存在",
            404
        )
    
    data = request.get_json()
    
    # 验证数据（不需要必需字段，因为是部分更新）
    if not data:
        return APIResponse.error(
            "请求数据不能为空",
            "INVALID_DATA",
            status_code=400
        )
    
    # 更新文章
    updated_post = db.update_post(post_id, data)
    if not updated_post:
        return APIResponse.error(
            "更新失败",
            "UPDATE_FAILED",
            status_code=500
        )
    
    return APIResponse.success(updated_post, "文章更新成功")


@app.route('/api/posts/<post_id>', methods=['DELETE'])
def delete_post(post_id):
    """DELETE /api/posts/<id> - 删除文章"""
    deleted = db.delete_post(post_id)
    if not deleted:
        return APIResponse.error(
            "文章未找到",
            "POST_NOT_FOUND",
            f"文章ID {post_id} 不存在",
            404
        )
    
    return APIResponse.success(None, "文章删除成功", 204)


@app.route('/api/posts/<post_id>/comments', methods=['GET'])
def get_comments(post_id):
    """GET /api/posts/<id>/comments - 获取文章评论"""
    # 检查文章是否存在
    post = db.get_post(post_id)
    if not post:
        return APIResponse.error(
            "文章未找到",
            "POST_NOT_FOUND",
            f"文章ID {post_id} 不存在",
            404
        )
    
    # 模拟返回评论数据
    comments = [
        {
            "id": str(uuid.uuid4()),
            "post_id": post_id,
            "author": "评论者1",
            "content": "这是一条示例评论。",
            "created_at": datetime.now().isoformat()
        },
        {
            "id": str(uuid.uuid4()),
            "post_id": post_id,
            "author": "评论者2",
            "content": "另一条评论。",
            "created_at": datetime.now().isoformat()
        }
    ]
    
    return APIResponse.success({
        "comments": comments,
        "count": len(comments)
    })


@app.route('/api/posts/<post_id>/comments', methods=['POST'])
def create_comment(post_id):
    """POST /api/posts/<id>/comments - 为文章添加评论"""
    # 检查文章是否存在
    post = db.get_post(post_id)
    if not post:
        return APIResponse.error(
            "文章未找到",
            "POST_NOT_FOUND",
            f"文章ID {post_id} 不存在",
            404
        )
    
    data = request.get_json()
    
    if not data or 'content' not in data or not data['content']:
        return APIResponse.error(
            "评论内容不能为空",
            "INVALID_COMMENT",
            status_code=400
        )
    
    # 创建评论
    comment = {
        "id": str(uuid.uuid4()),
        "post_id": post_id,
        "author": data.get('author', '匿名用户'),
        "content": data['content'],
        "created_at": datetime.now().isoformat()
    }
    
    return APIResponse.success(comment, "评论创建成功", 201)


# 错误处理
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


def demonstrate_restful_api():
    """演示RESTful API的使用"""
    print("RESTful API设计示例")
    print("=" * 50)
    print("启动服务器...")
    print("API端点:")
    print("  GET    /api/posts           # 获取文章列表")
    print("  POST   /api/posts           # 创建新文章")
    print("  GET    /api/posts/<id>      # 获取单篇文章")
    print("  PUT    /api/posts/<id>      # 更新文章")
    print("  DELETE /api/posts/<id>      # 删除文章")
    print("  GET    /api/posts/<id>/comments  # 获取文章评论")
    print("  POST   /api/posts/<id>/comments  # 为文章添加评论")
    print("\n访问 http://localhost:5004 查看API文档")
    print("使用 Ctrl+C 停止服务器")
    
    # 启动Flask应用
    app.run(host='localhost', port=5004, debug=True)


if __name__ == '__main__':
    demonstrate_restful_api()