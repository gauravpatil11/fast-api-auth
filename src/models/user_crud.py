from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models.db_models import User


def get_user_by_username(db: Session, username: str) -> User | None:
    return db.query(User).filter(User.username == username).first()


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def create_user(
    db: Session,
    *,
    username: str,
    email: str,
    hashed_password: str,
    is_admin: bool = False,
) -> User:
    db_user = User(
        username=username,
        email=email,
        hashed_password=hashed_password,
        is_admin=is_admin,
    )
    db.add(db_user)
    _commit_and_refresh(db, db_user)
    return db_user


def update_user(db: Session, user: User) -> User:
    db.add(user)
    _commit_and_refresh(db, user)
    return user


def list_users(db: Session) -> list[User]:
    return db.query(User).order_by(User.id.asc()).all()


def _commit_and_refresh(db: Session, user: User) -> None:
    try:
        db.commit()
        db.refresh(user)
    except SQLAlchemyError:
        db.rollback()
        raise
