from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import order as order_crud
from crud import order_items as order_items_crud
from crud import product as product_crud
from models.enums import OrderStatus
from models.order import Order
from models.user import User
from schemas.order import OrderCreate, OrderStatusUpdate

CENT = Decimal("0.01")


def create_order(db: Session, user: User, data: OrderCreate) -> Order:
    """Order a single product: create the order and its item and reserve stock in one transaction."""
    try:
        products = product_crud.get_many_for_update(db, [data.product_id])
        if not products:
            raise HTTPException(status_code=404, detail="Product not found")
        product = products[0]
        if data.quantity > product.stock_quantity:
            raise HTTPException(
                status_code=409,
                detail=f"Only {product.stock_quantity} unit(s) of '{product.name}' in stock",
            )

        total = (Decimal(product.price) * data.quantity).quantize(CENT)
        order = order_crud.create(db, user.id, OrderStatus.pending, float(total), commit=False)
        order_items_crud.create(db, order.id, product.id, data.quantity, product.price, commit=False)
        product.stock_quantity -= data.quantity

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return order


def list_orders(db: Session,limit: int,offset: int,user_id: int,status: str):
    total, items = order_crud.get_multi(db, limit, offset, user_id, status)
    return {"total": total, "limit": limit, "offset": offset, "items": items}

def get_order(db: Session, order_id: int):
    order = order_crud.get_by_id(db, order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return order

def update_order_status(db: Session, order_id: int, data: OrderStatusUpdate):
    order = get_order(db, order_id)
    return order_crud.update_status(db, order, data.status)
