import os

SPOTIFY_CONFIG = {
    "authorize_url": os.getenv("SPOTIFY_AUTHORIZE_URL"),
    "token_url": os.getenv("SPOTIFY_TOKEN_URL"),
    "api_base_url": os.getenv("SPOTIFY_API_BASE_URL"),
    "client_id": os.getenv("SPOTIFY_CLIENT_ID"),
    "client_secret": os.getenv("SPOTIFY_CLIENT_SECRET"),
    "redirect_uri": os.getenv("SPOTIFY_REDIRECT_URI"),
    "scope": os.getenv("SPOTIFY_SCOPE"),
}
