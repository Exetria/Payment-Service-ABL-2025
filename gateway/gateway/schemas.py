from marshmallow import Schema, fields


class CreateTestSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Int(required=True)

class GetTestSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    age = fields.Int()
