from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSongReviewDTO(BaseModel):
    title: str = Field(min_length=1, max_length=50)
    text: str = Field(min_length=1, max_length=1000)
    stars_count: int = Field(ge=1, le=5)
    spotify_song_id: str


class SongReviewUserResponseDTO(BaseModel):
    id: UUID
    name: str | None
    picture_url: str | None


class SongReviewResponseDTO(BaseModel):
    id: UUID
    title: str
    stars_count: int
    text: str
    image_url: str | None
    song_name: str | None
    song_artist: str | None
    song_album: str | None
    spotify_song_id: str
    spotify_album_id: str | None
    spotify_artist_id: str | None
    user: SongReviewUserResponseDTO | None
    created_at: datetime
    updated_at: datetime


class SongReviewsPaginatedResponseDTO(BaseModel):
    items: list[SongReviewResponseDTO]
    has_next_page: bool
