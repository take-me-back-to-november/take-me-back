from uuid import UUID

from pydantic import BaseModel

from dtos.song_review_dtos import SongReviewResponseDTO


class SpotifyProfileDTO(BaseModel):
    id: str
    display_name: str | None
    email: str | None
    image_url: str | None


class UserResponseDTO(BaseModel):
    id: UUID
    spotify_id: str
    email: str | None
    name: str | None
    picture_url: str | None


class AuthResponseDTO(BaseModel):
    user: UserResponseDTO
    access_token: str
    refresh_token: str


class RefreshTokenDTO(BaseModel):
    refresh_token: str


class RefreshTokenResponseDTO(BaseModel):
    access_token: str


class SpotifyAuthUrlResponseDTO(BaseModel):
    url: str


class SpotifyTokenResponseDTO(BaseModel):
    refresh_token: str | None
    access_token: str | None
    expires_in: int | None


class SpotifyCallbackResultDTO(BaseModel):
    user_id: str
    spotify_connected: bool
    redirect_url: str


class UserResumeDTO(BaseModel):
    id: UUID
    name: str
    email: str | None
    picture_url: str | None
    spotify_connected: bool
    reviews_count: int
    reviews_average_stars: float
    reviews: list[SongReviewResponseDTO]
