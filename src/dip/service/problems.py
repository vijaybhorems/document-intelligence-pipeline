"""RFC 9457 problem details for every error the service returns (SPEC §12)."""

from collections.abc import Mapping

from fastapi import FastAPI, HTTPException, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from dip.service.uploads import UploadError

PROBLEM = "application/problem+json"


def problem(
    status: int,
    title: str,
    detail: str = "",
    headers: Mapping[str, str] | None = None,
    **extra: object,
) -> JSONResponse:
    body = {"type": "about:blank", "title": title, "status": status, "detail": detail, **extra}
    return JSONResponse(body, status_code=status, media_type=PROBLEM, headers=dict(headers or {}))


def install(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_error(_: Request, exc: HTTPException) -> JSONResponse:
        # Keep the exception's headers: Retry-After on 429, WWW-Authenticate on 401.
        return problem(exc.status_code, str(exc.detail), str(exc.detail), headers=exc.headers)

    @app.exception_handler(UploadError)
    async def upload_error(_: Request, exc: UploadError) -> JSONResponse:
        return problem(exc.status, exc.title, exc.detail)

    @app.exception_handler(RequestValidationError)
    async def invalid_request(_: Request, exc: RequestValidationError) -> JSONResponse:
        return problem(422, "Invalid request", "see errors", errors=exc.errors())
