from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import db_func
from core.schemas import UserRead, Token, UserCreate
from core.utils.auth import create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from core.utils.security import verify_password


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register', response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(db_func.get_db)):
    """
    Реєстрація користувача
    """
    return db_func.add_user(db, user)

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_func.get_db)):
    """
    Авторизація користувача
    """
    user = db_func.get_user_by_username(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    access_token = create_access_token(data={'sub': user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': access_token, 'token_type': 'bearer'}
