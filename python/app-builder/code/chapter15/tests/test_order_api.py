import pytest
import json
from app.models import Order, Product, Category

class TestOrderApi:
    
    def test_create_order(self, client, init_database):
        """测试创建订单"""
        # 获取产品
        product = init_database.session.query(Product).first()
        
        order_data = {
            'customer_name': '张三',
            'customer_email': 'zhangsan@example.com',
            'shipping_address': '北京市朝阳区某某街道',
            'items': [
                {
                    'product_id': product.id,
                    'quantity': 2,
                    'unit_price': float(product.price)
                }
            ]
        }
        
        response = client.post(
            '/api/v1/order/',
            data=json.dumps(order_data),
            content_type='application/json'
        )
        
        assert response.status_code == 201
        
        # 验证订单已创建
        order = init_database.session.query(Order).filter_by(customer_name='张三').first()
        assert order is not None
        assert order.total_amount == product.price * 2
    
    def test_get_order_detail(self, client, init_database):
        """测试获取订单详情"""
        # 先创建一个订单
        product = init_database.session.query(Product).first()
        order = Order(
            customer_name='李四',
            customer_email='lisi@example.com',
            shipping_address='上海市浦东新区某某路',
            total_amount=product.price
        )
        
        init_database.session.add(order)
        init_database.session.commit()
        
        response = client.get(f'/api/v1/order/{order.id}')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data
        assert data['result']['id'] == order.id
        assert data['result']['customer_name'] == '李四'
    
    def test_update_order(self, client, init_database):
        """测试更新订单"""
        # 创建订单
        product = init_database.session.query(Product).first()
        order = Order(
            customer_name='王五',
            customer_email='wangwu@example.com',
            shipping_address='广州市天河区某某街',
            total_amount=product.price
        )
        
        init_database.session.add(order)
        init_database.session.commit()
        
        update_data = {
            'shipping_address': '深圳市南山区某某路',
            'status': 'shipped'
        }
        
        response = client.put(
            f'/api/v1/order/{order.id}',
            data=json.dumps(update_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        
        # 验证订单已更新
        updated_order = init_database.session.query(Order).get(order.id)
        assert updated_order.shipping_address == '深圳市南山区某某路'
        assert updated_order.status == 'shipped'
    
    def test_get_orders_list(self, client, init_database):
        """测试获取订单列表"""
        response = client.get('/api/v1/order/')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert 'result' in data