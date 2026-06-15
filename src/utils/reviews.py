from uuid import UUID

from models.song_review import SongReview
from models.user import User
from models.user_song_review_action import UserSongReviewAction


async def get_likes_counts(review_ids: list[UUID]) -> dict[UUID, int]:
    if not review_ids:
        return {}

    counts: dict[UUID, int] = {}
    actions = await UserSongReviewAction.filter(
        song_review_id__in=review_ids,
        action="like",
        deleted_at__isnull=True,
    ).values_list("song_review_id", flat=True)

    for review_id in actions:
        counts[review_id] = counts.get(review_id, 0) + 1

    return counts


def _get_review_author(review: SongReview) -> User | None:
    author = getattr(review, "_user", None)
    if isinstance(author, User):
        return author
    return None


def _get_review_actions(review: SongReview) -> list[UserSongReviewAction]:
    relation = getattr(review, "_song_review_actions", None)
    if relation is None or not relation._fetched:
        return []
    return relation.related_objects


def to_song_review_response(review: SongReview, *, likes_count: int = 0) -> dict:
    author = _get_review_author(review)
    return {
        "id": review.id,
        "title": review.title,
        "stars_count": review.stars_count,
        "text": review.text,
        "image_url": review.image_url,
        "song_name": review.song_name,
        "song_artist": review.song_artist,
        "song_album": review.song_album,
        "spotify_song_id": review.spotify_song_id,
        "spotify_album_id": review.spotify_album_id,
        "spotify_artist_id": review.spotify_artist_id,
        "created_at": review.created_at,
        "updated_at": review.updated_at,
        "likes_count": likes_count,
        "actions": [
            {
                "id": action.id,
                "action": action.action,
            }
            for action in _get_review_actions(review)
        ],
        "user": {
            "id": author.id,
            "name": author.name,
            "picture_url": author.picture_url,
        }
        if author
        else None,
    }
