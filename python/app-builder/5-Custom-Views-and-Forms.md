# 第五章：自定义视图和表单

## 自定义视图基础概念

在前面的章节中，我们学习了如何使用Flask App-Builder提供的ModelView来快速创建CRUD操作界面。但在实际开发中，我们经常需要创建更复杂的自定义视图来满足特定的业务需求。Flask App-Builder提供了多种方式来创建自定义视图。

## Flask App-Builder视图类型回顾

Flask App-Builder提供了多种视图基类：

1. **BaseView**：所有视图的基类
2. **ModelView**：用于模型的CRUD操作
3. **IndexView**：应用首页视图
4. **FormView**：用于处理表单的视图
5. **SimpleFormView**：简化版的表单视图
6. **PublicFormView**：公开的表单视图（无需认证）
7. **MultipleView**：组合多个视图
8. **MasterDetailView**：主从视图
9. **CompactCRUDMixin**：紧凑型CRUD视图

## 创建自定义BaseView

### 基本结构

BaseView是所有视图的基类，我们可以继承它来创建完全自定义的视图：

```python
from flask_appbuilder import BaseView, expose
from flask_appbuilder.security.decorators import has_access

class MyView(BaseView):
    route_base = "/myview"
    
    @expose('/method1/')
    @has_access
    def method1(self):
        # 你的业务逻辑
        return self.render_template('method1.html', 
                                   appbuilder=self.appbuilder)
    
    @expose('/method2/<string:param1>')
    @has_access
    def method2(self, param1):
        # 带参数的路由
        return self.render_template('method2.html', 
                                   param1=param1,
                                   appbuilder=self.appbuilder)
```

### 注册自定义视图

```python
# 在__init__.py中注册
from app.views import MyView

appbuilder.add_view_no_menu(MyView)
appbuilder.add_link("Method1", href='/myview/method1/', icon="fa-table", category="My Views")
```

## 创建自定义表单视图

### 使用FormView

FormView是专门用于处理表单的视图类：

```python
from flask_appbuilder.forms import DynamicForm
from flask_appbuilder.widgets import FormWidget
from flask_appbuilder import FormView
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, BS3PasswordFieldWidget
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Length
from flask import flash, redirect

class MyForm(DynamicForm):
    username = StringField('Username', 
                          widget=BS3TextFieldWidget(),
                          validators=[DataRequired(), Length(min=2, max=20)])
    password = PasswordField('Password', 
                            widget=BS3PasswordFieldWidget(),
                            validators=[DataRequired(), Length(min=6, max=20)])

class MyFormView(FormView):
    form = MyForm
    form_title = "My Custom Form"
    message = "Form submitted successfully"
    redirect_url = '/'

    def form_get(self, form):
        # 在GET请求时预填充表单
        form.username.data = "default_username"
        pass

    def form_post(self, form):
        # 处理POST请求
        # 这里添加你的业务逻辑
        flash(self.message, "info")
        return redirect(self.redirect_url)
```

### 使用SimpleFormView

SimpleFormView是FormView的简化版本：

```python
from flask_appbuilder import SimpleFormView
from flask import flash, redirect

class MySimpleFormView(SimpleFormView):
    form = MyForm
    form_title = "Simple Form"
    
    def form_post(self, form):
        # 处理表单提交
        flash(f"Hello {form.username.data}", "info")
        return redirect('/')
```

## 自定义模板

### 创建自定义模板目录

```
my_app/
├── app/
│   ├── templates/
│   │   ├── myview/
│   │   │   ├── method1.html
│   │   │   └── method2.html
│   │   └── myform.html
│   ├── __init__.py
│   ├── views.py
│   └── forms.py
├── run.py
└── requirements.txt
```

### 基本模板结构

```html
<!-- templates/myview/method1.html -->
{% extends "appbuilder/base.html" %}

{% block content %}
<div class="container">
    <h1>My Custom View</h1>
    <p>This is a custom view created with Flask App-Builder.</p>
    
    <!-- 使用Flask App-Builder的组件 -->
    <div class="well">
        <p>Content goes here</p>
    </div>
</div>
{% endblock %}
```

### 表单模板

```html
<!-- templates/myform.html -->
{% extends "appbuilder/base.html" %}
{% import 'appbuilder/general/lib.html' as lib %}

{% block content %}
<div class="container">
    <h1>{{ form_title }}</h1>
    
    <form class="form-horizontal" action="" method="post">
        {{ form.hidden_tag() }}
        
        {% for field in form %}
            {% if field.widget.input_type != 'hidden' %}
                <div class="form-group">
                    <label class="col-sm-2 control-label">{{ field.label }}</label>
                    <div class="col-sm-10">
                        {{ field(class_="form-control") }}
                        {% if field.errors %}
                            <div class="alert alert-danger">
                                {% for error in field.errors %}
                                    <p>{{ error }}</p>
                                {% endfor %}
                            </div>
                        {% endif %}
                    </div>
                </div>
            {% endif %}
        {% endfor %}
        
        <div class="form-group">
            <div class="col-sm-offset-2 col-sm-10">
                <input type="submit" value="Submit" class="btn btn-primary">
            </div>
        </div>
    </form>
</div>
{% endblock %}
```

## 自定义Widget

### 创建自定义Widget

```python
from flask_appbuilder.widgets import RenderTemplateWidget

class MyWidget(RenderTemplateWidget):
    template = 'widgets/my_widget.html'

class MyModelView(ModelView):
    datamodel = SQLAInterface(MyModel)
    widget = MyWidget()
```

### Widget模板

```html
<!-- templates/widgets/my_widget.html -->
<div class="well">
    <h3>Custom Widget</h3>
    <p>This is a custom widget for displaying model data.</p>
    <!-- 你的自定义内容 -->
</div>
```

## 高级自定义视图示例

### 仪表板视图

```python
from flask_appbuilder import BaseView, expose
from flask_appbuilder.security.decorators import has_access
from flask import render_template

class DashboardView(BaseView):
    route_base = '/dashboard'
    
    @expose('/')
    @has_access
    def index(self):
        # 获取统计数据
        user_count = self.appbuilder.get_session.query(User).count()
        contact_count = self.appbuilder.get_session.query(Contact).count()
        
        # 传递数据到模板
        return self.render_template(
            'dashboard/index.html',
            user_count=user_count,
            contact_count=contact_count,
            appbuilder=self.appbuilder
        )
```

### 报表视图

```python
from flask_appbuilder import BaseView, expose
from flask_appbuilder.security.decorators import has_access
import json

class ReportView(BaseView):
    route_base = '/reports'
    
    @expose('/contacts/')
    @has_access
    def contacts_report(self):
        # 获取联系人数据
        contacts = self.appbuilder.get_session.query(Contact).all()
        
        # 准备图表数据
        chart_data = {
            'labels': [c.name for c in contacts[:10]],
            'values': [len(c.name) for c in contacts[:10]]
        }
        
        return self.render_template(
            'reports/contacts.html',
            contacts=contacts,
            chart_data=json.dumps(chart_data),
            appbuilder=self.appbuilder
        )
```

## 表单验证和处理

### 自定义验证器

```python
from wtforms.validators import ValidationError

class UniqueUsername:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        user = self.appbuilder.get_session.query(User).filter_by(username=field.data).first()
        if user:
            raise ValidationError(self.message or 'Username already exists.')

class MyForm(DynamicForm):
    username = StringField('Username', validators=[
        DataRequired(),
        Length(min=2, max=20),
        UniqueUsername()
    ])
```

### 文件上传表单

```python
from flask_appbuilder.forms import DynamicForm
from flask_appbuilder.fieldwidgets import BS3FileUploadFieldWidget
from wtforms import FileField
from werkzeug.utils import secure_filename
import os

class UploadForm(DynamicForm):
    file = FileField('File', 
                     widget=BS3FileUploadFieldWidget(),
                     validators=[DataRequired()])
    
    def process_file(self, file):
        filename = secure_filename(file.filename)
        file.save(os.path.join('uploads', filename))
        return filename
```

## 完整示例

让我们创建一个包含自定义视图和表单的完整示例：

### 1. 项目结构

```
chapter5/
├── app/
│   ├── templates/
│   │   ├── dashboard/
│   │   │   └── index.html
│   │   ├── forms/
│   │   │   └── contact_form.html
│   │   └── appbuilder/
│   │       └── general/
│   │           └── lib.html
│   ├── __init__.py
│   ├── views.py
│   ├── forms.py
│   └── models.py
├── run.py
└── requirements.txt
```

### 2. 模型文件

```python
# models.py
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Date

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(200))

    def __repr__(self):
        return self.name
```

### 3. 表单文件

```python
# forms.py
from flask_appbuilder.forms import DynamicForm
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget, BS3TextAreaFieldWidget
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired, Email, Length

class ContactForm(DynamicForm):
    name = StringField('Name', 
                      widget=BS3TextFieldWidget(),
                      validators=[DataRequired(), Length(min=2, max=150)])
    email = StringField('Email', 
                       widget=BS3TextFieldWidget(),
                       validators=[DataRequired(), Email()])
    phone = StringField('Phone', 
                       widget=BS3TextFieldWidget(),
                       validators=[Length(max=20)])
    address = TextAreaField('Address', 
                           widget=BS3TextAreaFieldWidget(),
                           validators=[Length(max=200)])
```

### 4. 视图文件

```python
# views.py
from flask_appbuilder import BaseView, expose, FormView
from flask_appbuilder.security.decorators import has_access
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash, redirect
from .models import Contact
from .forms import ContactForm

class DashboardView(BaseView):
    route_base = '/dashboard'
    
    @expose('/')
    @has_access
    def index(self):
        # 获取统计数据
        contact_count = self.appbuilder.get_session.query(Contact).count()
        
        return self.render_template(
            'dashboard/index.html',
            contact_count=contact_count,
            appbuilder=self.appbuilder
        )

class ContactFormView(FormView):
    form = ContactForm
    form_title = "Add New Contact"
    message = "Contact added successfully"
    redirect_url = '/'

    def form_post(self, form):
        # 创建新联系人
        contact = Contact()
        contact.name = form.name.data
        contact.email = form.email.data
        contact.phone = form.phone.data
        contact.address = form.address.data
        
        # 保存到数据库
        self.appbuilder.get_session.add(contact)
        self.appbuilder.get_session.commit()
        
        flash(self.message, "success")
        return redirect(self.redirect_url)
```

### 5. 模板文件

```html
<!-- templates/dashboard/index.html -->
{% extends "appbuilder/base.html" %}

{% block content %}
<div class="container">
    <h1>Dashboard</h1>
    
    <div class="row">
        <div class="col-md-4">
            <div class="well text-center">
                <h2>{{ contact_count }}</h2>
                <p>Total Contacts</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="well text-center">
                <h2>0</h2>
                <p>New Messages</p>
            </div>
        </div>
        <div class="col-md-4">
            <div class="well text-center">
                <h2>0</h2>
                <p>Pending Tasks</p>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12">
            <h2>Quick Actions</h2>
            <a href="/contactform/add" class="btn btn-primary">Add Contact</a>
            <a href="/contacts/list/" class="btn btn-default">View Contacts</a>
        </div>
    </div>
</div>
{% endblock %}
```

### 6. 应用初始化文件

```python
# __init__.py
import logging
from flask import Flask
from flask_appbuilder import SQLA, AppBuilder

logging.basicConfig(format='%(asctime)s:%(levelname)s:%(name)s:%(message)s')
logging.getLogger().setLevel(logging.DEBUG)

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLA(app)
appbuilder = AppBuilder(app, db.session)

# 创建表
@app.before_first_request
def create_tables():
    db.create_all()

# 注册视图
from .views import DashboardView, ContactFormView

appbuilder.add_view_no_menu(DashboardView)
appbuilder.add_view(ContactFormView, "Add Contact", icon="fa-plus", category="Contacts")
appbuilder.add_link("Dashboard", href='/dashboard/', icon="fa-dashboard")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

### 7. 配置文件

```python
# config.py
import os

# 数据库配置
basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False

# 认证配置
AUTH_TYPE = 1  # 数据库认证
AUTH_ROLE_ADMIN = 'Admin'
AUTH_ROLE_PUBLIC = 'Public'

# 应用配置
APP_NAME = "Flask App-Builder Custom Views Tutorial"
APP_THEME = ""
```

### 8. 运行文件

```python
# run.py
from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
```

## 最佳实践

1. **模板继承**：始终继承`appbuilder/base.html`以保持一致的外观和导航
2. **权限控制**：使用`@has_access`装饰器保护视图
3. **错误处理**：添加适当的错误处理和用户反馈
4. **表单验证**：使用WTForms验证器确保数据完整性
5. **响应式设计**：使用Bootstrap类确保在不同设备上正常显示

## 总结

在本章中，我们学习了如何创建自定义视图和表单：

1. 不同类型的视图及其用途
2. 如何创建BaseView和FormView
3. 自定义模板和Widget的使用
4. 表单验证和处理技巧
5. 完整的自定义视图示例

通过这些知识，你可以创建更复杂和个性化的用户界面。在下一章中，我们将学习Flask App-Builder的高级安全特性。

## 进一步阅读

- [Flask App-Builder视图文档](https://flask-appbuilder.readthedocs.io/en/latest/views.html)
- [WTForms文档](https://wtforms.readthedocs.io/)
- [Bootstrap CSS框架](https://getbootstrap.com/)