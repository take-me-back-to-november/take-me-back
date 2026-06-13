from uuid import UUID

from fastapi import HTTPException, status

from models.song_review import SongReview
from models.user import User
from utils.reviews import to_song_review_response


async def main(user_id: UUID) -> dict:
    user = await User.filter(id=user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    reviews = await SongReview.filter(user_id=user_id).order_by("-created_at").all()
    reviews_count = len(reviews)
    reviews_average_stars = (
        sum(review.stars_count for review in reviews) / reviews_count
        if reviews_count > 0
        else 0.0
    )

    return {
        "id": user.id,
        "name": user.name,
        "email": user.google_email,
        "picture_url": user.picture_url,
        "reviews_count": reviews_count,
        "reviews_average_stars": reviews_average_stars,
        "reviews": [to_song_review_response(review) for review in reviews],
    }
