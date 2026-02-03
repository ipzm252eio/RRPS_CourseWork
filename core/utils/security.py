from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def verify_password(plain, hashed):
    """
    Перевірка пароля проти хешу

    Args:
        plain_password: Пароль у відкритому вигляді
        hashed_password: Bcrypt хеш пароля

    Returns:
        bool: True якщо пароль співпадає

    Note:
        Async для консистентності API, хоча bcrypt синхронний
    """
    return pwd_context.verify(plain, hashed)

async def get_password_hash(password):
    """
    Створення bcrypt хешу пароля

    Args:
        password: Пароль у відкритому вигляді

    Returns:
        str: Bcrypt хеш

    Note:
        Використовує автоматичне salt generation
    """
    return pwd_context.hash(password)