from flask_appbuilder.api import BaseApi
from flask_appbuilder import expose
from sqlalchemy.orm import joinedload
from .models import Product

class ProductApi(BaseApi):
    resource_name = 'products'
    
    @expose('/', methods=['GET'])
    def get_list(self):
        """获取产品列表"""
        products = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).all()
        
        result = []
        for product in products:
            result.append({
                'id': product.id,
                'name': product.name,
                'description': product.description,
                'price': product.price,
                'category': product.category.name if product.category else None
            })
        
        return self.response(200, result=result)
    
    @expose('/<int:pk>', methods=['GET'])
    def get(self, pk):
        """获取单个产品"""
        product = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).get(pk)
        
        if not product:
            return self.response_404()
        
        result = {
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'category': product.category.name if product.category else None
        }
        
        return self.response(200, result=result)