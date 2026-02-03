from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from core.database import db_func

SECRET_KEY = 'supersecretkey'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='auth/login')


async def create_access_token(data: dict, expires_delta: timedelta | None = None):
    """
    Створення JWT access токену

    Args:
        data: Дані для кодування (зазвичай {'sub': username})
        expires_delta: Час життя токену

    Returns:
        str: Закодований JWT токен
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_default_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_func.get_db)):
    """
    Dependency: перевірка токену та отримання користувача

    Доступно для: всіх авторизованих користувачів (будь-яка роль)

    Args:
        token: JWT токен з Authorization header
        db: Async сесія БД

    Returns:
        UserModel: Об'єкт користувача

    Raises:
        HTTPException 401: Якщо токен невалідний або користувач не знайдений
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise HTTPException(status_code=401, detail='Invalid token')
    except JWTError:
        raise HTTPException(status_code=401, detail='Invalid token')
    user = await db_func.get_user_by_username(db, username)
    if user is None:
        raise HTTPException(status_code=401, detail='User not found')
    return user

async def get_teacher_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_func.get_db)):
    """
    Dependency: доступ тільки для teacher та admin

    Args:
        token: JWT токен
        db: Async сесія БД

    Returns:
        UserModel: Об'єкт користувача з роллю teacher або admin

    Raises:
        HTTPException 403: Якщо користувач не має прав доступу
    """
    user = await get_default_user(token, db)
    if user.role == 'student':
        raise HTTPException(status_code=401, detail='Access denied')
    return user

async def get_admin_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(db_func.get_db)):
    """
    Dependency: доступ тільки для admin

    Raises:
        HTTPException 403: Якщо користувач не admin
    """
    user = await get_default_user(token, db)
    if user.role != 'admin':
        raise HTTPException(status_code=401, detail='Access denied')
    return user