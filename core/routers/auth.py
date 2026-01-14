from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from core.database import db_func, UserModel
from core.schemas import UserRead, Token, UserCreate
from core.utils.auth import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES


router = APIRouter(prefix='/auth', tags=['Auth'])

@router.post('/register', response_model=UserRead)
def register(user: UserCreate, db: Session = Depends(db_func.get_db)):
    """
    Реєстрація користувача
    """
    hashed_pw = get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post('/login', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(db_func.get_db)):
    """
    Авторизація користувача
    """
    user = db.query(UserModel).filter(UserModel.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail='Incorrect username or password')
    access_token = create_access_token(data={'sub': user.username}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {'access_token': access_token, 'token_type': 'bearer'}
