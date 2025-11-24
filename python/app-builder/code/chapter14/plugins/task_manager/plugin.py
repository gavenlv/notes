from flask_appbuilder import BasePlugin
from flask_appbuilder.models.sqla.interface import SQLAInterface
from .models import Task, TaskCategory
from .views import TaskModelView, TaskCategoryModelView, TaskDashboardView

class TaskManagerPlugin(BasePlugin):
    name = "Task Manager"
    category = "Productivity"
    version = "1.0.0"
    
    # 插件模型
    appbuilder_models = [
        Task,
        TaskCategory
    ]
    
    # 插件视图
    appbuilder_views = [
        {
            "name": "Tasks",
            "icon": "fa-tasks",
            "category": "Task Manager",
            "view": TaskModelView()
        },
        {
            "name": "Categories",
            "icon": "fa-tags",
            "category": "Task Manager",
            "view": TaskCategoryModelView()
        },
        {
            "name": "Dashboard",
            "icon": "fa-dashboard",
            "category": "Task Manager",
            "view": TaskDashboardView()
        }
    ]