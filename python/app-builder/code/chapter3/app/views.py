from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask import flash, redirect
from wtforms.validators import DataRequired, Length
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