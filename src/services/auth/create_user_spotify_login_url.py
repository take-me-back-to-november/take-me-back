from uuid import UUID

from utils.spotify import build_spotify_authorize_url


def main(user_id: UUID):
    return {"url": build_spotify_authorize_url(user_id)}
