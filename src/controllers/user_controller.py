from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.controllers.exceptions import ConflictError, DatabaseError, ServiceUnavailableError
from src.models.db_models import User
from src.models.schemas import UserUpdate
from src.models.user_crud import get_user_by_email, get_user_by_username, list_users, update_user
from src.utils.security import get_password_hash


def get_profile(current_user: User) -> User:
    return current_user


def update_profile(db: Session, current_user: User, payload: UserUpdate) -> User:
    try:
        if payload.username and payload.username != current_user.username:
            existing_username = get_user_by_username(db, payload.username)
            if existing_username:
                raise ConflictError("Username already registered")
            current_user.username = payload.username

        if payload.email and payload.email != current_user.email:
            existing_email = get_user_by_email(db, payload.email)
            if existing_email:
                raise ConflictError("Email already registered")
            current_user.email = payload.email

        if payload.password:
            current_user.hashed_password = get_password_hash(payload.password)

        return update_user(db, current_user)
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to update profile") from exc


def get_user_list(db: Session) -> list[User]:
    try:
        return list_users(db)
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to fetch users") from exc
