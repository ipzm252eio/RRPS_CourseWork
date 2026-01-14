from pydantic import BaseModel
from typing import List, Optional


class UserCreate(BaseModel):
    username: str
    password: str

class UserRead(BaseModel):
    id: int
    username: str
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
