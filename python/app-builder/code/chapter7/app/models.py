from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String

class Contact(AuditMixin, Model):
    __tablename__ = 'contact'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(150), nullable=False)
    phone = Column(String(50))
    
    def __repr__(self):
        return self.name