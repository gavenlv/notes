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