from fastapi import HTTPException
from sqlalchemy.orm import Session

from crud import order as order_crud
from crud import order_items as order_items_crud
from crud import product as product_crud
from models.order_items import OrderItem
from schemas.order_items import OrderItemCreate


def create_order_item(db: Session, item: OrderItemCreate) -> OrderItem:
    if order_crud.get_by_id(db, item.order_id) is None:
        raise HTTPException(status_code=404, detail="Order not found")

    if product_crud.get_by_id(db, item.product_id) is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return order_items_crud.create(
        db, item.order_id, item.product_id, item.quantity, item.unit_price
    )


def list_order_items(
    db: Session,
    limit: int,
    offset: int,
    order_id: int | None = None,
    product_id: int | None = None,
) -> dict:
    total, items = order_items_crud.get_multi(db, limit, offset, order_id, product_id)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_order_item(db: Session, order_item_id: int) -> OrderItem:
    item = order_items_crud.get_by_id(db, order_item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Order item not found")
    return item


def delete_order_item(db: Session, order_item_id: int) -> None:
    item = get_order_item(db, order_item_id)
    order_items_crud.delete(db, item)
