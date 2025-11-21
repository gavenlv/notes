# 第三章：视图和CRUD操作

## 视图基础概念

在Flask App-Builder中，视图（Views）是用户界面与数据模型之间的桥梁。视图定义了如何展示数据、如何处理用户输入以及如何与模型进行交互。Flask App-Builder提供了多种预定义的视图类型，可以快速实现常见的CRUD（创建、读取、更新、删除）操作。

## Flask App-Builder视图类型

Flask App-Builder提供了几种不同类型的视图，每种都有特定的用途：

### 1. ModelView
ModelView是最常用的视图类型，用于管理数据库模型的CRUD操作。它自动生成列表、创建、编辑和详情页面。

### 2. CompactCRUDMixin
用于在有限空间内显示CRUD操作，通常作为其他视图的组件使用。

### 3. MasterDetailView
用于显示主从关系的数据，例如显示某个类别下的所有产品。

### 4. MultipleView
允许在一个页面上显示多个视图。

### 5. PublicFormView
用于创建不需要认证的表单页面。

### 6. RestCRUDView
用于创建RESTful API端点。

## 创建ModelView

让我们继续使用第二章中的联系人管理系统模型来创建视图：

### 步骤1：创建视图文件

首先，在应用目录中创建一个`views.py`文件：

```
my_app/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py      # 新增
│   └── config.py
├── run.py
└── requirements.txt
```

### 步骤2：定义基本的ModelView

在`app/views.py`中添加以下代码：

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Contact, ContactGroup, Gender

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 列表页面显示的字段
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group']
    
    # 添加和编辑页面显示的字段
    add_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    edit_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 搜索字段
    search_columns = ['name', 'address', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 详情页面显示的字段
    show_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']

class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]

class GenderModelView(ModelView):
    datamodel = SQLAInterface(Gender)
    related_views = [ContactModelView]
```

### 视图配置选项

Flask App-Builder的ModelView提供了丰富的配置选项：

#### 字段显示控制
```python
# 列表页面显示的字段
list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group']

# 添加页面显示的字段
add_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']

# 编辑页面显示的字段
edit_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']

# 详情页面显示的字段
show_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
```

#### 搜索和过滤
```python
# 搜索字段
search_columns = ['name', 'address', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']

# 过滤器
base_filters = [['created_by', FilterEqualFunction, get_user]]
```

#### 排序和分页
```python
# 默认排序字段
base_order = ('name', 'asc')

# 每页显示记录数
page_size = 25
```

## 注册视图到应用

创建视图后，需要将它们注册到Flask App-Builder应用中：

### 更新__init__.py

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

# 注册视图
from .views import ContactModelView, GroupModelView, GenderModelView

appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-users", category="Contacts")
appbuilder.add_view(GenderModelView, "List Genders", icon="fa-circle", category="Contacts")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"
```

## 自定义视图行为

### 1. 重写默认方法

可以重写ModelView中的方法来自定义行为：

```python
class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 重写pre_add方法，在添加记录前执行
    def pre_add(self, item):
        # 可以在这里添加自定义逻辑
        print(f"Adding contact: {item.name}")
        super().pre_add(item)
    
    # 重写post_add方法，在添加记录后执行
    def post_add(self, item):
        # 可以在这里添加自定义逻辑
        print(f"Contact {item.name} added successfully")
        super().post_add(item)
    
    # 重写pre_update方法，在更新记录前执行
    def pre_update(self, item):
        print(f"Updating contact: {item.name}")
        super().pre_update(item)
    
    # 重写pre_delete方法，在删除记录前执行
    def pre_delete(self, item):
        print(f"Deleting contact: {item.name}")
        return super().pre_delete(item)  # 返回True允许删除，返回False阻止删除
```

### 2. 添加自定义操作

```python
from flask import flash, redirect
from flask_appbuilder.actions import action

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    @action("send_email", "Send Email", "Send email to selected contacts?", "fa-envelope")
    def send_email(self, items):
        # 自定义操作逻辑
        if isinstance(items, list):
            count = len(items)
        else:
            count = 1
            items = [items]
            
        # 这里添加发送邮件的逻辑
        flash(f"Email sent to {count} contacts", "info")
        return redirect(self.get_redirect())
```

## 表单验证和字段渲染

### 1. 自定义验证器

```python
from wtforms.validators import DataRequired, Length
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from flask_appbuilder.forms import DynamicForm

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 添加验证器
    validators_columns = {
        'name': [DataRequired(), Length(min=2, max=150)],
        'personal_celphone': [Length(max=20)]
    }
    
    # 自定义字段小部件
    widget = {
        'name': BS3TextFieldWidget(),
        'address': BS3TextFieldWidget()
    }
```

### 2. 字段渲染控制

```python
class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 隐藏字段
    add_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    add_exclude_columns = ['created_on', 'changed_on', 'created_by', 'changed_by']
    
    # 只读字段
    edit_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    edit_exclude_columns = ['created_on', 'changed_on', 'created_by', 'changed_by']
```

## 高级视图类型

### 1. MasterDetailView

用于显示主从关系的数据：

```python
from flask_appbuilder.views import MasterDetailView

class ContactMasterView(MasterDetailView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]
```

### 2. MultipleView

在一个页面上显示多个视图：

```python
from flask_appbuilder.views import MultipleView

class ContactAllView(MultipleView):
    views = [ContactModelView, GroupModelView]
```

## 完整示例

让我们创建一个完整的联系人管理系统示例：

### 1. 更新views.py

```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask import flash, redirect
from wtforms.validators import DataRequired, Length
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget
from .models import Contact, ContactGroup, Gender

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 列表页面显示的字段
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group']
    
    # 添加和编辑页面显示的字段
    add_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    edit_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 搜索字段
    search_columns = ['name', 'address', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 详情页面显示的字段
    show_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 添加验证器
    validators_columns = {
        'name': [DataRequired(), Length(min=2, max=150)],
        'personal_celphone': [Length(max=20)]
    }
    
    # 默认排序
    base_order = ('name', 'asc')
    
    # 自定义操作
    @action("send_email", "Send Email", "Send email to selected contacts?", "fa-envelope")
    def send_email(self, items):
        if isinstance(items, list):
            count = len(items)
        else:
            count = 1
            items = [items]
            
        flash(f"Email sent to {count} contacts", "info")
        return redirect(self.get_redirect())
    
    # 重写方法
    def pre_add(self, item):
        print(f"Adding contact: {item.name}")
        super().pre_add(item)
    
    def post_add(self, item):
        print(f"Contact {item.name} added successfully")
        super().post_add(item)

class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]
    
    # 添加验证器
    validators_columns = {
        'name': [DataRequired(), Length(min=2, max=50)]
    }

class GenderModelView(ModelView):
    datamodel = SQLAInterface(Gender)
    related_views = [ContactModelView]
    
    # 添加验证器
    validators_columns = {
        'name': [DataRequired(), Length(min=2, max=50)]
    }
```

### 2. 更新__init__.py

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

# 注册视图
from .views import ContactModelView, GroupModelView, GenderModelView

appbuilder.add_view(ContactModelView, "List Contacts", icon="fa-envelope", category="Contacts")
appbuilder.add_view(GroupModelView, "List Groups", icon="fa-users", category="Contacts")
appbuilder.add_view(GenderModelView, "List Genders", icon="fa-circle", category="Contacts")

@app.route('/hello')
def hello():
    return "Hello, Flask App-Builder!"
```

## 最佳实践

1. **合理组织视图**：根据业务逻辑将相关的视图组织在同一个类别下
2. **字段控制**：只显示用户需要的字段，隐藏不必要的技术字段
3. **验证和安全**：添加适当的验证器和权限控制
4. **用户体验**：合理使用搜索、过滤和排序功能
5. **自定义操作**：为常用操作创建自定义按钮和动作

## 总结

在本章中，我们学习了如何在Flask App-Builder中创建和配置视图，以及如何实现CRUD操作。我们了解了：
- 不同类型的视图及其用途
- 如何创建ModelView来管理数据模型
- 如何自定义视图行为和验证
- 如何注册视图到应用中
- 高级视图类型的使用

在下一章中，我们将学习Flask App-Builder的认证和授权系统，这是构建安全Web应用的重要组成部分。

## 进一步阅读

- [Flask App-Builder视图文档](https://flask-appbuilder.readthedocs.io/en/latest/views.html)
- [Flask App-Builder安全文档](https://flask-appbuilder.readthedocs.io/en/latest/security.html)
- [WTForms文档](https://wtforms.readthedocs.io/)