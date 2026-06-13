from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field


class CreateSongReviewDTO(BaseModel):
    text: str = Field(min_length=1, max_length=1000)
    stars_count: int = Field(ge=1, le=5)
    spotify_song_id: str


class SongReviewResponseDTO(BaseModel):
    id: UUID
    stars_count: int
    text: str
    image_url: str | None
    song_name: str | None
    song_artist: str | None
    song_album: str | None
    likes_count: int
    unlikes_count: int
    spotify_song_id: str
    created_at: datetime
    updated_at: datetime
