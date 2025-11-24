from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, ForeignKey, Date
from sqlalchemy.orm import relationship

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
    address = Column(String(564))
    birthday = Column(Date)
    personal_phone = Column(String(20))
    personal_celphone = Column(String(20))
    contact_group_id = Column(Integer, ForeignKey('contact_group.id'), nullable=False)
    contact_group = relationship("ContactGroup")
    gender_id = Column(Integer, ForeignKey('gender.id'), nullable=False)
    gender = relationship("Gender")

    def __repr__(self):
        return self.name