import os


def _normalize_base_url(url: str | None) -> str | None:
    if not url:
        return url
    return url.strip().rstrip("/")


FRONTEND_CONFIG = {
    "base_url": _normalize_base_url(os.getenv("FRONTEND_URL")),
}
