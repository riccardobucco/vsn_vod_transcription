"""API error response helpers."""

from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse


class AppError(HTTPException):
    """Application-specific HTTP error with a machine-readable code."""

    def __init__(self, status_code: int, code: str, message: str):
        self.code = code
        super().__init__(status_code=status_code, detail=message)


def error_response(status_code: int, code: str, message: str, request_id: str | None = None) -> JSONResponse:
    """Build a standard error JSON response."""
    body: dict = {"code": code, "message": message}
    if request_id:
        body["request_id"] = request_id
    return JSONResponse(status_code=status_code, content=body)


async def app_error_handler(request: Request, exc: AppError) -> JSONResponse:
    request_id = getattr(request.state, "request_id", None)
    return error_response(exc.status_code, exc.code, str(exc.detail), request_id)
