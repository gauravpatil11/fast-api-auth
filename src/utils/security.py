import hashlib
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext

from src.config import settings


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def verify_legacy_password(plain_password: str, hashed_password: str) -> bool:
    legacy_password = hashlib.sha256(plain_password.encode()).hexdigest()
    return pwd_context.verify(legacy_password, hashed_password)


def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.access_token_expire_minutes)
    )
    to_encode = data.copy()
    to_encode.update({"exp": expire})
    return jwt.encode(
        to_encode,
        settings.jwt_secret_key,
        algorithm=settings.jwt_algorithm,
    )
