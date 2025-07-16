from marshmallow import Schema, fields, validate

class UserRegistrationSchema(Schema):
    email = fields.Email(required=True)
    password = fields.Str(required=True, validate=validate.Length(min=8))
    name = fields.Str(required=True, validate=validate.Length(min=2))

class UserUpdateSchema(Schema):
    name = fields.Str(validate=validate.Length(min=2))
    email = fields.Email()