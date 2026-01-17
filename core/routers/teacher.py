from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from core.utils.auth import get_teacher_user
from core.schemas import (
    LessonRead, LessonCreate, ResourceCreate,
    CourseRead, CourseCreate, TestRead,
    TestCreate
)
from core.database import LessonModel, ResourceModel, db_func
from core.patterns import (
    stats,
    Lesson,
    CodeExampleFactory,
    QuizFactory,
    CourseBuilder,
    CodeExample,
    Quiz)


router = APIRouter(prefix='/teacher', dependencies=[Depends(get_teacher_user)], tags=['Teacher'])

@router.post('/lesson/', response_model=LessonRead)
def create_lesson(lesson: LessonCreate, db: Session = Depends(db_func.get_db)):
    """
    Створити урок і додати його в реєстр та SQLite
    """
    lesson = LessonModel(**lesson.dict())
    db_func.add_to_db(db, lesson)
    stats.increment_lessons()
    return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)

@router.post('/lesson/title/{title}/clone')
def clone_lesson(title: str, new_title: str, db: Session = Depends(db_func.get_db)):
    """
    Клонувати урок (патерн Прототип) і зберегти копію в SQLite
    """
    lesson = db_func.get_lesson_by_title(db, title)
    if lesson:
        new_lesson = Lesson(new_title, lesson.difficulty, lesson.content).clone()
        db_func.add_to_db(db, new_lesson)
        stats.increment_clones()
        return {'status': 'cloned', 'lesson': {'title': new_title, 'difficulty': new_lesson.difficulty, 'content': new_lesson.content}}
    return {'error': 'Lesson not found'}

@router.post('/resource/')
def create_resource(resource: ResourceCreate, db: Session = Depends(db_func.get_db)):
    """
    Створити ресурс використовуючи фабричний метод
    """
    if resource.type == "CodeExample":
        factory = CodeExampleFactory()
        created = factory.create(db, resource)
        stats.increment_resources()
    elif resource.type == "Quiz":
        factory = QuizFactory()
        created = factory.create(db, resource)
        stats.increment_resources()
    else:
        raise {"error": "Unsupported resource type"}
    return db_func.get_resource_by_title(db, created.title)

@router.post('/course/', response_model=CourseRead)
def create_course(course: CourseCreate, db: Session = Depends(db_func.get_db)):
    """
    Побудувати та зберігаємо в БД курс через Builder
    """
    builder = CourseBuilder(course.title, db)

    resources = db.query(ResourceModel).filter(ResourceModel.id.in_(course.resources)).all()
    for r in resources:
        if r.type == 'CodeExample':
            builder.add_resource(CodeExample(r.title, r.difficulty, r.code, r.description))
        elif r.type == 'Quiz':
            builder.add_resource(Quiz(r.title, r.difficulty, r.question, r.answer))

    db_course = builder.build_and_save()
    stats.increment_courses()
    return db_course

@router.post('/test', response_model=TestRead)
def create_test(test: TestCreate, db: Session = Depends(db_func.get_db)):
    return db_func.create_test(db, test)
