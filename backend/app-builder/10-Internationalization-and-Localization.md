# 第十章：国际化和本地化

在现代Web应用程序中，国际化(i18n)和本地化(l10n)是必不可少的功能，特别是对于面向全球用户的平台。Flask-AppBuilder提供了强大的国际化支持，可以轻松地将应用程序翻译成多种语言。本章将详细介绍如何在Flask-AppBuilder中实现国际化和本地化。

## 目录
1. 国际化基础概念
2. Flask-AppBuilder中的i18n支持
3. 创建多语言翻译文件
4. 配置语言切换
5. 翻译模型和视图
6. 自定义翻译
7. 完整示例
8. 最佳实践

## 1. 国际化基础概念

### 国际化(i18n) vs 本地化(l10n)
- **国际化(i18n)**: 设计和开发应用程序的过程，使其能够适应不同的语言和地区，而无需工程更改。
- **本地化(l10n)**: 为特定地区或语言适配软件的过程。

### Flask-Babel
Flask-AppBuilder使用Flask-Babel库来实现国际化支持：
- 提供翻译字符串的功能
- 支持复数形式
- 支持日期、时间和数字格式化
- 支持时区处理

## 2. Flask-AppBuilder中的i18n支持

Flask-AppBuilder内置了对国际化的支持，默认支持多种语言：
- 英语 (en)
- 西班牙语 (es)
- 法语 (fr)
- 中文 (zh)
- 德语 (de)
- 日语 (ja)
- 韩语 (ko)
- 俄语 (ru)
- 葡萄牙语 (pt)
- 阿拉伯语 (ar)

### 启用国际化
在配置文件中启用国际化：

```python
# config.py
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'
LANGUAGES = {
    'en': {'flag': 'gb', 'name': 'English'},
    'zh': {'flag': 'cn', 'name': 'Chinese'},
    'es': {'flag': 'es', 'name': 'Spanish'},
    'fr': {'flag': 'fr', 'name': 'French'}
}
```

## 3. 创建多语言翻译文件

### 项目结构
```
chapter10/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   └── translations/
│       ├── en/
│       │   └── LC_MESSAGES/
│       │       ├── messages.po
│       │       └── messages.mo
│       ├── zh/
│       │   └── LC_MESSAGES/
│       │       ├── messages.po
│       │       └── messages.mo
│       └── babel.cfg
├── config.py
└── run.py
```

### 配置babel.cfg
创建babel.cfg文件来指定需要翻译的文件：

```ini
[python: **.py]
[jinja2: **/templates/**.html]
extensions=jinja2.ext.autoescape,jinja2.ext.with_
```

### 提取翻译字符串
使用pybabel命令提取翻译字符串：

```bash
# 提取翻译字符串
pybabel extract -F babel.cfg -k _l -o app/translations/messages.pot .

# 初始化翻译文件
pybabel init -i app/translations/messages.pot -d app/translations -l zh

# 编译翻译文件
pybabel compile -d app/translations
```

## 4. 配置语言切换

### 在配置文件中设置语言选项

```python
# config.py
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

# Babel configuration
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'

# Available languages
LANGUAGES = {
    'en': {'flag': 'gb', 'name': 'English'},
    'zh': {'flag': 'cn', 'name': '中文'},
    'es': {'flag': 'es', 'name': 'Español'}
}

APP_NAME = "I18n Demo App"
```

### 在应用中启用语言切换

```python
# app/__init__.py
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder
from flask_babel import Babel
from flask import session, request, g
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
babel = Babel(app)
appbuilder = AppBuilder(app, db.session)

# 设置语言选择器
@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

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

## 5. 翻译模型和视图

### 翻译模型字段

```python
# app/models.py
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text
from flask_babel import lazy_gettext as _

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, info={'label': _('Name')})
    description = Column(Text, info={'label': _('Description')})
    price = Column(Integer, info={'label': _('Price')})
    
    def __repr__(self):
        return self.name
```

### 翻译视图标签

```python
# app/views.py
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import lazy_gettext as _
from .models import Product

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    # 翻译列表列标题
    list_columns = ['name', 'description', 'price']
    
    # 翻译字段集
    show_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']}),
        (_('Audit'), {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    edit_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    
    # 翻译标签
    label_columns = {
        'name': _('Product Name'),
        'description': _('Product Description'),
        'price': _('Product Price')
    }
```

## 6. 自定义翻译

### 在模板中使用翻译

```html
<!-- app/templates/product/list.html -->
{% extends "appbuilder/base.html" %}
{% from 'appbuilder/_formhelpers.html' import render_field %}

{% block content %}
<h1>{{ _('Product List') }}</h1>
<p>{{ _('Welcome to our product catalog') }}</p>

<table class="table table-striped">
    <thead>
        <tr>
            <th>{{ _('Name') }}</th>
            <th>{{ _('Description') }}</th>
            <th>{{ _('Price') }}</th>
        </tr>
    </thead>
    <tbody>
        {% for product in products %}
        <tr>
            <td>{{ product.name }}</td>
            <td>{{ product.description }}</td>
            <td>${{ product.price }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

### 在Python代码中使用翻译

```python
# app/views.py
from flask import flash
from flask_babel import lazy_gettext as _

class ProductModelView(ModelView):
    # ... 其他代码 ...
    
    def post_add(self, item):
        flash(_('Product %(name)s was successfully added.', name=item.name), 'info')
        super().post_add(item)
    
    def post_update(self, item):
        flash(_('Product %(name)s was successfully updated.', name=item.name), 'info')
        super().post_update(item)
    
    def post_delete(self, item):
        flash(_('Product %(name)s was successfully deleted.', name=item.name), 'info')
        super().post_delete(item)
```

## 7. 完整示例

### requirements.txt

```txt
Flask-AppBuilder==4.3.0
Flask-Babel==2.0.0
Babel==2.12.1
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

# Babel configuration
BABEL_DEFAULT_LOCALE = 'en'
BABEL_DEFAULT_TIMEZONE = 'UTC'

# Available languages
LANGUAGES = {
    'en': {'flag': 'gb', 'name': 'English'},
    'zh': {'flag': 'cn', 'name': '中文'},
    'es': {'flag': 'es', 'name': 'Español'}
}

APP_NAME = "I18n Demo App"
```

### 模型文件 (app/models.py)

```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text
from flask_babel import lazy_gettext as _

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, info={'label': _('Name')})
    description = Column(Text, info={'label': _('Description')})
    price = Column(Integer, info={'label': _('Price')})
    
    def __repr__(self):
        return self.name
```

### 视图文件 (app/views.py)

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_babel import lazy_gettext as _
from flask import flash
from .models import Product

class ProductModelView(ModelView):
    datamodel = SQLAInterface(Product)
    
    list_columns = ['name', 'description', 'price']
    show_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']}),
        (_('Audit'), {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    edit_fieldsets = [
        (_('Summary'), {'fields': ['name', 'description', 'price']})
    ]
    
    label_columns = {
        'name': _('Product Name'),
        'description': _('Product Description'),
        'price': _('Product Price')
    }
    
    def post_add(self, item):
        flash(_('Product %(name)s was successfully added.', name=item.name), 'info')
        super().post_add(item)
    
    def post_update(self, item):
        flash(_('Product %(name)s was successfully updated.', name=item.name), 'info')
        super().post_update(item)
    
    def post_delete(self, item):
        flash(_('Product %(name)s was successfully deleted.', name=item.name), 'info')
        super().post_delete(item)
```

### 应用初始化文件 (app/__init__.py)

```python
import logging
from flask import Flask, session, request
from flask_appbuilder import SQLA, AppBuilder
from flask_babel import Babel
import os

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('../config.py')

db = SQLA(app)
babel = Babel(app)
appbuilder = AppBuilder(app, db.session)

# 设置语言选择器
@babel.localeselector
def get_locale():
    if request.args.get('lang'):
        session['lang'] = request.args.get('lang')
    return session.get('lang', 'en')

# 添加视图
from .views import ProductModelView
appbuilder.add_view(
    ProductModelView,
    "Products",
    icon="fa-product-hunt",
    category="Catalog"
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

### 翻译文件示例 (app/translations/zh/LC_MESSAGES/messages.po)

```po
# Chinese translations for PROJECT.
# Copyright (C) 2023 ORGANIZATION
# This file is distributed under the same license as the PROJECT project.
# FIRST AUTHOR <EMAIL@ADDRESS>, 2023.
#
msgid ""
msgstr ""
"Project-Id-Version: PROJECT VERSION\n"
"Report-Msgid-Bugs-To: EMAIL@ADDRESS\n"
"POT-Creation-Date: 2023-01-01 00:00+0000\n"
"PO-Revision-Date: 2023-01-01 00:00+0000\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language: zh\n"
"Language-Team: zh <LL@li.org>\n"
"Plural-Forms: nplurals=1; plural=0\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=utf-8\n"
"Content-Transfer-Encoding: 8bit\n"
"Generated-By: Babel 2.12.1\n"

#: app/models.py:12
msgid "Name"
msgstr "名称"

#: app/models.py:13
msgid "Description"
msgstr "描述"

#: app/models.py:14
msgid "Price"
msgstr "价格"

#: app/views.py:15
msgid "Summary"
msgstr "摘要"

#: app/views.py:16
msgid "Audit"
msgstr "审计"

#: app/views.py:27
msgid "Product Name"
msgstr "产品名称"

#: app/views.py:28
msgid "Product Description"
msgstr "产品描述"

#: app/views.py:29
msgid "Product Price"
msgstr "产品价格"

#: app/views.py:34
#, python-format
msgid "Product %(name)s was successfully added."
msgstr "产品 %(name)s 已成功添加。"

#: app/views.py:38
#, python-format
msgid "Product %(name)s was successfully updated."
msgstr "产品 %(name)s 已成功更新。"

#: app/views.py:42
#, python-format
msgid "Product %(name)s was successfully deleted."
msgstr "产品 %(name)s 已成功删除。"
```

## 8. 最佳实践

### 翻译工作流程
1. 使用`pybabel extract`提取所有可翻译字符串
2. 使用`pybabel init`为新语言创建翻译文件
3. 编辑`.po`文件完成翻译
4. 使用`pybabel compile`编译翻译文件

### 翻译技巧
1. 使用描述性msgid而不是直接翻译
2. 注意复数形式的处理
3. 保持翻译的一致性
4. 测试所有支持的语言

### 性能优化
1. 使用`lazy_gettext`延迟翻译计算
2. 合理缓存翻译结果
3. 避免在循环中进行翻译操作

通过本章的学习，你应该能够：
- 理解国际化和本地化的基本概念
- 在Flask-AppBuilder中配置多语言支持
- 创建和管理翻译文件
- 翻译模型、视图和模板
- 遵循国际化最佳实践