from fastapi import HTTPException, status

from config.spotify import SPOTIFY_CONFIG
from instances.http_client import get_http_client
from utils.spotify import (
    ensure_spotify_access_token_is_valid,
    normalize_current_playing_song,
)
from utils.users import get_user_by_id


async def main(user_id: str):
    user = await get_user_by_id(user_id)
    await ensure_spotify_access_token_is_valid(user)

    http_client = get_http_client()
    response = await http_client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/me/player/currently-playing",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
        },
    )

    if response.status_code == status.HTTP_204_NO_CONTENT:
        return None

    print(response)

    if response.status_code != status.HTTP_200_OK:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch current playing song",
        )

    return normalize_current_playing_song(response.json())
