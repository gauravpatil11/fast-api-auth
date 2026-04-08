from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.controllers.exceptions import BadRequestError, ConflictError, DatabaseError, NotFoundError
from src.models.db_models import Strategy, User
from src.models.schemas import MessageResponseData, StrategyCreate, StrategyUpdate
from src.models.strategy_crud import (
    create_strategy,
    delete_strategy,
    get_strategy_by_id,
    get_strategy_by_user_and_name,
    list_strategies_by_user,
    update_strategy,
)


def create_user_strategy(db: Session, current_user: User, payload: StrategyCreate) -> Strategy:
    try:
        existing_strategy = get_strategy_by_user_and_name(db, current_user.id, payload.strategy_name)
        if existing_strategy:
            raise ConflictError("Strategy name already exists for this user")

        return create_strategy(
            db,
            user_id=current_user.id,
            strategy_name=payload.strategy_name,
            legs=[leg.model_dump(mode="json") for leg in payload.legs],
            multiplier=payload.multiplier,
        )
    except ConflictError:
        raise
    except IntegrityError as exc:
        raise ConflictError("Strategy name already exists for this user") from exc
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to create strategy") from exc


def list_user_strategies(db: Session, current_user: User) -> list[Strategy]:
    try:
        return list_strategies_by_user(db, current_user.id)
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to fetch strategies") from exc


def get_user_strategy(db: Session, current_user: User, strategy_id: int) -> Strategy:
    try:
        strategy = get_strategy_by_id(db, strategy_id)
        if strategy is None or strategy.user_id != current_user.id:
            raise NotFoundError("Strategy not found")
        return strategy
    except NotFoundError:
        raise
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to fetch strategy") from exc


def update_user_strategy(
    db: Session,
    current_user: User,
    strategy_id: int,
    payload: StrategyUpdate,
) -> Strategy:
    try:
        strategy = get_strategy_by_id(db, strategy_id)
        if strategy is None or strategy.user_id != current_user.id:
            raise NotFoundError("Strategy not found")

        if payload.strategy_name is not None and payload.strategy_name != strategy.strategy_name:
            existing_strategy = get_strategy_by_user_and_name(db, current_user.id, payload.strategy_name)
            if existing_strategy and existing_strategy.id != strategy.id:
                raise ConflictError("Strategy name already exists for this user")
            strategy.strategy_name = payload.strategy_name

        if payload.legs is not None:
            strategy.legs = [leg.model_dump(mode="json") for leg in payload.legs]

        if payload.multiplier is not None:
            strategy.multiplier = payload.multiplier

        return update_strategy(db, strategy)
    except (NotFoundError, ConflictError, BadRequestError):
        raise
    except IntegrityError as exc:
        raise ConflictError("Strategy name already exists for this user") from exc
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to update strategy") from exc


def delete_user_strategy(db: Session, current_user: User, strategy_id: int) -> MessageResponseData:
    try:
        strategy = get_strategy_by_id(db, strategy_id)
        if strategy is None or strategy.user_id != current_user.id:
            raise NotFoundError("Strategy not found")

        delete_strategy(db, strategy)
        return MessageResponseData(detail="Strategy deleted successfully")
    except NotFoundError:
        raise
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to delete strategy") from exc
