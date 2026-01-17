from sqlalchemy.orm import Session

from core.database.db import SessionLocal
from core.database.models import LessonModel, CourseModel, ResourceModel, UserModel
from core.schemas import UserCreate, UserRead
from core.utils.security import get_password_hash


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def add_to_db(db: Session, obj):
    db.add(obj)
    db.commit()
    db.refresh(obj)

def get_lesson_by_title(db: Session, title):
    return db.query(LessonModel).filter(LessonModel.title == title).first()

def get_lesson_by_id(db: Session, _id):
    return db.query(LessonModel).filter(LessonModel.id == _id).first()

def get_courses(db: Session):
    return db.query(CourseModel).all()

def get_resource_by_title(db: Session, title):
    return db.query(ResourceModel).filter(ResourceModel.title == title).first()

def get_resources_by_level(db: Session, level):
    return db.query(ResourceModel).filter(ResourceModel.difficulty.is_(level)).all()

def add_user(db: Session, user: UserCreate) -> UserRead:
    hashed_pw = get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return UserRead(
        id=db_user.id,
        username=db_user.username,
        role='student'
    )

def get_user_by_username(db: Session, username: str) -> UserRead:
    return db.query(UserModel).filter(UserModel.username == username).first()