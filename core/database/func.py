from sqlalchemy.orm import Session

from core.database.db import SessionLocal
from core.database.models import LessonModel, CourseModel, ResourceModel

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

def add_course(db: Session, course):
    db_course = CourseModel(title=course.title)
    db.add(db_course)
    db.commit()
    db.refresh(db_course)

    resources = db.query(ResourceModel).filter(ResourceModel.id.in_(course.resources)).all()
    db_course.resources.extend(resources)
    db.commit()
    db.refresh(db_course)

    return db_course

def get_courses(db: Session):
    return db.query(CourseModel).all()

def get_resourse_by_title(db: Session, title):
    return db.query(ResourceModel).filter(ResourceModel.title == title).first()

def get_resourses_by_level(db: Session, level):
    return db.query(ResourceModel).filter(ResourceModel.difficulty.is_(level)).all()
