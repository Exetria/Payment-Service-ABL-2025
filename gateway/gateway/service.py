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
    name = 'gateway'

    payments_rpc = RpcProxy('payments')

    @http("GET", "/payment", expected_exceptions=(BadRequest,))
    def get_payment_list(self, request):
        self.checkPaymentToken(request)
        
        paymentList = self.payments_rpc.get_payment_list()
        return Response(
            GetPaymentSchema(many=True).dumps(paymentList).data,
            mimetype='application/json'
        )
        
    @http("GET", "/payment/<int:payment_id>", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_by_id(self, request, payment_id):
        self.checkPaymentToken(request)

        payment = self.payments_rpc.get_payment_by_id(payment_id)
        
        return Response(
            GetPaymentSchema().dumps(payment).data,
            mimetype='application/json'
        )
    
    @http("GET", "/payment/customer/<int:customer_id>", expected_exceptions=(BadRequest,))
    def get_payment_by_customer_id(self, request, customer_id):
        self.checkPaymentToken(request)
        
        paymentList = self.payments_rpc.get_payment_by_customer_id(customer_id)
        
        return Response(
            GetPaymentSchema(many=True).dumps(paymentList).data,
            mimetype='application/json'
        )
    
    @http("GET", "/payment/requester/<int:requester_id>", expected_exceptions=(BadRequest,))
    def get_payment_by_requester_id(self, request, requester_id):
        self.checkPaymentToken(request)
        
        paymentList = self.payments_rpc.get_payment_by_requester_id(requester_id)
        
        return Response(
            GetPaymentSchema(many=True).dumps(paymentList).data,
            mimetype='application/json'
        )
        
    @http("GET", "/payment/<string:payment_id>/status", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_status(self, request, payment_id):
        self.checkPaymentToken(request)
        
        status = self.payments_rpc.get_payment_status(payment_id)
        
        status_text = {
        1: "Pending",
        2: "Completed",
        3: "Cancelled"
        }.get(status, "Unknown")
        
        return Response(
            json.dumps({"status": status_text}),
            mimetype='application/json'
        )
    
    @http("GET", "/payment/<string:payment_id>/amount", expected_exceptions=(PaymentNotFound,BadRequest,))
    def get_payment_amount(self, request, payment_id):
        self.checkPaymentToken(request)

        amount = self.payments_rpc.get_payment_amount(payment_id)
        return Response(
            json.dumps({"amount": amount}),
            mimetype='application/json'
        )
        
    @http("POST", "/payment", expected_exceptions=(BadRequest))
    def create_payment(self, request):
        self.checkPaymentToken(request)
        
        schema = CreatePaymentSchema(strict=True)

        try:
            payment_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        insertResult = self.payments_rpc.create_payment(payment_data)
        
        # newPaymentId = insertResult['id']
        # return Response(json.dumps({'id': newPaymentId}), mimetype='application/json')
        
        return Response(
            GetPaymentSchema().dumps(insertResult).data,
            mimetype='application/json'
        )
    
    @http("PATCH", "/payment/<int:payment_id>/complete", expected_exceptions=(PaymentNotFound,BadRequest,))
    def complete_payment(self, request, payment_id):
        self.checkPaymentToken(request)
        
        result = self.payments_rpc.complete_payment(payment_id)
        return Response(
            json.dumps({"response": result}),
            mimetype='application/json'
        )
    
    @http("PATCH", "/payment/<int:payment_id>/cancel", expected_exceptions=(PaymentNotFound,BadRequest,))
    def cancel_payment(self, request, payment_id):
        self.checkPaymentToken(request)
        
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
