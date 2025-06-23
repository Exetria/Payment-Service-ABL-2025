import os
import requests
from datetime import datetime
from base64 import b64encode

from nameko.exceptions import BadRequest
from nameko.events import EventDispatcher
from nameko.rpc import rpc
from nameko_sqlalchemy import DatabaseSession

from payments.models import DeclarativeBase, Payment, PaymentMethodEnum
from payments.schemas import PaymentSchema
from payments.exceptions import NotFound


class PaymentsService:
    name = 'payments'
    
    midtransUrl = 'https://api.sandbox.midtrans.com/v2'
    midtransSnapUrl = 'https://app.sandbox.midtrans.com/snap/v1'
    midtransServerKey = os.environ.get("PAYMENT_SECRET")

    db = DatabaseSession(DeclarativeBase)
    event_dispatcher = EventDispatcher()
    
    # reservation_rpc = rpc('reservation_service')
    # event_rpc = rpc('event_service')
    # order_rpc = rpc('order_service')
    delivery_rpc = rpc('delivery_service"')

    @rpc
    def get_payment_list(self):
        paymentList = self.db.query(Payment).all()

        return PaymentSchema(many=True).dump(paymentList).data
    
    @rpc
    def get_payment_by_id(self, payment_id):
        payment = self.db.query(Payment).get(payment_id)

        if not payment: raise NotFound(f'Payment with id {payment_id} not found')

        return PaymentSchema().dump(payment).data

    @rpc
    def get_payment_by_customer_id(self, customer_id):
        paymentList = (self.db.query(Payment).filter(Payment.customer_id == customer_id).all())

        return PaymentSchema(many=True).dump(paymentList).data
    
    @rpc
    def get_payment_by_requester_id(self, requester_id):
        paymentList = (self.db.query(Payment).filter(Payment.requester_id == requester_id).all())

        return PaymentSchema(many=True).dump(paymentList).data
    
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
            raise BadRequest("Validation failed: {}".format(errors))
        
        tempPaymentInstance = Payment(
            customer_id=validated['customer_id'],
            requester_type=validated['requester_type'],
            requester_id=validated['requester_id'],
            secondary_requester_id=validated['secondary_requester_id'],     # If None, default to Null in Schema

            payment_method=validated['payment_method'],
            payment_amount=validated['payment_amount'],
            status=validated['status'],                                     # If None, default to 1 in Schema

            psp_id=None,
            settle_date=None
        )
        
        self.db.add(tempPaymentInstance)
        self.db.commit()

        # If payment method is not cash, create Midtrans transaction
        # After that update the instance with the response from Midtrans
        if tempPaymentInstance.payment_method != PaymentMethodEnum.tunai:
            tempPaymentInstance.raw_response = self.createMidtransTransaction(tempPaymentInstance.id, tempPaymentInstance.payment_method, tempPaymentInstance.payment_amount)
            tempPaymentInstance.psp_id = tempPaymentInstance.raw_response.get('transaction_id')
            
            self.db.commit()
            
        return PaymentSchema().dump(tempPaymentInstance).data
    
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
            targetedPayment.settle_date = datetime.now()
            self.db.commit()
            
            # Update requester status
            self.update_requester_status(targetedPayment.requester_type, targetedPayment.requester_id, targetedPayment.secondary_requester_id, targetedPayment.status)
        
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
            targetedPayment.settle_date = datetime.now()
            self.db.commit()
            
            # Cancel Midtrans transaction if payment method is not cash
            if targetedPayment.payment_method != PaymentMethodEnum.tunai:
                self.cancelMidtransTransactionStatus(targetedPayment.psp_id)
            
            # Update requester status
            self.update_requester_status(targetedPayment.requester_type, targetedPayment.requester_id, targetedPayment.secondary_requester_id, targetedPayment.status)

            # Return status
            return "Success"
        
        except Exception as e:
            # Return status
            return "Failed"
    
    # TODO: Update requester status
    def update_requester_status(self, requester_type, requester_id, secondary_requester_id, status):
        # Status: 1 pending | 2 done | 3 cancelled  
        # 1 = RPC to Order | 2 to Reservation | 3  to Event
        
        # ORDER
        if requester_type == 1:
            # Call update API to order
            # self.order_rpc.update_order_status(requester_id, status)
            
            # DELIVERY 
            if secondary_requester_id is not None:
                # Call update API to delivery (if secondary_requester_id not null)
                status_text = {
                1: "Pending",
                2: "Completed",
                3: "Cancelled"
                }.get(status, "Unknown")
                
                self.delivery_rpc.update_delivery_status(secondary_requester_id, status_text)
            pass
        # RESERVATION   
        elif requester_type == 2:
            # Call update API to reservation
            pass
        # EVENT
        elif requester_type == 3:
            # Call update API to event
            pass

        return
        
# =================================================================================FUNGSI MIDTRANS=============================================================================== 

    def createMidtransTransaction(self, payment_id, payment_method, amount):
        # https://api.sandbox.midtrans.com/v2/charge
        url = self.midtransUrl + "/charge"

        auth = b64encode(f"{self.midtransServerKey}:".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }
        
        if payment_method == PaymentMethodEnum.bca_va:
            json_body = {
                "payment_type": "bank_transfer",
                "bank_transfer": {
                    "bank": "bca"
                },
                "transaction_details": {
                    "order_id": str(payment_id),
                    "gross_amount": amount
                }
            }
        # TODO: Replace with actual OVO phone number from member
        elif payment_method == PaymentMethodEnum.ovo:
            json_body = {
                "payment_type": payment_method.value,
                "transaction_details": {
                    "order_id": str(payment_id),
                    "gross_amount": amount
                },
                "ovo": {
                    "phone_number": "081234567890"          
                }
            }
        else:
            json_body = {
                "payment_type": payment_method.value,
                "transaction_details": {
                    "order_id": str(payment_id),
                    "gross_amount": amount
                }
            }
        return self.call_api("POST", url, headers=headers, json_body=json_body)
    
    def checkMidtransTransactionStatus(self, psp_id):
        # https://api.sandbox.midtrans.com/v2/{transaction_id}/cancel
        url = self.midtransUrl + "/" + psp_id + "/status"

        auth = b64encode(f"{self.midtransServerKey}:".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }

        return self.call_api("GET", url, headers=headers)
    
    def cancelMidtransTransactionStatus(self, psp_id):
        # https://api.sandbox.midtrans.com/v2/{transaction_id}/cancel
        url = self.midtransUrl + "/" + str(psp_id) + "/cancel"

        auth = b64encode(f"{self.midtransServerKey}:".encode()).decode()
        
        headers = {
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/json"
        }

        return self.call_api("POST", url, headers=headers)
    
    def call_api(self, method, url, headers=None, params=None, json_body=None, timeout=10):
        try:
            response = requests.request(
                method=method.upper(),
                url=url,
                headers=headers,
                params=params,
                json=json_body,
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "status_code": getattr(e.response, 'status_code', None)}

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
