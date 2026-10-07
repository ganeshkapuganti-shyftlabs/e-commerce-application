from fastapi import HTTPException
from sqlalchemy.orm import Session
from auth import hash_password
from crud import user as user_crud
from models.user import User
from schemas.user import UserCreate, UserPatch


def create_user(db: Session, user: UserCreate) -> User:
    if user_crud.get_by_email(db, user.email):
        raise HTTPException(status_code=400, detail="Email already exists")

    return user_crud.create(db, user.name, user.email, hash_password(user.password))


def list_users(db: Session, limit: int, offset: int):
    total, items = user_crud.get_multi(db, limit, offset)
    return {"total": total, "limit": limit, "offset": offset, "items": items}


def get_user(db: Session, user_id: int) -> User:
    user = user_crud.get_by_id(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


def update_user(db: Session, user_id: int, data: UserCreate) -> User:
    user = get_user(db, user_id)
    return user_crud.update(db, user, data.name, data.email, hash_password(data.password))


def patch_user(db: Session, user_id: int, data: UserPatch) -> User:
    user = get_user(db, user_id)

    return user_crud.update(
        db,
        user,
        name=data.name if data.name is not None else user.name,
        email=data.email if data.email is not None else user.email,
        password_hash=hash_password(data.password) if data.password is not None else user.password_hash,
    )


def delete_user(db: Session, user_id: int):
    user = get_user(db, user_id)
    user_crud.delete(db, user)
