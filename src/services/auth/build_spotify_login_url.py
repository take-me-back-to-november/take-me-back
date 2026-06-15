from config.frontend import get_validated_frontend_origin
from utils.jwt import create_spotify_state_token
from utils.spotify import build_spotify_authorize_url


def main(return_to: str | None = None):
    state = create_spotify_state_token(
        return_to=get_validated_frontend_origin(return_to)
    )
    return {"url": build_spotify_authorize_url(state)}
