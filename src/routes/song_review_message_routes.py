from uuid import UUID

from fastapi import APIRouter, Depends, status

from dependencies.auth import get_current_user_id
from dtos.song_review_message_dtos import CreateSongReviewMessageDTO
from services.messages.create_song_review_nested_message import (
    main as create_song_review_nested_message,
)
from services.messages.create_song_review_root_message import (
    main as create_song_review_root_message,
)
from services.messages.fetch_song_review_messages import (
    main as fetch_song_review_messages,
)

router = APIRouter(prefix="/reviews")


@router.post("/{review_id}/reply", status_code=status.HTTP_201_CREATED)
async def create_song_review_root_reply(
    review_id: UUID,
    body: CreateSongReviewMessageDTO,
    user_id: UUID = Depends(get_current_user_id),
):
    return await create_song_review_root_message(review_id, user_id, body)


@router.post(
    "/{review_id}/messages/{message_id}/reply",
    status_code=status.HTTP_201_CREATED,
)
async def create_song_review_nested_reply(
    review_id: UUID,
    message_id: UUID,
    body: CreateSongReviewMessageDTO,
    user_id: UUID = Depends(get_current_user_id),
):
    return await create_song_review_nested_message(
        review_id,
        message_id,
        user_id,
        body,
    )


@router.get("/{review_id}/messages", status_code=status.HTTP_200_OK)
async def get_song_review_messages(
    review_id: UUID,
    _: UUID = Depends(get_current_user_id),
):
    return await fetch_song_review_messages(review_id)
