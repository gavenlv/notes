from flask_appbuilder.api import BaseApi, expose
from flask_appbuilder.models.sqla.interface import SQLAInterface
from flask import request
from marshmallow import ValidationError
from .models import Contact
from .schemas import ContactSchema, ContactCreateSchema, ContactUpdateSchema

class ContactApi(BaseApi):
    resource_name = 'contacts'
    contact_schema = ContactSchema()
    create_schema = ContactCreateSchema()
    update_schema = ContactUpdateSchema()
    
    @expose('/', methods=['GET'])
    def get_list(self):
        """获取联系人列表"""
        contacts = self.appbuilder.get_session.query(Contact).all()
        result = self.contact_schema.dump(contacts, many=True)
        return self.response(200, result=result)
    
    @expose('/<int:id>', methods=['GET'])
    def get(self, id):
        """获取单个联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        result = self.contact_schema.dump(contact)
        return self.response(200, result=result)
    
    @expose('/', methods=['POST'])
    def create(self):
        """创建联系人"""
        try:
            data = self.create_schema.load(request.get_json())
        except ValidationError as err:
            return self.response_400(errors=err.messages)
        
        contact = Contact(**data)
        self.appbuilder.get_session.add(contact)
        self.appbuilder.get_session.commit()
        
        result = self.contact_schema.dump(contact)
        return self.response(201, result=result, message='Contact created')
    
    @expose('/<int:id>', methods=['PUT'])
    def update(self, id):
        """更新联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        try:
            data = self.update_schema.load(request.get_json(), partial=True)
        except ValidationError as err:
            return self.response_400(errors=err.messages)
        
        for key, value in data.items():
            setattr(contact, key, value)
        
        self.appbuilder.get_session.commit()
        
        result = self.contact_schema.dump(contact)
        return self.response(200, result=result, message='Contact updated')
    
    @expose('/<int:id>', methods=['DELETE'])
    def delete(self, id):
        """删除联系人"""
        contact = self.appbuilder.get_session.query(Contact).get(id)
        if not contact:
            return self.response_404()
        
        self.appbuilder.get_session.delete(contact)
        self.appbuilder.get_session.commit()
        
        return self.response(200, message='Contact deleted')