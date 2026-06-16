from uuid import UUID

from tortoise.query_utils import Prefetch

from dtos.song_review_dtos import SongReviewsPaginatedResponseDTO
from models.song_review import SongReview
from models.user_song_review_action import UserSongReviewAction
from utils.reviews import get_likes_counts, to_song_review_response


async def main(
    offset: int,
    limit: int,
    order_by: str,
    spotify_song_id: str | None,
    spotify_album_id: str | None,
    author_user_id: UUID | None,
    current_user_id: UUID,
):
    query_builder = SongReview.filter(deleted_at=None)
    if spotify_song_id:
        query_builder = query_builder.filter(spotify_song_id=spotify_song_id)
    if spotify_album_id:
        query_builder = query_builder.filter(spotify_album_id=spotify_album_id)
    if author_user_id:
        query_builder = query_builder.filter(user_id=author_user_id)
    query_builder = query_builder.order_by(order_by)
    query_builder = query_builder.offset(offset)
    query_builder = query_builder.limit(limit + 1)
    query_builder = query_builder.prefetch_related(
        Prefetch(
            "song_review_actions",
            queryset=UserSongReviewAction.filter(
                user_id=current_user_id,
                deleted_at__isnull=True,
            ),
        ),
    )

    reviews = await query_builder.all()
    has_next_page = len(reviews) > limit
    if has_next_page:
        reviews = reviews[:limit]

    await SongReview.fetch_for_list(reviews, "user")
    likes_counts = await get_likes_counts([review.id for review in reviews])
    return SongReviewsPaginatedResponseDTO(
        items=[
            to_song_review_response(review, likes_count=likes_counts.get(review.id, 0))
            for review in reviews
        ],
        has_next_page=has_next_page,
    )
