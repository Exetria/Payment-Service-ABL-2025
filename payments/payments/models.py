import datetime
import enum

from sqlalchemy import (
    Column, Integer, String, Enum, Float, DateTime
)
from sqlalchemy.ext.declarative import declarative_base


class Base(object):
    created_at = Column(
        DateTime,
        default=datetime.datetime.now,
        nullable=False
    )
    updated_at = Column(
        DateTime,
        default=datetime.datetime.now,
        onupdate=datetime.datetime.now,
        nullable=False
    )


DeclarativeBase = declarative_base(cls=Base)

# Python enum for payment_method
class PaymentMethodEnum(enum.Enum):
    tunai = "tunai"
    bca_va = "bca va"
    qris = "qris"
    gopay = "gopay"
    ovo = "ovo"

class Payment(DeclarativeBase):
    __tablename__ = "payment"

    id                       = Column(Integer, primary_key=True, autoincrement=True)
    
    customer_id              = Column(Integer, nullable=False)
    requester_type           = Column(Integer, nullable=False)
    requester_id             = Column(Integer, nullable=False)
    secondary_requester_id   = Column(Integer)
    
    payment_method           = Column(Enum(PaymentMethodEnum, name="payment_method_enum"), nullable=False)
    payment_amount           = Column(Float, nullable=False)
    status                   = Column(Integer, default=1, nullable=False)
    
    psp_id                   = Column(String)
    signature_key            = Column(String)
    
    settle_date              = Column(DateTime, nullable=True)

