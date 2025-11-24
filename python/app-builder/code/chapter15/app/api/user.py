from flask import request
from flask_appbuilder.api import ModelRestApi, BaseApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from flask_appbuilder.security.sqla.models import User
from ..models import Order

class UserApi(ModelRestApi):
    resource_name = 'user'
    datamodel = SQLAInterface(User)
    
    # 字段配置
    list_columns = ['id', 'username', 'email', 'first_name', 'last_name', 'active']
    show_columns = ['id', 'username', 'email', 'first_name', 'last_name', 'active', 'last_login']
    add_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'roles']
    edit_columns = ['username', 'email', 'first_name', 'last_name', 'active', 'roles']
    
    # 搜索配置
    search_columns = ['username', 'email', 'first_name', 'last_name']
    
    # 排序配置
    order_columns = ['id', 'username', 'created_on']
    
    # 分页配置
    page_size = 20

class UserProfileApi(BaseApi):
    resource_name = 'user-profile'
    
    @protect()
    def get(self):
        """获取当前用户资料"""
        user = self.get_user()
        if not user:
            return self.response_404(message="User not found")
        
        return self.response(200,
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            created_on=user.created_on.isoformat() if user.created_on else None
        )
    
    @protect()
    def put(self):
        """更新当前用户资料"""
        user = self.get_user()
        if not user:
            return self.response_404(message="User not found")
        
        data = request.get_json()
        
        # 更新允许的字段
        updatable_fields = ['first_name', 'last_name', 'email']
        for field in updatable_fields:
            if field in data:
                setattr(user, field, data[field])
        
        # 保存更改
        self.appbuilder.get_session.commit()
        
        return self.response(200, message="Profile updated successfully")

# 注册API端点
from . import bp
from flask_appbuilder import AppBuilder

@bp.record_once
def register_api(state):
    appbuilder = state.app.extensions['appbuilder']
    appbuilder.add_api(UserApi)
    appbuilder.add_api(UserProfileApi)