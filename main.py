from fastapi import FastAPI, Depends
from core.database import LessonModel, ResourceModel, db_func
from core.patterns import (
    stats,
    Lesson,
    CodeExampleFactory,
    QuizFactory, Quiz,
    CodeExample,
    CourseBuilder,
    AdvancedFactory,
    BeginnerFactory
)
from core.schemas import ResourceRead, LessonRead, LessonCreate, ResourceCreate, CourseRead, CourseCreate
from sqlalchemy.orm import Session
from typing import List

app = FastAPI(title='Python Learning API with Patterns')


@app.post('/lesson/', response_model=LessonRead)
def create_lesson(lesson: LessonCreate, db: Session = Depends(db_func.get_db)):
    """
    Створити урок і додати його в реєстр та SQLite
    """
    lesson = LessonModel(**lesson.dict())
    db_func.add_to_db(db, lesson)
    stats.increment_lessons()
    return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)

@app.get('/lesson/id/{lesson_id}')
def get_lesson(lesson_id: int, db: Session = Depends(db_func.get_db)):
    """
    Отримати урок з бази SQLite за ID
    """
    lesson = db_func.get_lesson_by_id(db, lesson_id)
    if lesson:
        return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)
    return {'error': 'Lesson not found'}

@app.get('/lesson/title/{title}')
def get_lesson(title: str, db: Session = Depends(db_func.get_db)):
    """
    Отримати урок з бази SQLite за назвою
    """
    lesson = db_func.get_lesson_by_title(db, title)
    if lesson:
        return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)
    return {'error': 'Lesson not found'}


@app.post('/lesson/title/{title}/clone')
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

@app.post('/resource/')
def create_resource(resource: ResourceCreate, db: Session = Depends(db_func.get_db)):
    """
    Створити ресурс використовуючи фабричний метод
    """
    if resource.type == "CodeExample":
        factory = CodeExampleFactory()
        created = factory.create(db, resource)
    elif resource.type == "Quiz":
        factory = QuizFactory()
        created = factory.create(db, resource)
    else:
        raise {"error": "Unsupported resource type"}
    return db_func.get_resourse_by_title(db, created.title)


@app.get('/resource/{level}', response_model=List[ResourceRead])
def get_resources(level: str, db: Session = Depends(db_func.get_db)):
    """
    Отримати ресурси за рівнем
    """
    return db_func.get_resourses_by_level(db, level)


@app.post('/course/', response_model=CourseRead)
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
    return db_course


@app.get('/courses/', response_model=List[CourseRead])
def list_courses(db: Session = Depends(db_func.get_db)):
    """
    Повертає всі курси з їхніми ресурсами
    """
    return db_func.get_courses(db)

@app.get('/example/{type}/{level}')
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




