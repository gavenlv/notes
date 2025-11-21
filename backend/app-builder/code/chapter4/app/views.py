from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash, redirect
from wtforms.validators import DataRequired, Length
from .models import Contact, ContactGroup, Gender, ExtendedUser

class ContactModelView(ModelView):
    datamodel = SQLAInterface(Contact)
    
    # 列表页面显示的字段
    list_columns = ['name', 'personal_celphone', 'birthday', 'contact_group']
    
    # 添加和编辑页面显示的字段
    add_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    edit_columns = ['name', 'address', 'birthday', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 搜索字段
    search_columns = ['name', 'address', 'personal_phone', 'personal_celphone', 'contact_group', 'gender']
    
    # 添加验证器
    validators_columns = {
        'name': [DataRequired(), Length(min=2, max=150)],
        'personal_celphone': [Length(max=20)]
    }

class GroupModelView(ModelView):
    datamodel = SQLAInterface(ContactGroup)
    related_views = [ContactModelView]

class GenderModelView(ModelView):
    datamodel = SQLAInterface(Gender)
    related_views = [ContactModelView]

class UserViewModel(ModelView):
    datamodel = SQLAInterface(ExtendedUser)
    list_columns = ['username', 'first_name', 'last_name', 'email', 'department']