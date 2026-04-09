from fastapi import APIRouter, BackgroundTasks, Depends, Request, status
from sqlalchemy.orm import Session

from src.constant.app_constants import APP_TAG_AUTH
from src.controllers.auth_controller import forgot_password, login_user, register_user, reset_password, send_password_reset_otp_email
from src.models.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponseData,
    LoginRequest,
    MessageResponseData,
    RegisterResponseData,
    ResetPasswordRequest,
    SuccessResponse,
    Token,
    UserRegister,
)
from src.utils.dependencies import get_db
from src.utils.responses import success_response_for_request


router = APIRouter(prefix="/auth", tags=[APP_TAG_AUTH])


@router.post("/register", response_model=SuccessResponse[RegisterResponseData], status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)) -> dict:
    user = register_user(db, payload)
    return success_response_for_request(
        request,
        data=user,
        message="User registered successfully",
    )


@router.post("/login", response_model=SuccessResponse[Token], status_code=status.HTTP_200_OK)
def login(
    request: Request,
    payload: LoginRequest,
    db: Session = Depends(get_db),
) -> dict:
    token = login_user(db, payload)
    return success_response_for_request(
        request,
        data=token,
        message="Login successful",
    )


@router.post(
    "/forgot-password",
    response_model=SuccessResponse[ForgotPasswordResponseData],
    status_code=status.HTTP_202_ACCEPTED,
)
def forgot_password_route(
    request: Request,
    payload: ForgotPasswordRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
) -> dict:
    data = forgot_password(
        db,
        payload,
        send_otp_callback=lambda email, otp: background_tasks.add_task(send_password_reset_otp_email, email, otp),
    )
    return success_response_for_request(
        request,
        data=data,
        message=data.detail,
    )


@router.post(
    "/reset-password",
    response_model=SuccessResponse[MessageResponseData],
    status_code=status.HTTP_200_OK,
)
def reset_password_route(
    request: Request,
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict:
    data = reset_password(db, payload)
    return success_response_for_request(
        request,
        data=data,
        message=data.detail,
    )
