from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from core.utils.auth import get_admin_user
from core.database import db_func
from core.schemas import UserRead


router = APIRouter(prefix='/admin', dependencies=[Depends(get_admin_user)], tags=['Admin'])


@router.get('/users', response_model=List[UserRead])
async def get_all_users(db: AsyncSession = Depends(db_func.get_db)):
    return await db_func.get_users(db)

@router.patch('/user/{user_id}/set_as_teacher', response_model=UserRead)
async def set_teacher(user_id: int, db: AsyncSession = Depends(db_func.get_db)):
    return await db_func.set_role_for_user(db, user_id, 'teacher')