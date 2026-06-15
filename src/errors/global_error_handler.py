from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from errors.discord_logger import log_server_error_to_discord


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        await log_server_error_to_discord(
            method=request.method,
            path=request.url.path,
            exc=exc,
        )
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"},
        )
