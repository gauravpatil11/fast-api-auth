from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.models.db_models import Strategy


def create_strategy(
    db: Session,
    *,
    user_id: int,
    strategy_name: str,
    legs: list[dict],
    multiplier: int,
) -> Strategy:
    db_strategy = Strategy(
        user_id=user_id,
        strategy_name=strategy_name.strip(),
        legs=legs,
        multiplier=multiplier,
    )
    db.add(db_strategy)
    _commit(db)
    db.refresh(db_strategy)
    return db_strategy


def get_strategy_by_id(db: Session, strategy_id: int) -> Strategy | None:
    statement = select(Strategy).where(Strategy.id == strategy_id)
    return db.scalar(statement)


def get_strategy_by_user_and_name(db: Session, user_id: int, strategy_name: str) -> Strategy | None:
    statement = select(Strategy).where(
        Strategy.user_id == user_id,
        Strategy.strategy_name == strategy_name.strip(),
    )
    return db.scalar(statement)


def list_strategies_by_user(db: Session, user_id: int) -> list[Strategy]:
    statement = (
        select(Strategy)
        .where(Strategy.user_id == user_id)
        .order_by(Strategy.updated_at.desc(), Strategy.id.desc())
    )
    return list(db.scalars(statement).all())


def update_strategy(db: Session, strategy: Strategy) -> Strategy:
    db.add(strategy)
    _commit(db)
    db.refresh(strategy)
    return strategy


def delete_strategy(db: Session, strategy: Strategy) -> None:
    db.delete(strategy)
    _commit(db)


def _commit(db: Session) -> None:
    try:
        db.commit()
    except SQLAlchemyError:
        db.rollback()
        raise
