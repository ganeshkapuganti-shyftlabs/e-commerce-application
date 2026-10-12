from sqlalchemy.orm import Session

from models.order_items import OrderItem


def get_by_id(db: Session, order_item_id: int):
    return db.query(OrderItem).filter(OrderItem.id == order_item_id).first()


def get_multi(db: Session,limit: int,offset: int,order_id: int | None = None,product_id: int | None = None,):
    query = db.query(OrderItem)
    if order_id is not None:
        query = query.filter(OrderItem.order_id == order_id)
    if product_id is not None:
        query = query.filter(OrderItem.product_id == product_id)
    total = query.count()
    items = query.order_by(OrderItem.id).offset(offset).limit(limit).all()
    return total, items


def create(db: Session, order_id: int, product_id: int, quantity: int, unit_price: float, commit: bool = True):
    item = OrderItem(order_id=order_id,product_id=product_id,quantity=quantity,unit_price=unit_price,)
    db.add(item)
    if commit:
        db.commit()
        db.refresh(item)
    else:
        db.flush()
    return item

def delete(db: Session, item: OrderItem):
    db.delete(item)
    db.commit()
