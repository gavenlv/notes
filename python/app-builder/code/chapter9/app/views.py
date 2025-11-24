from flask_appbuilder import ModelView
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import flash
from .models import Document, ImageGallery

class DocumentModelView(ModelView):
    datamodel = SQLAInterface(Document)
    
    list_columns = ['name', 'description', 'file', 'created_on']
    show_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']})
    ]
    edit_fieldsets = [
        ('Summary', {'fields': ['name', 'description', 'file']})
    ]
    
    def post_add(self, item):
        """添加后处理"""
        flash(f"文档 '{item.name}' 已成功上传!", "info")
        super().post_add(item)
    
    def post_update(self, item):
        """更新后处理"""
        flash(f"文档 '{item.name}' 已成功更新!", "info")
        super().post_update(item)
    
    def post_delete(self, item):
        """删除后处理"""
        flash(f"文档 '{item.name}' 已成功删除!", "info")
        super().post_delete(item)

class ImageGalleryModelView(ModelView):
    datamodel = SQLAInterface(ImageGallery)
    
    list_columns = ['title', 'image', 'created_on']
    show_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']}),
        ('Audit', {'fields': ['created_on', 'changed_on'], 'expanded': False})
    ]
    add_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']})
    ]
    edit_fieldsets = [
        ('Summary', {'fields': ['title', 'description', 'image']})
    ]