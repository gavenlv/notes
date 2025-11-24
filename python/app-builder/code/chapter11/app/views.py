from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import render_template, request
from flask_caching import Cache
from sqlalchemy.orm import joinedload
from .models import Product, Category

# 初始化缓存
cache = Cache()

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'category.name', 'price']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'category', 'price']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    
    # 优化查询，预加载关系
    base_query = datamodel.session.query(Product).options(
        joinedload(Product.category)
    )

class ProductPublicView(BaseView):
    route_base = '/products'
    default_view = 'list'
    
    @expose('/')
    @cache.cached(timeout=600, key_prefix='product_list_page')
    def list(self):
        # 预加载分类和产品数据
        categories = self.appbuilder.get_session.query(Category).all()
        products = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).all()
        
        return self.render_template(
            'product/list.html', 
            products=products, 
            categories=categories
        )
    
    @expose('/<int:product_id>')
    @cache.cached(timeout=600, key_prefix='product_detail')
    def detail(self, product_id):
        # 预加载产品和分类数据
        product = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).get(product_id)
        
        if not product:
            return "Product not found", 404
            
        return self.render_template('product/detail.html', product=product)

# API视图
class ProductApiView(BaseView):
    route_base = '/api/products'
    
    @expose('/', methods=['GET'])
    @cache.cached(timeout=300, key_prefix='api_product_list')
    def list(self):
        products = self.appbuilder.get_session.query(Product).options(
            joinedload(Product.category)
        ).all()
        
        # 返回JSON格式
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