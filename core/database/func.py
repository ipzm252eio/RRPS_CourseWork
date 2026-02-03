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
    """
    FastAPI dependency для отримання асинхронної сесії БД.

    Yields:
        AsyncSession: Асинхронна сесія бази даних

    Note:
        Сесія автоматично закривається після завершення запиту
        завдяки контекстному менеджеру async with
    """
    async with async_session_maker() as session:
        yield session


async def add_to_db(db: AsyncSession, obj):
    """
    Базова функція для додавання об'єкта до бази даних.

    Виконує стандартний цикл збереження об'єкта: додавання до сесії,
    commit транзакції та refresh для отримання згенерованих значень
    (наприклад, автоінкрементного ID).

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        obj: ORM об'єкт (модель SQLAlchemy) для збереження

    Returns:
        None: Функція змінює об'єкт in-place, додаючи йому ID та інші
              згенеровані БД значення

    Example:
        lesson = LessonModel(title="Python Basics", content="Introduction...")
        await add_to_db(db, lesson)
        # Тепер lesson.id містить згенерований ID

    Note:
        Після виконання функції об'єкт оновлюється даними з БД,
        включаючи автоматично згенеровані поля (ID, timestamps тощо)
    """
    db.add(obj)
    await db.commit()
    await db.refresh(obj)


async def get_lesson_by_title(db: AsyncSession, title: str):
    """
    Отримати урок за назвою.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        title (str): Назва уроку для пошуку

    Returns:
        LessonModel | None: Знайдений урок або None якщо не знайдено

    Example:
        lesson = await get_lesson_by_title(db, "Python Basics")
        if lesson:
            print(f"Found: {lesson.title}")
    """
    result = await db.execute(select(LessonModel).filter(LessonModel.title == title))
    return result.scalars().first()


async def get_lesson_by_id(db: AsyncSession, _id: int):
    """
    Отримати урок за унікальним ідентифікатором.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        _id (int): ID уроку

    Returns:
        LessonModel | None: Знайдений урок або None якщо не знайдено

    Example:
        lesson = await get_lesson_by_id(db, 1)
        if lesson:
            print(f"Lesson: {lesson.title}")
    """
    result = await db.execute(select(LessonModel).filter(LessonModel.id == _id))
    return result.scalars().first()


async def get_courses(db: AsyncSession):
    """
    Отримати всі курси з їх ресурсами.

    Note:
        Використання selectinload гарантує, що доступ до course.resources
        не викличе додаткових запитів до БД (вирішення N+1 проблеми)
    """
    result = await db.execute(
        select(CourseModel).options(selectinload(CourseModel.resources))
    )
    return result.scalars().all()

async def get_course_by_id(db: AsyncSession, _id: int):
    """
    Отримати курс за ID з його ресурсами.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        _id (int): ID курсу

    Returns:
        CourseModel | None: Знайдений курс з ресурсами або None

    Example:
        course = await get_course_by_id(db, 1)
        if course:
            print(f"Course has {len(course.resources)} resources")

    Note:
        Використовує eager loading для запобігання N+1 запитів
    """
    result = await db.execute(
        select(CourseModel)
        .options(selectinload(CourseModel.resources))
        .filter(CourseModel.id == _id)
    )
    return result.scalars().first()


async def save_course(db: AsyncSession, course: CourseModel):
    """
    Зберегти курс у базі даних.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        course (CourseModel): ORM об'єкт курсу для збереження

    Returns:
        CourseModel: Збережений курс з оновленими даними (включно з ID)

    Example:
        new_course = CourseModel(title="Python Course")
        saved = await save_course(db, new_course)
        print(f"Saved with ID: {saved.id}")
    """
    db.add(course)
    await db.commit()
    await db.refresh(course)
    return course


async def get_resources_by_ids(db: AsyncSession, ids: list[int]):
    """
    Отримати ресурси за списком ID.

    Ефективно завантажує кілька ресурсів одним запитом використовуючи
    оператор IN.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        ids (list[int]): Список ID ресурсів для отримання

    Returns:
        list[ResourceModel]: Список знайдених ресурсів

    Example:
        resources = await get_resources_by_ids(db, [1, 2, 3])
        print(f"Found {len(resources)} resources")

    Note:
        Якщо деякі ID не існують, вони просто не увійдуть до результату.
        Функція не викидає помилку для неіснуючих ID.
    """
    result = await db.execute(
        select(ResourceModel).filter(ResourceModel.id.in_(ids))
    )
    return result.scalars().all()


async def get_resource_by_title(db: AsyncSession, title: str):
    """
    Отримати ресурс за назвою.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        title (str): Назва ресурсу

    Returns:
        ResourceModel | None: Знайдений ресурс або None

    Example:
        resource = await get_resource_by_title(db, "Python Quiz")
    """
    result = await db.execute(select(ResourceModel).filter(ResourceModel.title == title))
    return result.scalars().first()


async def get_resources_by_level(db: AsyncSession, level: str):
    """
    Отримати всі ресурси певного рівня складності.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        level (str): Рівень складності ('beginner', 'intermediate', 'advanced')

    Returns:
        list[ResourceModel]: Список ресурсів заданого рівня

    Example:
        beginner_resources = await get_resources_by_level(db, 'beginner')
        print(f"Found {len(beginner_resources)} beginner resources")
    """
    result = await db.execute(select(ResourceModel).filter(ResourceModel.difficulty == level))
    return result.scalars().all()


async def get_users(db: AsyncSession):
    """
    Отримати всіх користувачів системи.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних

    Returns:
        list[UserModel]: Список всіх користувачів

    Example:
        users = await get_users(db)
        for user in users:
            print(f"{user.username} - {user.role}")

    Note:
        Використовуйте обережно на великих БД, краще додати пагінацію
    """
    result = await db.execute(select(UserModel))
    return result.scalars().all()


async def add_user(db: AsyncSession, user: UserCreate) -> UserRead:
    """
    Створити нового користувача з хешуванням пароля.

    Функція автоматично хешує пароль за допомогою bcrypt перед збереженням
    у базі даних. Plaintext пароль ніколи не зберігається.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        user (UserCreate): Pydantic схема з даними нового користувача

    Returns:
        UserRead: Створений користувач (без пароля!)

    Example:
        new_user = UserCreate(username="john", password="secret123")
        created = await add_user(db, new_user)
        print(f"Created user {created.username} with ID {created.id}")

    Security:
        - Пароль хешується через bcrypt з автоматичним salt
        - Plaintext пароль не зберігається в БД
        - У відповіді пароль не повертається
    """
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
    """
    Змінити роль користувача.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        user_id (int): ID користувача
        role (str): Нова роль ('student', 'teacher', 'admin')

    Returns:
        UserRead: Оновлений користувач

    Example:
        user = await set_role_for_user(db, user_id=1, role='teacher')
        print(f"User role updated to {user.role}")

    Raises:
        AttributeError: Якщо користувач з таким ID не існує
    """
    result = await db.execute(select(UserModel).filter(UserModel.id == user_id))
    db_user = result.scalars().first()
    db_user.role = role
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_user_by_username(db: AsyncSession, username: str) -> UserRead:
    """
    Отримати користувача за іменем користувача.

    Використовується для автентифікації та перевірки унікальності username.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        username (str): Ім'я користувача для пошуку

    Returns:
        UserModel | None: Знайдений користувач або None

    Example:
        user = await get_user_by_username(db, "john")
        if user:
            print(f"Found user with role: {user.role}")
        else:
            print("User not found")
    """
    result = await db.execute(select(UserModel).filter(UserModel.username == username))
    return result.scalars().first()


async def create_test(db: AsyncSession, test: TestCreate):
    """
    Створити новий тест з питаннями та варіантами відповідей.

    Функція створює тест та всі пов'язані об'єкти (питання, варіанти відповідей)
    в рамках кількох транзакцій для забезпечення цілісності даних.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        test (TestCreate): Pydantic схема з даними тесту, включно з питаннями

    Returns:
        TestRead: Створений тест з підрахованою кількістю питань

    Example:
        test_data = TestCreate(
            title="Python Quiz",
            course_id=1,
            questions=[
                QuestionCreate(
                    text="What is Python?",
                    options=[
                        OptionCreate(text="Language", is_correct=True),
                        OptionCreate(text="Snake", is_correct=False)
                    ]
                )
            ]
        )
        created = await create_test(db, test_data)
        print(f"Created test with {created.questions_count} questions")

    Note:
        Функція виконує кілька commit операцій для забезпечення правильного
        каскадного створення зв'язаних об'єктів з отриманням згенерованих ID.
    """
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
    """
    Отримати тест за ID з усіма питаннями та варіантами відповідей.

    Використовує вкладений eager loading для ефективного завантаження
    всієї структури тесту за мінімальну кількість запитів.

    Args:
        db (AsyncSession): Асинхронна сесія бази даних
        _id (int): ID тесту

    Returns:
        TestModel | None: Тест з питаннями та варіантами або None

    Example:
        test = await get_test_by_id(db, 1)
        if test:
            for question in test.questions:
                print(f"{question.text}: {len(question.options)} options")

    Note:
        Використовує nested selectinload для завантаження:
        Test → Questions → AnswerOptions
        Це запобігає N+1 проблемі при доступі до вкладених зв'язків
    """
    result = await db.execute(
        select(TestModel)
        .options(selectinload(TestModel.questions).selectinload(QuestionModel.options))
        .filter(TestModel.id == _id)
    )
    return result.scalars().first()

async def get_test_for_student_by_id(db: AsyncSession, _id: int):
    """
    Отримати тест для проходження студентом (БЕЗ правильних відповідей).

    Security:
        КРИТИЧНО: Правильні відповіді НЕ включаються в response для студента.
        Поле is_correct доступне тільки на backend при перевірці результатів.
    """
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
    """
    Зберегти результат проходження тесту та підрахувати бал.

    Algorithm:
        score = (correct_answers / total_questions) * max_score

        Приклад: якщо max_score=100, total_questions=10, correct=7
        --> score = (7/10) * 100 = 70.00
    """
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
