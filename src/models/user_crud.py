from sqlalchemy import func, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models.db_models import User


def get_user_by_id(db: Session, user_id: int) -> User | None:
    statement = select(User).where(User.id == user_id)
    return db.scalar(statement)


def get_user_by_username(db: Session, username: str) -> User | None:
    normalized_username = username.strip().lower()
    statement = select(User).where(func.lower(User.username) == normalized_username)
    return db.scalar(statement)


def get_user_by_email(db: Session, email: str) -> User | None:
    normalized_email = email.strip().lower()
    statement = select(User).where(func.lower(User.email) == normalized_email)
    return db.scalar(statement)


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    hashed_password: str,
    is_admin: bool = False,
) -> User:
    db_user = User(
        username=username.strip(),
        email=email.strip().lower(),
        hashed_password=hashed_password,
        is_admin=is_admin,
    )
    db.add(db_user)
    _commit(db)
    db.refresh(db_user)
    return db_user


def update_user(db: Session, user: User) -> User:
    db.add(user)
    _commit(db)
    db.refresh(user)
    return user


def list_users(db: Session) -> list[User]:
    statement = select(User).order_by(User.id.asc())
    return list(db.scalars(statement).all())


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
