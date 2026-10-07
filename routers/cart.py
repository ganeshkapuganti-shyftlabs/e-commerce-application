from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.user import User
from schemas.cart import CartItemCreate, CartItemUpdate, CartResponse
from services import cart_service


router = APIRouter(prefix="/api/v1/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
def get_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return cart_service.get_cart(db, current_user)


@router.post("/items", response_model=CartResponse)
def add_item(item: CartItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return cart_service.add_item(db, current_user, item)


@router.patch("/items/{item_id}", response_model=CartResponse)
def update_item(
    item_id: int,
    data: CartItemUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return cart_service.update_item(db, current_user, item_id, data)


@router.delete("/items/{item_id}", status_code=204)
def remove_item(item_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.remove_item(db, current_user, item_id)
    return None


@router.delete("", status_code=204)
def clear_cart(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    cart_service.clear_cart(db, current_user)
    return None
