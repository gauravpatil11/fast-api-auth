from fastapi import APIRouter, Depends, Request, status
from sqlalchemy.orm import Session

from src.controllers.auth_controller import LoginCredentials, login_user, register_user
from src.controllers.exceptions import BadRequestError
from src.models.schemas import LoginRequest, RegisterResponseData, SuccessResponse, Token, UserRegister
from src.utils.dependencies import get_db
from src.utils.responses import success_response_for_request


router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=SuccessResponse[RegisterResponseData], status_code=status.HTTP_201_CREATED)
def register(request: Request, payload: UserRegister, db: Session = Depends(get_db)) -> dict:
    user = register_user(db, payload)
    return success_response_for_request(
        request,
        data=user,
        message="User registered successfully",
    )


@router.post("/login", response_model=SuccessResponse[Token])
async def login(
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    content_type = request.headers.get("content-type", "").lower()

    if "application/json" in content_type:
        payload = LoginRequest.model_validate(await request.json())
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")
        if not username or not password:
            raise BadRequestError("Both username and password are required")
        payload = LoginCredentials(
            username=str(username),
            password=str(password),
        )

    token = login_user(db, payload)
    return success_response_for_request(
        request,
        data=token,
        message="Login successful",
    )
