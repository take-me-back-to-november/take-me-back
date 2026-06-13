from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from dependencies.auth import get_current_user_id
from services.spotify.fetch_current_playing_song import (
    main as fetch_current_playing_song,
)
from services.spotify.fetch_spotify_albums import main as fetch_spotify_albums
from services.spotify.fetch_spotify_tracks import main as fetch_spotify_tracks
from services.spotify.fetch_user_most_listened_songs import (
    main as fetch_user_most_listened_songs,
)
from services.spotify.remove_user_spotify_attachment import (
    main as remove_spotify_link,
)

router = APIRouter(prefix="/spotify")


@router.get("/songs/me")
async def get_most_listened_songs(
    user_id: UUID = Depends(get_current_user_id),
    limit: int = Query(default=5),
):
    return await fetch_user_most_listened_songs(user_id, limit)


@router.get("/tracks/search")
async def search_tracks(
    user_id: UUID = Depends(get_current_user_id),
    search_query: str = Query(default=""),
):
    return await fetch_spotify_tracks(user_id, search_query)


@router.get("/albums/search")
async def search_albums(
    user_id: UUID = Depends(get_current_user_id),
    search_query: str = Query(default=""),
):
    return await fetch_spotify_albums(user_id, search_query)


@router.get(
    "/songs/currently-playing",
    status_code=status.HTTP_200_OK,
)
async def get_currently_playing_song(
    user_id: UUID = Depends(get_current_user_id),
):
    return await fetch_current_playing_song(str(user_id))


@router.delete("/me", status_code=status.HTTP_204_NO_CONTENT)
async def remove_spotify_attachment(
    user_id: UUID = Depends(get_current_user_id),
):
    await remove_spotify_link(user_id)
