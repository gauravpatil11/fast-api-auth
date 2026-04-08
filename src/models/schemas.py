from datetime import date, datetime
from enum import Enum
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, EmailStr, field_validator, model_validator


USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 100
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
STRATEGY_NAME_MAX_LENGTH = 255
T = TypeVar("T")


def _normalize_email(value: str) -> str:
    return value.strip().lower()


def _normalize_username(value: str) -> str:
    return value.strip()


def _validate_username(value: str) -> str:
    normalized_value = _normalize_username(value)
    if not normalized_value:
        raise ValueError("Username is required")
    if len(normalized_value) < USERNAME_MIN_LENGTH:
        raise ValueError(f"Username must be at least {USERNAME_MIN_LENGTH} characters long")
    if len(normalized_value) > USERNAME_MAX_LENGTH:
        raise ValueError(f"Username must be at most {USERNAME_MAX_LENGTH} characters long")
    return normalized_value


def _validate_password(value: str) -> str:
    if len(value) < PASSWORD_MIN_LENGTH:
        raise ValueError(f"Password must be at least {PASSWORD_MIN_LENGTH} characters long")
    if len(value) > PASSWORD_MAX_LENGTH:
        raise ValueError(f"Password must be at most {PASSWORD_MAX_LENGTH} characters long")
    return value


def _validate_strategy_name(value: str) -> str:
    normalized_value = value.strip()
    if not normalized_value:
        raise ValueError("Strategy name is required")
    if len(normalized_value) > STRATEGY_NAME_MAX_LENGTH:
        raise ValueError(f"Strategy name must be at most {STRATEGY_NAME_MAX_LENGTH} characters long")
    return normalized_value


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    sub: str


class UserBase(BaseModel):
    username: str
    email: EmailStr

    @field_validator("username")
    @classmethod
    def validate_username(cls, value: str) -> str:
        return _validate_username(value)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: EmailStr) -> str:
        return _normalize_email(str(value))


class UserCreate(UserBase):
    password: str

    @field_validator("password")
    @classmethod
    def validate_password(cls, value: str) -> str:
        return _validate_password(value)


class UserRegister(UserCreate):
    pass


class UserPublic(UserBase):
    id: int
    is_active: bool
    is_admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserPublic):
    pass


class RegisterResponseData(BaseModel):
    user: UserPublic
    token: Token


class LoginRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(str(value))


class UserUpdate(BaseModel):
    username: str | None = None
    email: EmailStr | None = None

    @field_validator("username")
    @classmethod
    def validate_optional_username(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_username(value)

    @field_validator("email")
    @classmethod
    def validate_optional_email(cls, value: EmailStr | None) -> str | None:
        if value is None:
            return value
        return _normalize_email(str(value))


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password(value)


class ForgotPasswordRequest(BaseModel):
    email: EmailStr

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(str(value))


class ForgotPasswordResponseData(BaseModel):
    detail: str
    otp_preview: str | None = None


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    otp: str
    new_password: str

    @field_validator("email")
    @classmethod
    def normalize_email(cls, value: EmailStr) -> str:
        return _normalize_email(str(value))

    @field_validator("otp")
    @classmethod
    def validate_otp(cls, value: str) -> str:
        otp = value.strip()
        if len(otp) != 6 or not otp.isdigit():
            raise ValueError("OTP must be a 6 digit code")
        return otp

    @field_validator("new_password")
    @classmethod
    def validate_new_password(cls, value: str) -> str:
        return _validate_password(value)


class StrategySide(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class StrategyOptionType(str, Enum):
    CE = "CE"
    PE = "PE"


class StrategyLeg(BaseModel):
    side: StrategySide
    expiry: date
    strike: float
    type: StrategyOptionType
    lots: int

    @field_validator("strike")
    @classmethod
    def validate_strike(cls, value: float) -> float:
        if value <= 0:
            raise ValueError("Strike must be greater than 0")
        return value

    @field_validator("lots")
    @classmethod
    def validate_lots(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Lots must be greater than 0")
        return value


class StrategyBase(BaseModel):
    strategy_name: str
    legs: list[StrategyLeg]
    multiplier: int

    @field_validator("strategy_name")
    @classmethod
    def validate_strategy_name(cls, value: str) -> str:
        return _validate_strategy_name(value)

    @field_validator("multiplier")
    @classmethod
    def validate_multiplier(cls, value: int) -> int:
        if value <= 0:
            raise ValueError("Multiplier must be greater than 0")
        return value

    @model_validator(mode="after")
    def validate_legs(self) -> "StrategyBase":
        if not self.legs:
            raise ValueError("At least one strategy leg is required")
        return self


class StrategyCreate(StrategyBase):
    pass


class StrategyUpdate(BaseModel):
    strategy_name: str | None = None
    legs: list[StrategyLeg] | None = None
    multiplier: int | None = None

    @field_validator("strategy_name")
    @classmethod
    def validate_optional_strategy_name(cls, value: str | None) -> str | None:
        if value is None:
            return value
        return _validate_strategy_name(value)

    @field_validator("multiplier")
    @classmethod
    def validate_optional_multiplier(cls, value: int | None) -> int | None:
        if value is None:
            return value
        if value <= 0:
            raise ValueError("Multiplier must be greater than 0")
        return value

    @model_validator(mode="after")
    def validate_update_fields(self) -> "StrategyUpdate":
        if (
            self.strategy_name is None
            and self.legs is None
            and self.multiplier is None
        ):
            raise ValueError("At least one strategy field must be provided")
        if self.legs is not None and not self.legs:
            raise ValueError("At least one strategy leg is required")
        return self


class StrategyResponse(BaseModel):
    id: int
    user_id: int
    strategy_name: str
    legs: list[StrategyLeg]
    multiplier: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MessageResponseData(BaseModel):
    detail: str


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
