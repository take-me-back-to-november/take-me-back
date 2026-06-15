from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSongReviewMessageDTO(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


class SongReviewMessageUserResponseDTO(BaseModel):
    id: UUID
    name: str | None
    picture_url: str | None


class SongReviewMessageResponseDTO(BaseModel):
    id: UUID
    text: str
    parent_id: UUID | None
    song_review_id: UUID | None
    created_at: datetime
    updated_at: datetime
    user: SongReviewMessageUserResponseDTO | None
