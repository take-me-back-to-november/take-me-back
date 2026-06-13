import os

JWT_CONFIG = {
    "secret": os.getenv("JWT_SECRET"),
    "algorithm": os.getenv("JWT_ALGORITHM"),
    "expires_minutes": os.getenv("JWT_EXPIRES_MINUTES"),
}
