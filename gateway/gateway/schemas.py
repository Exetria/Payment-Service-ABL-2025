from marshmallow import Schema, fields, validate
    
class CreatePaymentSchema(Schema):
    customer_id = fields.Int(required=True)
    requester_type = fields.Int(required=True)
    requester_id = fields.Int(required=True)
    secondary_requester_id = fields.Int(allow_none=True)

    payment_method = fields.Str(
        required=True,
        validate=validate.OneOf(["tunai", "bca_va", "qris", "gopay", "ovo"])
    )
    payment_amount = fields.Float(required=True)

    # status, psp_id, signature_key, settle_date diisi di dalam service
    
class GetPaymentSchema(Schema):
    id = fields.Int()

    customer_id = fields.Int()
    requester_type = fields.Method("get_requester")
    requester_id = fields.Int()
    secondary_requester_id = fields.Int(allow_none=True)

    payment_method = fields.Str()
    payment_amount = fields.Float()
    payment_info = fields.Method("get_payment_info")
    status = fields.Int()

    settle_date = fields.DateTime(allow_none=True)
    created_at = fields.DateTime()
    updated_at = fields.DateTime()
    
    def get_requester(self, obj):
        requester_type = obj.get('requester_type', None)

        if requester_type == 1:
            return "Order"
        elif requester_type == 2:
            return "Reservation"
        elif requester_type == 3:
            return "Event"
        return "Unknown"
    
    def get_payment_info(self, obj):
        try:
            raw = obj.get('raw_response', {})
            method = obj.get('payment_method', '')

            if isinstance(raw, str):
                import json
                raw = json.loads(raw)
                
            # bank_transfer → BCA VA
            if method == "bca_va":
                va_list = raw.get("va_numbers", [])
                if va_list:
                    return va_list[0].get("va_number")

            # gopay or qris → use actions[].url
            if method in ["gopay", "qris"]:
                actions = raw.get("actions", [])
                for action in actions:
                    if action.get("name") == "generate-qr-code":
                        return action.get("url")

            return f"raw_response: {raw} | method: {method}"
        except Exception as e:
            return f"error: {str(e)}"  # Optional: for debugging