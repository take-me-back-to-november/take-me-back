from uuid import UUID

from fastapi import HTTPException

from dtos.spotify_dtos import SpotifySongDTO
from utils.spotify import normalize_spotify_song_list, search_spotify
from utils.users import get_user_by_id


async def main(user_id: UUID, search_query: str):
    user = await get_user_by_id(str(user_id))

    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=401, detail="User does not have a Spotify refresh token"
        )

    payload = await search_spotify(user, search_query, "track")
    tracks = normalize_spotify_song_list(payload)

    return [
        SpotifySongDTO(
            id=track["id"],
            type=track["type"],
            title=track["title"],
            artist=track["artist"],
            album_id=track["album_id"],
            album_title=track["album_title"],
            year=track["year"],
            cover_url=track["cover_url"],
            release_date=track["release_date"],
            duration_ms=track["duration_ms"],
            explicit=track["explicit"],
            spotify_url=track["spotify_url"],
        )
        for track in tracks
    ]
