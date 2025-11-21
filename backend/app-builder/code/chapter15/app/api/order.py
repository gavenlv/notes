from flask import request
from flask_appbuilder.api import ModelRestApi
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.security.decorators import protect
from ..models import Order, OrderItem
from .schemas import OrderSchema

class OrderApi(ModelRestApi):
    resource_name = 'order'
    datamodel = SQLAInterface(Order)
    
    # Schema配置
    list_model_schema = OrderSchema()
    show_model_schema = OrderSchema()
    add_model_schema = OrderSchema()
    edit_model_schema = OrderSchema()
    
    # 字段配置
    list_columns = ['id', 'order_number', 'customer_name', 'total_amount', 'status', 'created_on']
    show_columns = ['id', 'order_number', 'customer_name', 'customer_email', 'total_amount', 'status', 'created_on', 'items']
    add_columns = ['order_number', 'customer_name', 'customer_email', 'status']
    edit_columns = ['status']
    
    # 搜索配置
    search_columns = ['order_number', 'customer_name', 'customer_email', 'status']
    
    # 排序配置
    order_columns = ['id', 'created_on', 'order_number']
    order_direction = 'desc'
    
    # 分页配置
    page_size = 15
    
    # 自定义创建方法
    @protect()
    def post(self):
        """创建订单"""
        # 在创建订单前添加业务逻辑
        data = request.get_json()
        
        # 生成订单号（如果未提供）
        if 'order_number' not in data:
            import uuid
            data['order_number'] = f"ORD-{uuid.uuid4().hex[:8].upper()}"
        
        return super().post()
    
    # 自定义更新方法
    @protect()
    def put(self, pk):
        """更新订单"""
        # 添加订单状态变更日志
        order = self.datamodel.get(pk)
        old_status = order.status if order else None
        
        result = super().put(pk)
        
        # 记录状态变更（实际应用中可能写入日志表）
        if old_status and order and old_status != order.status:
            print(f"Order {order.order_number} status changed from {old_status} to {order.status}")
        
        return result

# 注册API端点
from . import bp
from flask_appbuilder import AppBuilder

@bp.record_once
def register_api(state):
    appbuilder = state.app.extensions['appbuilder']
    appbuilder.add_api(OrderApi)