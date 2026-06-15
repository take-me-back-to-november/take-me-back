from uuid import UUID

from fastapi import HTTPException, status

from dtos.song_review_message_dtos import CreateSongReviewMessageDTO
from models.song_review import SongReview
from models.song_review_message import SongReviewMessage
from utils.song_review_messages import to_song_review_message_response
from utils.users import get_user_by_id


async def main(
    review_id: UUID,
    user_id: UUID,
    body: CreateSongReviewMessageDTO,
):
    song_review = await SongReview.filter(
        id=review_id,
        deleted_at=None,
    ).first()
    if not song_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    message = await SongReviewMessage.create(
        user_id=user_id,
        text=body.text,
        song_review_id=review_id,
        parent_id=None,
    )
    message.user = await get_user_by_id(str(user_id))

    return to_song_review_message_response(message)
