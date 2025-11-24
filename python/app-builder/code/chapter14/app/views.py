from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Product, Category

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    # 列表视图列
    list_columns = ['name', 'category.name', 'price', 'stock_quantity', 'is_active']
    
    # 显示字段集
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description']}),
        ('Details', {'fields': ['category', 'price', 'stock_quantity', 'is_active']})
    ]
    
    # 编辑字段集
    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'description']}),
        ('Details', {'fields': ['category', 'price', 'stock_quantity', 'is_active']})
    ]
    
    # 添加字段集
    add_fieldsets = [
        ('Summary', {'fields': ['name', 'description']}),
        ('Details', {'fields': ['category', 'price', 'stock_quantity', 'is_active']})
    ]

class CategoryModelView(ModelView):
    datamodel = SQLAInterface(Category)
    
    # 列表视图列
    list_columns = ['name', 'description']
    
    # 相关视图
    related_views = [ProductModelView]