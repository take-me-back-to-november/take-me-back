from fastapi import HTTPException, status

from config.spotify import SPOTIFY_CONFIG
from instances.http_client import get_http_client
from utils.spotify import (
    ensure_spotify_access_token_is_valid,
    normalize_spotify_song_list,
)
from utils.users import get_user_by_id


async def main(user_id: str, limit: int) -> list[dict]:
    user = await get_user_by_id(user_id)

    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have a Spotify refresh token",
        )

    await ensure_spotify_access_token_is_valid(user)

    http_client = get_http_client()
    response = await http_client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/me/top/tracks?limit={limit}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
        },
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch most listened songs",
        )

    payload = response.json()
    return normalize_spotify_song_list(payload)
