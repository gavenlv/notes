import pytest
from flask_appbuilder.security.sqla.models import User

def test_product_model_view(client):
    """测试产品模型视图"""
    # 先登录管理员用户
    with client.application.app_context():
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@test.com'
        admin_user.active = True
        admin_user.password = 'admin'
        from app import db
        db.session.add(admin_user)
        db.session.commit()
    
    # 登录
    response = client.post('/login/', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # 访问产品列表页面
    response = client.get('/productmodelview/list/')
    assert response.status_code == 200

def test_category_model_view(client):
    """测试分类模型视图"""
    # 先登录管理员用户
    with client.application.app_context():
        admin_user = User()
        admin_user.username = 'admin'
        admin_user.email = 'admin@test.com'
        admin_user.active = True
        admin_user.password = 'admin'
        from app import db
        db.session.add(admin_user)
        db.session.commit()
    
    # 登录
    response = client.post('/login/', data={
        'username': 'admin',
        'password': 'admin'
    }, follow_redirects=True)
    
    assert response.status_code == 200
    
    # 访问分类列表页面
    response = client.get('/categorymodelview/list/')
    assert response.status_code == 200