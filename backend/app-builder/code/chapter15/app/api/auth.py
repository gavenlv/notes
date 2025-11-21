from flask import request, jsonify
from flask_appbuilder.api import BaseApi
from flask_appbuilder.security.decorators import authenticate
from flask_jwt_extended import create_access_token, jwt_required, get_jwt_identity

class AuthApi(BaseApi):
    resource_name = 'auth'
    
    @authenticate
    def post(self):
        """JWT登录端点"""
        username = request.json.get('username', None)
        password = request.json.get('password', None)
        
        # 验证用户凭据
        user = self.appbuilder.sm.auth_user_db(username, password)
        if not user:
            return self.response_401(message="Invalid credentials")
        
        # 创建访问令牌
        access_token = create_access_token(identity=user.id)
        return self.response(200, access_token=access_token)
    
    @jwt_required()
    def get(self):
        """获取用户资料"""
        current_user_id = get_jwt_identity()
        user = self.appbuilder.sm.get_user_by_id(current_user_id)
        
        if not user:
            return self.response_404(message="User not found")
        
        return self.response(200, 
            id=user.id,
            username=user.username,
            email=user.email
        )

# 注册API端点
from . import bp
from flask_appbuilder import AppBuilder

@bp.record_once
def register_api(state):
    appbuilder = state.app.extensions['appbuilder']
    appbuilder.add_api(AuthApi)