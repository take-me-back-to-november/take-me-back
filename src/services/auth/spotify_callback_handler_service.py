from urllib.parse import urlencode

from fastapi import HTTPException, status

from config.frontend import FRONTEND_CONFIG
from models.user import User
from utils.jwt import (
    create_access_jwt_token,
    create_refresh_token,
    verify_spotify_state_token,
)
from utils.spotify import (
    exchange_spotify_authorization_code,
    extract_spotify_tokens,
    fetch_spotify_profile,
    persist_spotify_tokens,
    validate_spotify_callback_params,
    validate_spotify_credentials,
)


async def upsert_user_from_spotify_profile(profile) -> User:
    user = await User.filter(spotify_id=profile.id, deleted_at=None).first()

    if not user:
        user = await User.create(
            spotify_id=profile.id,
            email=profile.email,
            name=profile.display_name,
            picture_url=profile.image_url,
            refresh_token=create_refresh_token(),
        )
        return user

    changes: dict[str, str | None] = {}
    if user.email != profile.email:
        changes["email"] = profile.email
    if user.name != profile.display_name:
        changes["name"] = profile.display_name
    if user.picture_url != profile.image_url:
        changes["picture_url"] = profile.image_url
    if not user.refresh_token:
        changes["refresh_token"] = create_refresh_token()

    if changes:
        await user.update_from_dict(changes).save()

    return user


def build_callback_redirect_url(access_token: str, refresh_token: str) -> str:
    fragment = urlencode(
        {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }
    )
    return f"{FRONTEND_CONFIG['base_url']}/auth/callback#{fragment}"


async def main(code: str, state: str):
    validate_spotify_callback_params(code, state)

    if not verify_spotify_state_token(state):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired state parameter",
        )

    client_id, client_secret, token_url = validate_spotify_credentials()
    token_data = await exchange_spotify_authorization_code(
        code,
        client_id,
        client_secret,
        token_url,
    )
    refresh_token, access_token, expires_in = extract_spotify_tokens(token_data)

    profile = await fetch_spotify_profile(access_token)
    user = await upsert_user_from_spotify_profile(profile)
    await persist_spotify_tokens(user, refresh_token, access_token, expires_in)

    app_access_token = create_access_jwt_token(user_id=user.id)

    return {
        "user_id": str(user.id),
        "spotify_connected": True,
        "redirect_url": build_callback_redirect_url(
            app_access_token, user.refresh_token
        ),
    }
