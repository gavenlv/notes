from flask import request
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from ..models import Category
from .schemas import CategorySchema

class CategoryApi(ModelRestApi):
    resource_name = 'category'
    datamodel = SQLAInterface(Category)
    
    # Schema配置
    list_model_schema = CategorySchema()
    show_model_schema = CategorySchema()
    add_model_schema = CategorySchema()
    edit_model_schema = CategorySchema()
    
    # 字段配置
    list_columns = ['id', 'name', 'description', 'is_active']
    show_columns = ['id', 'name', 'description', 'is_active', 'created_on', 'changed_on']
    add_columns = ['name', 'description', 'is_active']
    edit_columns = ['name', 'description', 'is_active']
    
    # 搜索配置
    search_columns = ['name', 'description']
    
    # 排序配置
    order_columns = ['id', 'name', 'created_on']
    
    # 分页配置
    page_size = 20

# 注册API端点
from . import bp
from flask_appbuilder import AppBuilder

@bp.record_once
def register_api(state):
    appbuilder = state.app.extensions['appbuilder']
    appbuilder.add_api(CategoryApi)