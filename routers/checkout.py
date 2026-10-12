from fastapi import APIRouter, Depends, Header, Response
from sqlalchemy.orm import Session

from authh import get_current_user
from database import get_db
from models.user import User
from schemas.checkout import CheckoutRequest, CheckoutResponse
from services import checkout_service


router = APIRouter(prefix="/api/v1/checkout", tags=["Checkout"])


@router.post("", response_model=CheckoutResponse, status_code=201)
def checkout(
    data: CheckoutRequest,
    response: Response,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key", max_length=64),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result, created = checkout_service.checkout(db, current_user, data, idempotency_key)
    if not created:
        response.status_code = 200
    return result
