from sqlalchemy.orm import Session

from core.database.db import SessionLocal
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

def get_lesson_by_id(db: Session, _id: int):
    return db.query(LessonModel).filter(LessonModel.id == _id).first()

def get_courses(db: Session):
    return db.query(CourseModel).all()

def get_course_by_id(db: Session, _id: int):
    return db.query(CourseModel).filter(CourseModel.id == _id).first()

def get_resource_by_title(db: Session, title):
    return db.query(ResourceModel).filter(ResourceModel.title == title).first()

def get_resources_by_level(db: Session, level):
    return db.query(ResourceModel).filter(ResourceModel.difficulty.is_(level)).all()

def get_users(db: Session):
    return db.query(UserModel).all()

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

def set_role_for_user(db: Session, user_id, role) -> UserRead:
    db_user = db.query(UserModel).filter(UserModel.id == user_id).first()
    db_user.role = role
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_username(db: Session, username: str) -> UserRead:
    return db.query(UserModel).filter(UserModel.username == username).first()

def create_test(db: Session, test: TestCreate):
    new_test = TestModel(
        title=test.title,
        description=test.description,
        max_score=test.max_score,
        course_id=test.course_id
    )
    db.add(new_test)
    db.commit()
    db.refresh(new_test)

    # додаємо питання та варіанти
    for q in test.questions:
        question = QuestionModel(text=q.text, test_id=new_test.id)
        db.add(question)
        db.commit()
        db.refresh(question)

        for opt in q.options:
            option = AnswerOptionModel(
                text=opt.text,
                is_correct=opt.is_correct,
                question_id=question.id
            )
            db.add(option)
        db.commit()

    # повертаємо кількість питань
    return TestRead(
        id=new_test.id,
        title=new_test.title,
        description=new_test.description,
        max_score=new_test.max_score,
        course_id=new_test.course_id,
        questions_count=len(new_test.questions)
    )

def get_test_by_id(db: Session, _id: int):
    return db.query(TestModel).filter(TestModel.id == _id).first()

def get_test_for_student_by_id(db: Session, _id: int):
    test = db.query(TestModel).filter(TestModel.id == _id).first()

    questions = []
    for q in test.questions:
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

def save_test_result(db: Session, test: TestModel, subm: TestSubmission):
    score = 0
    for ans in subm.answers:
        option = db.query(AnswerOptionModel).filter(
            AnswerOptionModel.id == ans.selected_option_id,
            AnswerOptionModel.question_id == ans.question_id
        ).first()
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
    db.commit()
    db.refresh(result)

    return result
