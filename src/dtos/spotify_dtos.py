from typing import Literal

from pydantic import BaseModel


class SpotifyAlbumDTO(BaseModel):
    id: str
    type: Literal["album"]
    title: str
    artist: str
    year: int
    cover_url: str
    release_date: str
    total_tracks: int
    album_type: str
    spotify_url: str | None


class SpotifySongDTO(BaseModel):
    id: str
    type: Literal["track"]
    title: str
    artist: str
    album_id: str
    album_title: str
    year: int
    cover_url: str
    release_date: str
    duration_ms: int
    explicit: bool
    spotify_url: str | None


class CurrentPlayingSongDTO(BaseModel):
    id: str
    name: str
    artist: str
    album: str
    duration: int
    progress: int
    image_url: str
    is_playing: bool


class SongPreviewDTO(BaseModel):
    preview_url: str


class SpotifyTrackReviewDataDTO(BaseModel):
    spotify_album_id: str | None
    spotify_artist_id: str | None
    image_url: str | None
    song_name: str | None
    song_artist: str | None
    song_album: str | None
