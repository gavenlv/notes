from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Date

class Contact(AuditMixin, Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    email = Column(String(100))
    phone = Column(String(20))
    address = Column(String(200))

    def __repr__(self):
        return self.name