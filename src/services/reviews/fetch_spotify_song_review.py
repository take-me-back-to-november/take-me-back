from models.song_review import SongReview
from utils.reviews import to_song_review_response


async def main(
    offset: int, limit: int, order_by: str, spotify_song_id: str | None
) -> list[dict]:
    query_builder = SongReview.filter()
    if spotify_song_id:
        query_builder = query_builder.filter(spotify_song_id=spotify_song_id)
    query_builder = query_builder.order_by(order_by)
    query_builder = query_builder.offset(offset)
    query_builder = query_builder.limit(limit)
    reviews = await query_builder.all()
    return [to_song_review_response(review) for review in reviews]
