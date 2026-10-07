from sqlalchemy import update
from sqlalchemy.orm import Session

from models.cart import Cart
from models.cart_item import CartItem


def get_by_user_id(db: Session, user_id: int):
    return db.query(Cart).filter(Cart.user_id == user_id).first()


def create(db: Session, user_id: int):
    cart = Cart(user_id=user_id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


def get_item(db: Session, cart_id: int, item_id: int):
    return (
        db.query(CartItem)
        .filter(CartItem.id == item_id, CartItem.cart_id == cart_id)
        .first()
    )


def get_item_by_product(db: Session, cart_id: int, product_id: int):
    return (
        db.query(CartItem)
        .filter(CartItem.cart_id == cart_id, CartItem.product_id == product_id)
        .first()
    )


def add_item(db: Session, cart_id: int, product_id: int, quantity: int):
    item = CartItem(cart_id=cart_id, product_id=product_id, quantity=quantity)
    db.add(item)
    db.commit()
    db.refresh(item)
    return item


def increment_item_quantity(db: Session, item_id: int, delta: int, max_quantity: int) -> bool:
    result = db.execute(
        update(CartItem)
        .where(CartItem.id == item_id, CartItem.quantity + delta <= max_quantity)
        .values(quantity=CartItem.quantity + delta)
    )
    db.commit()
    return result.rowcount == 1


def update_item_quantity(db: Session, item: CartItem, quantity: int):
    item.quantity = quantity
    db.commit()
    db.refresh(item)
    return item


def delete_item(db: Session, item: CartItem):
    db.delete(item)
    db.commit()


def clear(db: Session, cart: Cart):
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete(synchronize_session=False)
    db.commit()
