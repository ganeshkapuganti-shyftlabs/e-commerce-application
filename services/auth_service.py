from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from auth import create_access_token, verify_password
from crud import user as user_crud


def login(db: Session, email: str, password: str) -> dict:
    user = user_crud.get_by_email(db, email)
    if user is None or not verify_password(password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return {"access_token": create_access_token(user.id), "token_type": "bearer"}
