from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from core.database.models import CourseModel, ResourceModel


class CourseBuilder:
    def __init__(self, title: str, db: AsyncSession):
        self.title = title
        self.resources = []
        self.db = db

    def add_resource(self, resource):
        """Додаємо ресурс у список для курсу"""
        self.resources.append(resource)
        return self

    async def build_and_save(self):
        """Створюємо курс у БД та прив’язуємо ресурси"""
        db_course = CourseModel(title=self.title)
        self.db.add(db_course)
        await self.db.commit()
        await self.db.refresh(db_course)

        # Прив’язуємо ресурси
        for r in self.resources:
            result = await self.db.execute(
                select(ResourceModel).filter(ResourceModel.title == r.title)
            )
            db_resource = result.scalars().first()
            if db_resource:
                db_course.resources.append(db_resource)

        await self.db.commit()
        await self.db.refresh(db_course)

        return db_course