class StatisticsManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.lesson_count = 0
            cls._instance.resource_count = 0
            cls._instance.course_count = 0
            cls._instance.clone_count = 0
        return cls._instance

    def increment_lessons(self):
        self.lesson_count += 1

    def increment_resources(self):
        self.resource_count += 1

    def increment_courses(self):
        self.course_count += 1

    def increment_clones(self):
        self.clone_count += 1

    def report(self):
        return {
            "lessons_created": self.lesson_count,
            "resources_created": self.resource_count,
            "courses_built": self.course_count,
            "lessons_cloned": self.clone_count
        }

stats = StatisticsManager()

