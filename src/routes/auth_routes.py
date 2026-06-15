from fastapi import APIRouter, Query, status
from fastapi.responses import RedirectResponse

from dtos.user_dtos import RefreshTokenDTO
from services.auth.build_spotify_login_url import main as build_spotify_login_url
from services.auth.refresh_token_service import main as refresh_access_token
from services.auth.spotify_callback_handler_service import (
    main as handle_spotify_callback,
)

router = APIRouter(prefix="/auth")


@router.get("/login-url")
def spotify_login_url(return_to: str | None = Query(default=None)):
    return build_spotify_login_url(return_to=return_to)


@router.get("/spotify/callback")
async def spotify_callback(
    code: str = Query(),
    state: str = Query(),
):
    result = await handle_spotify_callback(code=code, state=state)
    return RedirectResponse(
        url=result["redirect_url"], status_code=status.HTTP_302_FOUND
    )


@router.post("/refresh")
async def refresh_token(body: RefreshTokenDTO):
    return await refresh_access_token(body.refresh_token)
