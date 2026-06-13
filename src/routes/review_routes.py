from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from dependencies.auth import get_current_user_id
from dtos.song_review_dtos import CreateSongReviewDTO
from services.reviews.create_spotify_song_review import (
    main as create_spotify_song_review,
)
from services.reviews.fetch_spotify_song_review import main as fetch_spotify_song_review

router = APIRouter(prefix="/reviews")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_song_review(
    body: CreateSongReviewDTO,
    user_id: UUID = Depends(get_current_user_id),
):
    return await create_spotify_song_review(user_id, body)


@router.get(
    "",
    dependencies=[Depends(get_current_user_id)],
    status_code=status.HTTP_200_OK,
)
async def fetch_song_reviews(
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    order_by: str = Query(default="created_at"),
    spotify_song_id: str | None = Query(default=None),
):
    return await fetch_spotify_song_review(offset, limit, order_by, spotify_song_id)
