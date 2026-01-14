from core.database.db import SessionLocal
from core.database import StatisticsModel


class StatisticsManager:
    _instance = None

    def __new__(cls, db=None):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.db = db or SessionLocal()
            stats = cls._instance.db.query(StatisticsModel).get(1)
            if not stats:
                stats = StatisticsModel()
                cls._instance.db.add(stats)
                cls._instance.db.commit()
            cls._instance.model = stats
        return cls._instance

    def increment_lessons(self):
        self.model.lessons_created += 1
        self.db.commit()

    def increment_resources(self):
        self.model.resources_created += 1
        self.db.commit()

    def increment_courses(self):
        self.model.courses_built += 1
        self.db.commit()

    def increment_clones(self):
        self.model.lessons_cloned += 1
        self.db.commit()

    def increment_users(self):
        self.model.users += 1
        self.db.commit()

    def report(self):
        return {
            'lessons_created': self.model.lessons_created,
            'resources_created': self.model.resources_created,
            'courses_built': self.model.courses_built,
            'lessons_cloned': self.model.lessons_cloned,
            'registered_users': self.model.users
        }


stats = StatisticsManager()