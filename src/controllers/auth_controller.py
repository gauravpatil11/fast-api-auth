from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.controllers.exceptions import ConflictError, DatabaseError, ServiceUnavailableError, UnauthorizedError
from src.models.db_models import User
from src.models.schemas import LoginRequest, RegisterResponseData, Token, UserRegister, UserResponse
from src.models.user_crud import create_user, get_user_by_email, get_user_by_username, update_user
from src.utils.security import (
    create_access_token,
    get_password_hash,
    verify_legacy_password,
    verify_password,
)


@dataclass
class LoginCredentials:
    username: str
    password: str


def register_user(db: Session, payload: UserRegister) -> RegisterResponseData:
    try:
        existing_username = get_user_by_username(db, payload.username)
        if existing_username:
            raise ConflictError("Username already registered")

        existing_email = get_user_by_email(db, payload.email)
        if existing_email:
            raise ConflictError("Email already registered")

        user = create_user(
            db,
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
        )
        token = Token(
            access_token=create_access_token(data={"sub": user.username}),
            token_type="bearer",
        )
        return RegisterResponseData(
            user=UserResponse.model_validate(user),
            token=token,
        )
    except IntegrityError as exc:
        raise ConflictError("Username or email already registered") from exc
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to register user") from exc


def authenticate_user(db: Session, payload: LoginRequest | LoginCredentials) -> User | None:
    try:
        user = get_user_by_username(db, payload.username)
        if not user:
            return None

        if not user.is_active:
            return None

        if verify_password(payload.password, user.hashed_password):
            return user

        if verify_legacy_password(payload.password, user.hashed_password):
            user.hashed_password = get_password_hash(payload.password)
            return update_user(db, user)

        return None
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to verify user credentials") from exc


def login_user(db: Session, payload: LoginRequest | LoginCredentials) -> Token:
    user = authenticate_user(db, payload)
    if not user:
        raise UnauthorizedError("Incorrect username or password")

    access_token = create_access_token(data={"sub": user.username})
    return Token(access_token=access_token, token_type="bearer")
