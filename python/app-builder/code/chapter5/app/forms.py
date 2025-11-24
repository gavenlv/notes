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