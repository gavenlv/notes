from flask_appbuilder.api.schemas import BaseModelSchema
from marshmallow import fields, validate, post_load
from ..models import Category, Product, Order, OrderItem

class CategorySchema(BaseModelSchema):
    class Meta:
        model = Category
        load_instance = True
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=50))
    description = fields.Str(validate=validate.Length(max=500))

class ProductSchema(BaseModelSchema):
    class Meta:
        model = Product
        load_instance = True
        include_relationships = True
    
    name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    description = fields.Str(validate=validate.Length(max=500))
    price = fields.Decimal(required=True, validate=validate.Range(min=0))
    stock_quantity = fields.Int(validate=validate.Range(min=0))
    
    # 关联字段
    category_name = fields.Method("get_category_name", dump_only=True)
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None

class OrderItemSchema(BaseModelSchema):
    class Meta:
        model = OrderItem
        load_instance = True
    
    product_name = fields.Method("get_product_name", dump_only=True)
    
    def get_product_name(self, obj):
        return obj.product.name if obj.product else None

class OrderSchema(BaseModelSchema):
    class Meta:
        model = Order
        load_instance = True
    
    items = fields.Nested(OrderItemSchema, many=True, dump_only=True)
    customer_name = fields.Str(required=True, validate=validate.Length(min=1, max=100))
    customer_email = fields.Email(validate=validate.Length(max=100))

class ProductSearchSchema(BaseModelSchema):
    """产品搜索参数Schema"""
    name = fields.Str(validate=validate.Length(max=100))
    min_price = fields.Decimal(validate=validate.Range(min=0))
    max_price = fields.Decimal(validate=validate.Range(min=0))
    category_id = fields.Int()