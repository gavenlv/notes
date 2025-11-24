# 第二章：模型和数据库集成

## 模型基础概念

在Flask App-Builder中，模型（Models）是应用程序的数据结构表示。它们定义了数据如何存储、检索、更新和删除。模型通常对应数据库中的表，模型的属性对应表中的列。

Flask App-Builder使用SQLAlchemy作为ORM（对象关系映射）工具，这使得我们可以使用Python类来定义数据库结构，而不是直接编写SQL语句。

## SQLAlchemy简介

SQLAlchemy是Python中最流行的ORM之一，它提供了完整的工具集来处理数据库操作。SQLAlchemy分为两个主要部分：

1. **Core**：提供了SQL表达式语言和数据库抽象层
2. **ORM**：提供了对象关系映射功能

在Flask App-Builder中，我们主要使用ORM部分来定义我们的数据模型。

## 创建第一个模型

让我们创建一个简单的联系人管理系统的模型作为示例：

### 步骤1：创建模型文件

首先，在我们的应用目录中创建一个`models.py`文件：

```
my_app/
├── app/
│   ├── __init__.py
│   ├── models.py      # 新增
│   ├── views.py
│   └── config.py
├── run.py
└── requirements.txt
```

### 步骤2：定义Contact模型

在`app/models.py`中添加以下代码：

```python
from sqlalchemy import Column, Integer, String, Text, DateTime
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder import Model

class Contact(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(500))
    birthday = Column(DateTime)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    
    def __repr__(self):
        return self.name
```

### 模型字段解释

- `Column`: 定义表中的列
- `Integer`: 整数类型
- `String(150)`: 最大长度为150的字符串
- `Text`: 长文本类型
- `DateTime`: 日期时间类型
- `primary_key=True`: 定义主键
- `nullable=False`: 字段不能为空

## Flask App-Builder Mixins

Flask App-Builder提供了一些有用的Mixin类，可以添加常见的功能到我们的模型中：

### AuditMixin

AuditMixin自动添加审计字段：
- `created_on`: 记录创建时间
- `changed_on`: 记录最后修改时间
- `created_by`: 记录创建者
- `changed_by`: 记录最后修改者

使用示例：

```python
from flask_appbuilder.models.mixins import AuditMixin

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    # ... 其他字段
```

### FileColumn

FileColumn用于处理文件上传：

```python
from flask_appbuilder.models.mixins import FileColumn

class Document(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    file = Column(FileColumn)
```

### ImageColumn

ImageColumn专门用于处理图片上传：

```python
from flask_appbuilder.models.mixins import ImageColumn

class Profile(Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    photo = Column(ImageColumn)
```

## 关系模型

大多数应用程序都需要在不同模型之间建立关系。SQLAlchemy支持三种主要的关系类型：

### 一对多关系

```python
from sqlalchemy.orm import relationship
from flask_appbuilder.models.mixins import AuditMixin

class ContactGroup(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(500))
    birthday = Column(DateTime)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey('contact_group.id'))
    contact_group = relationship("ContactGroup")
    
    def __repr__(self):
        return self.name
```

### 多对多关系

```python
from sqlalchemy import Table, Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

# 关联表
contact_event_table = Table('contact_event', Model.metadata,
    Column('contact_id', Integer, ForeignKey('contact.id')),
    Column('event_id', Integer, ForeignKey('event.id'))
)

class Event(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    contacts = relationship("Contact", secondary=contact_event_table, back_populates="events")
    
    def __repr__(self):
        return self.name

# 在Contact模型中添加反向关系
class Contact(AuditMixin, Model):
    # ... 其他字段
    
    events = relationship("Event", secondary=contact_event_table, back_populates="contacts")
```

## 数据库配置

Flask App-Builder支持多种数据库，包括SQLite、PostgreSQL、MySQL等。配置方式如下：

### SQLite配置（默认）

```python
# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
```

### PostgreSQL配置

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'postgresql://username:password@localhost:5432/database_name'
```

### MySQL配置

```python
# config.py
SQLALCHEMY_DATABASE_URI = 'mysql://username:password@localhost:3306/database_name'
```

## 数据库迁移

在开发过程中，我们经常需要修改数据库结构。Flask App-Builder推荐使用Alembic进行数据库迁移：

### 安装Alembic

```bash
pip install alembic
```

### 初始化迁移环境

```bash
alembic init alembic
```

### 创建迁移脚本

```bash
alembic revision --autogenerate -m "Add contact group"
```

### 应用迁移

```bash
alembic upgrade head
```

## 完整示例

让我们创建一个完整的联系人管理系统的示例：

### 1. 更新requirements.txt

```txt
Flask-AppBuilder==4.3.0
Alembic==1.12.0
```

### 2. 创建models.py

```python
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder import Model
from datetime import datetime

class ContactGroup(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class Gender(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(500))
    birthday = Column(DateTime)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey('contact_group.id'), nullable=False)
    contact_group = relationship("ContactGroup")
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    gender = relationship("Gender")
    
    def __repr__(self):
        return self.name
        
    def month_year(self):
        date = self.birthday or datetime.now()
        return datetime(date.year, date.month, 1) or datetime.now()
        
    def year(self):
        date = self.birthday or datetime.now()
        return datetime(date.year, 1, 1)
```

### 3. 更新__init__.py

```python
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from .config import APP_NAME

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 添加初始数据
@app.before_first_request
def create_tables():
    db.create_all()
    
    # 添加初始数据
    from .models import ContactGroup, Gender
    
    # 检查是否已有数据
    if not db.session.query(ContactGroup).first():
        db.session.add(ContactGroup(name='Friends'))
        db.session.add(ContactGroup(name='Family'))
        db.session.add(ContactGroup(name='Work'))
        db.session.commit()
        
    if not db.session.query(Gender).first():
        db.session.add(Gender(name='Male'))
        db.session.add(Gender(name='Female'))
        db.session.commit()

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"
```

## 最佳实践

1. **使用Mixins**：充分利用Flask App-Builder提供的AuditMixin等Mixin类
2. **合理命名**：使用清晰、描述性的模型和字段名称
3. **关系定义**：明确指定外键约束和关系参数
4. **数据验证**：在模型层面添加适当的验证逻辑
5. **迁移管理**：使用Alembic管理数据库结构变更

## 总结

在本章中，我们学习了如何在Flask App-Builder中定义和使用模型。我们了解了：
- SQLAlchemy基础知识
- 如何创建简单的模型
- Flask App-Builder提供的Mixin类
- 如何建立模型间的关系
- 数据库配置和迁移

在下一章中，我们将学习如何创建视图和CRUD操作，这将使我们能够实际操作这些模型中的数据。

## 进一步阅读

- [SQLAlchemy官方文档](https://www.sqlalchemy.org/)
- [Flask App-Builder模型文档](https://flask-appbuilder.readthedocs.io/en/latest/models.html)
- [Alembic文档](https://alembic.sqlalchemy.org/)