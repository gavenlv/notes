import pytest
from app import app, db

@pytest.fixture(scope='session')
def app_context():
    """创建应用上下文"""
    app.config.from_object('config.TestingConfig')
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def client(app_context):
    """创建测试客户端"""
    with app_context.test_client() as client:
        with app_context.app_context():
            db.create_all()
            yield client
            db.drop_all()

@pytest.fixture(scope='function')
def db_session(app_context):
    """创建数据库会话"""
    with app_context.app_context():
        db.create_all()
        yield db.session
        db.drop_all()