from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.controllers.exceptions import ForbiddenError, ServiceUnavailableError, UnauthorizedError
from src.models.database import get_db_session
from src.models.db_models import User
from src.models.user_crud import get_user_by_id
from src.utils.security import decode_access_token


bearer_scheme = HTTPBearer(auto_error=False)


def get_db() -> Session:
    yield from get_db_session()


def get_current_user(
    db: Session = Depends(get_db),
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> User:
    if credentials is None or not credentials.credentials:
        raise UnauthorizedError("Could not validate credentials")

    token_data = decode_access_token(credentials.credentials)

    try:
        user = get_user_by_id(db, int(token_data.sub))
    except ValueError as exc:
        raise UnauthorizedError("Could not validate credentials") from exc
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to load authenticated user") from exc

    if user is None:
        raise UnauthorizedError("Could not validate credentials")
    if not user.is_active:
        raise ForbiddenError("Inactive user account")
    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def get_current_admin(current_user: CurrentUser) -> User:
    if not current_user.is_admin:
        raise ForbiddenError("Admin access required")
    return current_user

