from pydantic import BaseModel
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
    role: str
    class Config:
        orm_mode = True

class Token(BaseModel):
    access_token: str
    token_type: str

class LessonCreate(BaseModel):
    title: str
    difficulty: str
    content: str

class LessonRead(LessonCreate):
    id: int
    class Config:
        orm_mode = True

class ResourceCreate(BaseModel):
    type: str
    title: str
    difficulty: str
    description: Optional[str] = None
    code: Optional[str] = None
    question: Optional[str] = None
    answer: Optional[str] = None

class ResourceRead(ResourceCreate):
    id: int
    class Config:
        orm_mode = True

class CourseCreate(BaseModel):
    title: str
    resources: List[int]

class CourseRead(BaseModel):
    id: int
    title: str
    resources: List[ResourceRead]
    class Config:
        orm_mode = True

class AnswerOption(BaseModel):
    text: str

class AnswerOptionReadForStudent(AnswerOption):
    id: int

class AnswerOptionCreate(AnswerOption):
    is_correct: bool

class Question(BaseModel):
    text: str

class QuestionCreate(Question):
    options: List[AnswerOptionCreate]

class QuestionRead(Question):
    id: int
    options: List[AnswerOptionReadForStudent]

class TestCreate(BaseModel):
    title: str
    description: str | None = None
    max_score: int
    course_id: int
    questions: List[QuestionCreate]

class TestRead(BaseModel):
    id: int
    title: str
    description: str | None
    max_score: int
    course_id: int
    questions_count: int

    class Config:
        orm_mode = True

class UserAnswer(BaseModel):
    question_id: int
    selected_option_id: int

class TestSubmission(BaseModel):
    test_id: int
    user_id: int
    answers: List[UserAnswer]

class TestReadForStudent(TestRead):
    questions: List[QuestionRead]

class TestResultResponse(BaseModel):
    test_id: int
    user_id: int
    score: float