from uuid import UUID

from fastapi import HTTPException

from dtos.spotify_dtos import SpotifyAlbumDTO
from utils.spotify import normalize_spotify_album_list, search_spotify
from utils.users import get_user_by_id


async def main(user_id: UUID, search_query: str):
    user = await get_user_by_id(str(user_id))

    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=401, detail="User does not have a Spotify refresh token"
        )

    payload = await search_spotify(user, search_query, "album")
    albums = normalize_spotify_album_list(payload)

    return [
        SpotifyAlbumDTO(
            id=album["id"],
            type=album["type"],
            title=album["title"],
            artist=album["artist"],
            year=album["year"],
            cover_url=album["cover_url"],
            release_date=album["release_date"],
            total_tracks=album["total_tracks"],
            album_type=album["album_type"],
            spotify_url=album["spotify_url"],
        )
        for album in albums
    ]
