from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from schemas.user import UserCreate, UserPatch, UserResponse, UserListResponse
from services import user_service


router = APIRouter(prefix="/api/v1/users", tags=["Users"])


@router.post("", response_model=UserResponse, status_code=201)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    return user_service.create_user(db, user)


@router.get("", dependencies=[Depends(get_current_user)], response_model=UserListResponse)
def get_users(
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    return user_service.list_users(db, limit, offset)


@router.get("/{user_id}", dependencies=[Depends(get_current_user)], response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    return user_service.get_user(db, user_id)


@router.put("/{user_id}", dependencies=[Depends(get_current_user)], response_model=UserResponse)
def update_user(user_id: int, user_data: UserCreate, db: Session = Depends(get_db)):
    return user_service.update_user(db, user_id, user_data)


@router.patch("/{user_id}", dependencies=[Depends(get_current_user)], response_model=UserResponse)
def patch_user(user_id: int, user_data: UserPatch, db: Session = Depends(get_db)):
    return user_service.patch_user(db, user_id, user_data)


@router.delete("/{user_id}", dependencies=[Depends(get_current_user)], status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_service.delete_user(db, user_id)
    return None
