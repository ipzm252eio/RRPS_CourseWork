# Курсова робота, на базі [RRPS04](https://github.com/ipzm252eio/Patterns2025) Ейсмонт Ігор ІПЗм-25-2

---

Навчальний проєкт на **FastAPI + SQLite**, який демонструє використання класичних патернів проєктування (**Singleton, Factory Method, Prototype, Builder, Abstract Factory**) у контексті REST API.

---

## Можливості
- **Уроки (Lessons)**  
  - Створення уроків та збереження у SQLite  
  - Отримання уроків за `id` або `title`  
  - Клонування уроків (патерн **Prototype**)  
  - Глобальна статистика (патерн **Singleton**)  

- **Ресурси (Resources)**  
  - Створення ресурсів через **Factory Method** (`CodeExample`, `Quiz`)  
  - Отримання ресурсів за рівнем складності  

- **Курси (Courses)**  
  - Побудова курсу з ресурсів через **Builder**  
  - Збереження курсу у SQLite  
  - Перегляд усіх курсів з їхніми ресурсами  

- **Приклади (Examples)**  
  - Отримання прикладів ресурсів (`Quiz`, `CodeExample`) за рівнем складності (`beginner`, `advanced`)  
  - Використання патерну **Abstract Factory** для генерації сімейств об’єктів  

---

## Використані технології
- FastAPI — сучасний Python веб‑фреймворк
- SQLAlchemy — ORM для роботи з SQLite
- Pydantic — валідація даних
- SQLite — проста база даних для навчальних цілей

---

## Структура проєкту
```
project/
│── core/
│   │── database/
│   │   ├── models.py    # Моделі SQLAlchemy 
│   │   ├── func.py      # Функції роботи з БД
│   │   ├── db.py        # Ініціалізація БД
│   │── patterns/        # Реалізація патернів (Singleton, Factory, Builder, Prototype, Abstract Factory)
│   ├── schemas.py       # Pydantic-схеми для валідації
│── main.py              # Основний файл FastAPI з ендпоінтами
```

---

## Основні ендпоінти

### Уроки
- `POST /lesson/` — створити урок  
- `GET /lesson/id/{lesson_id}` — отримати урок за ID  
- `GET /lesson/title/{title}` — отримати урок за назвою  
- `POST /lesson/title/{title}/clone?new_title=...` — клонувати урок (**Prototype**)  

### Ресурси
- `POST /resource/` — створити ресурс через Factory Method  
  ```json
  {
    "type": "CodeExample",
    "title": "Hello World",
    "difficulty": "beginner",
    "description": "Test example",
    "code": "print('Hello World!')"
  }
  ```
- `GET /resource/{level}` — отримати ресурси за рівнем  

### Курси
- `POST /course/` — створити курс через Builder  
  ```json
  {
    "title": "Beginner Python Course",
    "resources": [1, 2, 3]   // список ID ресурсів
  }
  ```
- `GET /courses/` — отримати всі курси з ресурсами  

### Приклади (Abstract Factory)
- `GET /example/{type}/{level}` — отримати приклад ресурсу за типом (`Quiz` або `CodeExample`) та рівнем (`beginner` або `advanced`)  

---

## Запуск проєкту

1. Клонувати репозиторій:
   ```bash
   git clone <repo_url>
   cd project
   ```

2. Встановити залежності:
   ```bash
   pip install -r requirements.txt
   ```

3. Запустити сервер:
   ```bash
   uvicorn main:app --reload
   ```

4. Відкрити документацію Swagger:
   ```
   http://127.0.0.1:8000/docs
   ```

---

## Патерни у проєкті
- **Singleton** — глобальний менеджер статистики (`stats`)  
- **Factory Method** — створення ресурсів (`CodeExampleFactory`, `QuizFactory`)  
- **Prototype** — клонування уроків  
- **Builder** — побудова курсів із ресурсів  
- **Abstract Factory** — генерація прикладів залежно від рівня (`BeginnerFactory`, `AdvancedFactory`)  
