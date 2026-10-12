from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from authh import get_current_user
from database import get_db
from models.user import User
from schemas.checkout import PaymentConfirm
from schemas.payment import PaymentCreate, PaymentResponse, PaymentListResponse
from services import checkout_service, payment_service


router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])


@router.post("", response_model=PaymentResponse, status_code=201)
def create_payment(payment: PaymentCreate, db: Session = Depends(get_db)):
    return payment_service.create_payment(db, payment)


@router.get("", response_model=PaymentListResponse)
def get_payments(
    order_id: int | None = None,
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return payment_service.list_payments(db, limit, offset, order_id)


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(payment_id: int, db: Session = Depends(get_db)):
    return payment_service.get_payment(db, payment_id)


@router.post("/{payment_id}/confirm", response_model=PaymentResponse)
def confirm_payment(
    payment_id: int,
    data: PaymentConfirm,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return checkout_service.confirm_payment(db, current_user, payment_id, data)


@router.post("/{payment_id}/fail", response_model=PaymentResponse)
def fail_payment(payment_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return checkout_service.fail_payment(db, current_user, payment_id)
