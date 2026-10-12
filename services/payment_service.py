from fastapi import HTTPException
from sqlalchemy.orm import Session
from crud import order as order_crud
from crud import payment as payment_crud
from models.payment import Payment
from schemas.payment import PaymentCreate


def create_payment(db: Session, payment: PaymentCreate):
    if order_crud.get_by_id(db, payment.order_id) is None:
        raise HTTPException(status_code=404, detail="Order not found")
    if payment.transaction_id is not None:
        if payment_crud.get_by_transaction_id(db, payment.transaction_id):
            raise HTTPException(status_code=400, detail="Transaction ID already exists")
    return payment_crud.create(
        db,
        payment.order_id,
        payment.amount,
        payment.payment_method,
        payment.status,
        payment.transaction_id,
    )


def list_payments(db: Session, limit: int, offset: int, order_id: int | None = None):
    total, items = payment_crud.get_multi(db, limit, offset, order_id)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_payment(db: Session, payment_id: int) -> Payment:
    payment = payment_crud.get_by_id(db, payment_id)
    if payment is None:
        raise HTTPException(status_code=404, detail="Payment not found")
    return payment
