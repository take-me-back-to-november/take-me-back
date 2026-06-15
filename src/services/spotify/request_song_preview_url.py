from uuid import UUID

from fastapi import HTTPException, status

from config.deezer import DEEZER_CONFIG
from config.spotify import SPOTIFY_CONFIG
from dtos.spotify_dtos import SongPreviewDTO
from instances.http_client import get_http_client
from utils.spotify import ensure_spotify_access_token_is_valid
from utils.users import get_user_by_id


async def main(user_id: UUID, spotify_song_id: str) -> SongPreviewDTO:
    user = await get_user_by_id(str(user_id))

    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have a Spotify refresh token",
        )

    await ensure_spotify_access_token_is_valid(user)
    http_client = get_http_client()

    spotify_response = await http_client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/tracks/{spotify_song_id}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
        },
    )

    if spotify_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch Spotify song",
        )

    spotify_song_data = spotify_response.json()
    isrc = spotify_song_data.get("external_ids", {}).get("isrc")

    if not isrc:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Spotify song does not have an ISRC code",
        )

    deezer_response = await http_client.get(
        f"{DEEZER_CONFIG['api_base_url']}/track/isrc:{isrc}",
    )

    if deezer_response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Failed to fetch Deezer song by ISRC",
        )

    preview_url = deezer_response.json().get("preview")
    if not preview_url:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preview not available for this song",
        )

    return SongPreviewDTO(preview_url=preview_url)
