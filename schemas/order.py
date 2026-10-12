from pydantic import BaseModel, ConfigDict, Field

from models.enums import OrderStatus
from schemas.order_items import OrderItemResponse

class OrderCreate(BaseModel):
    # user comes from the token; price, total and status are set by the server
    product_id: int
    quantity: int = Field(default=1, ge=1)


class OrderStatusUpdate(BaseModel):
    status: OrderStatus


class OrderResponse(BaseModel):
    id: int
    user_id: int
    status: OrderStatus
    total_amount: float

    model_config = ConfigDict(from_attributes=True)


class OrderDetailResponse(OrderResponse):
    items: list[OrderItemResponse]


class OrderListResponse(BaseModel):
    total: int
    limit: int
    offset: int
    items: list[OrderResponse]