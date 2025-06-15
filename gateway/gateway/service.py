import json

from marshmallow import ValidationError
from nameko import config
from nameko.exceptions import BadRequest
from nameko.rpc import RpcProxy
from werkzeug import Response

from gateway.entrypoints import http
from gateway.exceptions import OrderNotFound, ProductNotFound
from gateway.schemas import CreateTestSchema, GetTestSchema


class GatewayService(object):
    """
    Service acts as a gateway to other services over http.
    """

    name = 'gateway'

    echo_rpc = RpcProxy("greeting_service")
    orders_rpc = RpcProxy('orders')

    @http("GET", "/hello/<string:name>")
    def hello(self, request, name):
        greeting = self.echo_rpc.hello(name)
        return Response(json.dumps({"message": greeting}), mimetype="application/json")
    
    @http("GET", "/test/<int:test_id>", expected_exceptions=OrderNotFound)
    def get_test(self, request, test_id):
        test = self.orders_rpc.get_test(test_id)
        return Response(
            GetTestSchema().dumps(test).data,
            mimetype='application/json'
        )

    @http("POST", "/test",expected_exceptions=(ValidationError, ProductNotFound, BadRequest))
    def create_test(self, request):
        schema = CreateTestSchema(strict=True)

        # Validate JSON
        try:
            test_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # RPC call with validated JSON data
        result = self.orders_rpc.create_test(test_data)
        
        # Get ID
        resultId = result['id']
    
        # Return ID
        return Response(json.dumps({'id': resultId}), mimetype='application/json')\
    
    @http("PUT", "/test/<int:test_id>",expected_exceptions=(ValidationError, ProductNotFound, BadRequest))
    def update_test(self, request, test_id):
        schema = CreateTestSchema(strict=True)

        # Validate JSON
        try:
            test_data = schema.loads(request.get_data(as_text=True)).data
        except ValueError as exc:
            raise BadRequest("Invalid json: {}".format(exc))

        # RPC call with validated JSON data
        result = self.orders_rpc.update_test(test_id, test_data)
        
        # Return instance
        return Response(
            GetTestSchema().dumps(result).data,
            mimetype='application/json'
        )
    
    @http("DELETE", "/test/<int:test_id>", expected_exceptions=OrderNotFound)
    def delete_test(self, request, test_id):
        test = self.orders_rpc.delete_test(test_id)
        return Response(
            GetTestSchema().dumps(test).data,
            mimetype='application/json'
        )