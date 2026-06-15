from utils.jwt import create_spotify_state_token
from utils.spotify import build_spotify_authorize_url


def main():
    state = create_spotify_state_token()
    return {"url": build_spotify_authorize_url(state)}
