from uuid import UUID

from fastapi import APIRouter, Depends, Query, status

from dependencies.auth import get_current_user_id
from dtos.album_review_dtos import CreateAlbumReviewDTO
from services.reviews.create_album_review import main as create_album_review
from services.reviews.fetch_album_reviews import main as fetch_album_reviews

router = APIRouter(prefix="/album-reviews")


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_album_review_route(
    body: CreateAlbumReviewDTO,
    user_id: UUID = Depends(get_current_user_id),
):
    return await create_album_review(user_id, body)


@router.get(
    "",
    dependencies=[Depends(get_current_user_id)],
    status_code=status.HTTP_200_OK,
)
async def fetch_album_reviews_route(
    offset: int = Query(default=0),
    limit: int = Query(default=10),
    order_by: str = Query(default="created_at"),
    spotify_album_id: str | None = Query(default=None),
):
    return await fetch_album_reviews(offset, limit, order_by, spotify_album_id)
