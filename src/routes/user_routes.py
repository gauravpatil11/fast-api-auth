from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.controllers.user_controller import change_password, get_profile, get_user_list, update_profile
from src.models.db_models import User
from src.models.schemas import ChangePasswordRequest, MessageResponseData, SuccessResponse, UserResponse, UserUpdate
from src.utils.dependencies import CurrentUser, get_current_admin, get_db
from src.utils.responses import success_response_for_request


router = APIRouter(prefix="/user", tags=["user"])


@router.get("/profile", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_200_OK)
def read_profile(request: Request, current_user: CurrentUser) -> dict:
    profile = get_profile(current_user)
    return success_response_for_request(
        request,
        data=UserResponse.model_validate(profile),
        message="Profile fetched successfully",
    )


@router.put("/profile", response_model=SuccessResponse[UserResponse], status_code=status.HTTP_200_OK)
def edit_profile(
    request: Request,
    payload: UserUpdate,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    updated_user = update_profile(db, current_user, payload)
    return success_response_for_request(
        request,
        data=UserResponse.model_validate(updated_user),
        message="Profile updated successfully",
    )


@router.post(
    "/change-password",
    response_model=SuccessResponse[MessageResponseData],
    status_code=status.HTTP_200_OK,
)
def change_password_route(
    request: Request,
    payload: ChangePasswordRequest,
    current_user: CurrentUser,
    db: Session = Depends(get_db),
) -> dict:
    data = change_password(db, current_user, payload)
    return success_response_for_request(
        request,
        data=data,
        message=data.detail,
    )


@router.get("/userlist", response_model=SuccessResponse[list[UserResponse]], status_code=status.HTTP_200_OK)
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> dict:
    users = get_user_list(db)
    return success_response_for_request(
        request,
        data=[UserResponse.model_validate(user) for user in users],
        message="Users fetched successfully",
    )
