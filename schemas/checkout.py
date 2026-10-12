from pydantic import BaseModel, Field

from schemas.order import OrderResponse
from schemas.order_items import OrderItemResponse
from schemas.payment import PaymentResponse


class CheckoutRequest(BaseModel):
    payment_method: str = Field(min_length=1, max_length=30)


class CheckoutResponse(BaseModel):
    order: OrderResponse
    items: list[OrderItemResponse]
    payment: PaymentResponse


class PaymentConfirm(BaseModel):
    transaction_id: str | None = Field(default=None, max_length=255)
