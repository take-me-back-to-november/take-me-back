from dtos.album_review_dtos import AlbumReviewResponseDTO
from models.album_review import AlbumReview


async def main(offset: int, limit: int, order_by: str, spotify_album_id: str | None):
    query_builder = AlbumReview.filter(deleted_at=None)
    if spotify_album_id:
        query_builder = query_builder.filter(spotify_album_id=spotify_album_id)
    query_builder = query_builder.order_by(order_by)
    query_builder = query_builder.offset(offset)
    query_builder = query_builder.limit(limit)
    reviews = await query_builder.all()
    return [AlbumReviewResponseDTO.model_validate(review) for review in reviews]
