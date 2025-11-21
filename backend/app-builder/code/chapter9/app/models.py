from flask_appbuilder import Model
from flask_appbuilder.models.mixins import AuditMixin
from flask_appbuilder.fields import FileUploadField, ImageUploadField
from sqlalchemy import Column, Integer, String, Text
import os

def get_upload_path():
    """获取上传路径"""
    return os.path.join(os.path.dirname(__file__), '..', 'uploads')

class Document(AuditMixin, Model):
    __tablename__ = 'document'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(150), nullable=False)
    description = Column(Text)
    file = FileUploadField(
        'Document File',
        base_path=get_upload_path(),
        allow_overwrite=False
    )
    
    def __repr__(self):
        return self.name

class ImageGallery(AuditMixin, Model):
    __tablename__ = 'image_gallery'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(150), nullable=False)
    description = Column(Text)
    image = ImageUploadField(
        'Image',
        base_path=os.path.join(get_upload_path(), 'images'),
        thumbnail_size=(100, 100, True),
        allow_overwrite=False
    )
    
    def __repr__(self):
        return self.title