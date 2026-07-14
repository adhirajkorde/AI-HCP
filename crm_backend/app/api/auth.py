from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from crm_backend.app.core.db import get_db
from crm_backend.app.services.crm_services import AuthService
from crm_backend.app.schemas.crm_schemas import UserCreate, UserLogin, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return AuthService.register_user(db, user)

@router.post("/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # Map OAuth2 form data to schema
    credentials = UserLogin(username=form_data.username, password=form_data.password)
    return AuthService.login_for_access_token(db, credentials)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: UserResponse = Depends(AuthService.get_current_user)):
    return current_user
