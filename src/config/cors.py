import os

CORS_ALLOW_ORIGINS = [
    origin.strip().rstrip("/")
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
]
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOW_METHODS = ["*"]
CORS_ALLOW_HEADERS = ["*"]

CORS_ARGS = {
    "allow_origins": CORS_ALLOW_ORIGINS,
    "allow_credentials": CORS_ALLOW_CREDENTIALS,
    "allow_methods": CORS_ALLOW_METHODS,
    "allow_headers": CORS_ALLOW_HEADERS,
}
