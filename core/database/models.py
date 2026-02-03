from sqlalchemy import Column, Integer, String, Table, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from core.database.db import Base

course_resources = Table(
    "course_resources",
    Base.metadata,
    Column("course_id", Integer, ForeignKey("courses.id")),
    Column("resource_id", Integer, ForeignKey("resources.id"))
)


class UserModel(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    role = Column(String, default='student')
    hashed_password = Column(String)


class LessonModel(Base):
    __tablename__ = 'lessons'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True, index=True)
    difficulty = Column(String)
    content = Column(String)


class ResourceModel(Base):
    __tablename__ = 'resources'
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String)
    title = Column(String)
    difficulty = Column(String)
    description = Column(String)
    code = Column(String, nullable=True)
    question = Column(String, nullable=True)
    answer = Column(String, nullable=True)


class CourseModel(Base):
    __tablename__ = 'courses'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, unique=True)
    resources = relationship(
        "ResourceModel",
        secondary=course_resources,
        backref="courses",
        lazy="selectin"
    )


class StatisticsModel(Base):
    __tablename__ = 'statistics'
    id = Column(Integer, primary_key=True, default=1)
    lessons_created = Column(Integer, default=0)
    resources_created = Column(Integer, default=0)
    courses_built = Column(Integer, default=0)
    lessons_cloned = Column(Integer, default=0)
    users = Column(Integer, default=0)


class TestModel(Base):
    __tablename__ = 'tests'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    max_score = Column(Integer, default=100)
    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship(
        'CourseModel',
        backref='tests',
        lazy="selectin")


class QuestionModel(Base):
    __tablename__ = 'questions'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    test_id = Column(Integer, ForeignKey('tests.id'))
    test = relationship(
        'TestModel',
        backref='questions',
        lazy="selectin")


class AnswerOptionModel(Base):
    __tablename__ = 'answer_options'
    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
    is_correct = Column(Boolean, default=False)
    question_id = Column(Integer, ForeignKey('questions.id'))
    question = relationship(
        'QuestionModel',
        backref='options',
        lazy="selectin")


class TestResultModel(Base):
    __tablename__ = 'test_results'
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    test_id = Column(Integer, ForeignKey('tests.id'))
    score = Column(Integer)
    test = relationship(
        'TestModel',
        backref='results',
        lazy="selectin")