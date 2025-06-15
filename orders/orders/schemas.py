from marshmallow import Schema, fields

class TestSchema(Schema):
    id = fields.Int()
    name = fields.Str(required=True)
    age = fields.Int(required=True)