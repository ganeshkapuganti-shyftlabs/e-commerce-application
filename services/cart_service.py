from decimal import Decimal

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import cart as cart_crud
from crud import product as product_crud
from models.cart import Cart
from models.user import User
from schemas.cart import CartItemCreate, CartItemUpdate

CENT = Decimal("0.01")


def _to_response(cart: Cart | None) -> dict:
    if cart is None:
        return {"id": None, "items": [], "total_items": 0, "subtotal": 0.0}

    items = []
    subtotal = Decimal("0")
    total_items = 0
    for item in cart.items:
        unit_price = Decimal(item.product.price)
        line_total = (unit_price * item.quantity).quantize(CENT)
        subtotal += line_total
        total_items += item.quantity
        items.append({
            "id": item.id,
            "product_id": item.product_id,
            "product_name": item.product.name,
            "unit_price": unit_price,
            "quantity": item.quantity,
            "line_total": line_total,
        })
    return {
        "id": cart.id,
        "items": items,
        "total_items": total_items,
        "subtotal": subtotal.quantize(CENT),
    }


def _get_or_create_cart(db: Session, user: User) -> Cart:
    cart = cart_crud.get_by_user_id(db, user.id)
    if cart is None:
        try:
            cart = cart_crud.create(db, user.id)
        except IntegrityError:
            db.rollback()
            cart = cart_crud.get_by_user_id(db, user.id)
    return cart


def _get_cart_or_404(db: Session, user: User) -> Cart:
    cart = cart_crud.get_by_user_id(db, user.id)
    if cart is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    return cart


def _stock_error(product) -> HTTPException:
    return HTTPException(
        status_code=400,
        detail=f"Only {product.stock_quantity} unit(s) of '{product.name}' in stock",
    )


def _check_stock(product, quantity: int) -> None:
    if quantity > product.stock_quantity:
        raise _stock_error(product)


def _increase_quantity(db: Session, item, product, quantity: int) -> None:
    # atomic in SQL so simultaneous adds can't overwrite each other
    if not cart_crud.increment_item_quantity(db, item.id, quantity, product.stock_quantity):
        raise _stock_error(product)


def get_cart(db: Session, user: User) -> dict:
    return _to_response(cart_crud.get_by_user_id(db, user.id))


def add_item(db: Session, user: User, data: CartItemCreate) -> dict:
    product = product_crud.get_by_id(db, data.product_id)
    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    cart = _get_or_create_cart(db, user)
    existing = cart_crud.get_item_by_product(db, cart.id, product.id)

    if existing is not None:
        _increase_quantity(db, existing, product, data.quantity)
    else:
        _check_stock(product, data.quantity)
        try:
            cart_crud.add_item(db, cart.id, product.id, data.quantity)
        except IntegrityError:
            # another request added the same product at the same moment
            db.rollback()
            existing = cart_crud.get_item_by_product(db, cart.id, product.id)
            _increase_quantity(db, existing, product, data.quantity)

    db.refresh(cart)
    return _to_response(cart)


def update_item(db: Session, user: User, item_id: int, data: CartItemUpdate) -> dict:
    cart = _get_cart_or_404(db, user)
    item = cart_crud.get_item(db, cart.id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")

    _check_stock(item.product, data.quantity)
    cart_crud.update_item_quantity(db, item, data.quantity)
    db.refresh(cart)
    return _to_response(cart)


def remove_item(db: Session, user: User, item_id: int) -> None:
    cart = _get_cart_or_404(db, user)
    item = cart_crud.get_item(db, cart.id, item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Cart item not found")
    cart_crud.delete_item(db, item)


def clear_cart(db: Session, user: User) -> None:
    cart = cart_crud.get_by_user_id(db, user.id)
    if cart is not None:
        cart_crud.clear(db, cart)
