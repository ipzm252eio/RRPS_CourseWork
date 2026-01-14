from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from core.database.db import Base, engine

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
        backref="courses"
    )

class StatisticsModel(Base):
    __tablename__ = "statistics"
    id = Column(Integer, primary_key=True, default=1)
    lessons_created = Column(Integer, default=0)
    resources_created = Column(Integer, default=0)
    courses_built = Column(Integer, default=0)
    lessons_cloned = Column(Integer, default=0)
    users = Column(Integer, default=0)


Base.metadata.create_all(bind=engine)
