from uuid import UUID

from pydantic import BaseModel

from dtos.song_review_dtos import SongReviewResponseDTO


class CreateUserAndSessionDTO(BaseModel):
    google_id: str


class GoogleUserInfoDTO(BaseModel):
    sub: str | None
    email: str | None
    name: str | None
    given_name: str | None
    family_name: str | None
    picture: str | None
    hd: str | None
    email_verified: bool | None


class UserResponseDTO(BaseModel):
    id: UUID
    google_id: str
    google_email: str | None
    email_verified: bool | None
    name: str | None
    first_name: str | None
    last_name: str | None
    picture_url: str | None
    hosted_domain: str | None


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
    email: str
    picture_url: str | None
    spotify_connected: bool
    reviews_count: int
    reviews_average_stars: float
    reviews: list[SongReviewResponseDTO]
