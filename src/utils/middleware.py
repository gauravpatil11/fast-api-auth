import logging
import time
import uuid

from fastapi import FastAPI, Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.utils.request_context import set_request_id


logger = logging.getLogger(__name__)


class RequestContextMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())
        set_request_id(request_id)
        request.state.request_id = request_id

        start_time = time.perf_counter()
        try:
            response = await call_next(request)
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)

            response.headers["X-Request-ID"] = request_id
            response.headers["X-Process-Time-MS"] = str(process_time_ms)

            logger.info(
                "Request completed | method=%s path=%s status_code=%s duration_ms=%s",
                request.method,
                request.url.path,
                response.status_code,
                process_time_ms,
            )
            return response
        except Exception:
            process_time_ms = round((time.perf_counter() - start_time) * 1000, 2)
            logger.exception(
                "Request failed | method=%s path=%s duration_ms=%s",
                request.method,
                request.url.path,
                process_time_ms,
            )
            raise


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(RequestContextMiddleware)
