from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import lazy_gettext as _
from flask import flash
from .models import Product

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'description', 'price']
    show_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']}),
        (_('Audit'), {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    edit_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    
    label_columns = {
        'name': _('Product Name'),
        'description': _('Product Description'),
        'price': _('Product Price')
    }
    
    def post_add(self, item):
        flash(_('Product %(name)s was successfully added.', name=item.name), 'info')
        super().post_add(item)
    
    def post_update(self, item):
        flash(_('Product %(name)s was successfully updated.', name=item.name), 'info')
        super().post_update(item)
    
    def post_delete(self, item):
        flash(_('Product %(name)s was successfully deleted.', name=item.name), 'info')
        super().post_delete(item)