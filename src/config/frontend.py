import os


def _normalize_base_url(url: str | None) -> str | None:
    if not url:
        return url
    return url.strip().rstrip("/")


def get_allowed_frontend_origins() -> set[str]:
    origins: set[str] = set()
    frontend_url = _normalize_base_url(os.getenv("FRONTEND_URL"))
    if frontend_url:
        origins.add(frontend_url)
    for origin in os.getenv("CORS_ALLOWED_ORIGINS", "").split(","):
        normalized = _normalize_base_url(origin)
        if normalized:
            origins.add(normalized)
    return origins


def get_validated_frontend_origin(return_to: str | None) -> str | None:
    normalized = _normalize_base_url(return_to)
    if normalized and normalized in get_allowed_frontend_origins():
        return normalized
    return None


def is_allowed_frontend_origin(return_to: str | None) -> bool:
    return get_validated_frontend_origin(return_to) is not None


def resolve_frontend_base_url(return_to: str | None) -> str:
    default = FRONTEND_CONFIG["base_url"]
    if not default:
        raise ValueError("FRONTEND_URL is not configured")
    validated = get_validated_frontend_origin(return_to)
    return validated or default


FRONTEND_CONFIG = {
    "base_url": _normalize_base_url(os.getenv("FRONTEND_URL")),
}
