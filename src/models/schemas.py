import re
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, field_validator


EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")
T = TypeVar("T")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserBase(BaseModel):
    username: str
    email: str

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email format")
        return value.lower()


class UserRegister(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class UserResponse(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class RegisterResponseData(BaseModel):
    user: UserResponse
    token: Token


class LoginRequest(BaseModel):
    username: str
    password: str


class UserUpdate(BaseModel):
    username: str | None = None
    email: str | None = None
    password: str | None = None

    @field_validator("email")
    @classmethod
    def validate_optional_email(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if not EMAIL_PATTERN.match(value):
            raise ValueError("Invalid email format")
        return value.lower()

    @field_validator("password")
    @classmethod
    def validate_optional_password(cls, value: str | None) -> str | None:
        if value is None:
            return value
        if len(value) < 6:
            raise ValueError("Password must be at least 6 characters long")
        return value


class ErrorDetail(BaseModel):
    message: str | None = None
    field: str | None = None
    type: str | None = None


class ErrorInfo(BaseModel):
    code: str
    details: list[dict[str, Any] | ErrorDetail]


class ResponseMeta(BaseModel):
    request_id: str | None = None


class SuccessResponse(BaseModel, Generic[T]):
    success: bool = True
    message: str
    data: T
    error: None = None
    meta: ResponseMeta | None = None


class ErrorResponse(BaseModel):
    success: bool = False
    message: str
    data: None = None
    error: ErrorInfo
    meta: ResponseMeta | None = None
