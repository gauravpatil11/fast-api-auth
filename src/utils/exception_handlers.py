import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from src.controllers.exceptions import AppError


logger = logging.getLogger(__name__)


def _error_response(
    *,
    request: Request,
    status_code: int,
    message: str,
    error_code: str,
    details: list,
    headers: dict | None = None,
) -> JSONResponse:
    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "message": message,
            "data": None,
            "error": {
                "code": error_code,
                "details": details,
            },
            "meta": {
                "request_id": getattr(request.state, "request_id", None),
            },
        },
        headers=headers,
    )


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(AppError)
    async def handle_app_error(request: Request, exc: AppError) -> JSONResponse:
        return _error_response(
            request=request,
            status_code=exc.status_code,
            message=exc.message,
            error_code=exc.error_code,
            details=exc.errors,
        )

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
        return _error_response(
            request=request,
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            message="Validation failed",
            error_code="validation_error",
            details=exc.errors(),
        )

    @app.exception_handler(HTTPException)
    async def handle_http_exception(request: Request, exc: HTTPException) -> JSONResponse:
        details = exc.detail if isinstance(exc.detail, list) else [{"message": str(exc.detail)}]
        message = exc.detail if isinstance(exc.detail, str) else "Request failed"
        return _error_response(
            request=request,
            status_code=exc.status_code,
            message=message,
            error_code="http_error",
            details=details,
            headers=exc.headers,
        )

    @app.exception_handler(Exception)
    async def handle_unexpected_exception(request: Request, exc: Exception) -> JSONResponse:
        logger.exception("Unhandled server error", exc_info=exc)
        return _error_response(
            request=request,
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            message="Internal server error",
            error_code="internal_server_error",
            details=[],
        )
