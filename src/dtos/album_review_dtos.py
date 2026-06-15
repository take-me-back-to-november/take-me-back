from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateAlbumReviewDTO(BaseModel):
    description: str = Field(min_length=1, max_length=1000)
    spotify_album_id: str


class AlbumReviewResponseDTO(BaseModel):
    id: UUID
    description: str
    spotify_album_id: str
    user_id: UUID
    created_at: datetime
    updated_at: datetime
