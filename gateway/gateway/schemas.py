from marshmallow import Schema, fields, validate
    
class CreatePaymentSchema(Schema):
    requester_type = fields.Int(required=True)
    requester_id = fields.Int(required=True)
    secondary_requester_id = fields.Int(allow_none=True)

    payment_method = fields.Str(
        required=True,
        validate=validate.OneOf(["tunai", "bca va", "qris", "gopay", "ovo"])
    )
    payment_amount = fields.Float(required=True)

    # status, psp_id, signature_key, settle_date diisi di dalam service
    
class GetPaymentSchema(Schema):
    id = fields.Int()

    requester_type = fields.Int()
    requester_id = fields.Int()
    secondary_requester_id = fields.Int(allow_none=True)

    payment_method = fields.Str()
    payment_amount = fields.Float()
    status = fields.Int()

    psp_id = fields.Str(allow_none=True)
    signature_key = fields.Str(allow_none=True)

    settle_date = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()

# TEST
class CreateTestSchema(Schema):
    name = fields.Str(required=True)
    age = fields.Int(required=True)

class GetTestSchema(Schema):
    id = fields.Int()
    name = fields.Str()
    age = fields.Int()
