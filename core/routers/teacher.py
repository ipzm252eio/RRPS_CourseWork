from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from core.utils.auth import get_teacher_user
from core.schemas import (
    LessonRead, LessonCreate, ResourceCreate,
    CourseRead, CourseCreate, TestRead,
    TestCreate
)
from core.database import LessonModel, ResourceModel, db_func
from core.patterns import (
    StatisticsManager,
    Lesson,
    CodeExampleFactory,
    QuizFactory,
    CourseBuilder,
    CodeExample,
    Quiz)


router = APIRouter(prefix='/teacher', dependencies=[Depends(get_teacher_user)], tags=['Teacher'])

@router.post('/lesson/', response_model=LessonRead)
async def create_lesson(
        lesson: LessonCreate,
        request: Request,
        db: AsyncSession = Depends(db_func.get_db),
):
    """
    Створити урок і додати його в реєстр та SQLite
    """
    stats: StatisticsManager = request.app.state.stats
    lesson = LessonModel(**lesson.dict())
    await db_func.add_to_db(db, lesson)
    await stats.increment_lessons()
    return LessonRead(id=lesson.id, title=lesson.title, difficulty=lesson.difficulty, content=lesson.content)

@router.post('/lesson/title/{title}/clone')
async def clone_lesson(
        title: str,
        new_title: str,
        request: Request,
        db: AsyncSession = Depends(db_func.get_db),
):
    """
    Клонувати урок (патерн Прототип) і зберегти копію в SQLite
    """
    stats: StatisticsManager = request.app.state.stats
    lesson = db_func.get_lesson_by_title(db, title)
    if lesson:
        new_lesson = Lesson(new_title, lesson.difficulty, lesson.content).clone()
        await db_func.add_to_db(db, new_lesson)
        await stats.increment_clones()
        return {'status': 'cloned',
                'lesson': {
                    'title': new_title,
                    'difficulty': new_lesson.difficulty,
                    'content': new_lesson.content
                    }
                }
    return {'error': 'Lesson not found'}

@router.post('/resource/')
async def create_resource(
        resource: ResourceCreate,
        request: Request,
        db: AsyncSession = Depends(db_func.get_db),
):
    """
    Створити ресурс використовуючи фабричний метод
    """
    stats: StatisticsManager = request.app.state.stats
    if resource.type == "CodeExample":
        factory = CodeExampleFactory()
        created = await factory.create(db, resource)
        await stats.increment_resources()
    elif resource.type == "Quiz":
        factory = QuizFactory()
        created = await factory.create(db, resource)
        await stats.increment_resources()
    else:
        raise {"error": "Unsupported resource type"}
    return await db_func.get_resource_by_title(db, created.title)

@router.post('/course/', response_model=CourseRead)
async def create_course(
        course: CourseCreate,
        request: Request,
        db: AsyncSession = Depends(db_func.get_db),
):
    """
    Побудувати та зберегти курс через Builder
    """
    builder = CourseBuilder(course.title, db)
    stats: StatisticsManager = request.app.state.stats

    resources = await db_func.get_resources_by_ids(db, course.resources)
    for r in resources:
        if r.type == 'CodeExample':
            builder.add_resource(CodeExample(r.title, r.difficulty, r.code, r.description))
        elif r.type == 'Quiz':
            builder.add_resource(Quiz(r.title, r.difficulty, r.question, r.answer))

    db_course = await builder.build_and_save()
    await stats.increment_courses()
    return db_course

@router.post('/test', response_model=TestRead)
async def create_test(
        test: TestCreate,
        db: AsyncSession = Depends(db_func.get_db)
):
    return await db_func.create_test(db, test)
