from flask import request
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from sqlalchemy import and_
from ..models import Product, Category
from .schemas import ProductSchema, ProductSearchSchema

class ProductApi(ModelRestApi):
    resource_name = 'product'
    datamodel = SQLAInterface(Product)
    
    # Schema配置
    list_model_schema = ProductSchema()
    show_model_schema = ProductSchema()
    add_model_schema = ProductSchema()
    edit_model_schema = ProductSchema()
    
    # 字段配置
    list_columns = ['id', 'name', 'category_name', 'price', 'stock_quantity', 'is_active']
    show_columns = ['id', 'name', 'description', 'category.name', 'price', 'stock_quantity', 'is_active', 'created_on']
    add_columns = ['name', 'description', 'price', 'stock_quantity', 'category', 'is_active']
    edit_columns = ['name', 'description', 'price', 'stock_quantity', 'category', 'is_active']
    
    # 搜索配置
    search_columns = ['name', 'description', 'category', 'price']
    
    # 排序配置
    order_columns = ['id', 'name', 'price', 'created_on']
    
    # 分页配置
    page_size = 20
    
    # 自定义搜索端点
    @protect()
    def get_list(self):
        """自定义列表获取，支持高级搜索"""
        # 获取搜索参数
        search_params = {}
        for key in ['name', 'min_price', 'max_price', 'category_id']:
            if key in request.args:
                search_params[key] = request.args.get(key)
        
        # 如果有搜索参数，应用自定义过滤
        if search_params:
            query = self.datamodel.session.query(self.datamodel.obj)
            
            # 名称模糊匹配
            if 'name' in search_params:
                query = query.filter(Product.name.contains(search_params['name']))
            
            # 价格范围过滤
            if 'min_price' in search_params:
                query = query.filter(Product.price >= search_params['min_price'])
            if 'max_price' in search_params:
                query = query.filter(Product.price <= search_params['max_price'])
            
            # 类别过滤
            if 'category_id' in search_params:
                query = query.filter(Product.category_id == search_params['category_id'])
            
            # 只返回活跃产品
            query = query.filter(Product.is_active == True)
            
            # 应用分页和排序
            return self.paginate_query(query)
        
        # 否则使用默认行为
        return super().get_list()

# 注册API端点
from . import bp
from flask_appbuilder import AppBuilder

@bp.record_once
def register_api(state):
    appbuilder = state.app.extensions['appbuilder']
    appbuilder.add_api(ProductApi)