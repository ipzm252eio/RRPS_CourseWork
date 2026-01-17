from fastapi import APIRouter, Depends, HTTPException
from core.database import db_func
from core.database.models import TestResultModel
from core.patterns import (
    AdvancedFactory,
    BeginnerFactory
)
from core.schemas import ResourceRead, LessonRead, CourseRead, TestReadForStudent, TestSubmission, TestResultResponse
from core.utils.auth import get_default_user
from sqlalchemy.orm import Session
from typing import List

router = APIRouter(prefix='/learn', dependencies=[Depends(get_default_user)], tags=['Learn'])


@router.get('/lesson/id/{lesson_id}')
def get_lesson(lesson_id: int, db: Session = Depends(db_func.get_db)):
    """
    Отримати урок з бази SQLite за ID
    """
    lesson = db_func.get_lesson_by_id(db, lesson_id)
    if lesson:
        return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)
    return {'error': 'Lesson not found'}

@router.get('/lesson/title/{title}')
def get_lesson(title: str, db: Session = Depends(db_func.get_db)):
    """
    Отримати урок з бази SQLite за назвою
    """
    lesson = db_func.get_lesson_by_title(db, title)
    if lesson:
        return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)
    return {'error': 'Lesson not found'}

@router.get('/resource/{level}', response_model=List[ResourceRead])
def get_resources(level: str, db: Session = Depends(db_func.get_db)):
    """
    Отримати ресурси за рівнем
    """
    return db_func.get_resources_by_level(db, level)

@router.get('/courses/', response_model=List[CourseRead])
def list_courses(db: Session = Depends(db_func.get_db)):
    """
    Повертає всі курси з їхніми ресурсами
    """
    return db_func.get_courses(db)

@router.get('/course/{course_id}/test/{test_id}', response_model=TestReadForStudent)
def get_test_from_course_by_id(course_id: int, test_id: int, db: Session = Depends(db_func.get_db)):
    course = db_func.get_course_by_id(db, course_id)
    if not course:
        raise HTTPException(status_code=404, detail='Course not found')
    test = db_func.get_test_by_id(db, test_id)
    if not test:
        raise HTTPException(status_code=404, detail='Test not found')
    return db_func.get_test_for_student_by_id(db, test_id)

@router.post('/course/test/submit', response_model=TestResultResponse)
def submit_test(submission: TestSubmission, db: Session = Depends(db_func.get_db)):
    test = db_func.get_test_by_id(db, submission.test_id)
    if not test:
        raise HTTPException(status_code=404, detail='Test not found')
    return db_func.save_test_result(db, test, submission)

@router.get('/example/{type}/{level}')
def get_example(example_type: str, level: str):
    """
    Отримати приклад ресурс за його типом (Quiz/CodeExample) та рівнем складності (beginner/advanced). Ендпоінт використовує патерн Абстрактної фабрики
    """
    if level == 'beginner':
        beginner = BeginnerFactory()
        if example_type == 'Quiz':
            return beginner.create_quiz()
        elif example_type == 'CodeExample':
            return beginner.create_example()
        else:
            raise {"error": "Unsupported example type"}
    elif level == 'advanced':
        advanced = AdvancedFactory()
        if example_type == 'Quiz':
            return advanced.create_quiz()
        elif example_type == 'CodeExample':
            return advanced.create_example()
        else:
            raise {"error": "Unsupported example type"}
    else:
        raise {"error": "Unsupported example level"}

