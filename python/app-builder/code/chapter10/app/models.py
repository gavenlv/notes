from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from sqlalchemy import Column, Integer, String, Text
from flask_babel import lazy_gettext as _

class Product(AuditMixin, Model):
    __tablename__ = 'product'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False, info={'label': _('Name')})
    description = Column(Text, info={'label': _('Description')})
    price = Column(Integer, info={'label': _('Price')})
    
    def __repr__(self):
        return self.name