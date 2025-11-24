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