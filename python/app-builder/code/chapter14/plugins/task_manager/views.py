from flask_appbuilder import ModelView, BaseView, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask_appbuilder.actions import action
from flask import flash, redirect, url_for
from flask_appbuilder.security.decorators import has_access
from .models import Task, TaskCategory

def get_user():
    from flask import g
    return g.user

class TaskModelView(ModelView):
    datamodel = SQLAInterface(Task)
    
    # 列表视图配置
    list_columns = ['title', 'category.name', 'priority_label', 'status_label', 'due_date', 'created_on']
    
    # 显示字段集
    show_fieldsets = [
        ('Summary', {'fields': ['title', 'description']}),
        ('Details', {'fields': ['category', 'priority', 'status', 'due_date']}),
        ('Audit', {'fields': ['created_on', 'changed_on', 'created_by'], 'expanded': False})
    ]
    
    # 编辑字段集
    edit_fieldsets = [
        ('Summary', {'fields': ['title', 'description']}),
        ('Details', {'fields': ['category', 'priority', 'status', 'due_date']})
    ]
    
    # 添加字段集
    add_fieldsets = [
        ('Summary', {'fields': ['title', 'description']}),
        ('Details', {'fields': ['category', 'priority', 'status', 'due_date']})
    ]
    
    # 搜索和过滤
    search_columns = ['title', 'description', 'category', 'priority', 'status']
    
    # 操作按钮
    @action("mark_completed", "Mark Completed", "Mark selected tasks as completed?", "fa-check")
    def mark_completed(self, items):
        """标记为完成"""
        count = 0
        for item in items:
            item.status = 'completed'
            item.is_completed = True
            count += 1
        self.datamodel.session.commit()
        flash(f"Successfully marked {count} tasks as completed", "success")
        return redirect(url_for('TaskModelView.list'))
    
    @action("mark_in_progress", "Mark In Progress", "Mark selected tasks as in progress?", "fa-play")
    def mark_in_progress(self, items):
        """标记为进行中"""
        count = 0
        for item in items:
            item.status = 'in_progress'
            item.is_completed = False
            count += 1
        self.datamodel.session.commit()
        flash(f"Successfully marked {count} tasks as in progress", "success")
        return redirect(url_for('TaskModelView.list'))

class TaskCategoryModelView(ModelView):
    datamodel = SQLAInterface(TaskCategory)
    list_columns = ['name', 'description', 'color']

class TaskDashboardView(BaseView):
    route_base = "/taskmanager"
    default_view = "dashboard"
    
    @expose('/')
    @has_access
    def dashboard(self):
        """任务仪表板"""
        # 获取当前用户的任务统计
        user = get_user()
        total_tasks = self.appbuilder.get_session.query(Task).count()
        completed_tasks = self.appbuilder.get_session.query(Task).filter_by(is_completed=True).count()
        pending_tasks = self.appbuilder.get_session.query(Task).filter_by(status='pending').count()
        in_progress_tasks = self.appbuilder.get_session.query(Task).filter_by(status='in_progress').count()
        
        # 按优先级分组的任务
        high_priority_tasks = self.appbuilder.get_session.query(Task).filter_by(
            priority=3, 
            is_completed=False
        ).order_by(Task.due_date).limit(5).all()
        
        return self.render_template(
            'task_manager/dashboard.html',
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            pending_tasks=pending_tasks,
            in_progress_tasks=in_progress_tasks,
            high_priority_tasks=high_priority_tasks
        )