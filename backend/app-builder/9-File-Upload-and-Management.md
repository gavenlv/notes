# 第九章：文件上传和管理

在现代Web应用程序中，文件上传和管理是一个常见且重要的功能。Flask-AppBuilder提供了灵活的方式来处理文件上传、存储和管理。本章将详细介绍如何在Flask-AppBuilder中实现文件上传功能。

## 目录
1. 文件上传基础
2. 使用FileUploadField
3. 自定义文件存储
4. 文件验证
5. 文件管理界面
6. 完整示例
7. 最佳实践

## 1. 文件上传基础

Flask-AppBuilder提供了多种方式来处理文件上传：
- 使用内置的FileUploadField字段
- 自定义文件处理逻辑
- 集成第三方存储服务

### 基本概念
- **FileUploadField**: 专门用于文件上传的表单字段
- **ImageUploadField**: 专门用于图片上传的表单字段
- **文件存储**: 可以存储在本地文件系统或云存储中
- **文件验证**: 支持文件类型、大小等验证

## 2. 使用FileUploadField

FileUploadField是Flask-AppBuilder提供的专门用于文件上传的字段。

### 基本用法

```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.fields import FileUploadField
from sqlalchemy import Column, Integer, String

class Document(AuditMixin, Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    file = FileUploadField('File', base_path='/path/to/uploads/')
    
    def __repr__(self):
        return self.name
```

### 图片上传字段

```python
from flask_appbuilder.fields import ImageUploadField

class Profile(AuditMixin, Model):
    __tablename__ = 'profile'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    avatar = ImageUploadField('Avatar', base_path='/path/to/images/', 
                             thumbnail_size=(50, 50, True))
    
    def __repr__(self):
        return self.name
```

## 3. 自定义文件存储

Flask-AppBuilder允许你自定义文件存储位置和方式。

### 配置文件存储路径

```python
# config.py
import os

basedir = os.path.abspath(os.path.dirname(__file__))

# 文件上传配置
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
IMG_UPLOAD_FOLDER = os.path.join(basedir, 'images')
IMG_UPLOAD_URL = '/images/'
</code></pre>

### 动态文件路径

```python
from flask_appbuilder.models.mixins import FileColumn

class Document(Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    file_path = FileColumn()
    
    def file_path_expression(self):
        # 动态生成文件路径
        return f"documents/{self.id}/"
```

## 4. 文件验证

Flask-AppBuilder支持对上传文件进行各种验证。

### 文件类型验证

```python
from flask_appbuilder.fields import FileUploadField

class Document(Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    pdf_file = FileUploadField(
        'PDF File',
        base_path='/path/to/uploads/',
        validators=[
            FileAllowed(['pdf'], '只允许上传PDF文件!')
        ]
    )
```

### 文件大小限制

```python
from wtforms.validators import Length

class Document(Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    file = FileUploadField(
        'File',
        base_path='/path/to/uploads/',
        validators=[
            Length(max=10*1024*1024)  # 限制为10MB
        ]
    )
```

## 5. 文件管理界面

Flask-AppBuilder可以自动为包含文件字段的模型生成管理界面。

### 基本文件管理视图

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Document

class DocumentModelView(ModelView):
    datamodel = SQLAInterface(Document)
    
    list_columns = ['name', 'file']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'file']})
    ]
    add_fieldsets = [
        ('Summary', {'fields': ['name', 'file']})
    ]
    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'file']})
    ]
```

### 自定义文件显示

```python
from flask_appbuilder.fieldwidgets import BS3FileUploadFieldWidget
from wtforms import Form, FileField

class DocumentForm(Form):
    name = StringField('Name')
    file = FileField('File', widget=BS3FileUploadFieldWidget())

class DocumentModelView(ModelView):
    datamodel = SQLAInterface(Document)
    add_form = DocumentForm
    edit_form = DocumentForm
```

## 6. 完整示例

让我们创建一个完整的文件管理系统示例：

### 项目结构
```
chapter9/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── templates/
├── uploads/
├── config.py
└── run.py
```

### 配置文件 (config.py)

```python
import os
from flask_appbuilder.security.manager import AUTH_DB

basedir = os.path.abspath(os.path.dirname(__file__))

# Your App secret key
SECRET_KEY = '\2\1thisismyscretkey\1\2\e\y\y\h'

# The SQLAlchemy connection string.
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# Flask-WTF flag for CSRF
CSRF_ENABLED = True

# Authentication configuration
AUTH_TYPE = AUTH_DB
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# File upload configuration
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
IMG_UPLOAD_FOLDER = os.path.join(basedir, 'uploads', 'images')
IMG_UPLOAD_URL = '/uploads/images/'

APP_NAME = "File Management App"
```

### 模型文件 (app/models.py)

```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.fields import FileUploadField, ImageUploadField
from sqlalchemy import Column, Integer, String, Text
import os

def get_upload_path():
    """获取上传路径"""
    return os.path.join(os.path.dirname(__file__), '..', 'uploads')

class Document(AuditMixin, Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    file = FileUploadField(
        'Document File',
        base_path=get_upload_path(),
        allow_overwrite=False
    )
    
    def __repr__(self):
        return self.name

class ImageGallery(AuditMixin, Model):
    __tablename__ = 'image_gallery'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    image = ImageUploadField(
        'Image',
        base_path=os.path.join(get_upload_path(), 'images'),
        thumbnail_size=(100, 100, True),
        allow_overwrite=False
    )
    
    def __repr__(self):
        return self.title
```

### 视图文件 (app/views.py)

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash, redirect
from .models import Document, ImageGallery

class DocumentModelView(ModelView):
    datamodel = SQLAInterface(Document)
    
    list_columns = ['name', 'description', 'file', 'created_on']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']})
    ]
    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']})
    ]
    
    def post_add(self, item):
        """添加后处理"""
        flash(f"文档 '{item.name}' 已成功上传!", "info")
        super().post_add(item)
    
    def post_update(self, item):
        """更新后处理"""
        flash(f"文档 '{item.name}' 已成功更新!", "info")
        super().post_update(item)
    
    def post_delete(self, item):
        """删除后处理"""
        flash(f"文档 '{item.name}' 已成功删除!", "info")
        super().post_delete(item)

class ImageGalleryModelView(ModelView):
    datamodel = SQLAInterface(ImageGallery)
    
    list_columns = ['title', 'image', 'created_on']
    show_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']})
    ]
    edit_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']})
    ]
```

### 应用初始化文件 (app/__init__.py)

```python
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_appbuilder.security.manager import AUTH_DB
from flask_migrate import Migrate
from .views import DocumentModelView, ImageGalleryModelView
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
migrate = Migrate(app, db)
appbuilder = AppBuilder(app, db.session, auth_type=AUTH_DB)

# 创建上传目录
upload_path = os.path.join(os.path.dirname(__file__), '..', 'uploads')
os.makedirs(upload_path, exist_ok=True)
os.makedirs(os.path.join(upload_path, 'images'), exist_ok=True)

# 添加视图
appbuilder.add_view(
    DocumentModelView,
    "Documents",
    icon="fa-file-text-o",
    category="File Management"
)

appbuilder.add_view(
    ImageGalleryModelView,
    "Image Gallery",
    icon="fa-picture-o",
    category="File Management"
)

@app.route('/')
def index():
    return '<a href="/login/">Click here to login</a>'

# 初始化数据库
@app.before_first_request
def init_db():
    db.create_all()
    
    # 创建默认管理员用户
    if not appbuilder.sm.find_user(username='admin'):
        appbuilder.sm.add_user(
            username='admin',
            first_name='Admin',
            last_name='User',
            email='admin@fab.org',
            role=appbuilder.sm.find_role(appbuilder.sm.auth_role_admin),
            password='admin'
        )
```

### 运行文件 (run.py)

```python
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## 7. 最佳实践

### 安全考虑
1. 验证文件类型和扩展名
2. 限制文件大小
3. 使用安全的文件命名策略
4. 将上传文件存储在Web根目录之外

### 性能优化
1. 使用缩略图减少图片加载时间
2. 实现文件缓存机制
3. 考虑使用CDN分发静态文件

### 用户体验
1. 提供清晰的上传进度指示
2. 显示文件预览
3. 允许批量上传操作
4. 提供友好的错误提示

通过本章的学习，你应该能够：
- 在Flask-AppBuilder中实现文件上传功能
- 自定义文件存储和验证规则
- 创建美观的文件管理界面
- 遵循文件上传的最佳实践