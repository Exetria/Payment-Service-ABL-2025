import requests
from datetime import datetime
from base64 import b64encode

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
        try:
            payments = self.db.query(Payment).all()
            if not payments:
                return "No Payments Found"

            return PaymentSchema(many=True).dump(payments).data

        except Exception as e:
            return "Failed to fetch payments"

    @rpc
    def get_payment_by_id(self, payment_id):
        try:
            payment = self.db.query(Payment).get(payment_id)
            if not payment:
                return "Payment Not Found"

            return PaymentSchema().dump(payment).data

        except Exception as e:
            return "Failed to fetch payment"
    
    @rpc
    def get_payment_by_customer_id(self, customer_id):
        try:
            payments = self.db.query(Payment).filter(Payment.customer_id == customer_id).all()
            if not payments:
                return "No Payments Found for this Customer"

            return PaymentSchema(many=True).dump(payments).data
        except Exception as e:
            return f"Failed to fetch payment by customer_id: {str(e)}"

    @rpc
    def get_payment_by_requester_id(self, requester_id):
        try:
            payments = self.db.query(Payment).filter(Payment.requester_id == requester_id).all()
            if not payments:
                return "No Payments Found for this Requester"

            return PaymentSchema(many=True).dump(payments).data
        except Exception as e:
            return f"Failed to fetch payment by requester_id: {str(e)}"
    
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
        try: 
            # Fetch the existing instance
            targetedPayment = self.db.query(Payment).get(payment_id)

            # If not found or already completed/cancelled, return
            if not targetedPayment:
                return "Payment Not Found"
            if targetedPayment.status != 1:
                return "Already Finished or Cancelled"
            
            # Update the instance in db
            targetedPayment.status = 2                  # DONE
            self.db.commit()
            
            # Update requester status
            self.update_requester_status(targetedPayment.requester_type, targetedPayment.requester_id, targetedPayment.secondary_requester_id, 1)
        
            # Return status
            return "Success"
        
        except Exception as e:
            # Return status
            return "Failed"
        
    @rpc
    def cancel_payment(self, payment_id):
        try:
            # Fetch the existing instance
            targetedPayment = self.db.query(Payment).get(payment_id)

            # If not found or already completed/cancelled, return
            if not targetedPayment:
                return "Payment Not Found"
            if targetedPayment.status != 1:
                return "Already Finished or Cancelled"
            
            # Update the instance in db
            targetedPayment.status = 3                  # CANCELLED
            self.db.commit()
            
            # Update requester status
            self.update_requester_status(targetedPayment.requester_type, targetedPayment.requester_id, targetedPayment.secondary_requester_id, 0)

            # Return status
            return "Success"
        
        except Exception as e:
            # Return status
            return "Failed"

    def update_requester_status(self, requester_type, requester_id, secondary_requester_id, status):
        # TODO: handle status, 0 for cancel, 1 for complete
        
        # 1 = RPC to Order | 2 to Reservation | 3  to Event	
        if requester_type == 1:
            # Call update API to order
            if secondary_requester_id is not None:
                # Call update API to delivery (if secondary_requester_id not null)
                pass
            pass
        elif requester_type == 2:
            # Call update API to reservation
            pass
        elif requester_type == 3:
            # Call update API to event
            pass

        return
    
# =================================================================================FUNGSI MIDTRANS=============================================================================== 

    def createMidtransTransaction(self):
        return "hello create midtrans transaction"
    
    def checkMidtransTransactionStatus(self):
        return "hello check midtrans transaction status"
    
    def cancelMidtransTransactionStatus(self):
        return "hello cancel midtrans transaction status"
    
    @rpc
    def handle_midtrans_callback(self, midtrans_transaction_id, midtrans_transaction_status):
        try: 
            # Fetch the existing instance
            targetedPayment = self.db.query(Payment).filter(Payment.psp_id == midtrans_transaction_id).first()
            
            # If not found or already completed/cancelled, return
            if not targetedPayment:
                return "Payment Not Found"
            if targetedPayment.status != 1:
                return "Already Finished or Cancelled"
            
            # Update the instance in db
            # DONE
            if midtrans_transaction_status == "settlement":
                targetedPayment.status = 2           
            # CANCELLED       
            elif midtrans_transaction_status == "cancel" or midtrans_transaction_status == "expire":
                targetedPayment.status = 3           
            else:
                return "Status Not Valid"
            
            targetedPayment.settle_date = datetime.now()
            self.db.commit()
            
            # Update requester status
            self.update_requester_status(targetedPayment.requester_type, targetedPayment.requester_id, targetedPayment.secondary_requester_id, targetedPayment.status)
        
            # Return status
            return "Success"
        
        except Exception as e:
            # Return status
            return "Failed"
    
# =================================================================================FUNGSI TEST=============================================================================== 

    @rpc
    def test_get_payment_list(self):
        try:
            payments = self.db.query(Payment).all()
            if not payments:
                return "No Payments Found"

            return PaymentSchema(many=True).dump(payments).data
        except Exception as e:
            return f"Error: {str(e)}"

    @rpc
    def test_get_payment_by_id(self, payment_id):
        try:
            payment = self.db.query(Payment).get(payment_id)
            if not payment:
                return "Payment Not Found"

            return PaymentSchema().dump(payment).data
        except Exception as e:
            return f"Error: {str(e)}"

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