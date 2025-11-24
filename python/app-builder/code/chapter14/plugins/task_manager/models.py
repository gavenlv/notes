from flask_appbuilder import Model
from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from flask_appbuilder.models.mixins import AuditMixin

class TaskCategory(Model):
    __tablename__ = 'task_category'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    description = Column(Text)
    color = Column(String(7), default='#007bff')  # HEX颜色代码
    
    tasks = relationship("Task", back_populates="category")
    
    def __repr__(self):
        return self.name

class Task(AuditMixin, Model):
    __tablename__ = 'task'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    due_date = Column(DateTime)
    priority = Column(Integer, default=1)  # 1=Low, 2=Medium, 3=High
    status = Column(String(20), default='pending')  # pending, in_progress, completed, cancelled
    is_completed = Column(Boolean, default=False)
    
    category_id = Column(Integer, ForeignKey('task_category.id'))
    category = relationship("TaskCategory", back_populates="tasks")
    
    def __repr__(self):
        return self.title
    
    @property
    def priority_label(self):
        """优先级标签"""
        labels = {1: 'Low', 2: 'Medium', 3: 'High'}
        return labels.get(self.priority, 'Unknown')
    
    @property
    def status_label(self):
        """状态标签"""
        labels = {
            'pending': 'Pending',
            'in_progress': 'In Progress',
            'completed': 'Completed',
            'cancelled': 'Cancelled'
        }
        return labels.get(self.status, 'Unknown')