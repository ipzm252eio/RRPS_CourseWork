from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

# Використовуємо асинхронний драйвер для SQLite
DATABASE_URL = "sqlite+aiosqlite:///./learning.db"

# Створюємо асинхронний engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    future=True
)

# Асинхронний sessionmaker
async_session_maker = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
    autoflush=False,
    autocommit=False
)

# Базовий клас для моделей
Base = declarative_base()