from uuid import UUID

from fastapi import HTTPException, status

from models.song_review_message import SongReviewMessage
from models.user import User


def _get_message_author(message: SongReviewMessage) -> User | None:
    author = getattr(message, "_user", None)
    if isinstance(author, User):
        return author
    return None


def to_song_review_message_response(message: SongReviewMessage) -> dict:
    author = _get_message_author(message)
    return {
        "id": message.id,
        "text": message.text,
        "parent_id": message.parent_id,
        "song_review_id": message.song_review_id,
        "created_at": message.created_at,
        "updated_at": message.updated_at,
        "user": {
            "id": author.id,
            "name": author.name,
            "picture_url": author.picture_url,
        }
        if author
        else None,
    }


async def resolve_review_id_for_message(message_id: UUID) -> UUID:
    current_id = message_id
    visited: set[UUID] = set()

    while current_id is not None:
        if current_id in visited:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )
        visited.add(current_id)

        message = await SongReviewMessage.filter(
            id=current_id,
            deleted_at=None,
        ).first()
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found",
            )

        if message.song_review_id is not None:
            return message.song_review_id

        current_id = message.parent_id

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Message not found",
    )
