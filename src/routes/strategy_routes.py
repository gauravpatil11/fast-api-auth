from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.constant.app_constants import APP_TAG_STRATEGIES
from src.controllers.strategy_controller import (
    create_user_strategy,
    delete_user_strategy,
    get_user_strategy,
    list_user_strategies,
    update_user_strategy,
)
from src.models.schemas import (
    MessageResponseData,
    StrategyCreate,
    StrategyResponse,
    StrategyUpdate,
    SuccessResponse,
)
from src.utils.dependencies import CurrentUser, get_db
from src.utils.responses import success_response_for_request


router = APIRouter(prefix="/strategies", tags=[APP_TAG_STRATEGIES])


@router.post("", response_model=SuccessResponse[StrategyResponse], status_code=status.HTTP_201_CREATED)
def create_strategy_route(
    request: Request,
    payload: StrategyCreate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    strategy = create_user_strategy(db, current_user, payload)
    return success_response_for_request(
        request,
        data=StrategyResponse.model_validate(strategy),
        message="Strategy created successfully",
    )


@router.get("", response_model=SuccessResponse[list[StrategyResponse]], status_code=status.HTTP_200_OK)
def list_strategies_route(
    request: Request,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    strategies = list_user_strategies(db, current_user)
    return success_response_for_request(
        request,
        data=[StrategyResponse.model_validate(strategy) for strategy in strategies],
        message="Strategies fetched successfully",
    )


@router.get("/{strategy_id}", response_model=SuccessResponse[StrategyResponse], status_code=status.HTTP_200_OK)
def get_strategy_route(
    request: Request,
    strategy_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    strategy = get_user_strategy(db, current_user, strategy_id)
    return success_response_for_request(
        request,
        data=StrategyResponse.model_validate(strategy),
        message="Strategy fetched successfully",
    )


@router.put("/{strategy_id}", response_model=SuccessResponse[StrategyResponse], status_code=status.HTTP_200_OK)
def update_strategy_route(
    request: Request,
    strategy_id: int,
    payload: StrategyUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    strategy = update_user_strategy(db, current_user, strategy_id, payload)
    return success_response_for_request(
        request,
        data=StrategyResponse.model_validate(strategy),
        message="Strategy updated successfully",
    )


@router.delete(
    "/{strategy_id}",
    response_model=SuccessResponse[MessageResponseData],
    status_code=status.HTTP_200_OK,
)
def delete_strategy_route(
    request: Request,
    strategy_id: int,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    data = delete_user_strategy(db, current_user, strategy_id)
    return success_response_for_request(
        request,
        data=data,
        message=data.detail,
    )
