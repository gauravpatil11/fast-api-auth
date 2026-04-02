from typing import Any

from fastapi import Request
from fastapi.encoders import jsonable_encoder


def success_response(
    *,
    data: Any,
    message: str,
    request_id: str | None = None,
) -> dict[str, Any]:
    return {
        "success": True,
        "message": message,
        "data": jsonable_encoder(data),
        "error": None,
        "meta": {
            "request_id": request_id,
        },
    }


def success_response_for_request(
    request: Request,
    *,
    data: Any,
    message: str,
) -> dict[str, Any]:
    return success_response(
        data=data,
        message=message,
        request_id=getattr(request.state, "request_id", None),
    )
