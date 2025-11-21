from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder import Model
from datetime import datetime

class ContactGroup(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class Gender(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(50), unique=True, nullable=False)
    
    def __repr__(self):
        return self.name

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    address = Column(String(500))
    birthday = Column(DateTime)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey('contact_group.id'), nullable=False)
    contact_group = relationship("ContactGroup")
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    gender = relationship("Gender")
    
    def __repr__(self):
        return self.name
        
    def month_year(self):
        date = self.birthday or datetime.now()
        return datetime(date.year, date.month, 1) or datetime.now()
        
    def year(self):
        date = self.birthday or datetime.now()
        return datetime(date.year, 1, 1)