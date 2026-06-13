from uuid import UUID

from fastapi import HTTPException, status

from config.spotify import SPOTIFY_CONFIG
from dtos.song_review_dtos import CreateSongReviewDTO
from instances.http_client import get_http_client
from models.song_review import SongReview
from utils.reviews import to_song_review_response
from utils.spotify import (
    ensure_spotify_access_token_is_valid,
    extract_track_review_metadata,
)
from utils.users import get_user_by_id


async def main(user_id: UUID, body: CreateSongReviewDTO) -> dict:
    user = await get_user_by_id(str(user_id))
    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Spotify is not connected",
        )
    await ensure_spotify_access_token_is_valid(user)

    http_client = get_http_client()
    response = await http_client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/tracks/{body.spotify_song_id}",
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
        },
    )

    track = response.json()
    is_song_valid = track.get("id")

    if response.status_code != 200 or not is_song_valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to get song from Spotify",
        )

    track_metadata = extract_track_review_metadata(track)

    song_review = await SongReview.create(
        user_id=user_id,
        spotify_song_id=body.spotify_song_id,
        stars_count=body.stars_count,
        text=body.text,
        **track_metadata,
    )

    return to_song_review_response(song_review)
