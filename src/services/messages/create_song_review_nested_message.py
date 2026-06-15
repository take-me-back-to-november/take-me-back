from uuid import UUID

from fastapi import HTTPException, status

from dtos.song_review_message_dtos import CreateSongReviewMessageDTO
from models.song_review_message import SongReviewMessage
from utils.song_review_messages import (
    resolve_review_id_for_message,
    to_song_review_message_response,
)
from utils.users import get_user_by_id


async def main(
    review_id: UUID,
    message_id: UUID,
    user_id: UUID,
    body: CreateSongReviewMessageDTO,
):
    parent_message = await SongReviewMessage.filter(
        id=message_id,
        deleted_at=None,
    ).first()
    if not parent_message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found",
        )

    parent_review_id = await resolve_review_id_for_message(message_id)
    if parent_review_id != review_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this review",
        )

    message = await SongReviewMessage.create(
        user_id=user_id,
        text=body.text,
        song_review_id=None,
        parent_id=message_id,
    )
    message.user = await get_user_by_id(str(user_id))

    return to_song_review_message_response(message)
