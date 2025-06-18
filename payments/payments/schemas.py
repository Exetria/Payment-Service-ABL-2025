from marshmallow import Schema, fields, validate

class PaymentSchema(Schema):
    id = fields.Int(dump_only=True)
    
    customer_id = fields.Int(required=True)
    requester_type = fields.Int(required=True)
    requester_id = fields.Int(required=True)
    secondary_requester_id = fields.Int(allow_none=True)

    payment_method = fields.Method("get_payment_method")
    payment_amount = fields.Float(required=True)
    status = fields.Int(missing=1)
    
    psp_id = fields.Str(allow_none=True)
    raw_response = fields.Dict(allow_none=True)
    
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
    settle_date = fields.DateTime(allow_none=True)
    
    def get_payment_method(self, obj):
        return obj.payment_method.value if hasattr(obj.payment_method, "value") else str(obj.payment_method)