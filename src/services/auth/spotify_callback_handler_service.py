from config.frontend import FRONTEND_CONFIG
from utils.spotify import (
    exchange_spotify_authorization_code,
    extract_spotify_tokens,
    persist_spotify_tokens,
    validate_spotify_callback_params,
    validate_spotify_credentials,
)
from utils.users import get_user_by_id


async def main(code: str, state: str):
    validate_spotify_callback_params(code, state)
    client_id, client_secret, token_url = validate_spotify_credentials()
    user = await get_user_by_id(str(state))
    token_data = await exchange_spotify_authorization_code(
        code,
        client_id,
        client_secret,
        token_url,
    )
    refresh_token, access_token, expires_in = extract_spotify_tokens(token_data)
    await persist_spotify_tokens(user, refresh_token, access_token, expires_in)

    return {
        "user_id": str(user.id),
        "spotify_connected": True,
        "redirect_url": f"{FRONTEND_CONFIG['base_url']}/auth/spotify/return",
    }
