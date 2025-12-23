import copy

class PrototypeMixin:
    def clone(self):
        return copy.deepcopy(self)

class Lesson(PrototypeMixin):
    def __init__(self, title, difficulty, content):
        self.title = title
        self.difficulty = difficulty
        self.content = content
