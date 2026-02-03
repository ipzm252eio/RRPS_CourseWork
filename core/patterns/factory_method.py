from sqlalchemy.ext.asyncio import AsyncSession
from core.schemas import ResourceCreate
from core.database.models import ResourceModel


class Resource:
    def show(self):
        raise NotImplementedError


class CodeExample(Resource):
    def __init__(self, title, difficulty, code, description):
        self.title = title
        self.difficulty = difficulty
        self.code = code
        self.description = description

    def show(self):
        return {
            'type': 'CodeExample',
            'title': self.title,
            'difficulty': self.difficulty,
            'description': self.description,
            'code': self.code
        }


class Quiz(Resource):
    def __init__(self, title, difficulty, question, answer):
        self.title = title
        self.difficulty = difficulty
        self.question = question
        self.answer = answer

    def show(self):
        return {
            'type': 'Quiz',
            'title': self.title,
            'difficulty': self.difficulty,
            'question': self.question,
            'answer': self.answer
        }


class ResourceFactory:
    async def create(self, db: AsyncSession, resource_data: ResourceCreate) -> Resource:
        raise NotImplementedError


class CodeExampleFactory(ResourceFactory):
    async def create(self, db: AsyncSession, resource_data: ResourceCreate) -> CodeExample:
        # створюємо Python-об’єкт
        example = CodeExample(
            resource_data.title,
            resource_data.difficulty,
            resource_data.code,
            resource_data.description
        )
        # записуємо в БД
        db_resource = ResourceModel(
            type="CodeExample",
            title=resource_data.title,
            difficulty=resource_data.difficulty,
            description=resource_data.description,
            code=resource_data.code
        )
        db.add(db_resource)
        await db.commit()
        await db.refresh(db_resource)
        return example


class QuizFactory(ResourceFactory):
    async def create(self, db: AsyncSession, resource_data: ResourceCreate) -> Quiz:
        quiz = Quiz(
            resource_data.title,
            resource_data.difficulty,
            resource_data.question,
            resource_data.answer
        )
        db_resource = ResourceModel(
            type="Quiz",
            title=resource_data.title,
            difficulty=resource_data.difficulty,
            question=resource_data.question,
            answer=resource_data.answer
        )
        db.add(db_resource)
        await db.commit()
        await db.refresh(db_resource)
        return quiz