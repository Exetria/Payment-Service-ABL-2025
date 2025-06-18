import json

from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest
from nameko.rpc import RpcProxy
from werkzeug import Response

from gateway.entrypoints import http
from gateway.exceptions import PaymentNotFound
from gateway.schemas import CreatePaymentSchema, GetPaymentSchema


class GatewayService(object):
    """
    Service acts as a gateway to other services over http.
    """

    name = 'gateway'

    echo_rpc = RpcProxy("greeting_service")
    payments_rpc = RpcProxy('payments')
    
    
    @http("GET", "/payment", expected_exceptions=(BadRequest,))
    def get_payment_list(self, request):
        """
        Get list of payments.
        """
        payments = self.payments_rpc.get_payment_list()
        return Response(
            json.dumps(payments),
            mimetype='application/json'
        )
        
    @http("GET", "/payment/<int:payment_id>", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_by_id(self, request, payment_id):
        """
        Get payment by ID.
        """
        payment = self.payments_rpc.get_payment_by_id(payment_id)
        return Response(
            json.dumps(payment),
            mimetype='application/json'
        )
    
    @http("GET", "/payment/requester/<int:requester_id>", expected_exceptions=(BadRequest,))
    def get_payment_by_requester_id(self, request, requester_id):
        """
        Get payment by requester ID.
        """
        payments = self.payments_rpc.get_payment_by_requester_id(requester_id)
        return Response(
            json.dumps(payments),
            mimetype='application/json'
        )
        
    @http("GET", "/payment/<string:payment_id>/status", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_status(self, request, payment_id):
        # return Response(json.dumps({"message": "Get payment status by payment ID"}), mimetype="application/json")
        
        status = self.payments_rpc.get_payment_status(payment_id)
        return Response(
            json.dumps({"status": status}),
            mimetype='application/json'
        )
    
    @http("GET", "/payment/<string:payment_id>/amount", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_amount(self, request, payment_id):
        # return Response(json.dumps({"message": "Get payment amount by payment ID"}), mimetype="application/json")

        amount = self.payments_rpc.get_payment_amount(payment_id)
        return Response(
            json.dumps({"amount": amount}),
            mimetype='application/json'
        )
        
    @http("POST", "/payment", expected_exceptions=(BadRequest))
    def create_payment(self, request):
        schema = CreatePaymentSchema(strict=True)

        # Validate JSON
        try:
            payment_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # RPC call with validated JSON data
        result = self.payments_rpc.create_payment(payment_data)
        
        # Get ID
        resultId = result['id']
    
        # Return ID
        return Response(json.dumps({'id': resultId}), mimetype='application/json')
    
    @http("PATCH", "/payment/<int:payment_id>/complete", expected_exceptions=(PaymentNotFound,BadRequest,))
    def complete_payment(self, request, payment_id):
        # return Response(json.dumps({"message": "Complete a payment by ID"}), mimetype="application/json")
        
        result = self.payments_rpc.complete_payment(payment_id)
        return Response(
            json.dumps({"response": result}),
            mimetype='application/json'
        )
    
    @http("PATCH", "/payment/<int:payment_id>/cancel", expected_exceptions=(PaymentNotFound,BadRequest,))
    def cancel_payment(self, request, payment_id):
        # return Response(json.dumps({"message": "Cancel a payment by ID"}), mimetype="application/json")
        
        result = self.payments_rpc.cancel_payment(payment_id)
        return Response(
            json.dumps({"response": result}),
            mimetype='application/json'
        )
    
    @http("POST", "/payment/midtrans/callback")
    def midtrans_callback(self, request):
        try:
            midtrans_data = json.loads(request.get_data(as_text=True))
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))
        
        transaction_id = midtrans_data.get("transaction_id")
        transaction_status = midtrans_data.get("transaction_status")
        
        result = self.payments_rpc.handle_midtrans_callback(transaction_id, transaction_status)
        return Response(
            json.dumps({"response": result}),
            mimetype='application/json'
        )

    def checkPaymentToken(self, request):
        # TODO: Delete return & fill entities' token
        return
        orderToken = ""
        reservationToken = ""
        eventToken = ""
        
        token = request.headers.get("Authorization")
        
        if token not in [orderToken, reservationToken, eventToken]:
            raise BadRequest("Invalid token")
    
# ========================================================================================================================================================================== 
    # Ini buat test   
    # @http("GET", "/hello/<string:name>")
    # def hello(self, request, name):
    #     greeting = self.echo_rpc.hello(name)
    #     return Response(json.dumps({"message": greeting}), mimetype="application/json")
    
    # @http("GET", "/test/<int:test_id>", expected_exceptions=OrderNotFound)
    # def get_test(self, request, test_id):
    #     test = self.payments_rpc.get_test(test_id)
    #     return Response(
    #         GetTestSchema().dumps(test).data,
    #         mimetype='application/json'
    #     )

    # @http("POST", "/test",expected_exceptions=(ValidationError, ProductNotFound, BadRequest))
    # def create_test(self, request):
    #     schema = CreateTestSchema(strict=True)

    #     # Validate JSON
    #     try:
    #         test_data = schema.loads(request.get_data(as_text=True)).data
    #     except ValueError as exc:
    #         raise BadRequest("Invalid json: {}".format(exc))

    #     # RPC call with validated JSON data
    #     result = self.payments_rpc.create_test(test_data)
        
    #     # Get ID
    #     resultId = result['id']
    
    #     # Return ID
    #     return Response(json.dumps({'id': resultId}), mimetype='application/json')
    
    # @http("PUT", "/test/<int:test_id>",expected_exceptions=(ValidationError, ProductNotFound, BadRequest))
    # def update_test(self, request, test_id):
    #     schema = CreateTestSchema(strict=True)

    #     # Validate JSON
    #     try:
    #         test_data = schema.loads(request.get_data(as_text=True)).data
    #     except ValueError as exc:
    #         raise BadRequest("Invalid json: {}".format(exc))

    #     # RPC call with validated JSON data
    #     result = self.payments_rpc.update_test(test_id, test_data)
        
    #     # Return instance
    #     return Response(
    #         GetTestSchema().dumps(result).data,
    #         mimetype='application/json'
    #     )
    
    # @http("DELETE", "/test/<int:test_id>", expected_exceptions=OrderNotFound)
    # def delete_test(self, request, test_id):
        test = self.payments_rpc.delete_test(test_id)
        return Response(
            GetTestSchema().dumps(test).data,
            mimetype='application/json'
        )