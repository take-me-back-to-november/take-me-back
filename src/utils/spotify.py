from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from urllib.parse import urlencode

from fastapi import HTTPException, status

from config.spotify import SPOTIFY_CONFIG
from dtos.spotify_dtos import (
    CurrentPlayingSongDTO,
    SpotifyAlbumDTO,
    SpotifySongDTO,
    SpotifyTrackReviewDataDTO,
)
from dtos.user_dtos import SpotifyProfileDTO
from instances.http_client import get_http_client
from models.user import User


def build_spotify_authorize_url(state: str) -> str:
    params = urlencode(
        {
            "response_type": "code",
            "client_id": SPOTIFY_CONFIG["client_id"],
            "redirect_uri": SPOTIFY_CONFIG["redirect_uri"],
            "scope": SPOTIFY_CONFIG["scope"],
            "state": state,
            "show_dialog": "true",
        }
    )
    return f"{SPOTIFY_CONFIG['authorize_url']}?{params}"


async def fetch_spotify_profile(access_token: str) -> SpotifyProfileDTO:
    client = get_http_client()
    response = await client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/me",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to fetch Spotify profile",
        )

    data = response.json()
    images = data.get("images") or []

    if not data.get("id"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spotify profile did not return an id",
        )

    return SpotifyProfileDTO(
        id=data["id"],
        display_name=data.get("display_name"),
        email=data.get("email"),
        image_url=images[0].get("url") if images else None,
    )


def validate_spotify_callback_params(code: str, state: str) -> None:
    if not code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing code parameter",
        )

    if not state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing state parameter",
        )


def validate_spotify_credentials() -> tuple[str, str, str]:
    client_id = SPOTIFY_CONFIG["client_id"]
    client_secret = SPOTIFY_CONFIG["client_secret"]
    token_url = SPOTIFY_CONFIG["token_url"]

    if not client_id or not client_secret:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Spotify client credentials are not configured",
        )

    if not token_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Spotify token URL is not configured",
        )

    return client_id, client_secret, token_url


async def exchange_spotify_authorization_code(
    code: str,
    client_id: str,
    client_secret: str,
    token_url: str,
) -> dict:
    client = get_http_client()
    response = await client.post(
        token_url,
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": SPOTIFY_CONFIG["redirect_uri"],
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to exchange Spotify authorization code",
        )

    data = response.json()
    return {
        "refresh_token": data.get("refresh_token"),
        "access_token": data.get("access_token"),
        "expires_in": data.get("expires_in"),
    }


def extract_spotify_tokens(token_data: dict) -> tuple[str, str, int]:
    refresh_token = token_data.get("refresh_token")
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spotify did not return a refresh token",
        )

    if not access_token or not expires_in:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Spotify did not return an access token",
        )

    return refresh_token, access_token, expires_in


async def persist_spotify_tokens(
    user: User,
    refresh_token: str,
    access_token: str,
    expires_in: int,
) -> None:
    user.spotify_refresh_token = refresh_token
    user.spotify_access_token = access_token
    user.spotify_access_token_expires_at = datetime.now(UTC) + timedelta(
        seconds=expires_in
    )
    await user.save()


def parse_spotify_track_review_data(track: dict[str, Any]) -> SpotifyTrackReviewDataDTO:
    album = track.get("album") or {}
    images = album.get("images") or []
    artists = track.get("artists") or []
    primary_artist = artists[0] if artists else {}
    artist_names = [artist.get("name", "") for artist in artists if artist.get("name")]

    return SpotifyTrackReviewDataDTO(
        spotify_album_id=album.get("id"),
        spotify_artist_id=primary_artist.get("id"),
        image_url=images[0].get("url") if images else None,
        song_name=track.get("name"),
        song_artist=", ".join(artist_names) or None,
        song_album=album.get("name"),
    )


def normalize_current_playing_song(payload: Any) -> CurrentPlayingSongDTO:
    item = payload["item"]
    album = item.get("album") or {}
    images = album.get("images") or []
    artists = item.get("artists") or []

    return CurrentPlayingSongDTO(
        id=item["id"],
        name=item["name"],
        artist=artists[0]["name"] if artists else "",
        album=album.get("name", ""),
        duration=item["duration_ms"],
        progress=payload["progress_ms"],
        image_url=images[0]["url"] if images else "",
        is_playing=payload["is_playing"],
    )


def normalize_spotify_album_list(payload: Any) -> list[SpotifyAlbumDTO]:
    items = payload.get("albums", {}).get("items", [])
    albums: list[SpotifyAlbumDTO] = []

    for item in items:
        if not item.get("id"):
            continue

        images = item.get("images") or []
        artist_names = [
            artist.get("name")
            for artist in item.get("artists", [])
            if artist.get("name")
        ]

        albums.append(
            SpotifyAlbumDTO(
                id=item["id"],
                type="album",
                title=item["name"],
                artist=", ".join(artist_names),
                year=int(item["release_date"].split("-")[0]),
                cover_url=images[0].get("url", "") if images else "",
                release_date=item["release_date"],
                total_tracks=item.get("total_tracks", 0),
                album_type=item.get("album_type", "album"),
                spotify_url=item.get("external_urls", {}).get("spotify"),
            )
        )

    return albums


def normalize_spotify_song_list(payload: Any) -> list[SpotifySongDTO]:
    if "tracks" in payload:
        items = payload.get("tracks", {}).get("items", [])
    else:
        items = payload.get("items", [])

    songs: list[SpotifySongDTO] = []

    for item in items:
        if not item.get("id"):
            continue

        album = item.get("album") or {}
        images = album.get("images") or []
        artist_names = [
            artist.get("name")
            for artist in item.get("artists", [])
            if artist.get("name")
        ]

        songs.append(
            SpotifySongDTO(
                id=item["id"],
                type="track",
                title=item["name"],
                artist=", ".join(artist_names),
                album_id=album["id"],
                album_title=album["name"],
                year=int(album["release_date"].split("-")[0]),
                cover_url=images[0].get("url", "") if images else "",
                release_date=album["release_date"],
                duration_ms=item.get("duration_ms", 0),
                explicit=bool(item.get("explicit", False)),
                spotify_url=item.get("external_urls", {}).get("spotify"),
            )
        )

    return songs


async def search_spotify(
    user: User,
    search_query: str,
    search_type: Literal["track", "album"],
    limit: int = 10,
) -> dict:
    await ensure_spotify_access_token_is_valid(user)

    http_client = get_http_client()
    response = await http_client.get(
        f"{SPOTIFY_CONFIG['api_base_url']}/search",
        params={
            "q": search_query,
            "type": search_type,
            "limit": limit,
            "offset": 0,
        },
        headers={
            "Authorization": f"Bearer {user.spotify_access_token}",
        },
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch Spotify search results",
        )

    return response.json()


async def refresh_spotify_access_token(user_id: str) -> None:
    client_id = SPOTIFY_CONFIG["client_id"]
    client_secret = SPOTIFY_CONFIG["client_secret"]
    token_url = SPOTIFY_CONFIG["token_url"]

    if not client_id or not client_secret or not token_url:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Spotify client credentials are not configured",
        )

    user = await User.filter(id=user_id, deleted_at=None).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    if not user.spotify_refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User does not have a Spotify refresh token",
        )

    http_client = get_http_client()
    response = await http_client.post(
        token_url,
        data={
            "grant_type": "refresh_token",
            "refresh_token": user.spotify_refresh_token,
        },
        auth=(client_id, client_secret),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to refresh Spotify access token",
        )

    token_data = response.json()
    access_token = token_data.get("access_token")
    expires_in = token_data.get("expires_in")

    if not access_token or not expires_in:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Spotify did not return a valid access token",
        )

    user.spotify_access_token = access_token
    user.spotify_access_token_expires_at = datetime.now(UTC) + timedelta(
        seconds=expires_in
    )

    new_refresh_token = token_data.get("refresh_token")
    if new_refresh_token:
        user.spotify_refresh_token = new_refresh_token

    await user.save()


async def ensure_spotify_access_token_is_valid(user: User) -> None:
    if (
        user.spotify_access_token_expires_at is None
        or user.spotify_access_token_expires_at < datetime.now(UTC)
    ):
        await refresh_spotify_access_token(str(user.id))
        refreshed_user = await User.filter(id=user.id, deleted_at=None).first()
        if not refreshed_user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )

        user.spotify_refresh_token = refreshed_user.spotify_refresh_token
        user.spotify_access_token = refreshed_user.spotify_access_token
        user.spotify_access_token_expires_at = (
            refreshed_user.spotify_access_token_expires_at
        )
