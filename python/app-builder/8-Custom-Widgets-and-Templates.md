# 第八章：自定义Widgets和Templates

Flask App-Builder 提供了强大的模板和部件系统，允许开发者创建高度定制化的用户界面。通过自定义 widgets 和 templates，您可以完全控制应用程序的外观和用户体验。

## 目录
1. [Widgets基础概念](#widgets基础概念)
2. [内置Widgets](#内置widgets)
3. [创建自定义Widgets](#创建自定义widgets)
4. [模板系统](#模板系统)
5. [自定义模板](#自定义模板)
6. [表单Widgets](#表单widgets)
7. [列表Widgets](#列表widgets)
8. [图表Widgets](#图表widgets)
9. [完整示例](#完整示例)
10. [最佳实践](#最佳实践)

## Widgets基础概念

Widgets 是 Flask App-Builder 中用于渲染特定UI元素的可重用组件。它们封装了HTML、CSS和JavaScript，使得开发者可以轻松地在不同地方重复使用相同的UI组件。

### Widget的优势
- **可重用性**：一次编写，多处使用
- **一致性**：保持整个应用的UI风格一致
- **可维护性**：集中管理UI组件的逻辑和样式
- **扩展性**：可以根据需求自定义行为和外观

## 内置Widgets

Flask App-Builder 提供了许多内置的 widgets，涵盖了常见的UI需求：

### 表单Widgets
- `FormWidget` - 标准表单渲染
- `CompactFormWidget` - 紧凑型表单渲染
- `ModalFormWidget` - 模态框表单渲染

### 列表Widgets
- `ListWidget` - 标准列表渲染
- `ListItem` - 列表项渲染
- `ThumbnailItem` - 缩略图列表项渲染
- `TableWidget` - 表格渲染

### 图表Widgets
- `ChartWidget` - 图表渲染
- `DirectChartWidget` - 直接图表渲染

### 使用内置Widgets示例
```python
from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.widgets import ListWidget, FormWidget

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 使用自定义列表widget
    list_widget = ListWidget()
    
    # 使用自定义表单widget
    form_widget = FormWidget()
```

## 创建自定义Widgets

### 基础Widget类
要创建自定义 widget，需要继承 Flask App-Builder 的基础 widget 类：

```python
from flask_appbuilder.widgets import RenderTemplateWidget

class CustomWidget(RenderTemplateWidget):
    template = 'widgets/custom_widget.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # 初始化自定义属性
        self.custom_data = kwargs.get('custom_data', {})
```

### 自定义列表Widget
```python
from flask_appbuilder.widgets import ListWidget

class CardListWidget(ListWidget):
    template = 'widgets/card_list.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_color = kwargs.get('background_color', '#ffffff')
```

对应的模板文件 (`templates/widgets/card_list.html`)：
```html
{% extends "appbuilder/general/widgets/list.html" %}

{% block list scoped %}
<div class="card-container" style="background-color: {{ widget.background_color }};">
    {% for item in include_widgets %}
        <div class="card">
            <div class="card-header">
                <h4>{{ item.data.name }}</h4>
            </div>
            <div class="card-body">
                <p>Email: {{ item.data.email }}</p>
                <p>Phone: {{ item.data.phone }}</p>
            </div>
        </div>
    {% endfor %}
</div>
{% endblock %}
```

### 自定义表单Widget
```python
from flask_appbuilder.widgets import FormWidget

class WizardFormWidget(FormWidget):
    template = 'widgets/wizard_form.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.steps = kwargs.get('steps', [])
        self.current_step = kwargs.get('current_step', 1)
```

对应的模板文件 (`templates/widgets/wizard_form.html`)：
```html
{% extends "appbuilder/general/widgets/form.html" %}

{% block form_start %}
<div class="wizard-form">
    <!-- 步骤指示器 -->
    <div class="wizard-steps">
        {% for step in widget.steps %}
            <div class="step {% if loop.index <= widget.current_step %}active{% endif %}">
                {{ step }}
            </div>
        {% endfor %}
    </div>
    
    <form action="{{ form_action }}" method="post" enctype="multipart/form-data">
{% endblock %}

{% block form_end %}
    </form>
</div>
{% endblock %}
```

## 模板系统

Flask App-Builder 基于 Jinja2 模板引擎，提供了丰富的模板继承和扩展机制。

### 模板继承
```html
<!-- base.html -->
<!DOCTYPE html>
<html>
<head>
    <title>{% block title %}{% endblock %}</title>
    {% block head_css %}{% endblock %}
</head>
<body>
    <header>
        {% block header %}{% endblock %}
    </header>
    
    <main>
        {% block content %}{% endblock %}
    </main>
    
    <footer>
        {% block footer %}{% endblock %}
    </footer>
    
    {% block tail_js %}{% endblock %}
</body>
</html>
```

### 扩展基础模板
```html
<!-- mypage.html -->
{% extends "appbuilder/base.html" %}

{% block title %}My Custom Page{% endblock %}

{% block content %}
<div class="container">
    <h1>Welcome to My Custom Page</h1>
    <p>This is a custom page using Flask App-Builder templates.</p>
</div>
{% endblock %}
```

## 自定义模板

### 覆盖默认模板
可以通过在应用的 templates 目录中创建同名文件来覆盖默认模板：

```
app/
├── templates/
│   ├── appbuilder/
│   │   ├── base.html
│   │   ├── general/
│   │   │   ├── widgets/
│   │   │   │   ├── list.html
│   │   │   │   └── form.html
│   │   │   └── lib.html
│   │   └── navbar.html
│   └── myview/
│       └── index.html
```

### 自定义基础模板
```html
<!-- templates/appbuilder/base.html -->
{% extends 'appbuilder/baselayout.html' %}

{% block head_css %}
    {{ super() }}
    <link href="{{url_for('static',filename='css/custom.css')}}" rel="stylesheet">
{% endblock %}

{% block body %}
    <div class="wrapper">
        {% block navbar %}
            {% include 'appbuilder/navbar.html' %}
        {% endblock %}
        
        <div class="content-wrapper">
            {% block content %}{% endblock %}
        </div>
        
        {% block footer %}
            {% include 'appbuilder/footer.html' %}
        {% endblock %}
    </div>
{% endblock %}

{% block tail_js %}
    {{ super() }}
    <script src="{{url_for('static',filename='js/custom.js')}}"></script>
{% endblock %}
```

### 自定义导航栏
```html
<!-- templates/appbuilder/navbar.html -->
<nav class="navbar navbar-default navbar-fixed-top">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="{{url_for('IndexView.index')}}">
                {{ appbuilder.app_name }}
            </a>
        </div>
        
        <div class="collapse navbar-collapse" id="navbar">
            <ul class="nav navbar-nav">
                {% for item in appbuilder.menu %}
                    {% if item | is_menu_visible %}
                        <li>
                            <a href="{{item.href}}">{{_(item.label)}}</a>
                        </li>
                    {% endif %}
                {% endfor %}
            </ul>
            
            <ul class="nav navbar-nav navbar-right">
                {% if current_user.is_authenticated %}
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            <i class="fa fa-user"></i> {{g.user.get_full_name()}}<b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="{{url_for('UserDBModelView.show',pk=current_user.id)}}">Profile</a></li>
                            <li class="divider"></li>
                            <li><a href="{{url_for('AuthDBView.logout')}}">Logout</a></li>
                        </ul>
                    </li>
                {% else %}
                    <li><a href="{{url_for('AuthDBView.login')}}">Login</a></li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

## 表单Widgets

### 自定义表单字段Widget
```python
from flask_appbuilder.fieldwidgets import BS3TextFieldWidget

class CustomTextFieldWidget(BS3TextFieldWidget):
    def __call__(self, field, **kwargs):
        kwargs.setdefault('class', 'form-control custom-input')
        kwargs.setdefault('placeholder', field.label.text)
        return super().__call__(field, **kwargs)
```

### 使用自定义表单Widget
```python
from wtforms import StringField
from flask_appbuilder.forms import DynamicForm

class ContactForm(DynamicForm):
    name = StringField(
        'Name',
        widget=CustomTextFieldWidget(),
        validators=[DataRequired()]
    )
```

### 复杂表单Widget
```python
from flask_appbuilder.widgets import RenderTemplateWidget

class AddressFormWidget(RenderTemplateWidget):
    template = 'widgets/address_form.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.country_choices = kwargs.get('country_choices', [])
```

模板文件 (`templates/widgets/address_form.html`)：
```html
<div class="address-widget">
    <div class="form-group">
        <label>Street</label>
        <input type="text" name="street" class="form-control" value="{{ street or '' }}">
    </div>
    
    <div class="form-group">
        <label>City</label>
        <input type="text" name="city" class="form-control" value="{{ city or '' }}">
    </div>
    
    <div class="form-group">
        <label>Country</label>
        <select name="country" class="form-control">
            {% for choice in widget.country_choices %}
                <option value="{{ choice[0 }}" {% if country == choice[0] %}selected{% endif %}>
                    {{ choice[1] }}
                </option>
            {% endfor %}
        </select>
    </div>
</div>
```

## 列表Widgets

### 自定义列表项Widget
```python
from flask_appbuilder.widgets import ListItem

class ContactListItem(ListItem):
    template = 'widgets/contact_list_item.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.avatar_size = kwargs.get('avatar_size', 40)
```

模板文件 (`templates/widgets/contact_list_item.html`)：
```html
<div class="contact-item">
    <div class="avatar" style="width: {{ widget.avatar_size }}px; height: {{ widget.avatar_size }}px;">
        {% if item.data.avatar %}
            <img src="{{ item.data.avatar }}" alt="{{ item.data.name }}">
        {% else %}
            <div class="initials">{{ item.data.name|first|upper }}</div>
        {% endif %}
    </div>
    
    <div class="contact-info">
        <h4>{{ item.data.name }}</h4>
        <p class="email">{{ item.data.email }}</p>
        <p class="phone">{{ item.data.phone }}</p>
    </div>
    
    <div class="actions">
        <a href="{{ url_for('ContactModelView.show', pk=item.data.id) }}" class="btn btn-default btn-sm">
            View
        </a>
        <a href="{{ url_for('ContactModelView.edit', pk=item.data.id) }}" class="btn btn-primary btn-sm">
            Edit
        </a>
    </div>
</div>
```

### 使用自定义列表Widget
```python
class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_widget = ContactListItem
```

## 图表Widgets

### 自定义图表Widget
```python
from flask_appbuilder.widgets import ChartWidget

class CustomBarChartWidget(ChartWidget):
    template = 'widgets/bar_chart.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chart_colors = kwargs.get('chart_colors', ['#3366cc', '#dc3912', '#ff9900'])
```

模板文件 (`templates/widgets/bar_chart.html`)：
```html
<div class="chart-container">
    <canvas id="barChart" width="400" height="200"></canvas>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('barChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: {{ labels|tojson }},
            datasets: [{
                label: '{{ label }}',
                data: {{ values|tojson }},
                backgroundColor: {{ widget.chart_colors|tojson }}
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
});
</script>
```

## 完整示例

让我们创建一个完整的自定义Widgets和Templates示例：

### 项目结构
```
chapter8/
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── views.py
│   ├── widgets.py
│   └── templates/
│       ├── appbuilder/
│       │   ├── base.html
│       │   └── navbar.html
│       ├── dashboard/
│       │   └── index.html
│       └── widgets/
│           ├── contact_card.html
│           ├── contact_form.html
│           └── stats_chart.html
├── static/
│   ├── css/
│   │   └── custom.css
│   └── js/
│       └── custom.js
├── config.py
└── run.py
```

### 模型定义 (models.py)
```python
from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text

class Contact(AuditMixin, Model):
    __tablename__ = 'contact'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50))
    address = Column(Text)
    avatar = Column(String(200))
    
    def __repr__(self):
        return self.name
```

### 自定义Widgets (widgets.py)
```python
from flask_appbuilder.widgets import RenderTemplateWidget, ListWidget

class ContactCardWidget(RenderTemplateWidget):
    template = 'widgets/contact_card.html'

class ContactListWidget(ListWidget):
    template = 'widgets/contact_card.html'

class StatsChartWidget(RenderTemplateWidget):
    template = 'widgets/stats_chart.html'
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.chart_title = kwargs.get('chart_title', 'Statistics')
        self.chart_type = kwargs.get('chart_type', 'bar')
```

### 视图定义 (views.py)
```python
from flask_appbuilder import BaseView, expose, ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import render_template
from .models import Contact
from .widgets import ContactCardWidget, StatsChartWidget

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    list_widget = ContactCardWidget
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'email', 'phone']}),
        ('Personal Info', {'fields': ['address'], 'expanded': False}),
    ]

class DashboardView(BaseView):
    route_base = '/dashboard'
    
    @expose('/')
    def index(self):
        # 获取统计数据
        total_contacts = self.appbuilder.get_session.query(Contact).count()
        
        # 渲染自定义模板
        return self.render_template(
            'dashboard/index.html',
            total_contacts=total_contacts,
            chart_widget=StatsChartWidget(
                chart_title='Contacts Overview',
                labels=['Active', 'Inactive'],
                values=[total_contacts, 0]
            )
        )

class CustomBaseView(BaseView):
    @expose('/custom')
    def custom_page(self):
        return self.render_template('custom/page.html')
```

### 基础模板 (templates/appbuilder/base.html)
```html
{% extends 'appbuilder/baselayout.html' %}

{% block head_css %}
    {{ super() }}
    <link href="{{url_for('static',filename='css/custom.css')}}" rel="stylesheet">
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.4/css/all.min.css" rel="stylesheet">
{% endblock %}

{% block body %}
    <div class="wrapper">
        {% block navbar %}
            {% include 'appbuilder/navbar.html' %}
        {% endblock %}
        
        <div class="content-wrapper">
            {% block messages %}
                {{ super() }}
            {% endblock %}
            
            {% block content %}{% endblock %}
        </div>
        
        {% block footer %}
            <footer class="main-footer">
                <div class="pull-right hidden-xs">
                    <b>Version</b> 1.0.0
                </div>
                <strong>Copyright &copy; 2023 Flask App-Builder Demo.</strong> All rights reserved.
            </footer>
        {% endblock %}
    </div>
{% endblock %}

{% block tail_js %}
    {{ super() }}
    <script src="{{url_for('static',filename='js/custom.js')}}"></script>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
{% endblock %}
```

### 导航栏模板 (templates/appbuilder/navbar.html)
```html
<nav class="navbar navbar-default navbar-fixed-top">
    <div class="container-fluid">
        <div class="navbar-header">
            <button type="button" class="navbar-toggle collapsed" data-toggle="collapse" data-target="#navbar">
                <span class="sr-only">Toggle navigation</span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
                <span class="icon-bar"></span>
            </button>
            <a class="navbar-brand" href="{{url_for('IndexView.index')}}">
                <i class="fas fa-address-book"></i> {{ appbuilder.app_name }}
            </a>
        </div>
        
        <div class="collapse navbar-collapse" id="navbar">
            <ul class="nav navbar-nav">
                <li><a href="{{url_for('DashboardView.index')}}"><i class="fas fa-tachometer-alt"></i> Dashboard</a></li>
                <li><a href="{{url_for('ContactModelView.list')}}"><i class="fas fa-users"></i> Contacts</a></li>
            </ul>
            
            <ul class="nav navbar-nav navbar-right">
                {% if current_user.is_authenticated %}
                    <li class="dropdown">
                        <a href="#" class="dropdown-toggle" data-toggle="dropdown">
                            <i class="fas fa-user"></i> {{g.user.get_full_name()}}<b class="caret"></b>
                        </a>
                        <ul class="dropdown-menu">
                            <li><a href="{{url_for('UserDBModelView.show',pk=current_user.id)}}"><i class="fas fa-user-circle"></i> Profile</a></li>
                            <li class="divider"></li>
                            <li><a href="{{url_for('AuthDBView.logout')}}"><i class="fas fa-sign-out-alt"></i> Logout</a></li>
                        </ul>
                    </li>
                {% else %}
                    <li><a href="{{url_for('AuthDBView.login')}}"><i class="fas fa-sign-in-alt"></i> Login</a></li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>
```

### 联系人卡片模板 (templates/widgets/contact_card.html)
```html
{% if not item_wrapper_class %}
    <div class="contact-grid">
        {% for item in include_widgets %}
            <div class="contact-card">
                <div class="card-avatar">
                    {% if item.data.avatar %}
                        <img src="{{ item.data.avatar }}" alt="{{ item.data.name }}">
                    {% else %}
                        <div class="avatar-placeholder">
                            <i class="fas fa-user"></i>
                        </div>
                    {% endif %}
                </div>
                
                <div class="card-content">
                    <h3>{{ item.data.name }}</h3>
                    <p class="email"><i class="fas fa-envelope"></i> {{ item.data.email }}</p>
                    <p class="phone"><i class="fas fa-phone"></i> {{ item.data.phone or 'N/A' }}</p>
                    
                    <div class="card-actions">
                        <a href="{{ url_for('ContactModelView.show', pk=item.data.id) }}" class="btn btn-sm btn-default">
                            <i class="fas fa-eye"></i> View
                        </a>
                        <a href="{{ url_for('ContactModelView.edit', pk=item.data.id) }}" class="btn btn-sm btn-primary">
                            <i class="fas fa-edit"></i> Edit
                        </a>
                    </div>
                </div>
            </div>
        {% endfor %}
    </div>
{% else %}
    <div class="{{ item_wrapper_class }}">
        {% for item in include_widgets %}
            {{ item() }}
        {% endfor %}
    </div>
{% endif %}

<style>
.contact-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
    gap: 20px;
    padding: 20px 0;
}

.contact-card {
    border: 1px solid #ddd;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s, box-shadow 0.2s;
}

.contact-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.card-avatar {
    height: 120px;
    background-color: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
}

.card-avatar img {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    object-fit: cover;
}

.avatar-placeholder {
    width: 80px;
    height: 80px;
    border-radius: 50%;
    background-color: #007bff;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 32px;
}

.card-content {
    padding: 20px;
}

.card-content h3 {
    margin: 0 0 15px 0;
    color: #333;
}

.card-content p {
    margin: 8px 0;
    color: #666;
}

.card-content i {
    width: 20px;
    text-align: center;
    margin-right: 8px;
}

.card-actions {
    margin-top: 20px;
    display: flex;
    gap: 10px;
}

.card-actions .btn {
    flex: 1;
    text-align: center;
}
</style>
```

### 统计图表模板 (templates/widgets/stats_chart.html)
```html
<div class="chart-widget">
    <h3>{{ widget.chart_title }}</h3>
    <canvas id="statsChart" width="400" height="200"></canvas>
</div>

<script>
document.addEventListener('DOMContentLoaded', function() {
    const ctx = document.getElementById('statsChart').getContext('2d');
    const chart = new Chart(ctx, {
        type: '{{ widget.chart_type }}',
        data: {
            labels: {{ labels|tojson }},
            datasets: [{
                label: 'Count',
                data: {{ values|tojson }},
                backgroundColor: [
                    'rgba(54, 162, 235, 0.6)',
                    'rgba(255, 99, 132, 0.6)'
                ],
                borderColor: [
                    'rgba(54, 162, 235, 1)',
                    'rgba(255, 99, 132, 1)'
                ],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        precision: 0
                    }
                }
            }
        }
    });
});
</script>

<style>
.chart-widget {
    background: white;
    border-radius: 8px;
    padding: 20px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.chart-widget h3 {
    margin-top: 0;
    color: #333;
}
</style>
```

### 仪表板模板 (templates/dashboard/index.html)
```html
{% extends "appbuilder/base.html" %}

{% block content %}
<div class="container-fluid">
    <div class="row">
        <div class="col-md-12">
            <h1><i class="fas fa-tachometer-alt"></i> Dashboard</h1>
            <p class="lead">Welcome to the Flask App-Builder Custom Widgets Demo</p>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-4">
            <div class="info-box">
                <div class="info-box-icon bg-blue">
                    <i class="fas fa-users"></i>
                </div>
                <div class="info-box-content">
                    <span class="info-box-text">Total Contacts</span>
                    <span class="info-box-number">{{ total_contacts }}</span>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="info-box">
                <div class="info-box-icon bg-green">
                    <i class="fas fa-check-circle"></i>
                </div>
                <div class="info-box-content">
                    <span class="info-box-text">Active Contacts</span>
                    <span class="info-box-number">{{ total_contacts }}</span>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="info-box">
                <div class="info-box-icon bg-yellow">
                    <i class="fas fa-chart-bar"></i>
                </div>
                <div class="info-box-content">
                    <span class="info-box-text">Statistics</span>
                    <span class="info-box-number">100%</span>
                </div>
            </div>
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12">
            {{ chart_widget(labels=['Active', 'Inactive'], values=[total_contacts, 0]) }}
        </div>
    </div>
    
    <div class="row">
        <div class="col-md-12">
            <div class="box">
                <div class="box-header">
                    <h3 class="box-title">Quick Actions</h3>
                </div>
                <div class="box-body">
                    <a href="{{ url_for('ContactModelView.add') }}" class="btn btn-primary">
                        <i class="fas fa-plus"></i> Add New Contact
                    </a>
                    <a href="{{ url_for('ContactModelView.list') }}" class="btn btn-default">
                        <i class="fas fa-list"></i> View All Contacts
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>
{% endblock %}

{% block tail_js %}
{{ super() }}
<script>
// 添加一些交互效果
document.addEventListener('DOMContentLoaded', function() {
    // 为info-box添加悬停效果
    const infoBoxes = document.querySelectorAll('.info-box');
    infoBoxes.forEach(box => {
        box.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
            this.style.boxShadow = '0 4px 8px rgba(0,0,0,0.15)';
        });
        
        box.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
            this.style.boxShadow = '0 2px 4px rgba(0,0,0,0.1)';
        });
    });
});
</script>
{% endblock %}