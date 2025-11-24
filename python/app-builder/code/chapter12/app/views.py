from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Product, Category

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'category.name', 'price']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'category', 'price']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    
    def pre_add(self, item):
        """在添加产品前验证"""
        if item.price < 0:
            raise ValueError("Price cannot be negative")
        super().pre_add(item)

class CategoryModelView(ModelView):
    datamodel = SQLAInterface(Category)
    list_columns = ['name', 'product_count']