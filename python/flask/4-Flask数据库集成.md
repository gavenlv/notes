# 第四章 Flask数据库集成

## 4.1 数据库基础

大多数Web应用都需要持久化存储数据，Flask支持多种数据库解决方案。

### SQLAlchemy简介
SQLAlchemy是Python中最流行的ORM(Object Relational Mapping)框架之一，Flask-SQLAlchemy是其针对Flask的扩展。

### 安装依赖
```bash
pip install Flask-SQLAlchemy
```

## 4.2 配置数据库

### 基本配置
```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# SQLite数据库配置
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# 禁用跟踪修改以节省内存
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
```

### 连接其他数据库
```python
# MySQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/dbname'

# PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://username:password@localhost/dbname'
```

## 4.3 定义模型

模型是数据库表在代码中的表示。

### 基本模型定义
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    
    def __repr__(self):
        return f'<User {self.username}>'
```

### 字段类型和约束
```python
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # 关系定义
    user = db.relationship('User', backref=db.backref('posts', lazy=True))
```

## 4.4 数据库操作

### 创建表
```python
# 在应用上下文中创建所有表
with app.app_context():
    db.create_all()
```

### 添加数据
```python
@app.route('/add_user')
def add_user():
    user = User(username='john', email='john@example.com')
    db.session.add(user)
    db.session.commit()
    return '用户添加成功'
```

### 查询数据
```python
@app.route('/users')
def get_users():
    # 查询所有用户
    users = User.query.all()
    
    # 根据条件查询
    user = User.query.filter_by(username='john').first()
    
    # 使用原生SQL查询
    users = db.session.execute(db.select(User)).scalars().all()
    
    return render_template('users.html', users=users)
```

### 更新数据
```python
@app.route('/update_user/<int:user_id>')
def update_user(user_id):
    user = User.query.get_or_404(user_id)
    user.email = 'newemail@example.com'
    db.session.commit()
    return '用户信息更新成功'
```

### 删除数据
```python
@app.route('/delete_user/<int:user_id>')
def delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    return '用户删除成功'
```

## 4.5 关系映射

### 一对多关系
```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # 一对多关系
    posts = db.relationship('Post', backref='author', lazy=True)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
```

### 多对多关系
```python
# 关联表
tags_posts = db.Table('tags_posts',
    db.Column('tag_id', db.Integer, db.ForeignKey('tag.id'), primary_key=True),
    db.Column('post_id', db.Integer, db.ForeignKey('post.id'), primary_key=True)
)

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    # 多对多关系
    tags = db.relationship('Tag', secondary=tags_posts, lazy='subquery',
                          backref=db.backref('posts', lazy=True))

class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
```

## 4.6 数据库迁移

随着应用的发展，数据库结构可能需要改变，Flask-Migrate可以帮助管理数据库迁移。

### 安装和初始化
```bash
pip install Flask-Migrate
```

```python
from flask_migrate import Migrate

migrate = Migrate(app, db)
```

### 迁移命令
```bash
# 初始化迁移仓库
flask db init

# 生成迁移脚本
flask db migrate -m "添加用户表"

# 应用迁移
flask db upgrade
```

## 4.7 总结

本章介绍了Flask中数据库集成的方法，包括SQLAlchemy的使用、模型定义、CRUD操作、关系映射以及数据库迁移。这些知识是构建数据驱动Web应用的基础。下一章我们将学习用户认证和权限管理。