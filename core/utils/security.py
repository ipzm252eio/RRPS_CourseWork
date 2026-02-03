from passlib.context import CryptContext

pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')

async def verify_password(plain, hashed):
    return pwd_context.verify(plain, hashed)

async def get_password_hash(password):
    return pwd_context.hash(password)