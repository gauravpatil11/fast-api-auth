from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.config import settings
from src.controllers.exceptions import ForbiddenError, ServiceUnavailableError, UnauthorizedError
from src.models.database import get_db_session
from src.models.db_models import User
from src.models.schemas import TokenData
from src.models.user_crud import get_user_by_username


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


def get_db() -> Session:
    yield from get_db_session()


def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        username = payload.get("sub")
        if username is None:
            raise UnauthorizedError("Could not validate credentials")
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise UnauthorizedError("Could not validate credentials") from exc

    try:
        user = get_user_by_username(db, token_data.username)
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to load authenticated user") from exc
    if user is None:
        raise UnauthorizedError("Could not validate credentials")
    if not user.is_active:
        raise ForbiddenError("Inactive user account")
    return user


def get_current_admin(current_user: User = Depends(get_current_user)) -> User:
    if not current_user.is_admin:
        raise ForbiddenError("Admin access required")
    return current_user
