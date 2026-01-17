from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.orm import Session
from core.database import db_func

SECRET_KEY = 'supersecretkey'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def get_default_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_func.get_db)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = db_func.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')
    return user

def get_teacher_user(token: str = Depends(oauth2_scheme), db: Session = Depends(db_func.get_db)):
    user = get_default_user(token, db)
    if user.role != 'teacher':
        raise HTTPException(status_code=401, detail='Access denied')
    return user