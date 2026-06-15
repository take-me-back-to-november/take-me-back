from uuid import UUID

from fastapi import HTTPException, status

from models.song_review import SongReview
from models.song_review_message import SongReviewMessage
from utils.song_review_messages import (
    resolve_review_id_for_message,
    to_song_review_message_response,
)


async def main(review_id: UUID):
    song_review = await SongReview.filter(
        id=review_id,
        deleted_at=None,
    ).first()
    if not song_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    root_messages = await SongReviewMessage.filter(
        song_review_id=review_id,
        deleted_at=None,
    ).all()

    nested_messages = await SongReviewMessage.filter(
        parent_id__not_isnull=True,
        deleted_at=None,
    ).all()

    review_messages = list(root_messages)
    for message in nested_messages:
        message_review_id = await resolve_review_id_for_message(message.id)
        if message_review_id == review_id:
            review_messages.append(message)

    review_messages.sort(key=lambda message: message.created_at)
    await SongReviewMessage.fetch_for_list(review_messages, "user")

    return [to_song_review_message_response(message) for message in review_messages]
