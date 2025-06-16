from nameko.exceptions import BadRequest
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from payments.exceptions import NotFound
from payments.models import DeclarativeBase, Payment, PaymentMethodEnum
from payments.schemas import PaymentSchema


class PaymentsService:
    name = 'payments'

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()

    @rpc
    def get_payment_list(self):
        return "hello payment list"
    
    @rpc
    def get_payment_by_id(self, payment_id):
        return "hello payment by id"
    
    @rpc
    def get_payment_by_requester_id(self, requester_id):
        return "hello payment by requester id"
    
    @rpc
    def get_payment_status(self, payment_id):
        status = self.db.query(Payment.status).filter(Payment.id == payment_id).scalar()

        if not status: raise NotFound(f'Payment with id {payment_id} not found')

        return status
    
    @rpc
    def get_payment_amount(self, payment_id):
        amount = self.db.query(Payment.payment_amount).filter(Payment.id == payment_id).scalar()

        if not amount: raise NotFound(f'Payment with id {payment_id} not found')

        return amount
    
    @rpc
    def create_payment(self, data):
        validated, errors = PaymentSchema().load(data)
        if errors:
            raise BadRequest(f"Validation failed: {errors}")

        new_payment = Payment(
            customer_id=validated['customer_id'],
            requester_type=validated['requester_type'],
            requester_id=validated['requester_id'],
            secondary_requester_id=validated['secondary_requester_id'],     # If None, default to Null in Schema

            payment_method=validated['payment_method'],
            payment_amount=validated['payment_amount'],
            status=validated['status'],                                     # If None, default to 1 in Schema

            psp_id=None,
            signature_key=None,
            settle_date=None
        )

        self.db.add(new_payment)
        self.db.commit()

        # Dispatch event in Docker
        # self.event_dispatcher('test_object_created', {
        #     'test_result': testResult,
        # })

        return PaymentSchema().dump(new_payment).data
    
    @rpc
    def complete_payment(self, payment_id):
        return "hello complete payment"

    @rpc
    def cancel_payment(self, payment_id):
        return "hello cancel payment"
    
# =================================================================================FUNGSI MIDTRANS=============================================================================== 

    def createMidtransTransaction(self):
        return "hello create midtrans transaction"
    
    def checkMidtransTransactionStatus(self):
        return "hello check midtrans transaction status"
    
    def completeMidtransTransactionStatus(self):
        return "hello complete midtrans transaction status"
    
    def cancelMidtransTransactionStatus(self):
        return "hello cancel midtrans transaction status"
    
# =================================================================================FUNGSI TEST=============================================================================== 
    
    @rpc
    def get_test(self, test_id):
        test = self.db.query(Payment).get(test_id)

        if not test:
            raise NotFound('Payment with id {} not found'.format(test_id))

        return PaymentSchema().dump(test).data

    @rpc
    def create_test(self, data):
        # Validate input
        validated, errors = PaymentSchema().load(data)
        if errors:
            raise BadRequest("Validation failed: {}".format(errors))
        
        # Create Instance
        test = Payment(
            name=validated['name'],
            age=validated['age']
        )
        
        # Add to db
        self.db.add(test)
        self.db.commit()

        # Serialize the instance
        testResult = PaymentSchema().dump(test).data

        # Dispatch event in Docker
        self.event_dispatcher('test_object_created', {
            'test_result': testResult,
        })

        # Return the serialized instance
        return testResult

    @rpc
    def update_test(self, test_id, data):
        # Validate input
        validated, errors = PaymentSchema().load(data)
        if errors:
            raise BadRequest("Validation failed: {}".format(errors))

        # Fetch the existing instance
        test = self.db.query(Payment).get(test_id)

        # If not found, raise NotFound exception
        if not test:
            raise NotFound('Payment with id {} not found'.format(data['id']))
        
        # Update the instance in db
        test.name = data['name']
        test.age = data['age']
        self.db.commit()
        
        # Return updated instance (serialized)
        return PaymentSchema().dump(test).data

    @rpc
    def delete_test(self, test_id):
        # Fetch targeted instance
        test = self.db.query(Payment).get(test_id)
        
        # Delete in db
        self.db.delete(test)
        self.db.commit()

