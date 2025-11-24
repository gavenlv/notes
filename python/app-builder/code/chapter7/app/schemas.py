from marshmallow import Schema, fields

class ContactSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()
    created_on = fields.DateTime(dump_only=True)
    changed_on = fields.DateTime(dump_only=True)

class ContactCreateSchema(Schema):
    name = fields.Str(required=True)
    email = fields.Email(required=True)
    phone = fields.Str()

class ContactUpdateSchema(Schema):
    name = fields.Str()
    email = fields.Email()
    phone = fields.Str()