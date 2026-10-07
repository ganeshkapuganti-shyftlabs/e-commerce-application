from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth import get_current_user
from database import get_db
from models.user import User
from schemas.auth import LoginRequest, Token
from schemas.user import UserResponse
from services import auth_service


router = APIRouter(prefix="/api/v1/auth", tags=["Auth"])


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return auth_service.login(db, credentials.email, credentials.password)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)):
    return current_user
