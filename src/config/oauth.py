import os

GOOGLE_OAUTH_CONFIG = {
    "base_url": os.getenv("GOOGLE_OAUTH_BASE_URL"),
    "client_id": os.getenv("GOOGLE_CLIENT_ID"),
}
