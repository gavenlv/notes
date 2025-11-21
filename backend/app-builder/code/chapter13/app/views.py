from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Product, Category

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'category.name', 'price']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'category', 'price']}),
    ]

class CategoryModelView(ModelView):
    datamodel = SQLAInterface(Category)
    list_columns = ['name']