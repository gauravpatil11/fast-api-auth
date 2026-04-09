from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.controllers.exceptions import BadRequestError, ConflictError, DatabaseError, ServiceUnavailableError
from src.models.db_models import User
from src.models.schemas import ChangePasswordRequest, MessageResponseData, UserUpdate
from src.models.user_crud import (
    get_user_by_username,
    list_users,
    update_user,
)
from src.utils.security import get_password_hash, verify_password


def get_profile(current_user: User) -> User:
    return current_user


def update_profile(db: Session, current_user: User, payload: UserUpdate) -> User:
    try:
        if payload.username is None:
            raise BadRequestError("Username must be provided")

        if payload.username and payload.username.lower() != current_user.username.lower():
            existing_username = get_user_by_username(db, payload.username)
            if existing_username and existing_username.id != current_user.id:
                raise ConflictError("Username already registered")
            current_user.username = payload.username

        return update_user(db, current_user)
    except BadRequestError:
        raise
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to update profile") from exc


def change_password(db: Session, current_user: User, payload: ChangePasswordRequest) -> MessageResponseData:
    try:
        if not verify_password(payload.current_password, current_user.hashed_password):
            raise BadRequestError("Current password is incorrect")

        if verify_password(payload.new_password, current_user.hashed_password):
            raise BadRequestError("New password must be different from the current password")

        current_user.hashed_password = get_password_hash(payload.new_password)
        current_user.password_reset_otp_hash = None
        current_user.password_reset_otp_created_at = None
        current_user.password_reset_otp_expires_at = None
        update_user(db, current_user)
        return MessageResponseData(detail="Password changed successfully")
    except BadRequestError:
        raise
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to change password") from exc


def get_user_list(db: Session) -> list[User]:
    try:
        return list_users(db)
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to fetch users") from exc
