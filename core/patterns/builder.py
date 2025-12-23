from core.database.models import CourseModel, ResourceModel
from sqlalchemy.orm import Session

class CourseBuilder:
    def __init__(self, title: str, db: Session):
        self.title = title
        self.resources = []
        self.db = db

    def add_resource(self, resource):
        self.resources.append(resource)
        return self

    def build_and_save(self):
        # створюємо курс у БД
        db_course = CourseModel(title=self.title)
        self.db.add(db_course)
        self.db.commit()
        self.db.refresh(db_course)

        # прив’язуємо ресурси
        for r in self.resources:
            db_resource = self.db.query(ResourceModel).filter(ResourceModel.title == r.title).first()
            if db_resource:
                db_course.resources.append(db_resource)

        self.db.commit()
        self.db.refresh(db_course)

        return db_course
