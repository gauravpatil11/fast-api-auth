class AppError(Exception):
    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        error_code: str,
        errors: list[dict] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code
        self.errors = errors or []


class BadRequestError(AppError):
    def __init__(self, message: str, errors: list[dict] | None = None) -> None:
        super().__init__(
            message,
            status_code=400,
            error_code="bad_request",
            errors=errors,
        )


class UnauthorizedError(AppError):
    def __init__(self, message: str = "Unauthorized") -> None:
        super().__init__(
            message,
            status_code=401,
            error_code="unauthorized",
        )


class ForbiddenError(AppError):
    def __init__(self, message: str = "Forbidden") -> None:
        super().__init__(
            message,
            status_code=403,
            error_code="forbidden",
        )


class NotFoundError(AppError):
    def __init__(self, message: str = "Resource not found") -> None:
        super().__init__(
            message,
            status_code=404,
            error_code="not_found",
        )


class ConflictError(AppError):
    def __init__(self, message: str) -> None:
        super().__init__(
            message,
            status_code=409,
            error_code="conflict",
        )


class DatabaseError(AppError):
    def __init__(self, message: str = "Database operation failed") -> None:
        super().__init__(
            message,
            status_code=500,
            error_code="database_error",
        )


class ServiceUnavailableError(AppError):
    def __init__(self, message: str = "Service unavailable") -> None:
        super().__init__(
            message,
            status_code=503,
            error_code="service_unavailable",
        )
