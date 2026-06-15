from uuid import UUID

from fastapi import HTTPException, status

from models.song_review import SongReview


async def main(review_id: UUID, user_id: UUID):
    song_review = await SongReview.filter(
        id=review_id, user_id=user_id, deleted_at=None
    ).first()
    if not song_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )

    await song_review.soft_delete()
