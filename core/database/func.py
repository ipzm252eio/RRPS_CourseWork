from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload
from core.database.db import async_session_maker
from core.database.models import (
    LessonModel, CourseModel, ResourceModel,
    UserModel, TestModel, QuestionModel,
    AnswerOptionModel, TestResultModel
)
from core.schemas import (
    UserCreate, UserRead, TestCreate, TestRead,
    TestReadForStudent, AnswerOptionReadForStudent, QuestionRead,
    TestSubmission
)
from core.utils.security import get_password_hash


async def get_db() -> AsyncSession:
    async with async_session_maker() as session:
        yield session


async def add_to_db(db: AsyncSession, obj):
    db.add(obj)
    await db.commit()
    await db.refresh(obj)


async def get_lesson_by_title(db: AsyncSession, title: str):
    result = await db.execute(select(LessonModel).filter(LessonModel.title == title))
    return result.scalars().first()


async def get_lesson_by_id(db: AsyncSession, _id: int):
    result = await db.execute(select(LessonModel).filter(LessonModel.id == _id))
    return result.scalars().first()


async def get_courses(db: AsyncSession):
    result = await db.execute(
        select(CourseModel).options(selectinload(CourseModel.resources))
    )
    return result.scalars().all()

async def get_course_by_id(db: AsyncSession, _id: int):
    result = await db.execute(
        select(CourseModel)
        .options(selectinload(CourseModel.resources))
        .filter(CourseModel.id == _id)
    )
    return result.scalars().first()


async def save_course(db: AsyncSession, course: CourseModel):
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def get_resources_by_ids(db: AsyncSession, ids: list[int]):
    result = await db.execute(
        select(ResourceModel).filter(ResourceModel.id.in_(ids))
    )
    return result.scalars().all()


async def get_resource_by_title(db: AsyncSession, title: str):
    result = await db.execute(select(ResourceModel).filter(ResourceModel.title == title))
    return result.scalars().first()


async def get_resources_by_level(db: AsyncSession, level: str):
    result = await db.execute(select(ResourceModel).filter(ResourceModel.difficulty == level))
    return result.scalars().all()


async def get_users(db: AsyncSession):
    result = await db.execute(select(UserModel))
    return result.scalars().all()


async def add_user(db: AsyncSession, user: UserCreate) -> UserRead:
    hashed_pw = await get_password_hash(user.password)
    db_user = UserModel(username=user.username, hashed_password=hashed_pw)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return UserRead(
        id=db_user.id,
        username=db_user.username,
        role='student'
    )


async def set_role_for_user(db: AsyncSession, user_id: int, role: str) -> UserRead:
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    db_user = result.scalars().first()
    db_user.role = role
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str) -> UserRead:
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    return result.scalars().first()


async def create_test(db: AsyncSession, test: TestCreate):
    new_test = TestModel(
        title=test.title,
        description=test.description,
        max_score=test.max_score,
        course_id=test.course_id
    )
    db.add(new_test)
    await db.commit()
    await db.refresh(new_test)

    for q in test.questions:
        question = QuestionModel(text=q.text, test_id=new_test.id)
        db.add(question)
        await db.commit()
        await db.refresh(question)

        for opt in q.options:
            option = AnswerOptionModel(
                text=opt.text,
                is_correct=opt.is_correct,
                question_id=question.id
            )
            db.add(option)
        await db.commit()

    questions_count = len(test.questions)

    return TestRead(
        id=new_test.id,
        title=new_test.title,
        description=new_test.description,
        max_score=new_test.max_score,
        course_id=new_test.course_id,
        questions_count=questions_count
    )


async def get_test_by_id(db: AsyncSession, _id: int):
    result = await db.execute(
        select(TestModel)
        .options(selectinload(TestModel.questions).selectinload(QuestionModel.options))
        .filter(TestModel.id == _id)
    )
    return result.scalars().first()

async def get_test_for_student_by_id(db: AsyncSession, _id: int):
    result = await db.execute(
        select(TestModel)
        .options(selectinload(TestModel.questions).selectinload(QuestionModel.options))
        .filter(TestModel.id == _id)
    )
    test = result.scalars().first()

    questions = []
    for q in test.questions:  # тепер вони вже завантажені
        options = [AnswerOptionReadForStudent(id=o.id, text=o.text) for o in q.options]
        questions.append(QuestionRead(id=q.id, text=q.text, options=options))

    return TestReadForStudent(
        id=test.id,
        title=test.title,
        description=test.description,
        max_score=test.max_score,
        course_id=test.course_id,
        questions_count=len(test.questions),
        questions=questions
    )


async def save_test_result(db: AsyncSession, test: TestModel, subm: TestSubmission):
    result = await db.execute(
        select(TestModel)
        .options(selectinload(TestModel.questions))
        .filter(TestModel.id == test.id)
    )
    test = result.scalars().first()

    score = 0
    for ans in subm.answers:
        result = await db.execute(
            select(AnswerOptionModel).filter(
                AnswerOptionModel.id == ans.selected_option_id,
                AnswerOptionModel.question_id == ans.question_id
            )
        )
        option = result.scalars().first()
        if option and option.is_correct:
            score += 1

    max_score = test.max_score
    total_questions = len(test.questions)
    final_score = float(score / total_questions * max_score)

    result = TestResultModel(
        user_id=subm.user_id,
        test_id=subm.test_id,
        score=f'{final_score:.2f}'
    )
    db.add(result)
    await db.commit()
    await db.refresh(result)

    return result
