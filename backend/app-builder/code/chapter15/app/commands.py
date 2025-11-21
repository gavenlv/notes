import click
from flask.cli import with_appcontext
from flask import current_app
from flask_appbuilder import Model
from .models import Category, Product

@click.command()
@with_appcontext
def init_db():
    """初始化数据库"""
    db = current_app.extensions['sqlalchemy'].db
    db.create_all()
    click.echo('Database initialized.')

@click.command()
@with_appcontext
def seed_data():
    """填充示例数据"""
    db = current_app.extensions['sqlalchemy'].db
    
    # 创建示例类别
    electronics = Category(name="电子产品", description="各种电子设备")
    books = Category(name="图书", description="各类书籍")
    clothing = Category(name="服装", description="时尚服饰")
    
    db.session.add_all([electronics, books, clothing])
    db.session.commit()
    
    # 创建示例产品
    products = [
        Product(
            name="智能手机",
            description="最新款智能手机",
            price=6999.99,
            stock_quantity=100,
            category_id=electronics.id
        ),
        Product(
            name="笔记本电脑",
            description="高性能笔记本电脑",
            price=12999.99,
            stock_quantity=50,
            category_id=electronics.id
        ),
        Product(
            name="Python编程入门",
            description="Python编程初学者指南",
            price=59.99,
            stock_quantity=200,
            category_id=books.id
        ),
        Product(
            name="休闲T恤",
            description="舒适的棉质T恤",
            price=89.99,
            stock_quantity=150,
            category_id=clothing.id
        )
    ]
    
    db.session.add_all(products)
    db.session.commit()
    
    click.echo('Sample data seeded.')