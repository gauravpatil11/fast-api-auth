import logging
import smtplib
from email.message import EmailMessage
from typing import Callable

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from src.config import settings
from src.controllers.exceptions import BadRequestError, ConflictError, DatabaseError, ServiceUnavailableError, UnauthorizedError
from src.models.db_models import User
from src.models.schemas import (
    ForgotPasswordRequest,
    ForgotPasswordResponseData,
    LoginRequest,
    MessageResponseData,
    RegisterResponseData,
    ResetPasswordRequest,
    Token,
    UserPublic,
    UserRegister,
)
from src.models.user_crud import (
    create_user,
    get_user_by_email,
    get_user_by_username,
    update_user,
)
from src.utils.security import (
    create_access_token,
    generate_password_reset_otp,
    get_password_hash,
    get_password_reset_token_expiry,
    hash_password_reset_token,
    normalize_client_time,
    verify_password,
)


logger = logging.getLogger(__name__)

INVALID_LOGIN_MESSAGE = "Incorrect email or password"
FORGOT_PASSWORD_MESSAGE = "If the account exists, password reset instructions will be sent"
RESET_PASSWORD_SUCCESS_MESSAGE = "Password reset successfully"


def send_password_reset_otp_email(recipient_email: str, otp: str) -> None:
    if not settings.mail_host or not settings.mail_from_email:
        logger.info("Password reset OTP for %s is %s", recipient_email, otp)
        return

    message = EmailMessage()
    message["Subject"] = "Your password reset OTP"
    message["From"] = settings.mail_from_email
    message["To"] = recipient_email
    message.set_content(
        f"Your OTP for password reset is {otp}. It will expire in "
        f"{settings.reset_token_expire_minutes} minutes."
    )

    with smtplib.SMTP(settings.mail_host, settings.mail_port) as smtp:
        if settings.mail_use_tls:
            smtp.starttls()
        if settings.mail_username and settings.mail_password:
            smtp.login(settings.mail_username, settings.mail_password)
        smtp.send_message(message)


def register_user(db: Session, payload: UserRegister) -> RegisterResponseData:
    try:
        existing_username = get_user_by_username(db, payload.username)
        if existing_username:
            raise ConflictError("Username already registered")

        existing_email = get_user_by_email(db, payload.email)
        if existing_email:
            raise ConflictError("Email already registered")

        user = create_user(
            db,
            username=payload.username,
            email=payload.email,
            hashed_password=get_password_hash(payload.password),
        )
        token = Token(
            access_token=create_access_token(str(user.id)),
            token_type="bearer",
        )
        return RegisterResponseData(
            user=UserPublic.model_validate(user),
            token=token,
        )
    except IntegrityError as exc:
        raise ConflictError("Username or email already registered") from exc
    except SQLAlchemyError as exc:
        raise DatabaseError("Unable to register user") from exc


def authenticate_user(db: Session, payload: LoginRequest) -> User | None:
    try:
        user = get_user_by_email(db, payload.email)
        if not user or not user.is_active:
            return None

        if verify_password(payload.password, user.hashed_password):
            return user

        return None
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to verify user credentials") from exc


def login_user(db: Session, payload: LoginRequest) -> Token:
    user = authenticate_user(db, payload)
    if not user:
        raise UnauthorizedError(INVALID_LOGIN_MESSAGE)

    access_token = create_access_token(str(user.id))
    return Token(access_token=access_token, token_type="bearer")


def forgot_password(
    db: Session,
    payload: ForgotPasswordRequest,
    *,
    send_otp_callback: Callable[[str, str], None] | None = None,
) -> ForgotPasswordResponseData:
    try:
        user = get_user_by_email(db, payload.email)
        if not user or not user.is_active:
            return ForgotPasswordResponseData(detail=FORGOT_PASSWORD_MESSAGE)

        otp = generate_password_reset_otp()
        user.password_reset_otp_hash = hash_password_reset_token(otp)
        user.password_reset_otp_created_at = normalize_client_time(payload.client_time)
        user.password_reset_otp_expires_at = get_password_reset_token_expiry(payload.client_time)
        update_user(db, user)
        if send_otp_callback is not None:
            send_otp_callback(payload.email, otp)
        else:
            send_password_reset_otp_email(payload.email, otp)

        return ForgotPasswordResponseData(
            detail=FORGOT_PASSWORD_MESSAGE,
            otp_preview=otp if not settings.is_production else None,
        )
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to process forgot password request") from exc
    except smtplib.SMTPException as exc:
        raise ServiceUnavailableError("Unable to send password reset OTP") from exc


def reset_password(db: Session, payload: ResetPasswordRequest) -> MessageResponseData:
    try:
        user = get_user_by_email(db, payload.email)
        if user is None or not user.is_active:
            raise BadRequestError("Invalid OTP or expired OTP")

        token_hash = hash_password_reset_token(payload.otp)
        if user.password_reset_otp_hash is None or user.password_reset_otp_hash != token_hash:
            raise BadRequestError("Invalid OTP or expired OTP")

        if user.password_reset_otp_expires_at is None:
            raise BadRequestError("Invalid OTP or expired OTP")

        if normalize_client_time(payload.client_time) > user.password_reset_otp_expires_at:
            raise BadRequestError("Invalid OTP or expired OTP")

        user.hashed_password = get_password_hash(payload.new_password)
        user.password_reset_otp_hash = None
        user.password_reset_otp_created_at = None
        user.password_reset_otp_expires_at = None
        update_user(db, user)
        return MessageResponseData(detail=RESET_PASSWORD_SUCCESS_MESSAGE)
    except BadRequestError:
        raise
    except SQLAlchemyError as exc:
        raise ServiceUnavailableError("Unable to reset password") from exc
