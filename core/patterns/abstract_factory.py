from core.patterns.factory_method import CodeExample, Quiz

class AbstractLearningFactory:
    def create_example(self): pass
    def create_quiz(self): pass

class BeginnerFactory(AbstractLearningFactory):
    def create_example(self):
        return CodeExample('Hello World', 'beginner', "print('Hello, Python!')", 'Базовий приклад')
    def create_quiz(self):
        return Quiz('Exponentiation', 'beginner', 'Що виведе print(2**3)?', '8')

class AdvancedFactory(AbstractLearningFactory):
    def create_example(self):
        return CodeExample('List Comprehension', 'advanced', '[x**2 for x in range(5)]', 'Складніший приклад')
    def create_quiz(self):
        return Quiz('Decorators', 'advanced', 'Що таке @staticmethod?', 'Декоратор для методів класу')

