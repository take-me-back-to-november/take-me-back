from uuid import UUID

from fastapi import HTTPException, status
from tortoise.query_utils import Prefetch

from models.song_review import SongReview
from models.user import User
from models.user_song_review_action import UserSongReviewAction
from utils.reviews import get_likes_counts, to_song_review_response


async def main(user_id: UUID):
    user = await User.filter(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    reviews = (
        await SongReview.filter(user_id=user_id, deleted_at=None)
        .order_by("-created_at")
        .prefetch_related(
            Prefetch(
                "song_review_actions",
                queryset=UserSongReviewAction.filter(
                    user_id=user_id,
                    deleted_at__isnull=True,
                ),
            ),
        )
        .all()
    )
    await SongReview.fetch_for_list(reviews, "user")
    likes_counts = await get_likes_counts([review.id for review in reviews])
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
        "spotify_connected": bool(user.spotify_refresh_token),
        "reviews_count": reviews_count,
        "reviews_average_stars": reviews_average_stars,
        "reviews": [
            to_song_review_response(review, likes_count=likes_counts.get(review.id, 0))
            for review in reviews
        ],
    }
