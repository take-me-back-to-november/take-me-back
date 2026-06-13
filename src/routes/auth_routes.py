from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse

from dependencies.auth import get_current_user_id
from dtos.user_dtos import CreateUserAndSessionDTO, RefreshTokenDTO
from services.auth.create_user_and_session_service import (
    main as create_user_and_session,
)
from services.auth.create_user_spotify_login_url import (
    main as create_user_spotify_login_url,
)
from services.auth.refresh_token_service import main as refresh_access_token
from services.auth.spotify_callback_handler_service import (
    main as handle_spotify_callback,
)

router = APIRouter(prefix="/auth")


@router.post("/google", status_code=status.HTTP_201_CREATED)
async def google_auth(body: CreateUserAndSessionDTO):
    return await create_user_and_session(body)


@router.post("/spotify", status_code=status.HTTP_201_CREATED)
def spotify_auth(
    user_id: UUID = Depends(get_current_user_id),
):
    return create_user_spotify_login_url(user_id)


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
