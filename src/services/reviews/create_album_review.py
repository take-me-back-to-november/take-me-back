from uuid import UUID

from dtos.album_review_dtos import AlbumReviewResponseDTO, CreateAlbumReviewDTO
from models.album_review import AlbumReview


async def main(user_id: UUID, body: CreateAlbumReviewDTO):
    album_review = await AlbumReview.create(
        user_id=user_id,
        description=body.description,
        spotify_album_id=body.spotify_album_id,
    )

    return AlbumReviewResponseDTO.model_validate(album_review)
