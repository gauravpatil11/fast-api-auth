from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from src.controllers.user_controller import get_profile, get_user_list, update_profile
from src.models.db_models import User
from src.models.schemas import SuccessResponse, UserResponse, UserUpdate
from src.utils.dependencies import get_current_admin, get_current_user, get_db
from src.utils.responses import success_response_for_request


router = APIRouter(prefix="/users", tags=["users"])


@router.get("/profile", response_model=SuccessResponse[UserResponse])
def read_profile(request: Request, current_user: User = Depends(get_current_user)) -> dict:
    profile = get_profile(current_user)
    return success_response_for_request(
        request,
        data=profile,
        message="Profile fetched successfully",
    )


@router.put("/profile", response_model=SuccessResponse[UserResponse])
def edit_profile(
    request: Request,
    payload: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    updated_user = update_profile(db, current_user, payload)
    return success_response_for_request(
        request,
        data=updated_user,
        message="Profile updated successfully",
    )


@router.get("/userlist", response_model=SuccessResponse[list[UserResponse]])
def list_users(
    request: Request,
    db: Session = Depends(get_db),
    _: User = Depends(get_current_admin),
) -> dict:
    users = get_user_list(db)
    return success_response_for_request(
        request,
        data=users,
        message="Users fetched successfully",
    )
