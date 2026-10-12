from datetime import datetime, timezone
from decimal import Decimal
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from crud import cart as cart_crud
from crud import order as order_crud
from crud import order_items as order_items_crud
from crud import payment as payment_crud
from crud import product as product_crud
from models.enums import OrderStatus, PaymentStatus
from models.order import Order
from models.payment import Payment
from models.user import User
from schemas.checkout import CheckoutRequest, PaymentConfirm

CENT = Decimal("0.01")


def _to_response(order: Order) -> dict:
    return {
        "order": order,
        "items": order.items,
        "payment": max(order.payments, key=lambda p: p.id),
    }


def checkout(db: Session, user: User, data: CheckoutRequest, idempotency_key: str | None) -> tuple[dict, bool]:
    """Turn the user's cart into an order, its items and a pending payment in one transaction.

    Returns (response, created). created is False when the idempotency key was already used.
    """
    try:
        # locking the cart makes two checkouts by the same user run one after the other
        cart = cart_crud.get_by_user_id_for_update(db, user.id)

        if idempotency_key is not None:
            existing = order_crud.get_by_idempotency_key(db, user.id, idempotency_key)
            if existing is not None:
                db.rollback()
                return _to_response(existing), False

        if cart is None or not cart.items:
            raise HTTPException(status_code=400, detail="Cart is empty")

        cart_items = list(cart.items)
        products = {p.id: p for p in product_crud.get_many_for_update(db, [i.product_id for i in cart_items])}

        problems = []
        for item in cart_items:
            product = products.get(item.product_id)
            if product is None:
                problems.append({"product_id": item.product_id, "detail": "Product no longer exists"})
            elif item.quantity > product.stock_quantity:
                problems.append({
                    "product_id": product.id,
                    "detail": f"Only {product.stock_quantity} unit(s) of '{product.name}' in stock",
                })
        if problems:
            raise HTTPException(status_code=409, detail=problems)

        total = sum(
            (Decimal(products[i.product_id].price) * i.quantity for i in cart_items), Decimal("0")
        ).quantize(CENT)

        order = order_crud.create(
            db, user.id, OrderStatus.pending, float(total), idempotency_key, commit=False
        )
        for item in cart_items:
            product = products[item.product_id]
            # price is copied so later price changes don't rewrite the order
            order_items_crud.create(db, order.id, product.id, item.quantity, product.price, commit=False)
            product.stock_quantity -= item.quantity

        payment_crud.create(
            db, order.id, total, data.payment_method, PaymentStatus.pending, None, commit=False
        )
        cart_crud.delete_items(db, cart.id, [i.id for i in cart_items])

        db.commit()
    except IntegrityError:
        # same idempotency key committed by a parallel request
        db.rollback()
        existing = idempotency_key and order_crud.get_by_idempotency_key(db, user.id, idempotency_key)
        if not existing:
            raise
        return _to_response(existing), False
    except Exception:
        db.rollback()
        raise

    db.refresh(order)
    return _to_response(order), True


def _lock_own_pending_payment(db: Session, user: User, payment_id: int) -> tuple[Payment, Order]:
    payment = payment_crud.get_by_id(db, payment_id)
    if payment is None or payment.order.user_id != user.id:
        raise HTTPException(status_code=404, detail="Payment not found")

    # order first, then payment: the same lock order everywhere avoids deadlocks
    order = order_crud.get_by_id_for_update(db, payment.order_id)
    payment = payment_crud.get_by_id_for_update(db, payment_id)

    if payment.status != PaymentStatus.pending:
        raise HTTPException(status_code=409, detail=f"Payment is already {payment.status.value}")
    if order.status != OrderStatus.pending:
        raise HTTPException(status_code=409, detail=f"Order is already {order.status.value}")
    return payment, order


def confirm_payment(db: Session, user: User, payment_id: int, data: PaymentConfirm) -> Payment:
    try:
        payment, order = _lock_own_pending_payment(db, user, payment_id)

        payment.status = PaymentStatus.completed
        payment.paid_at = datetime.now(timezone.utc)
        payment.transaction_id = data.transaction_id or f"txn_{uuid4().hex}"
        order.status = OrderStatus.paid
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Transaction ID already exists")
    except Exception:
        db.rollback()
        raise

    db.refresh(payment)
    return payment


def fail_payment(db: Session, user: User, payment_id: int) -> Payment:
    try:
        payment, order = _lock_own_pending_payment(db, user, payment_id)

        payment.status = PaymentStatus.failed
        order.status = OrderStatus.cancelled

        # give the reserved stock back
        quantities = {}
        for item in order.items:
            quantities[item.product_id] = quantities.get(item.product_id, 0) + item.quantity
        for product in product_crud.get_many_for_update(db, list(quantities)):
            product.stock_quantity += quantities[product.id]

        db.commit()
    except Exception:
        db.rollback()
        raise

    db.refresh(payment)
    return payment
