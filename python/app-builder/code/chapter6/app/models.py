from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from datetime import datetime

class User(AuditMixin, Model):
    __tablename__ = 'ab_user'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(64), unique=True, nullable=False)
    email = Column(String(64), unique=True, nullable=False)
    password = Column(String(256))
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime)
    department = Column(String(64))
    
    def __repr__(self):
        return self.username

class AuditLog(Model):
    __tablename__ = 'audit_log'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer)
    action = Column(String(100))
    resource = Column(String(100))
    timestamp = Column(DateTime, default=datetime.utcnow)
    details = Column(String(500))
    
    def __repr__(self):
        return f"{self.action} on {self.resource}"