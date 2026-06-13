from datetime import UTC, datetime, timedelta
from typing import Any, Literal
from urllib.parse import urlencode
from uuid import UUID

from fastapi import HTTPException, status

from config.spotify import SPOTIFY_CONFIG
from instances.http_client import get_http_client
from models.user import User


def build_spotify_authorize_url(user_id: UUID) -> str:
    params = urlencode(
        {
            "response_type": "code",
            "client_id": SPOTIFY_CONFIG["client_id"],
            "redirect_uri": SPOTIFY_CONFIG["redirect_uri"],
            "scope": SPOTIFY_CONFIG["scope"],
            "state": str(user_id),
            "show_dialog": "true",
        }
    )
    return f"{SPOTIFY_CONFIG['authorize_url']}?{params}"


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


def normalize_current_playing_song(payload: Any) -> dict:
    item = payload["item"]
    return {
        "id": item["id"],
        "name": item["name"],
        "artist": item["artists"][0]["name"],
        "album": item["album"]["name"],
        "duration": item["duration_ms"],
        "progress": payload["progress_ms"],
        "image_url": item["album"]["images"][0]["url"],
        "is_playing": payload["is_playing"],
    }


def extract_track_review_metadata(track: dict) -> dict:
    album = track.get("album")
    images = album.get("images")
    artists = track.get("artists")

    return {
        "image_url": images[0].get("url"),
        "song_name": track.get("name"),
        "song_artist": (
            ", ".join(
                artist.get("name", "") for artist in artists if artist.get("name")
            )
            or None
        ),
        "song_album": album.get("name"),
    }


def normalize_spotify_album_list(payload: Any) -> list[dict]:
    items = payload.get("albums", {}).get("items", [])
    normalized_album_list: list[dict] = []

    for item in items:
        images = item.get("images") or []
        cover_url = images[0].get("url") if images else ""
        artist_names = [artist.get("name") for artist in item.get("artists", [])]

        normalized_album_list.append(
            {
                "id": item["id"],
                "type": "album",
                "title": item["name"],
                "artist": ", ".join(name for name in artist_names if name),
                "year": int(item["release_date"].split("-")[0]),
                "cover_url": cover_url,
                "release_date": item["release_date"],
                "total_tracks": item.get("total_tracks", 0),
                "album_type": item.get("album_type", "album"),
                "spotify_url": item.get("external_urls", {}).get("spotify"),
            }
        )

    return normalized_album_list


def normalize_spotify_song_list(payload: Any) -> list[dict]:
    if "tracks" in payload:
        items = payload.get("tracks", {}).get("items", [])
    else:
        items = payload.get("items", [])

    normalized_song_list: list[dict] = []

    for item in items:
        track_id = item.get("id")
        album = item.get("album")
        images = album.get("images")
        cover_url = images[0].get("url")
        artist_names = [artist.get("name") for artist in item.get("artists")]

        normalized_song_list.append(
            {
                "id": track_id,
                "type": "track",
                "title": item["name"],
                "artist": ", ".join(artist_names),
                "album_id": album["id"],
                "album_title": album["name"],
                "year": int(album["release_date"].split("-")[0]),
                "cover_url": cover_url,
                "release_date": album["release_date"],
                "duration_ms": item.get("duration_ms", 0),
                "explicit": bool(item.get("explicit", False)),
                "spotify_url": item.get("external_urls", {}).get("spotify"),
            }
        )
    return normalized_song_list


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

    user = await User.filter(id=user_id).first()
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
        await user.refresh_from_db()
