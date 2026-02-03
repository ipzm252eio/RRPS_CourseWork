from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.database.db import async_session_maker
from core.database.models import StatisticsModel


class StatisticsManager:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    @classmethod
    async def init(cls):
        """Ініціалізація менеджера статистики (singleton)."""
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if not stats:
                stats = StatisticsModel(id=1)
                session.add(stats)
                await session.commit()
                await session.refresh(stats)

        instance = cls()
        # Завантажуємо модель без прив'язки до сесії
        await instance._reload_model()
        return instance

    async def _reload_model(self):
        """Перезавантажити дані моделі з бази."""
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                # Зберігаємо дані, а не об'єкт моделі
                self._model = {
                    'lessons_created': stats.lessons_created,
                    'resources_created': stats.resources_created,
                    'courses_built': stats.courses_built,
                    'lessons_cloned': stats.lessons_cloned,
                    'users': stats.users
                }

    async def increment_lessons(self):
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                stats.lessons_created += 1
                await session.commit()
        await self._reload_model()

    async def increment_resources(self):
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                stats.resources_created += 1
                await session.commit()
        await self._reload_model()

    async def increment_courses(self):
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                stats.courses_built += 1
                await session.commit()
        await self._reload_model()

    async def increment_clones(self):
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                stats.lessons_cloned += 1
                await session.commit()
        await self._reload_model()

    async def increment_users(self):
        async with async_session_maker() as session:
            result = await session.execute(select(StatisticsModel).filter(StatisticsModel.id == 1))
            stats = result.scalars().first()
            if stats:
                stats.users += 1
                await session.commit()
        await self._reload_model()

    async def report(self):
        """Отримати актуальну статистику."""
        await self._reload_model()
        return {
            'lessons_created': self._model['lessons_created'],
            'resources_created': self._model['resources_created'],
            'courses_built': self._model['courses_built'],
            'lessons_cloned': self._model['lessons_cloned'],
            'registered_users': self._model['users']
        }
