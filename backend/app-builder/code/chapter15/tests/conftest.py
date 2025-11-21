import pytest
import os
import tempfile
from app import create_app
from app import db as _db
from app.models import Category, Product

@pytest.fixture
def app():
    """Create application for testing."""
    # Create temporary database
    db_fd, db_path = tempfile.mkstemp()
    
    # Configure app for testing
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': f'sqlite:///{db_path}',
        'WTF_CSRF_ENABLED': False,
        'SECRET_KEY': 'test-secret-key',
        'JWT_SECRET_KEY': 'test-jwt-secret'
    })
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()
    
    # Close and remove temporary database
    os.close(db_fd)
    os.unlink(db_path)

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def runner(app):
    """Create test CLI runner."""
    return app.test_cli_runner()

@pytest.fixture
def init_database(app):
    """Initialize database with test data."""
    with app.app_context():
        # Create test categories
        electronics = Category(name="电子产品", description="各种电子设备")
        books = Category(name="图书", description="各类书籍")
        
        _db.session.add_all([electronics, books])
        _db.session.commit()
        
        # Create test products
        smartphone = Product(
            name="智能手机",
            description="最新款智能手机",
            price=6999.99,
            stock_quantity=100,
            category_id=electronics.id
        )
        
        book = Product(
            name="Python编程入门",
            description="Python编程初学者指南",
            price=59.99,
            stock_quantity=200,
            category_id=books.id
        )
        
        _db.session.add_all([smartphone, book])
        _db.session.commit()
        
        yield _db
        
        # Cleanup
        meta = _db.metadata
        for table in reversed(meta.sorted_tables):
            _db.session.execute(table.delete())
        _db.session.commit()